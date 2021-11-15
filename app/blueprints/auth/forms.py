from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField 
#from wtforms.fields.core import FloatField
from wtforms.fields.simple import FileField
from wtforms.validators import Email, DataRequired, EqualTo, ValidationError 
from app.models import User
import random
from jinja2 import Markup
#from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    r1=random.randint(1,1000)
    r2=random.randint(1001,2000)
    r3=random.randint(2001,3000)
    r4=random.randint(3001,4000)

    r1_img=Markup(f'<img src="https://avatars.dicebear.com/api/identicon/{r1}.svg" style="height:75px">')
    r2_img=Markup(f'<img src="https://avatars.dicebear.com/api/identicon/{r2}.svg" style="height:75px">')
    r3_img=Markup(f'<img src="https://avatars.dicebear.com/api/identicon/{r3}.svg" style="height:75px">')
    r4_img=Markup(f'<img src="https://avatars.dicebear.com/api/identicon/{r4}.svg" style="height:75px">')

    icon = RadioField('Avatar',
                    choices=[(r1,r1_img),(r2,r2_img),(r3,r3_img),(r4,r4_img)],
                    validators=[DataRequired()])

        # MUST BE LIKE THIS VALIDATE_FIELDNAME
    def validate_email(form, field):                                #give me only the first result returns 1 user object
        same_email_user = User.query.filter_by(email = field.data).first()
                        # SELECT * FROM user WHERE email = ???
                        # filter_by always gives a list
        if same_email_user:
            raise ValidationError("Email is Already in Use")


class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    r1=random.randint(1,1000)
    r2=random.randint(1001,2000)
    r3=random.randint(2001,3000)
    r4=random.randint(3001,4000)

    r1_img=Markup(f'<img src="https://avatars.dicebear.com/api/identicon/{r1}.svg" style="height:75px">')
    r2_img=Markup(f'<img src="https://avatars.dicebear.com/api/identicon/{r2}.svg" style="height:75px">')
    r3_img=Markup(f'<img src="https://avatars.dicebear.com/api/identicon/{r3}.svg" style="height:75px">')
    r4_img=Markup(f'<img src="https://avatars.dicebear.com/api/identicon/{r4}.svg" style="height:75px">')

    icon = RadioField('Avatar',
                    choices=[(9000,"Don't Change"),(r1,r1_img),(r2,r2_img),(r3,r3_img),(r4,r4_img)],
                    validators=[DataRequired()])




class ProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    image = StringField('Image URL')
    submit = SubmitField()

class SearchForm(FlaskForm):
    class Meta:
        csrf = False
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')