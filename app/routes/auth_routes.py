from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func, or_

from app import db
from app.forms.auth_forms import ForgotPasswordForm, LoginForm, ResetPasswordForm
from app.models.admin import Admin

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and getattr(current_user, "role_type", None) == "admin":
        return redirect(url_for("admin.dashboard"))
    if current_user.is_authenticated:
        logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data.strip().lower()
        admin = Admin.query.filter(or_(
            func.lower(Admin.email) == identifier,
            func.lower(Admin.username) == identifier,
        )).first()
        if admin and admin.is_active_account and admin.check_password(form.password.data):
            login_user(admin)
            return redirect(request.args.get("next") or url_for("admin.dashboard"))
        flash("Invalid admin email/username or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Signed out.", "soft")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    reset_url = None
    if form.validate_on_submit():
        identifier = form.identifier.data.strip().lower()
        admin = Admin.query.filter(or_(
            func.lower(Admin.email) == identifier,
            func.lower(Admin.username) == identifier,
        )).first()
        if admin:
            token = admin.generate_reset_token()
            db.session.commit()
            reset_url = url_for("auth.reset_password", admin_id=admin.id, token=token, _external=True)
        flash("If the account exists, a reset link has been created.", "success")
    return render_template("auth/forgot_password.html", form=form, reset_url=reset_url)


@auth_bp.route("/reset-password/<int:admin_id>/<token>", methods=["GET", "POST"])
def reset_password(admin_id, token):
    admin = Admin.query.get_or_404(admin_id)
    if not admin.check_reset_token(token):
        flash("This reset link is invalid or expired.", "danger")
        return redirect(url_for("auth.forgot_password"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        admin.set_password(form.password.data)
        admin.clear_reset_token()
        db.session.commit()
        flash("Password reset successful. Please sign in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)
