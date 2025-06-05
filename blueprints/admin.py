import os
from datetime import date, datetime
from flask import Blueprint, render_template, request, session, redirect, abort, url_for,flash,Flask
# Added
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField,PasswordField
from wtforms.validators import InputRequired, length,AnyOf
import requests
from sqlalchemy import text

import config

from extensions import db
from models.coupon import Coupon
from models.cart import Cart
from models.product import Product
from models.product_discount import ProductDiscount
from models.product_set import ProductSet
from models.user import User

app = Blueprint("admin", __name__)

# # Added
# RECAPTCHA_PUBLIC_KEY = '6LdUuQcqAAAAAH4IoOikoKuVH7NJhSBbaCH_86MD'
# RECAPTCHA_PRIVATE_KEY ='6LdUuQcqAAAAACN8W0_IUxBJPMLC6sgzwpaq4H8l'

@app.before_request
def before_request():
    # print(request.endpoint)
    if session.get('admin_login', None) is None and request.endpoint != "admin.login":
        abort(403)
# Added
class LoginForm(FlaskForm):
    username = StringField('Username',validators=[InputRequired('User is required!'),length(min=5,max=10,message='Must be between 5 and 10 characters')])
    password = PasswordField('Password', validators=[InputRequired('Password is required!')])
    recaptcha = RecaptchaField()

@app.route('/admin/login', methods=["POST", "GET"])
def login():
    login = LoginForm()
    if login.validate_on_submit():
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['admin_login'] = username
            return redirect("/admin/dashboard")
        else:
            return redirect("/admin/login")
    return render_template("/admin/login.html",login=login)
    # if request.method == "POST":

    #     # Added
    #     # print(request.form)
    #     # secret_response = request.form['g-recaptcha-response']
    #     # verify_response = requests.post(url=f'{{VERIFY_URL}}?secret={{SECRET_KEY_RECAPTCHA}}&response={secret_response}').json()
    #     # print(verify_response)
    #     # if verify_response['success'] == False or verify_response['score'] <0.5:
    #     #     abort(401)



    # else:
    #     return render_template("/admin/login.html")


@app.route('/admin/dashboard', methods=["GET"])
def dashboard():
    sort_by = request.args.get('sort_by', 'username')  # Default to 'username'
    sort_order = request.args.get('sort_order', 'asc')
    # Define valid columns to sort by
    valid_sort_columns = {
        # 'order_number': Cart.id,
        'username': User.username,
        'phone': User.phone,
        'status': Cart.status
    }
    
    # Get the column to sort by, or default to 'order_number' if the column is invalid
    sort_column = valid_sort_columns.get(sort_by, User.username)
    query = text('''
        SELECT 
            u.username AS username,
            u.phone AS phone,
            c.status AS status,
            COUNT(c.id) AS OrderCount
        FROM 
            users AS u
        JOIN 
            carts AS c
            ON u.id = c.user_id
        
        GROUP BY 
            u.username, c.status
        ORDER BY 
            {} {};
    '''.format(sort_by, sort_order))
    # Apply sort order
   
    orders = db.session.execute(query).fetchall()
    detailed_orders = None
    
    return render_template('admin/dashboard.html', carts=orders, detailed_orders=detailed_orders)
    
    # Query to get all orders, with sorting
    # orders = db.session.query(Cart).join(User).order_by(sort_column).all()
    # return render_template('admin/dashboard.html', carts=orders)

@app.route('/admin/order_details', methods=["GET"])
def order_details():
    username = request.args.get('username')
    status = request.args.get('status')
    order_number = request.args.get('order_number', None)  # Optional parameter for specific order details

    if order_number:
        TotalPrice_query =  text('''
            select sum(ci.quantity* ci.price) as TotalPrice
            from users as u
            join carts as c 
            on u.id=c.user_id
            join cart_items as ci
            on ci.cart_id=c.id
            WHERE 
                ci.cart_id = :order_number
        ''')
        # Query to fetch all items in the specific order
        item_query = text('''
            SELECT 
                p.id AS product_id,
                p.name AS product_name,
                ci.price AS price,
                ci.quantity AS quantity,
                (ci.price * ci.quantity) AS subtotal
            FROM 
                cart_items AS ci
            JOIN 
                products AS p
                ON ci.product_id = p.id
            WHERE 
                ci.cart_id = :order_number
        ''')
        paymentInfo_query =text('''
            select p.cart_id as paymentid, p.status,
                p.refid,
                p.transaction_id,
                p.card_pan,
                p.date_created,
                p.amount_to_pay,
                co.code,
                co.discount_percent
            from payments as p
            left join coupons as co
                on p.coupon_id = co.id
            where p.cart_id= :order_number
        ''')
        order_items = db.session.execute(item_query, {'order_number': order_number}).fetchall()
        TotalPrice = db.session.execute(TotalPrice_query, {'order_number': order_number}).fetchall()
        paymentInfo = db.session.execute(paymentInfo_query, {'order_number': order_number}).fetchall()
 
        # Fetch details for the order along with its items
        return render_template('admin/order_details.html', order_items=order_items, order_number=order_number,cart=TotalPrice,paymentInfo=paymentInfo)
    else:
        # Original detailed order query




        detailed_query = text('''
            SELECT 
                c.id AS order_number,
                p.name AS product_name,
                ci.quantity AS quantity,
                sum(ci.price * ci.quantity) AS total_price,
                u.username AS username,
                c.status AS status
            FROM 
                cart_items AS ci
            JOIN 
                products AS p
                ON ci.product_id = p.id
            JOIN 
                users AS u
                ON c.user_id = u.id
            JOIN 
                carts AS c
                ON ci.cart_id = c.id
        WHERE
            u.username = :username
            AND c.status = :status
        GROUP BY 
            c.id;
        ''')
        
        detailed_orders = db.session.execute(detailed_query, {'username': username, 'status': status}).fetchall()
        
        # Re-run the main query to show the original grouped orders
        return dashboard_with_details(detailed_orders)

def dashboard_with_details(detailed_orders):
    sort_by = request.args.get('sort_by', 'username')  # Default to 'username'
    sort_order = request.args.get('sort_order', 'asc')
    
    # Define valid columns to sort by
    valid_sort_columns = {
        'username': User.username,
        'phone': User.phone,
        'status': Cart.status
    }
    
    sort_column = valid_sort_columns.get(sort_by, User.username)
    
    # Query to get grouped orders
    query = text('''
        SELECT 
            u.username AS username,
            u.phone AS phone,
            c.status AS status,
            COUNT(c.id) AS OrderCount
        FROM 
            users AS u
        JOIN 
            carts AS c
            ON u.id = c.user_id
        GROUP BY 
            u.username, c.status
        ORDER BY 
            {} {};
    '''.format(sort_by, sort_order))
    
    orders = db.session.execute(query).fetchall()
    
    return render_template('admin/dashboard.html', carts=orders, detailed_orders=detailed_orders)

# ------------------------------------------------------------------------------

@app.route('/admin/dashboard/order/<id>', methods=["GET", "POST"])
def order(id):
    cart = Cart.query.filter(Cart.id == id).first_or_404()
    if request.method == "GET":
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
        return render_template('admin/order.html', cart=cart,payments=payments)

        # return render_template("admin/order.html", cart=cart)
    else:
        status = request.form.get('status')
        cart.status = status
        db.session.commit()
        flash("Status is updated successfully")
        return redirect(url_for('admin.order', id=id))


@app.route('/admin/dashboard/products', methods=["GET", "POST"])
def products():
    if request.method == "GET":
        products = Product.query.all()
        discounts = ProductDiscount.query.all()
        productsset=ProductSet.query.all()
        # print("Products:", products)
        # print("Discounts:", discounts)
        # print(productsset)
         # Create a dictionary mapping discount_id to discountpercent
        product_discounts = {discount.id: discount.discountpercent for discount in discounts}
        discounts_active = {discount.id: discount.active for discount in discounts}
        discount_expiration ={discount.id: discount.expiration_date for discount in discounts}
        return render_template("admin/products.html",today = date.today(),discount_expiration=discount_expiration,discounts=discounts,discounts_active=discounts_active,products=products,product_discounts=product_discounts,productsset=productsset)
    else:
        name = request.form.get('name', None)
        description = request.form.get('description', None)
        price = request.form.get('price', None)
        active = request.form.get('active', None)
        file = request.files.get('cover', None)
        # Added
        cat = request.form.get('category', None)
        discount_id = request.form.get('discount_id', None)
        p = Product(name=name.title(), description=description.title(), price=price, active=active,category=cat)
        if active == None:
            p.active = 0
        else:
            p.active = 1
        db.session.add(p)
        db.session.commit()
        pset = ProductSet(product_id=p.id,created_at=p.created_at,discount_id=discount_id)
        print(pset)
        print(discount_id)
        db.session.add(pset)
        db.session.commit()
        
        file.save(f'static/cover/{p.id}.jpg')
        flash("New product is Added")
        return redirect(url_for("admin.products"))


@app.route('/admin/dashboard/edit-product/<id>', methods=["GET", "POST"])
def edit_product(id):
    product = Product.query.filter(Product.id == id).first_or_404()
    productset = ProductSet.query.filter(ProductSet.product_id == id).first_or_404()
    # productdiscount = ProductDiscount.query.filter(ProductDiscount.id==id).first_or_404()
    
    discounts = ProductDiscount.query.all()
    # print(product)
    

    if request.method == "GET":

        query = text('''
        select  distinct product_discount.id,product_discount.discountpercent  
        from product_set
        LEFT JOIN products on products.id==product_set.product_id
        LEFT JOIN product_discount on product_discount.id==product_set.discount_id 
        WHERE products.id = :id
        
         ''')
        # results = db.session.execute(query).fetchall()
        results = db.session.execute(query, {'id': id}).fetchall()
        context = {
          'products_with_discounts': results,
                     }
        

        return render_template("admin/edit-product.html",**context, discounts=discounts, product=product)

        # return render_template("admin/edit-product.html",**context, discounts=discounts, product=product, productset=productset, productdiscount=productdiscount)
    else:
        name = request.form.get('name', None)
        description = request.form.get('description', None)
        price = request.form.get('price', None)
        active = request.form.get('active', None)
        file = request.files.get('cover', None)
        # Added
        category = request.form.get('category', None)
        # p = Product(name=name.title(), description=description.title(), price=price, active=active)
        product.name = name
        product.description = description
        product.price = price
        
        # Added
        product.category = category
        if active == None:
            product.active = 0
        else:
            product.active = 1
        db.session.commit()
        if file.filename != "":
            file.save(f'static/cover/{product.id}.jpg')
        discount=request.form.get('discount_id',None)
        productset.discount_id=discount

        db.session.commit()
        flash("Product is Edited")
        # Added
        return redirect(url_for("admin.products"))


# Added
@app.route('/admin/dashboard/delete-product/<id>', methods=["GET", "POST"])
def delete_product(id):
    product = Product.query.filter(Product.id == id).first_or_404()
    if request.method == "GET":

        return render_template("admin/delete-product.html", product=product)
    else:
         # Deleting the product
        db.session.delete(product)
        db.session.commit()
        
        # Remove the associated image file if it exists
        image_path = f'static/cover/{product.id}.jpg'
        if os.path.exists(image_path):
            os.remove(image_path)
        
        flash("Product has been deleted")
        return redirect(url_for("admin.products"))
        # name = request.form.get('name', None)
        # description = request.form.get('description', None)
        # price = request.form.get('price', None)
        # active = request.form.get('active', None)
        # file = request.files.get('cover', None)
        # # p = Product(name=name.title(), description=description.title(), price=price, active=active)
        # product.name = name
        # product.description = description
        # product.price = price

        # if active == None:
        #     product.active = 0
        # else:
        #     product.active = 1
        # db.session.commit()
        # if file.filename != "":
        #     file.save(f'static/cover/{product.id}.jpg')
        # flash("Product is Deleted")
        # return redirect(url_for("admin.products"))


@app.route('/admin/dashboard/discount', methods=["GET", "POST"])
def discounts():
    if request.method == "GET":
      
        discounts = ProductDiscount.query.all()
        
       
        # print("Discounts:", discounts)

        return render_template("admin/discount.html",discounts=discounts)
    else:
        discpercent = request.form.get('discount', None)
        created_at=request.form.get('creatat', None)
        modified_at=request.form.get('modifiedat', None)
        active = request.form.get('active', None)
        expiration_date=request.form.get('expiration_date')
        if  expiration_date:
            # Parse date in %Y-%m-%d format
            expiration_date = datetime.strptime( expiration_date, '%Y-%m-%d')
            print(expiration_date)
        else:
            expiration_date = None
        pdis =ProductDiscount(discountpercent=discpercent,created_at=created_at, modified_at=modified_at,active=active,expiration_date=expiration_date)
        if active == None:
            pdis.active = 0
        else:
            pdis.active = 1

        db.session.add(pdis)
        db.session.commit()
        
        flash("New discount is Added")
        return redirect(url_for("admin.discounts"))



@app.route('/admin/dashboard/edit-discount/<id>', methods=["GET", "POST"])
def edit_discount(id):
    discount = ProductDiscount.query.filter(ProductDiscount.id == id).first_or_404()
    if request.method == "GET":

        return render_template("admin/edit-discount.html", discount=discount)
    else:
        discpercent = request.form.get('discount', None)
        active = request.form.get('active', None)
        
        discount.discountpercent = discpercent
        if active == None:
            discount.active = 0
        else:
            discount.active = 1
        print(discpercent)
        db.session.commit()
        flash("Discount is Edited")
        # Added
        return redirect(url_for("admin.discounts"))


@app.route('/admin/dashboard/coupons', methods=['GET', 'POST'])
def manage_coupons():
    if request.method == "GET":
        coupons = Coupon.query.all()
        return render_template('admin/coupons.html', coupons=coupons)
        
    else:
        code = request.form['code']
        discount_percent = int(request.form['discount_percent'])
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        usage_limit = int(request.form['usage_limit']) if request.form['usage_limit'] else -1

        if not code or not discount_percent or not end_date or not start_date:
            flash('All fields are required!', 'danger')
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            new_coupon = Coupon(
                code=code,
                discount_percent=discount_percent,
                start_date=start_date,
                end_date=end_date,
                usage_limit=usage_limit
            )
            db.session.add(new_coupon)
            db.session.commit()
            flash('Coupon added successfully!', 'success')
            return redirect(url_for('admin.manage_coupons'))

    
