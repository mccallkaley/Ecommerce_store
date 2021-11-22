from flask import render_template, request, flash, g,redirect, make_response
from flask.helpers import url_for
from flask_wtf import *
import requests
from flask_login import login_required, current_user
from app.blueprints.auth.forms import  ProductForm, ProductEditingForm
from werkzeug.datastructures import MultiDict
from app.blueprints.auth.routes import token_auth
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User, Product, Cart
import secrets
import os


from app.models import *
from .import bp as main

@main.get('/category')
@token_auth.login_required()
def get_category():
    cats = Category.query.all()
    cats_dicts= [cat.to_dict() for cat in cats]
    return make_response({"categories":cats_dicts},200)

# create a new category
# {"name":"my cat name"}
@main.post('/category')
@token_auth.login_required()
def post_category():
    if not g.current_user.is_admin:
        return make_response({"You are not Admin"},403)
    cat_name = request.get_json().get("name")
    cat = Category(name=cat_name)
    cat.save()
    return make_response(f"category {cat.id} with name {cat.name} created",200)

# change my category 
#{"name":"new name"}
@main.put('/category/<int:id>')
@token_auth.login_required()
def put_category(id):
    if not g.current_user.is_admin:
        return make_response({"You are not Admin"},403)
    cat_name = request.get_json().get('name')
    cat = Category.query.get(id)
    if not cat:
        return make_response("Invalid category", 404)
    cat.name = cat_name
    cat.save()
    return make_response(f"category {cat.id} has new name {cat.name}",200)

# Discard a category
@main.delete('/category/<int:id>')
@token_auth.login_required()
def delete_category(id):
    if not g.current_user.is_admin:
        return make_response({"You are not Admin"},403)
    cat = Category.query.get(id)
    if not cat:
        return make_response("Invalid category id",404)
    cat.delete()
    return make_response(f"Category id: {id} has been murdered",200)

@main.route('/', methods = ['GET'])
@login_required
def index():
    return render_template('index.html.j2')


# # Create a product
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
    if current_user.is_admin!=True:
        return redirect(url_for('main.products'))
    form = ProductEditingForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new_product_data = {
                "name":form.product_name.data,
                "price":form.price.data,
                "image":form.image.data,
                "description":form.description.data,
            }
            #create and empty product
            new_product_object = Product()
            # build product with form data
            new_product_object.from_dict(new_product_data)
            # save product to database
            new_product_object.save()
        except:
            error_string = "There was an Error creating the product. Please Try again."
            flash(error_string)
            return render_template('create_product.html.j2',form=form, error = error_string)
        return redirect(url_for('main.products'))
    
    return render_template("create_product.html.j2", form=form)


@main.route('/products', methods = ['GET', 'POST'])
def products():
    all_products=Product.query.all()
    

    return render_template('products.html.j2', products = all_products)

#@main.route("/select_products", methods=['GET', 'POST'])
#def select_products():
 #   products = Product.query.all()
 #   return render_template('select_products.html', products=products)

@main.route('/edit_product/<int:id>', methods=['GET','POST'])
@login_required
def edit_product(id):
    if current_user.is_admin!=True:
        return redirect(url_for('main.products'))
    product=Product.query.get(id)
    if request.method == 'GET':
        form = ProductEditingForm(formdata=MultiDict({'name': product.product_name, 
                                                   'price': product.price, 
                                                   'image': product.image}))
                                                                            
    else:
        form = ProductEditingForm()
    if request.method == 'POST' and form.validate_on_submit():
        altered_product_data = {
            "name":form.product_name.data,
            "price":form.price.data,
            "image":form.image.data,
            "description":form.description.data,
        }
        
        try:
            product.from_dict(altered_product_data)
            product.save()
            flash('product edited', 'success')
        except:
            flash('There was an unexpected error', 'danger')
            return redirect(url_for('main.edit_product'))
        return redirect(url_for('main.products'))
    return render_template('edit_product.html.j2', form = form)


@main.route('/add_to_cart/<int:id>', methods=['GET','POST'])
@login_required
def add_to_cart(id):
    if request.method == 'POST':
        product_add = Product.query.get(id)
        product_add.add_to_cart(user=current_user)
        flash(f'{product_add.product_name} was added to your cart')
        return redirect(url_for('main.products'))

@main.route('/show_product/<int:id>', methods=['GET','POST'])
@login_required
def show_product(id):
    if request.method == 'POST':
        product_to_show = Product.query.get(id)
        return render_template('show_product.html.j2', product = product_to_show)


@main.route('/cart', methods=['GET'])
@login_required
def cart():
    user_cart = Cart.query.filter_by(user_id = current_user.id).all()
    cart_products = (Product.query.filter_by(id = product.product_id).first() for product in user_cart)
    products = list(cart_products)
    total = Product().total_price(user_id= current_user.id)
    return render_template("cart.html.j2", products = products, total = total)


@main.route('/deletefromcart/<int:id>', methods=['GET','POST'])
@login_required
def deletefromcart(id):
    if request.method == 'POST':
        product_to_remove = Product.query.get(id)
        product_to_remove.remove_from_cart()
        flash(f'{product_to_remove.name} was removed to your cart')
        return redirect(url_for('main.products'))
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

    
       