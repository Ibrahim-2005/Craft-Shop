from datetime import datetime

from app import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(500))
    badge = db.Column(db.String(255))
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    category = db.relationship("Category", back_populates="products")
    images = db.relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    media = db.relationship("ProductMedia", back_populates="product", cascade="all, delete-orphan", order_by="ProductMedia.sort_order")

    @property
    def badges(self):
        if not self.badge:
            return []
        return [badge.strip() for badge in self.badge.split(",") if badge.strip()]

    @property
    def cover_media_url(self):
        image_media = next((item for item in self.media if item.media_type == "image"), None)
        return image_media.media_url if image_media else self.image_url


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(180))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    product = db.relationship("Product", back_populates="images")


class ProductMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_url = db.Column(db.String(500), nullable=False)
    media_type = db.Column(db.String(20), nullable=False, default="image")
    original_filename = db.Column(db.String(255))
    alt_text = db.Column(db.String(180))
    sort_order = db.Column(db.Integer, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    product = db.relationship("Product", back_populates="media")
