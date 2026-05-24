from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app import db
from app.forms.public_forms import ContactForm, CustomOrderForm, ReviewForm
from app.models.category import Category
from app.models.order import Order
from app.models.product import Product
from app.models.review import Review
from app.models.settings import GalleryItem, WebsiteSettings
from app.services.upload_service import save_upload

public_bp = Blueprint("public", __name__)


def site_settings():
    settings = WebsiteSettings.query.first()
    if not settings:
        settings = WebsiteSettings()
        db.session.add(settings)
        db.session.commit()
    return settings


@public_bp.app_context_processor
def inject_settings():
    return {"settings": site_settings()}


@public_bp.route("/")
def home():
    featured = Product.query.filter_by(is_active=True, is_featured=True).limit(6).all()
    categories = Category.query.filter_by(is_featured=True).limit(4).all()
    reviews = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).limit(6).all()
    return render_template("public/home.html", featured=featured, categories=categories, reviews=reviews)


@public_bp.route("/shop")
def shop():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    category_slug = request.args.get("category")
    query = Product.query.filter_by(is_active=True)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=9)
    categories = Category.query.order_by(Category.name).all()
    return render_template("public/shop.html", products=products, categories=categories, q=q, selected_category=category_slug)


@public_bp.route("/product/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = Product.query.filter(Product.category_id == product.category_id, Product.id != product.id).limit(3).all()
    return render_template("public/product_detail.html", product=product, related=related)


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/gallery")
def gallery():
    return redirect(url_for("public.home"))


@public_bp.route("/testimonials", methods=["GET", "POST"])
def testimonials():
    form = ReviewForm()
    if form.validate_on_submit():
        db.session.add(Review(
            customer_name=form.customer_name.data,
            instagram_id=form.instagram_id.data,
            message=form.message.data,
            is_approved=False,
        ))
        db.session.commit()
        flash("Thank you. Your review is waiting for approval.", "success")
        return redirect(url_for("public.testimonials"))
    reviews = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).all()
    return render_template("public/testimonials.html", reviews=reviews, form=form)


@public_bp.route("/custom-order", methods=["GET", "POST"])
def custom_order():
    form = CustomOrderForm()
    if request.method == "GET" and current_user.is_authenticated and getattr(current_user, "role_type", None) == "customer":
        form.customer_name.data = current_user.name
        form.phone.data = current_user.phone
    if form.validate_on_submit():
        try:
            image_path = save_upload(form.reference_image.data)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("public/custom_order.html", form=form)
        order = Order(
            customer_name=form.customer_name.data,
            phone=form.phone.data,
            instagram_id=form.instagram_id.data,
            occasion=form.occasion.data,
            budget=form.budget.data,
            delivery_date=form.delivery_date.data,
            color_theme=form.color_theme.data,
            custom_message=form.custom_message.data,
            product_type=form.product_type.data,
            reference_image=image_path,
            extra_notes=form.extra_notes.data,
            customer_id=current_user.id if current_user.is_authenticated and getattr(current_user, "role_type", None) == "customer" else None,
        )
        db.session.add(order)
        db.session.commit()
        flash("Your custom request has been received. We will confirm the details personally.", "success")
        return redirect(url_for("public.custom_order"))
    return render_template("public/custom_order.html", form=form)


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash("Message received. The studio will reply soon.", "success")
        return redirect(url_for("public.contact"))
    return render_template("public/contact.html", form=form)
