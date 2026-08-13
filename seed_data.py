import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopEase.settings')
django.setup()

from shop.models import Category, Product

def populate():
    print("Populating initial data...")

    Product.objects.all().delete()
    Category.objects.all().delete()

    categories = {
        'Electronics': 'Gadgets, audio equipment, and household appliances.',
        'Fashion': 'Modern clothing, footwear, and wearable style items.',
        'Mobile Accessories': 'Cases, fast chargers, cables, and screen protectors.',
        'Home & Kitchen': 'Cookware, decoration, and home organizers.',
        'Computer Accessories': 'Mice, keyboards, storage devices, and USB hubs.'
    }

    cat_objs = {}
    for name, desc in categories.items():
        cat = Category.objects.create(name=name, description=desc, slug=name.lower().replace(' ', '-'))
        cat_objs[name] = cat

    products_data = [
        ("Wireless Noise-Canceling Headphones", "Electronics", 4999.00, 10, 4.5, True, True),
        ("Bluetooth Soundbar 120W", "Electronics", 6500.00, 15, 4.3, False, True),
        ("Smart Fitness Watch", "Electronics", 2999.00, 5, 4.7, True, True),
        ("4K Ultra HD Action Camera", "Electronics", 8999.00, 20, 4.2, False, False),

        ("Classic Men's Denim Jacket", "Fashion", 1999.00, 15, 4.4, True, False),
        ("Women's Cotton Casual Top", "Fashion", 799.00, 0, 4.1, False, True),
        ("Sports Running Shoes", "Fashion", 2499.00, 20, 4.6, True, True),
        ("Leather Minimalist Wallet", "Fashion", 499.00, 0, 4.0, False, False),

        ("20000mAh Fast Charging Power Bank", "Mobile Accessories", 1499.00, 10, 4.8, True, True),
        ("Magnetic Car Phone Mount", "Mobile Accessories", 399.00, 0, 4.2, False, False),
        ("Braided Type-C Fast Cable 2m", "Mobile Accessories", 299.00, 0, 4.5, False, True),
        ("Wireless Charging Pad 15W", "Mobile Accessories", 999.00, 15, 4.1, False, False),

        ("Stainless Steel Electric Kettle", "Home & Kitchen", 1299.00, 10, 4.6, False, True),
        ("Non-Stick Cookware Set (3 Piece)", "Home & Kitchen", 2199.00, 12, 4.4, True, False),
        ("Digital Kitchen Scale", "Home & Kitchen", 599.00, 0, 4.3, False, False),
        ("Air Purifier for Home", "Home & Kitchen", 7499.00, 25, 4.7, True, True),

        ("Ergonomic Wireless Optical Mouse", "Computer Accessories", 699.00, 10, 4.5, False, True),
        ("Mechanical RGB Gaming Keyboard", "Computer Accessories", 3200.00, 15, 4.8, True, True),
        ("1TB External Portable Hard Drive", "Computer Accessories", 4500.00, 5, 4.6, False, True),
        ("Multi-Port USB-C Docking Station", "Computer Accessories", 1899.00, 10, 4.3, False, False),
    ]

    for title, cat_name, price, disc, rating, feat, pop in products_data:
        Product.objects.create(
            name=title,
            category=cat_objs[cat_name],
            description=f"High quality {title} carefully curated for high durability and daily needs.",
            price=price,
            discount=disc,
            rating=rating,
            is_featured=feat,
            is_popular=pop,
            stock=25
        )

    print("Populated database with 5 categories and 20 products successfully!")

if __name__ == '__main__':
    populate()