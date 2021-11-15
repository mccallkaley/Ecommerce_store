from flask import render_template, request, flash, g,redirect
from flask.helpers import url_for
from flask_wtf import *
import requests
from flask_login import login_required
from app.blueprints.auth.forms import  ProductForm 

from app.models import User, Product, Cart
import secrets
import os


from app.models import *
from .import bp as main

@main.route('/', methods = ['GET'])
@login_required
def index():
    return render_template('index.html.j2')


# # Create a item
# {
#     "name": new name
#     "description": new desc
#     "price": new price
#     "img": new img
#     "category_id":new cat id
# }
# route for  new product created
@main.route('/createproduct', methods=['GET','POST'])
@login_required
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        product_name = form.product_name.data
        price = form.price.data
        image = form.image.data

        new_product = Product(product_name, price, image)

        db.session.add(new_product)
        db.session.commit()

      
        print("Product has been saved!")
        return redirect(url_for("index"))
    
    return render_template("create_product.html.j2", form=form)


@main.route('/products', methods = ['GET', 'POST'])
def products():
    my_products=Product.query.all()

    return render_template('products.html', products = my_products)

#@main.route("/select_products", methods=['GET', 'POST'])
#def select_products():
 #   products = Product.query.all()
 #   return render_template('select_products.html', products=products)


@main.route('/add_to_cart/<int:product_id>', methods=['GET'])
@login_required
def add_to_cart(product_id):
     # check if product is already in cart
    row = Cart.query.filter_by(product_id=product_id, buyer=current_user).first()
    product_name = Product.query.filter(Product.id == product_id)
    if row:
        # if in cart update quantity : +1
        row.quantity += 1
        db.session.commit()
        flash('This item is already in your cart, 1 quantity added!', 'success')
        
        # if not, add item to cart
    else:
        cart_item = Cart(product=product_name)
        db.session.add(cart_item)
        db.session.commit()

        return render_template('products.html', product=products)


@main.route('/cart', methods=['GET'])
@login_required
def cart():
    user_cart = Cart.query.filter_by(user_id = current_user.id).all()
    cart_products = (Product.query.filter_by(id = product.product_id).first() for product in user_cart)
    products = list(cart_products)
    total = Product().total_price(user_id= current_user.id)
    return render_template("cart.html.j2", products = products, total = total)


@main.route('/deletefromcart/<int:product_id>', methods=['GET'])
@login_required
def deletefromcart(product_id):
    product = Cart.query.filter_by(product_id = product_id, user_id = current_user.id).first()
    db.session.delete(product)
    db.session.commit()
    flash('Product has been removed', 'success')
    return redirect(url_for('cart'))


@main.route('/deleteallfromcart', methods=['GET'])
@login_required
def deleteallfromcart():
    db.session.query(Cart).filter(Cart.user_id == current_user.id).delete()
    db.session.commit()
    flash('All products have been removed', 'success')
    return redirect(url_for('index'))






 #if user and current_user.email != user.email:

    
       