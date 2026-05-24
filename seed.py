from datetime import date

from app import create_app, db
from app.models.admin import Admin
from app.models.category import Category
from app.models.order import MaterialCost, Order
from app.models.product import Product, ProductMedia
from app.models.review import Review
from app.models.settings import GalleryItem, WebsiteSettings
from app.utils.slugify import slugify


IMAGE_BASE = "https://images.unsplash.com"

CATEGORIES = [
    {
        "name": "Luxury Bouquets",
        "description": "Fresh and everlasting floral bunches for birthdays, proposals, and celebrations.",
        "image_url": f"{IMAGE_BASE}/photo-1525310072745-f49212b5ac6d?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Gift Hampers",
        "description": "Layered keepsake boxes with florals, treats, notes, and small luxuries.",
        "image_url": f"{IMAGE_BASE}/photo-1513201099705-a9746e1e201f?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Pipe Cleaner Florals",
        "description": "Soft handmade stems that stay bright long after the moment.",
        "image_url": f"{IMAGE_BASE}/photo-1455659817273-f96807779a8a?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Keepsake Gifts",
        "description": "Personalized keychains, message pieces, and surprise minis.",
        "image_url": f"{IMAGE_BASE}/photo-1512909006721-3d6018887383?auto=format&fit=crop&w=900&q=80",
    },
]

PRODUCTS = [
    {
        "name": "Blush Bloom Bouquet",
        "category": "Luxury Bouquets",
        "description": "A romantic pink-toned bouquet with premium wrapping, satin ribbon, and a handwritten mini note.",
        "price": 1499,
        "badge": "Bestseller, Custom colors",
        "image_url": f"{IMAGE_BASE}/photo-1561181286-d3fee7d55364?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Birthday Surprise Hamper",
        "category": "Gift Hampers",
        "description": "A curated birthday box with florals, chocolates, photo notes, and optional fairy lights.",
        "price": 2199,
        "badge": "Personalized",
        "image_url": f"{IMAGE_BASE}/photo-1549465220-1a8b9238cd48?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Everlasting Tulip Bunch",
        "category": "Pipe Cleaner Florals",
        "description": "Hand-shaped pipe cleaner tulips arranged in soft wrapping for a low-maintenance floral keepsake.",
        "price": 899,
        "badge": "Handmade",
        "image_url": f"{IMAGE_BASE}/photo-1520763185298-1b434c919102?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Mini Memory Keychain Set",
        "category": "Keepsake Gifts",
        "description": "A small personalized keychain set with initials, charms, and gift-ready packaging.",
        "price": 499,
        "badge": "Quick gift",
        "image_url": f"{IMAGE_BASE}/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Proposal Rose Edit",
        "category": "Luxury Bouquets",
        "description": "A statement rose bouquet with dramatic wrapping, custom message card, and premium finish.",
        "price": 2499,
        "badge": "Premium",
        "image_url": f"{IMAGE_BASE}/photo-1518895949257-7621c3c786d7?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Soft Pastel Snack Hamper",
        "category": "Gift Hampers",
        "description": "Pastel-themed hamper with snacks, blooms, ribbons, and a custom note for everyday surprises.",
        "price": 1699,
        "badge": "Made to order",
        "image_url": f"{IMAGE_BASE}/photo-1513885535751-8b9238bd345a?auto=format&fit=crop&w=900&q=80",
    },
]

REVIEWS = [
    ("Ayesha", "@ayesha.notes", "The bouquet looked exactly like the reference and felt even prettier in person."),
    ("Rida", "@ridagifts", "The birthday hamper was packed beautifully and the custom note made it so personal."),
    ("Naina", "@nainamakes", "Loved the pipe cleaner flowers. They are soft, cute, and perfect for a desk corner."),
]


def upsert_seed():
    settings = WebsiteSettings.query.first() or WebsiteSettings()
    settings.brand_name = "Curated by Afza"
    settings.hero_title = "Custom Gifts Curated With Soft Detail"
    settings.hero_subtitle = "Handmade bouquets, hampers, pipe cleaner florals, and keepsakes designed around your story, colors, budget, and occasion."
    settings.whatsapp_number = "916360249286"
    settings.instagram_url = "https://instagram.com/afzasdiaries"
    settings.contact_email = "curatedbyafza@gmail.com"
    settings.studio_address = "Available for custom gifting orders by appointment"
    db.session.add(settings)

    admin = Admin.query.filter_by(email="curatedbyafza@gmail.com").first()
    if not admin:
        admin = Admin(name="Studio Owner", username="afza", email="curatedbyafza@gmail.com")
        admin.set_password("123456789")
        db.session.add(admin)
    else:
        admin.username = admin.username or "afza"
        admin.is_active_account = True

    categories_by_name = {}
    for item in CATEGORIES:
        category = Category.query.filter_by(slug=slugify(item["name"])).first()
        if not category:
            category = Category(name=item["name"], slug=slugify(item["name"]))
        category.description = item["description"]
        category.image_url = item["image_url"]
        category.is_featured = True
        db.session.add(category)
        categories_by_name[item["name"]] = category
    db.session.flush()

    for item in PRODUCTS:
        product = Product.query.filter_by(slug=slugify(item["name"])).first()
        if not product:
            product = Product(name=item["name"], slug=slugify(item["name"]))
        product.description = item["description"]
        product.price = item["price"]
        product.badge = item["badge"]
        product.image_url = item["image_url"]
        product.category = categories_by_name[item["category"]]
        product.is_featured = True
        product.is_active = True
        db.session.add(product)
        db.session.flush()
        if not product.media:
            product.media.append(ProductMedia(
                media_url=item["image_url"],
                media_type="image",
                original_filename=f"{product.slug}.jpg",
                alt_text=product.name,
                sort_order=0,
            ))

    for name, instagram_id, message in REVIEWS:
        existing = Review.query.filter_by(customer_name=name, message=message).first()
        if not existing:
            db.session.add(Review(
                customer_name=name,
                instagram_id=instagram_id,
                message=message,
                rating=5,
                is_approved=True,
            ))

    if not Order.query.first():
        order = Order(
            customer_name="Sample Customer",
            phone="9999999999",
            instagram_id="@sampleorder",
            occasion="Birthday",
            budget=2000,
            delivery_date=date.today(),
            color_theme="Blush pink and white",
            custom_message="Happy birthday, always blooming.",
            product_type="Gift Hamper",
            extra_notes="Demo order for analytics and profit tracking.",
            status="Delivered",
            selling_price=1999,
        )
        order.materials = [
            MaterialCost(material_name="Florals", quantity="1 set", amount=450),
            MaterialCost(material_name="Hamper box", quantity="1", amount=250),
            MaterialCost(material_name="Ribbon and note card", quantity="1", amount=80),
        ]
        db.session.add(order)

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        upsert_seed()
        print("Seeded demo data.")
        print("Admin login: curatedbyafza@gmail.com / 123456789")
