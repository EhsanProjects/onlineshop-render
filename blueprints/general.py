from flask import Blueprint, render_template, request
from sqlalchemy.sql.expression import func

from models.product import Product

app = Blueprint("general", __name__)


@app.route('/')
def main():  # put application's code here
    # products = Product.query.all()
    # Main page shows Only Active Products.
    search = request.args.get('search', None)
    products = Product.query.filter(Product.active == 1)
    if search != None:
        products = products.filter(Product.name.like(f'%{search}%'))
    # ///////order by price
    # products = products.order_by(Product.price.desc()).all()  
    products = products.order_by(func.random()).all()

    # products = Product.query.filter(Product.active == 1).all()

    return render_template('main.html', products=products, search=search)


@app.route('/product/<int:id>/<name>')
def product(id, name):
    # product = Product.query.filter(Product.id == id).filter(Product.name == name).first_or_404()
    product = Product.query.filter(Product.id == id).filter(Product.name == name).filter(
        Product.active == 1).first_or_404()

    another_products = Product.query.filter(Product.active == 1).filter(
        Product.name.like(f'%{product.name[0:3]}%')).order_by(func.random()).limit(3).all()
    return render_template('product.html', product=product, another_products=another_products)


@app.route('/about')
def about():  # put application's code here
    return render_template('about.html')
