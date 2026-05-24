from datetime import datetime
from enum import Enum

from app import db


class OrderStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    PREPARING = "Preparing"
    READY = "Ready"
    OUT_FOR_DELIVERY = "Out for Delivery"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(140), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    instagram_id = db.Column(db.String(120))
    occasion = db.Column(db.String(140))
    budget = db.Column(db.Numeric(10, 2))
    delivery_date = db.Column(db.Date)
    color_theme = db.Column(db.String(120))
    custom_message = db.Column(db.Text)
    product_type = db.Column(db.String(160), nullable=False)
    reference_image = db.Column(db.String(500))
    extra_notes = db.Column(db.Text)
    status = db.Column(db.String(40), default=OrderStatus.PENDING.value, index=True)
    selling_price = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=True, index=True)

    materials = db.relationship("MaterialCost", back_populates="order", cascade="all, delete-orphan")
    customer = db.relationship("Customer", backref="orders")

    @property
    def total_cost(self):
        return sum(float(item.amount or 0) for item in self.materials)

    @property
    def profit(self):
        return float(self.selling_price or 0) - self.total_cost


class MaterialCost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_name = db.Column(db.String(160), nullable=False)
    quantity = db.Column(db.String(80), nullable=False, default="1")
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)

    order = db.relationship("Order", back_populates="materials")
