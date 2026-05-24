from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from app import db
from app.forms.admin_forms import AdminAccountForm, CategoryForm, OrderAdminForm, ProductForm, SettingsForm
from app.models.admin import Admin
from app.models.category import Category
from app.models.order import MaterialCost, Order
from app.models.product import Product, ProductMedia
from app.models.review import Review
from app.models.settings import WebsiteSettings
from app.services.analytics_service import category_mix, dashboard_metrics, monthly_finance, monthly_insights
from app.services.profit_service import order_profit_snapshot
from app.services.upload_service import save_media_upload, save_upload
from app.utils.slugify import slugify

admin_bp = Blueprint("admin", __name__)
MAX_MATERIAL_ROWS = 40


@admin_bp.before_request
def require_admin_account():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login", next=request.url))
    if getattr(current_user, "role_type", None) != "admin":
        flash("Please use an admin account for the studio dashboard.", "danger")
        return redirect(url_for("auth.login"))


def normalize_badges(value):
    if not value:
        return None
    badges = [badge.strip() for badge in value.split(",") if badge.strip()]
    return ", ".join(dict.fromkeys(badges))


def category_conflict(name, category=None):
    slug = slugify(name)
    query = Category.query.filter(or_(
        func.lower(Category.name) == name.strip().lower(),
        Category.slug == slug,
    ))
    if category and category.id:
        query = query.filter(Category.id != category.id)
    return query.first()


def account_conflict(form, account=None):
    email = form.email.data.strip().lower()
    username = form.username.data.strip().lower() if form.username.data else None
    filters = [func.lower(Admin.email) == email]
    if username:
        filters.append(func.lower(Admin.username) == username)
    query = Admin.query.filter(or_(*filters))
    if account and account.id:
        query = query.filter(Admin.id != account.id)
    return query.first()


@admin_bp.route("/")
@login_required
def dashboard():
    metrics = dashboard_metrics()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    finance = monthly_finance()
    product_stats = {
        "total": Product.query.count(),
        "active": Product.query.filter_by(is_active=True).count(),
        "featured": Product.query.filter_by(is_featured=True).count(),
        "inactive": Product.query.filter_by(is_active=False).count(),
    }
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(6).all()
    return render_template(
        "admin/dashboard.html",
        metrics=metrics,
        recent_orders=recent_orders,
        finance=finance,
        monthly=monthly_insights(finance),
        categories=category_mix(),
        product_stats=product_stats,
        recent_products=recent_products,
    )


@admin_bp.route("/products")
@login_required
def products():
    page = request.args.get("page", 1, type=int)
    products_page = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=12)
    return render_template("admin/products.html", products=products_page)


@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def product_form(product_id=None):
    product = Product.query.get(product_id) if product_id else Product(is_active=True)
    form = ProductForm(obj=product)
    form.category_id.choices = [(cat.id, cat.name) for cat in Category.query.order_by(Category.name)]
    if form.validate_on_submit():
        product.name = form.name.data
        product.slug = slugify(form.name.data)
        product.description = form.description.data
        product.price = form.price.data
        product.category_id = form.category_id.data
        product.badge = normalize_badges(form.badge.data)
        product.is_featured = form.is_featured.data
        product.is_active = form.is_active.data
        db.session.add(product)
        db.session.flush()
        for media_file in form.media.data or []:
            if not media_file or not media_file.filename:
                continue
            media = save_media_upload(media_file)
            product.media.append(ProductMedia(
                media_url=media["url"],
                media_type=media["media_type"],
                original_filename=media["filename"],
                alt_text=product.name,
                sort_order=len(product.media),
            ))
            if media["media_type"] == "image" and not product.image_url:
                product.image_url = media["url"]
        db.session.commit()
        flash("Product saved.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", form=form, product=product)


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    db.session.delete(Product.query.get_or_404(product_id))
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        if category_conflict(form.name.data):
            flash("A category with that name already exists.", "danger")
            return render_template("admin/categories.html", form=form, categories=Category.query.order_by(Category.name).all(), editing_category=None)
        image_path = save_upload(form.image.data)
        category = Category(
            name=form.name.data,
            slug=slugify(form.name.data),
            description=form.description.data,
            image_url=image_path,
            is_featured=form.is_featured.data,
        )
        db.session.add(category)
        db.session.commit()
        flash("Category added.", "success")
        return redirect(url_for("admin.categories"))
    categories_list = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", form=form, categories=categories_list, editing_category=None)


@admin_bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    form.submit.label.text = "Save category"
    if form.validate_on_submit():
        if category_conflict(form.name.data, category):
            flash("A category with that name already exists.", "danger")
            return render_template("admin/categories.html", form=form, categories=Category.query.order_by(Category.name).all(), editing_category=category)
        category.name = form.name.data
        category.slug = slugify(form.name.data)
        category.description = form.description.data
        category.is_featured = form.is_featured.data
        image_path = save_upload(form.image.data)
        if image_path:
            category.image_url = image_path
        db.session.commit()
        flash("Category updated.", "success")
        return redirect(url_for("admin.categories"))
    categories_list = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", form=form, categories=categories_list, editing_category=category)


@admin_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products.count():
        flash("Move or delete products in this category before deleting it.", "danger")
        return redirect(url_for("admin.categories"))
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted.", "success")
    return redirect(url_for("admin.categories"))


@admin_bp.route("/orders")
@login_required
def orders():
    page = request.args.get("page", 1, type=int)
    orders_page = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=12)
    return render_template("admin/orders.html", orders=orders_page)


def save_order_from_form(order, form):
    order.customer_name = form.customer_name.data
    order.phone = form.phone.data
    order.instagram_id = form.instagram_id.data
    order.occasion = form.occasion.data
    order.budget = form.budget.data
    order.delivery_date = form.delivery_date.data
    order.color_theme = form.color_theme.data
    order.custom_message = form.custom_message.data
    order.product_type = form.product_type.data
    order.extra_notes = form.extra_notes.data
    order.status = form.status.data
    order.selling_price = form.selling_price.data or 0
    order.materials.clear()
    for material_form in form.materials:
        name = material_form.material_name.data
        amount = material_form.amount.data
        if name and amount is not None:
            order.materials.append(MaterialCost(
                material_name=name,
                quantity=material_form.quantity.data or "1",
                amount=amount,
            ))


def load_material_rows(form, order):
    while len(form.materials) < MAX_MATERIAL_ROWS:
        form.materials.append_entry()
    for idx, material in enumerate(order.materials[:len(form.materials)]):
        form.materials[idx].material_name.data = material.material_name
        form.materials[idx].quantity.data = material.quantity
        form.materials[idx].amount.data = material.amount


def ensure_material_rows(form):
    while len(form.materials) < MAX_MATERIAL_ROWS:
        form.materials.append_entry()


@admin_bp.route("/orders/new", methods=["GET", "POST"])
@login_required
def new_order():
    order = Order()
    form = OrderAdminForm(obj=order)
    form.submit.label.text = "Create order"
    ensure_material_rows(form)
    if form.validate_on_submit():
        save_order_from_form(order, form)
        db.session.add(order)
        db.session.commit()
        flash("Order created.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))
    return render_template("admin/order_form.html", form=form, order=order, title="Add order")


@admin_bp.route("/orders/<int:order_id>/edit", methods=["GET", "POST"])
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderAdminForm(obj=order)
    form.submit.label.text = "Save order"
    if request.method == "GET":
        load_material_rows(form, order)
    else:
        ensure_material_rows(form)
    if form.validate_on_submit():
        save_order_from_form(order, form)
        db.session.commit()
        flash("Order updated.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))
    return render_template("admin/order_form.html", form=form, order=order, title="Edit order")


@admin_bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderAdminForm(obj=order)
    if request.method == "GET":
        load_material_rows(form, order)
    if form.validate_on_submit():
        save_order_from_form(order, form)
        db.session.commit()
        flash("Order, costs, and profit updated.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))
    return render_template("admin/order_detail.html", order=order, form=form, profit=order_profit_snapshot(order))


@admin_bp.route("/orders/<int:order_id>/delete", methods=["POST"])
@login_required
def delete_order(order_id):
    db.session.delete(Order.query.get_or_404(order_id))
    db.session.commit()
    flash("Order deleted.", "success")
    return redirect(url_for("admin.orders"))


@admin_bp.route("/testimonials")
@login_required
def manage_testimonials():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("admin/testimonials.html", reviews=reviews)


@admin_bp.route("/testimonials/<int:review_id>/toggle", methods=["POST"])
@login_required
def toggle_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = not review.is_approved
    db.session.commit()
    return redirect(url_for("admin.manage_testimonials"))


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    settings_obj = WebsiteSettings.query.first() or WebsiteSettings()
    form = SettingsForm(obj=settings_obj)
    if form.validate_on_submit():
        form.populate_obj(settings_obj)
        db.session.add(settings_obj)
        db.session.commit()
        flash("Website settings saved.", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html", form=form)


@admin_bp.route("/analytics")
@login_required
def analytics():
    return render_template("admin/analytics.html", metrics=dashboard_metrics(), finance=monthly_finance(), categories=category_mix())


@admin_bp.route("/accounts")
@login_required
def accounts():
    accounts_list = Admin.query.order_by(Admin.created_at.desc()).all()
    return render_template("admin/accounts.html", accounts=accounts_list)


@admin_bp.route("/accounts/new", methods=["GET", "POST"])
@admin_bp.route("/accounts/<int:account_id>/edit", methods=["GET", "POST"])
@login_required
def account_form(account_id=None):
    account = Admin.query.get(account_id) if account_id else Admin(is_active_account=True)
    form = AdminAccountForm(obj=account)
    form.submit.label.text = "Save account"
    if form.validate_on_submit():
        if account_conflict(form, account):
            flash("That email or username is already used by another account.", "danger")
            return render_template("admin/account_form.html", form=form, account=account)
        if not account.id and not form.password.data:
            flash("Password is required for a new account.", "danger")
            return render_template("admin/account_form.html", form=form, account=account)
        account.name = form.name.data
        account.username = form.username.data.strip().lower() if form.username.data else None
        account.email = form.email.data.strip().lower()
        account.is_active_account = form.is_active_account.data
        if form.password.data:
            account.set_password(form.password.data)
        db.session.add(account)
        db.session.commit()
        flash("Admin account saved.", "success")
        return redirect(url_for("admin.accounts"))
    return render_template("admin/account_form.html", form=form, account=account)


@admin_bp.route("/accounts/<int:account_id>/delete", methods=["POST"])
@login_required
def delete_account(account_id):
    account = Admin.query.get_or_404(account_id)
    if account.id == current_user.id:
        flash("You cannot delete the account you are currently using.", "danger")
        return redirect(url_for("admin.accounts"))
    db.session.delete(account)
    db.session.commit()
    flash("Admin account deleted.", "success")
    return redirect(url_for("admin.accounts"))


@admin_bp.route("/accounts/<int:account_id>/reset-link", methods=["POST"])
@login_required
def account_reset_link(account_id):
    account = Admin.query.get_or_404(account_id)
    token = account.generate_reset_token()
    db.session.commit()
    reset_url = url_for("auth.reset_password", admin_id=account.id, token=token, _external=True)
    flash(f"Reset link: {reset_url}", "success")
    return redirect(url_for("admin.accounts"))
