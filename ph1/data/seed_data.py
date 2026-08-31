"""
P07 Shopping Agent — Seed DynamoDB with sample product data
Equivalent to Dhaval's SQLite store.db
"""
import boto3
import uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

PRODUCTS_TABLE = 'p07-ph1-shopping-agent-dev-products'
REVIEWS_TABLE  = 'p07-ph1-shopping-agent-dev-reviews'

# ── Products ─────────────────────────────────────────────────────
products = [
    # Honey
    {"product_id": "P001", "name": "Organic Raw Honey",        "category": "Honey",           "price": Decimal("15.99"), "description": "Pure organic raw honey, unfiltered and unprocessed", "is_organic": True},
    {"product_id": "P005", "name": "Organic Buckwheat Honey",  "category": "Honey",           "price": Decimal("18.99"), "description": "Dark rich buckwheat honey with strong antioxidant properties", "is_organic": True},
    {"product_id": "P007", "name": "Organic Acacia Honey",     "category": "Honey",           "price": Decimal("19.99"), "description": "Light golden acacia honey with delicate floral flavor", "is_organic": True},
    {"product_id": "P013", "name": "Manuka Honey",             "category": "Honey",           "price": Decimal("34.99"), "description": "Premium New Zealand Manuka honey UMF 10+", "is_organic": False},
    # Oils
    {"product_id": "P002", "name": "Coconut Oil",              "category": "Oils",            "price": Decimal("12.49"), "description": "Cold pressed virgin coconut oil for cooking and skincare", "is_organic": False},
    {"product_id": "P006", "name": "Extra Virgin Olive Oil",   "category": "Oils",            "price": Decimal("22.99"), "description": "Cold pressed extra virgin olive oil from Mediterranean olives", "is_organic": False},
    {"product_id": "P012", "name": "Avocado Oil",              "category": "Oils",            "price": Decimal("16.99"), "description": "Pure avocado oil great for high heat cooking", "is_organic": False},
    # Grains
    {"product_id": "P003", "name": "Organic Oats",             "category": "Grains",          "price": Decimal("8.99"),  "description": "Whole grain rolled oats, gluten-free certified", "is_organic": True},
    {"product_id": "P008", "name": "Organic Quinoa",           "category": "Grains",          "price": Decimal("11.99"), "description": "Organic white quinoa high in protein and fiber", "is_organic": True},
    # Nut Butters
    {"product_id": "P004", "name": "Almond Butter",            "category": "Nut Butters",     "price": Decimal("14.99"), "description": "Creamy almond butter with no added sugar or salt", "is_organic": False},
    {"product_id": "P009", "name": "Peanut Butter",            "category": "Nut Butters",     "price": Decimal("7.99"),  "description": "Natural peanut butter made from roasted peanuts only", "is_organic": False},
    # Seeds
    {"product_id": "P010", "name": "Organic Chia Seeds",       "category": "Seeds",           "price": Decimal("9.99"),  "description": "Organic black chia seeds rich in omega-3 fatty acids", "is_organic": True},
    {"product_id": "P011", "name": "Organic Flaxseeds",        "category": "Seeds",           "price": Decimal("6.99"),  "description": "Whole organic golden flaxseeds high in fiber", "is_organic": True},
    # Protein
    {"product_id": "P014", "name": "Organic Whey Protein",     "category": "Protein",         "price": Decimal("29.99"), "description": "Organic grass-fed whey protein vanilla flavor 1lb", "is_organic": True},
    {"product_id": "P015", "name": "Pea Protein Powder",       "category": "Protein",         "price": Decimal("24.99"), "description": "Plant-based pea protein powder unflavored", "is_organic": False},
    # Beverages
    {"product_id": "P016", "name": "Organic Green Tea",        "category": "Beverages",       "price": Decimal("13.99"), "description": "Premium Japanese organic green tea 50 bags", "is_organic": True},
    {"product_id": "P017", "name": "Matcha Powder",            "category": "Beverages",       "price": Decimal("27.99"), "description": "Ceremonial grade organic matcha powder from Japan", "is_organic": True},
    # Snacks
    {"product_id": "P018", "name": "Organic Dark Chocolate",   "category": "Snacks",          "price": Decimal("5.99"),  "description": "70% cacao organic dark chocolate bar", "is_organic": True},
    {"product_id": "P019", "name": "Mixed Nuts",               "category": "Snacks",          "price": Decimal("17.99"), "description": "Premium mixed nuts with almonds cashews and walnuts", "is_organic": False},
]

# ── Reviews ──────────────────────────────────────────────────────
reviews = [
    # P001 Organic Raw Honey (avg 4.63)
    {"review_id": str(uuid.uuid4()), "product_id": "P001", "reviewer": "Alice",   "comment": "Amazing quality honey, love it!", "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P001", "reviewer": "Bob",     "comment": "Good honey but slightly pricey",   "rating": Decimal("4")},
    {"review_id": str(uuid.uuid4()), "product_id": "P001", "reviewer": "Carol",   "comment": "Best raw honey I have tried",      "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P001", "reviewer": "David",   "comment": "Great taste and texture",          "rating": Decimal("4.5")},
    # P002 Coconut Oil (avg 3.83)
    {"review_id": str(uuid.uuid4()), "product_id": "P002", "reviewer": "Eve",     "comment": "Works great for cooking",          "rating": Decimal("4")},
    {"review_id": str(uuid.uuid4()), "product_id": "P002", "reviewer": "Frank",   "comment": "Good quality coconut oil",         "rating": Decimal("3.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P002", "reviewer": "Grace",   "comment": "Nice smell and consistency",       "rating": Decimal("4")},
    # P003 Organic Oats (avg 4.5)
    {"review_id": str(uuid.uuid4()), "product_id": "P003", "reviewer": "Henry",   "comment": "Perfect for breakfast",            "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P003", "reviewer": "Irene",   "comment": "Great oats, cook evenly",          "rating": Decimal("4.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P003", "reviewer": "Jack",    "comment": "Good value for money",             "rating": Decimal("4")},
    # P004 Almond Butter (avg 4.75)
    {"review_id": str(uuid.uuid4()), "product_id": "P004", "reviewer": "Rachel",  "comment": "Smooth and creamy",                "rating": Decimal("4.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P004", "reviewer": "Sam",     "comment": "Kids love it",                     "rating": Decimal("5")},
    # P005 Organic Buckwheat Honey (avg 4.75)
    {"review_id": str(uuid.uuid4()), "product_id": "P005", "reviewer": "Kate",    "comment": "Strong flavor, love it",           "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P005", "reviewer": "Liam",    "comment": "Good for sore throat",             "rating": Decimal("4.5")},
    # P006 Extra Virgin Olive Oil (avg 4.33)
    {"review_id": str(uuid.uuid4()), "product_id": "P006", "reviewer": "Tom",     "comment": "Excellent flavor for salads",      "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P006", "reviewer": "Uma",     "comment": "Good quality olive oil",           "rating": Decimal("4")},
    {"review_id": str(uuid.uuid4()), "product_id": "P006", "reviewer": "Victor",  "comment": "A bit expensive but worth it",     "rating": Decimal("4")},
    # P007 Organic Acacia Honey (avg 4.5)
    {"review_id": str(uuid.uuid4()), "product_id": "P007", "reviewer": "Mia",     "comment": "Light and delicious",              "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P007", "reviewer": "Noah",    "comment": "Best acacia honey around",         "rating": Decimal("4.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P007", "reviewer": "Olivia",  "comment": "Great on toast",                   "rating": Decimal("4")},
    # P008 Organic Quinoa (avg 4.33)
    {"review_id": str(uuid.uuid4()), "product_id": "P008", "reviewer": "Peter",   "comment": "Great protein source",             "rating": Decimal("4.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P008", "reviewer": "Queen",   "comment": "Cooks perfectly every time",       "rating": Decimal("4")},
    {"review_id": str(uuid.uuid4()), "product_id": "P008", "reviewer": "Rose",    "comment": "Good but takes time to cook",      "rating": Decimal("4.5")},
    # P009 Peanut Butter (avg 3.83)
    {"review_id": str(uuid.uuid4()), "product_id": "P009", "reviewer": "Steve",   "comment": "Classic peanut butter taste",      "rating": Decimal("4")},
    {"review_id": str(uuid.uuid4()), "product_id": "P009", "reviewer": "Tina",    "comment": "Decent but prefer almond butter",  "rating": Decimal("3.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P009", "reviewer": "Ursula",  "comment": "Good value for money",             "rating": Decimal("4")},
    # P010 Organic Chia Seeds (avg 4.5)
    {"review_id": str(uuid.uuid4()), "product_id": "P010", "reviewer": "Paul",    "comment": "Fresh and high quality",           "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P010", "reviewer": "Quinn",   "comment": "Good for smoothies",               "rating": Decimal("4")},
    # P011 Organic Flaxseeds (avg 4.17)
    {"review_id": str(uuid.uuid4()), "product_id": "P011", "reviewer": "Vera",    "comment": "Good for baking",                  "rating": Decimal("4")},
    {"review_id": str(uuid.uuid4()), "product_id": "P011", "reviewer": "Walter",  "comment": "High quality flaxseeds",           "rating": Decimal("4.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P011", "reviewer": "Xena",    "comment": "Good fiber source",                "rating": Decimal("4")},
    # P012 Avocado Oil (avg 4.5)
    {"review_id": str(uuid.uuid4()), "product_id": "P012", "reviewer": "Yara",    "comment": "Great for high heat cooking",      "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P012", "reviewer": "Zack",    "comment": "Light flavor, love it",            "rating": Decimal("4")},
    # P013 Manuka Honey (avg 4.83)
    {"review_id": str(uuid.uuid4()), "product_id": "P013", "reviewer": "Anna",    "comment": "Worth every penny, amazing!",      "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P013", "reviewer": "Ben",     "comment": "Premium quality manuka honey",     "rating": Decimal("4.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P013", "reviewer": "Clara",   "comment": "Great medicinal properties",       "rating": Decimal("5")},
    # P014 Organic Whey Protein (avg 4.5)
    {"review_id": str(uuid.uuid4()), "product_id": "P014", "reviewer": "Dan",     "comment": "Great taste and mixes well",       "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P014", "reviewer": "Ella",    "comment": "Clean ingredients, love it",       "rating": Decimal("4")},
    # P015 Pea Protein (avg 3.75)
    {"review_id": str(uuid.uuid4()), "product_id": "P015", "reviewer": "Finn",    "comment": "Good plant based option",          "rating": Decimal("4")},
    {"review_id": str(uuid.uuid4()), "product_id": "P015", "reviewer": "Gina",    "comment": "Bit chalky but decent",            "rating": Decimal("3.5")},
    # P016 Organic Green Tea (avg 4.67)
    {"review_id": str(uuid.uuid4()), "product_id": "P016", "reviewer": "Hank",    "comment": "Smooth flavor, great quality",     "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P016", "reviewer": "Iris",    "comment": "Best green tea I have had",        "rating": Decimal("4.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P016", "reviewer": "Jake",    "comment": "Relaxing and delicious",           "rating": Decimal("4.5")},
    # P017 Matcha Powder (avg 4.75)
    {"review_id": str(uuid.uuid4()), "product_id": "P017", "reviewer": "Kim",     "comment": "Authentic ceremonial grade",       "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P017", "reviewer": "Leo",     "comment": "Vibrant color and great taste",    "rating": Decimal("4.5")},
    # P018 Organic Dark Chocolate (avg 4.5)
    {"review_id": str(uuid.uuid4()), "product_id": "P018", "reviewer": "Maya",    "comment": "Rich and not too sweet",           "rating": Decimal("5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P018", "reviewer": "Nate",    "comment": "Great quality chocolate",          "rating": Decimal("4")},
    # P019 Mixed Nuts (avg 4.17)
    {"review_id": str(uuid.uuid4()), "product_id": "P019", "reviewer": "Opal",    "comment": "Fresh and crunchy mix",            "rating": Decimal("4.5")},
    {"review_id": str(uuid.uuid4()), "product_id": "P019", "reviewer": "Pete",    "comment": "Good variety of nuts",             "rating": Decimal("4")},
    {"review_id": str(uuid.uuid4()), "product_id": "P019", "reviewer": "Quinn",   "comment": "A bit pricey but good quality",    "rating": Decimal("4")},
]

def clear_table(table_name):
    table = dynamodb.Table(table_name)
    response = table.scan()
    items = response.get('Items', [])
    pk = table.key_schema[0]['AttributeName']
    for item in items:
        table.delete_item(Key={pk: item[pk]})
    print(f"  Cleared {len(items)} items from {table_name}")

def seed_products():
    table = dynamodb.Table(PRODUCTS_TABLE)
    for p in products:
        table.put_item(Item=p)
        print(f"  ✅ {p['name']} (${p['price']})")
    print(f"Seeded {len(products)} products")

def seed_reviews():
    table = dynamodb.Table(REVIEWS_TABLE)
    for r in reviews:
        table.put_item(Item=r)
    print(f"Seeded {len(reviews)} reviews across {len(set(r['product_id'] for r in reviews))} products")

if __name__ == '__main__':
    print("Clearing existing data...")
    clear_table(PRODUCTS_TABLE)
    clear_table(REVIEWS_TABLE)

    print("\nSeeding products...")
    seed_products()

    print("\nSeeding reviews...")
    seed_reviews()

    print("\n✅ Done — DynamoDB tables seeded")
    print(f"\nSummary:")
    print(f"  {len(products)} products across {len(set(p['category'] for p in products))} categories")
    print(f"  {len(reviews)} reviews")
    print(f"  Price range: ${min(float(p['price']) for p in products):.2f} - ${max(float(p['price']) for p in products):.2f}")
    print(f"  Organic products: {sum(1 for p in products if p['is_organic'])}")
