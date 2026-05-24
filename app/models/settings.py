from app import db


class WebsiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(160), default="Luna & Lace Gifts")
    hero_title = db.Column(db.String(220), default="Handmade Gifts, Softly Tailored To The Moment")
    hero_subtitle = db.Column(db.Text, default="Customized bouquets, luxury hampers, pipe cleaner florals, and aesthetic surprise gifts made with patience, texture, and a little sparkle.")
    whatsapp_number = db.Column(db.String(40), default="919999999999")
    instagram_url = db.Column(db.String(300), default="https://instagram.com/")
    contact_email = db.Column(db.String(180), default="hello@lunaandlace.example")
    studio_address = db.Column(db.String(300), default="By appointment, your city")


class GalleryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(240))
    sort_order = db.Column(db.Integer, default=0)
