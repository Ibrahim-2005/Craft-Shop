from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


PRODUCT_TYPES = [
    ("Customized bouquet", "Customized bouquet"),
    ("Gift hamper", "Gift hamper"),
    ("Pipe cleaner flower bouquet", "Pipe cleaner flower bouquet"),
    ("Pipe cleaner keychain", "Pipe cleaner keychain"),
    ("Handmade surprise gift", "Handmade surprise gift"),
    ("Customized aesthetic gift", "Customized aesthetic gift"),
]


class CustomOrderForm(FlaskForm):
    customer_name = StringField("Customer name", validators=[DataRequired(), Length(max=140)])
    phone = StringField("Phone number", validators=[DataRequired(), Length(max=40)])
    instagram_id = StringField("Instagram ID", validators=[Optional(), Length(max=120)])
    occasion = StringField("Occasion", validators=[Optional(), Length(max=140)])
    budget = DecimalField("Budget", validators=[Optional()], places=2)
    delivery_date = DateField("Delivery date", validators=[Optional()])
    color_theme = StringField("Color theme", validators=[Optional(), Length(max=120)])
    custom_message = TextAreaField("Custom message", validators=[Optional()])
    product_type = SelectField("Product type", choices=PRODUCT_TYPES, validators=[DataRequired()])
    reference_image = FileField("Reference image", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"])])
    extra_notes = TextAreaField("Extra notes", validators=[Optional()])
    submit = SubmitField("Send custom request")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=140)])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=40)])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send message")


class ReviewForm(FlaskForm):
    customer_name = StringField("Name", validators=[DataRequired(), Length(max=140)])
    instagram_id = StringField("Instagram ID", validators=[Optional(), Length(max=120)])
    message = TextAreaField("Review", validators=[DataRequired(), Length(min=12)])
    submit = SubmitField("Share review")
