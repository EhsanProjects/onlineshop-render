from datetime import datetime
from sqlalchemy import null
import stripe
import math
from flask import Blueprint, render_template, request, redirect, url_for, flash,session,current_app 
from flask_login import login_user, login_required, current_user,logout_user
from passlib.hash import sha256_crypt
from extensions import db
from models.cart import Cart
from models.Payment import Payment
from models.cart_item import CartItem
from models.coupon import Coupon
from models.product import Product
import os

from models.shepa_log import ShepaStatusLog
IS_DEV = os.environ.get('FLASK_ENV') == 'development'

def check_shepa_status():
    try:
        response = requests.get("https://sandbox.shepa.com", timeout=3)
        if response.status_code >= 500:
            flash("Shepa.com is currently experiencing server issues. Please try again later.", "danger")
            log = ShepaStatusLog(status="DOWN", message=f"HTTP {response.status_code}",user_id=current_user.id)  # ✅ use logged-in user
            db.session.add(log)
            db.session.commit()
            return False
        # Log successful status
        log = ShepaStatusLog(status="UP", message="Service available",user_id=current_user.id)  # ✅ use logged-in user
        db.session.add(log)
        db.session.commit()
        return True
    except requests.RequestException as e:
        flash("Cannot connect to Shepa.com to make a payment. It may be down. Please try again later.", "danger")
        log = ShepaStatusLog(status="DOWN", message=str(e),user_id=current_user.id)  # ✅ use logged-in user
        db.session.add(log)
        db.session.commit()
        return False

# Added
from models.product_set import ProductSet
from models.product_discount import ProductDiscount
from models.rate import Rate
from models.cart import  Cart
from models.user import User
import models.user
import requests
import config
import logging

# user_bp = Blueprint("user", __name__, url_prefix="/user")
user_bp = Blueprint("user", __name__)

def apply_coupon(coupon_code, cart):
    discount_percent = 0
    discounted_total = cart.total_price()

    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code).first()
        if coupon:
            # Check if the coupon is valid (active, not expired, and usage limit not exceeded)
            if coupon.active and coupon.end_date >= datetime.now().date() and \
                    ((coupon.used_count < coupon.usage_limit) or coupon.usage_limit == -1):
                discount_percent = coupon.discount_percent
                session['coupon_code'] = coupon_code  # Store the coupon code in the session
                flash(f'Coupon "{coupon_code}" applied successfully!', 'success')
            else:
                flash('Coupon is invalid or expired.', 'danger')
        else:
            flash('Coupon not found.', 'danger')
    
    # Calculate the total price with the discount if any
    if discount_percent > 0:
        discounted_total = cart.total_price() * (1 - discount_percent / 100)

    # Store the discounted total price in the session
    session['discounted_total'] = math.ceil(discounted_total)

    return discounted_total

@user_bp.app_template_filter('ceil')
# @app.app_template_filter('ceil')
def ceil_filter(value):
    return math.ceil(value)
@user_bp.route('/user/login', methods=['GET', 'POST'])
# @user.route('/user/login', methods=['GET', 'POST'])
def login():  # put application's code here
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect (url_for('user.dashboard'))

        return render_template('user/login.html')
    else:
        register = request.form.get('register', None)
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        phone = request.form.get('phone', None)
        address = request.form.get('address', None)
        if register != None:
            user = User.query.filter(User.username == username).first()
            if user != None:
                flash('That username is taken. Try another.')
                return redirect(url_for('user.login'))

            user = User(username=username, password=sha256_crypt.encrypt(password), phone=phone, address=address)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('user.dashboard'))
        else:
            user = User.query.filter(User.username == username).first()
            if user == None:
                flash('Wrong password or username. Try again or click Forgot password to reset it.')
                return redirect(url_for('user.login'))
        if sha256_crypt.verify(password, user.password):
            login_user(user)
            return redirect(url_for('user.dashboard'))
        else:
            flash('Wrong password or username. Try again or click Forgot password to reset it.')
            return redirect(url_for('user.login'))



@user_bp.route('/user/add-to-cart', methods=['GET'])
@login_required
def add_to_cart():
    id = request.args.get('id')
    product = Product.query.filter(Product.id == id).first_or_404()
    cart = current_user.carts.filter(Cart.status == 'pending').first()
    if cart == None:
        cart = Cart()
        current_user.carts.append(cart)
        db.session.add(cart)

    cart_item = cart.cart_items.filter(CartItem.product == product).first()

    if cart_item == None:
        item = CartItem(quantity=1)
        item.price = product.price
        item.cart = cart
        item.product = product
        db.session.add(item)
    else:
        cart_item.quantity += 1


    db.session.commit()

    return redirect(url_for('user.cart'))



# ----------------------------------------------------------------------------
@user_bp.route('/user/remove-from-cart', methods=['GET'])
@login_required
def remove_from_cart():
    id = request.args.get('id')
    cart_item = CartItem.query.filter(CartItem.id == id).first_or_404()
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('user.cart'))


# ----------------------------------------------------------------------------
@user_bp.route('/user/cart', methods=['GET', 'POST'])
@login_required
def cart():
    cart = current_user.carts.filter(Cart.status == 'pending').first()
    if not cart :
        flash('Your cart is empty.', 'warning')
        return render_template('user/cart.html', cart=None, discounted_total=0)
    # Initialize discounted_total with the default cart total price
    discounted_total = cart.total_price()

    if request.method == 'POST':
        coupon_code = request.form.get('coupon_code')
        discounted_total = apply_coupon(coupon_code, cart)  
    else:
        coupon_code = request.form.get('coupon_code')
        discounted_total = apply_coupon(coupon_code, cart)
         # Retrieve discounted total price from session
        discounted_total = session.get('discounted_total',cart.total_price())
    return render_template('user/cart.html', cart=cart, discounted_total=discounted_total)
# ------------------------------------------------------
@user_bp.route('/payment', methods=['GET'])
@login_required
def payment():
    cart = current_user.carts.filter(Cart.status == 'pending').first()
    
    if not cart:
        flash('No pending cart found.', 'danger')
        return redirect(url_for('user.cart'))  # Ensure you have a 'cart' route
    
    if not check_shepa_status(): # Check Shepa availability before calling their API
        flash('No Shepa.com availability.', 'danger')
        
        amount=session.get('discounted_total', cart.total_price())
        pay = Payment(price=amount, token="504 Gateway Timeout")
        pay.cart = cart
        pay.status="error"
        pay.cart_id= cart
        
        db.session.add(pay)
        db.session.commit()
        return redirect(url_for('user.cart'))

    try:
        
        discounted_total = session.get('discounted_total', cart.total_price())
        amount=discounted_total 

        print("this is :",amount)
        r = requests.post(config.PAYMENT_FIRST_REQUEST_URL, data={
            'api': config.PAYMENT_MERCHANT,
            'amount': amount,
            'callback': config.PAYMENT_CALLBACK
        })

        r.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        response_data = r.json()
        print(response_data)
        # Log the entire response for debugging purposes
        current_app.logger.debug('Response from payment API: %s', response_data)

        # Check if the expected keys are in the response
        if 'result' not in response_data :
            current_app.logger.error('Unexpected response format: %s', response_data)
            flash('1Payment request failed. Please try again later.', 'danger')
            return redirect(url_for('user.cart')) # Ensure you have a 'cart' route
        
        if 'token' not in response_data['result'] or 'url' not in response_data['result']:
                    current_app.logger.error('Unexpected response format: %s', response_data)
                    flash('2Payment request failed. Please try again later.', 'danger')
                    return redirect(url_for('user.cart')) # Ensure you have a 'cart' route
        if  'url' not in response_data['result']:
                    current_app.logger.error('Unexpected response format: %s', response_data)
                    flash('3Payment request failed. Please try again later.', 'danger')
                    return redirect(url_for('user.cart')) # Ensure you have a 'cart' route
        token = response_data['result']['token']
        url = response_data['result']['url']

        pay = Payment(price=amount, token=token)
        pay.cart = cart
        db.session.add(pay)
        db.session.commit()

        return redirect(url)

    except requests.RequestException as e:
        current_app.logger.error('Payment request failed: %s', e)
        # Optional: show debug info in development
        if IS_DEV:
            flash(f'Debug info: {str(e)}', 'warning')
        # Check if the error indicates a Gateway Timeout
        if '504' in str(e) or 'Gateway Timeout' in str(e):
            flash('The payment gateway (Shepa) is temporarily down (504 Gateway Timeout). Please try again later.', 'danger')
        else:
            flash('4Payment request failed. Please try again later.', 'danger')
        return redirect(url_for('user.cart'))  # Ensure you have a 'cart' route

    except KeyError as e:
        current_app.logger.error('Key error: %s', e)
        flash('Unexpected response from the payment server. Please try again later.', 'danger')
        return redirect(url_for('user.cart'))  # Ensure you have a 'cart' route
    


@user_bp.route('/verify', methods=['GET'])
@login_required
def verify():
    token = request.args.get('token')
    pay = Payment.query.filter(Payment.token == token).first_or_404()
    r = requests.post(config.PAYMENT_VERIFY_REQUEST_URL,
                      data={
                          'api': 'sandbox',
                          'amount': pay.price,
                          'token': token
                      })

    pay_status = bool(r.json()['success'])
    print("pay status: ",pay_status)
    if pay_status:
        print("pay status2: ",pay_status)
        transaction_id = r.json()['result']['transaction_id']
        refid = r.json()['result']['refid']
        card_pan = r.json()['result']['card_pan']

        pay.card_pan = card_pan
        pay.transaction_id = transaction_id
        pay.refid = refid
        pay.status = 'success'
        pay.cart.status = 'paid'
        pay.amount_to_pay= session.get('discounted_total')
        # Retrieve the coupon used and increment its used_count

        coupon_code = session.get('coupon_code')
        print("coupan code ",coupon_code)
        if coupon_code:
            print("coupan code is none ",coupon_code)
            coupon_id = Coupon.query.filter(Coupon.code == coupon_code).first_or_404()
            pay.coupon_id= coupon_id.id
            coupon = Coupon.query.filter_by(code=coupon_code).first_or_404()
            if coupon:
                coupon.used_count += 1
                db.session.add(coupon)
        # Clear the discounted total from session
        session.pop('discounted_total', None)
        # Clear the coupon_code from session
        session.pop('coupon_code', None)
        flash("پرداخت موفق آمیز بود")
    else:
        flash("پرداخت با خطا مواجه شد")
        pay.status = 'failed'

    db.session.commit()

    return redirect(url_for('user.dashboard'))




# -------------------------------------------------------------------------
@user_bp.route('/user/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method=='GET':
        return render_template(('user/dashboard.html'))
    else:
        username = request.form.get('username', None)
        
        phone = request.form.get('phone', None)
        address = request.form.get('address', None)
        user = User.query.filter(User.username == username).first()

        current_user.address = address
        current_user.phone = phone


        db.session.commit()
        flash('Profile is updated')
        return redirect(url_for('user.dashboard'))


@user_bp.route('/user/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Logout was successful')
    return redirect('/')

@user_bp.route('/user/dashboard/order/<id>', methods=['GET'])
@login_required
def order(id):
    cart = current_user.carts.filter(Cart.id == id).first_or_404()
   
    payments = []
    for pay in cart.payments:
        payment_info = {
            'status': pay.status,
            'refid': pay.refid,
            'transaction_id': pay.transaction_id,
            'card_pan': pay.card_pan,
            'date_created': pay.date_created,
            'amount_to_pay': pay.amount_to_pay,
            'coupon_code': pay.coupon.code if pay.coupon else None,
            'discount_percent': pay.coupon.discount_percent if pay.coupon else None
        }
        
        payments.append(payment_info)
        # print(payments)
    return render_template('user/order.html', cart=cart,payments=payments)

# Added

# user = Blueprint("user", __name__)
