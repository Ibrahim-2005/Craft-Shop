from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, MultipleFileField
from wtforms import Form
from wtforms import BooleanField, DateField, DecimalField, FieldList, FormField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

from app.models.order import OrderStatus
from app.forms.public_forms import PRODUCT_TYPES


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[Optional()])
    image = FileField("Image", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"])])
    is_featured = BooleanField("Feature on home")
    submit = SubmitField("Save category")


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=180)])
    description = TextAreaField("Description", validators=[DataRequired()])
    original_price = DecimalField("Original price", validators=[Optional()], places=2)
    price = DecimalField("Buying price", validators=[DataRequired()], places=2)
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    badge = StringField("Badges", validators=[Optional(), Length(max=255)])
    media = MultipleFileField("Media or images", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp", "mp4", "webm", "mov", "mp3", "wav", "ogg", "m4a"])])
    is_featured = BooleanField("Featured")
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save product")


class MaterialForm(Form):
    material_name = StringField("Material", validators=[Optional(), Length(max=160)])
    quantity = StringField("Qty", validators=[Optional(), Length(max=80)])
    amount = DecimalField("Amount", validators=[Optional()], places=2)


class OrderAdminForm(FlaskForm):
    customer_name = StringField("Customer name", validators=[DataRequired(), Length(max=140)])
    phone = StringField("Phone number", validators=[DataRequired(), Length(max=40)])
    instagram_id = StringField("Instagram ID", validators=[Optional(), Length(max=120)])
    occasion = StringField("Occasion", validators=[Optional(), Length(max=140)])
    budget = DecimalField("Budget", validators=[Optional()], places=2)
    delivery_date = DateField("Delivery date", validators=[Optional()])
    color_theme = StringField("Color theme", validators=[Optional(), Length(max=120)])
    custom_message = TextAreaField("Custom message", validators=[Optional()])
    product_type = SelectField("Category", validators=[DataRequired()])
    extra_notes = TextAreaField("Extra notes", validators=[Optional()])
    status = SelectField("Status", choices=[(status.value, status.value) for status in OrderStatus])
    selling_price = DecimalField("Selling price", validators=[Optional()], places=2)
    materials = FieldList(FormField(MaterialForm), min_entries=1, max_entries=40)
    submit = SubmitField("Update order")


class SettingsForm(FlaskForm):
    brand_name = StringField("Brand name", validators=[DataRequired()])
    hero_title = StringField("Hero title", validators=[DataRequired()])
    hero_subtitle = TextAreaField("Hero subtitle", validators=[DataRequired()])
    whatsapp_number = StringField("WhatsApp number", validators=[DataRequired()])
    instagram_url = StringField("Instagram URL", validators=[DataRequired()])
    contact_email = StringField("Contact email", validators=[DataRequired()])
    studio_address = StringField("Studio address", validators=[DataRequired()])
    submit = SubmitField("Save settings")


class AdminAccountForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    username = StringField("Username", validators=[Optional(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=180)])
    password = PasswordField("Password", validators=[Optional(), Length(min=8)])
    is_active_account = BooleanField("Active account", default=True)
    submit = SubmitField("Save account")
