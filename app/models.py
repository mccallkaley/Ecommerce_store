from sqlalchemy.orm import backref
from app import db
from flask_login import current_user,  UserMixin
from datetime import datetime as dt, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
import secrets
#step one create tables (model
# make a new database in elephant sql)
# hide in .env


#set columns and what they are
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  #create our column
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(200), unique=True, index=True) #username need a unique one
    password = db.Column(db.String(200))
    icon = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, default=dt.utcnow) #ut universal time zone  always do this
    products = db.relationship("Product", backref="author", lazy=True)
    cart = db.relationship("Cart", backref="user", lazy=True)
    token = db.Column(db.String, index=True, unique=True)
    token_exp = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)

    #give methods to take instance of user class
    def __repr__(self):  #will print out when you print your object
        return f'<User: {self.id} | {self.email}>'

    ##################################################
    ############## Methods for Token auth ############
    ##################################################

    def get_token(self, exp=86400):
        current_time = dt.utcnow()
        # give the user their token if the token is not expired
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        # if not a token create a token and exp date
        self.token = secrets.token_urlsafe(32)
        self.token_exp = current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=61)

    @staticmethod
    def check_token(token):
        u = User.query.filter_by(token=token).first()
        if not u or u.token_exp < dt.utcnow():
            return None
        return u

    #########################################
    ############# End Methods for tokens ####
    #########################################



    #McCall = User()
    #print(McCall)

    #data is a dict with username first name last name

    def from_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data["email"]
        self.icon = data['icon']
        self.password = self.hash_password(data['password'])

        # use hashing for password = takes your string and gives you scrambled combos that = it 
        # use salting that adds a unique string before the hashing so that someone cant undo it 
        # makes it harder to steal passwords

    def hash_password(self, original_password):
        return generate_password_hash(original_password)
    # compares the user password to the password provided in the login form
    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    # saves the user to the database and when you have to change user you need to change this 
    
    def save(self):
        db.session.add(self) # add the user to the db session
        db.session.commit()  # save everything in session to the database do this LAST

    def get_icon_url(self):
        return f'https://avatars.dicebear.com/api/identicon/{self.icon}.svg'

    
@login.user_loader   #this is going to decorate a func- make a func that tells flask login what criteria
                    # we need to get them logged in
def load_user(id):
    return User.query.get(int(id))    #id in table user is = to this id (select from user = USER)
    

# same as(SELECT * FROM user WHERE id = ???)

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)  #create our column
    product_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #pulls in user id  from user table
    cart = db.relationship("Cart", backref="products", lazy=True)
    category_id = db.Column(db.ForeignKey('category.id'))
    
    
    def __repr__(self):
        return f'<Product: {self.id} | {self.name}>'

    def add_to_cart(self, user):
        self.owner = user.id
        db.session.commit()

    def remove_from_cart(self):
        self.owner = None
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

        def __repr__(self):
            return f"{self.name}"

    def to_dict(self):
        data={
            'id':self.id,
            "name":self.name,
            "price":self.price,
            "image":self.image,
            "created_on":self.created_on
        }
        return data

    def from_dict(self, data):
        for field in ["name","price","image","description"]:
            if field in data:
                setattr(self, field, data[field])
        return data

    def total_price(self, user_id):
        price_list = []
        cart_product = Cart.query.filter_by(user_id = user_id).all()
        for product in cart_product:
            product_price =  Product.query.filter_by(id = product.product_id).first().price 
            price_list.append(product_price)
        return sum(price_list)
    
    def save(self):
        db.session.add(self)
        db.session.commit()



class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    products = db.relationship('Product', cascade ='all, delete-orphan',  backref="category")

    def __repr__(self):
        return f'<Catergoy: {self.id} | {self.name}>'

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        data={
            "id": self.id,
            "name": self.name
        }
        return data

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id  = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    def __repr__(self):
        product = Product.query.filter_by(id = self.product_id).first()
        return f'{product.product_name}'

    def from_dict(self, data):
        self.user_id = data['user_id']
        self.product_id = data['product_id']
        self.save()

    def save(self):
        db.session.add(self) 
        db.session.commit() 

    









#class Post(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    body = db.Column(db.Text)
#    date_created = db.Column(db.DateTime, default=dt.utcnow)
 #   date_updated = db.Column(db.DateTime, onupdate=dt.utcnow)
 #   user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # saves the Post to the database
#    def save(self):
  #      db.session.add(self) # add the Post to the db session
  #      db.session.commit() #save everything in the session to the database

#    def edit(self, new_body):
#        self.body=new_body
#        self.save()
##    def __repr__(self):
 #       return f'<id:{self.id} | Post: {self.body[:15]}>'