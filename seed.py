from datetime import date

from app import create_app, db
from app.models.admin import Admin
from app.models.category import Category
from app.models.order import MaterialCost, Order
from app.models.product import Product, ProductMedia
from app.models.review import Review
from app.models.settings import GalleryItem, WebsiteSettings
from app.utils.schema import ensure_runtime_schema
from app.utils.slugify import slugify

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        ensure_runtime_schema()
        print("Seeded demo data.")
        print("Admin login: curatedbyafza@gmail.com / 123456789")
