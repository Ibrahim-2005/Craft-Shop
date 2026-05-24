from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from sqlalchemy import func, or_

from app import db
from app.forms.customer_forms import (
    CustomerForgotPasswordForm,
    CustomerResetPasswordForm,
)
from app.models.customer import Customer
from app.models.order import Order

customer_auth_bp = Blueprint("customer_auth", __name__)


def find_customer(identifier):
    value = identifier.strip().lower()
    return Customer.query.filter(or_(
        func.lower(Customer.email) == value,
        func.lower(Customer.username) == value,
    )).first()


@customer_auth_bp.route("/register", methods=["GET", "POST"])
def register():
    return redirect(url_for("auth.login"))


@customer_auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return redirect(url_for("auth.login", next=request.args.get("next")))


@customer_auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Signed out.", "soft")
    return redirect(url_for("public.home"))


@customer_auth_bp.route("/account")
@login_required
def dashboard():
    if getattr(current_user, "role_type", None) != "customer":
        return redirect(url_for("admin.dashboard"))
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    return render_template("customer/dashboard.html", orders=orders)


@customer_auth_bp.route("/account/orders")
@login_required
def orders():
    if getattr(current_user, "role_type", None) != "customer":
        return redirect(url_for("admin.dashboard"))
    orders_list = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("customer/orders.html", orders=orders_list)


@customer_auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = CustomerForgotPasswordForm()
    reset_url = None
    if form.validate_on_submit():
        customer = find_customer(form.identifier.data)
        if customer:
            token = customer.generate_reset_token()
            db.session.commit()
            reset_url = url_for("customer_auth.reset_password", customer_id=customer.id, token=token, _external=True)
        flash("If the account exists, a reset link has been created.", "success")
    return render_template("customer/forgot_password.html", form=form, reset_url=reset_url)


@customer_auth_bp.route("/reset-password/<int:customer_id>/<token>", methods=["GET", "POST"])
def reset_password(customer_id, token):
    customer = Customer.query.get_or_404(customer_id)
    if not customer.check_reset_token(token):
        flash("This reset link is invalid or expired.", "danger")
        return redirect(url_for("customer_auth.forgot_password"))
    form = CustomerResetPasswordForm()
    if form.validate_on_submit():
        customer.set_password(form.password.data)
        customer.clear_reset_token()
        db.session.commit()
        flash("Password reset successful. Please sign in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("customer/reset_password.html", form=form)
