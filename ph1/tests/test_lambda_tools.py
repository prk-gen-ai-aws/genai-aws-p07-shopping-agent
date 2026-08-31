"""
P07 Shopping Agent — Lambda Tools Test Suite
Regression tests for all Lambda tool functionality
Run: python3 ph1/tests/test_lambda_tools.py
"""
import boto3
import json
import sys

LAMBDA_NAME = 'p07-ph1-shopping-agent-dev-tools'
REGION      = 'us-east-1'

client = boto3.client('lambda', region_name=REGION)

# ── Test runner ──────────────────────────────────────────────────
passed = 0
failed = 0
errors = []

def invoke(payload):
    response = client.invoke(
        FunctionName=LAMBDA_NAME,
        Payload=json.dumps(payload).encode()
    )
    result = json.loads(response['Payload'].read())
    return json.loads(result['body'])

def test(name, payload, assertions):
    global passed, failed
    try:
        result = invoke(payload)
        for assertion_fn, msg in assertions:
            assert assertion_fn(result), f"FAILED: {msg}\n  Result: {json.dumps(result, indent=2)}"
        print(f"  ✅ {name}")
        passed += 1
    except AssertionError as e:
        print(f"  ❌ {name}")
        print(f"     {e}")
        failed += 1
        errors.append(name)
    except Exception as e:
        print(f"  ❌ {name} — ERROR: {e}")
        failed += 1
        errors.append(name)


# ════════════════════════════════════════════════════════════════
# TEST GROUP 1: search_products — keyword filtering
# ════════════════════════════════════════════════════════════════
print("\n📦 Group 1: search_products — keyword filtering")

test("search by keyword 'honey' returns 4 products",
    {"action": "search_products", "keyword": "honey"},
    [(lambda r: r['count'] == 4, "expected 4 honey products"),
     (lambda r: all('honey' in p['name'].lower() or 'honey' in p['description'].lower() for p in r['products']), "all results should contain honey")])

test("search by keyword 'oats' returns 1 product",
    {"action": "search_products", "keyword": "oats"},
    [(lambda r: r['count'] == 1, "expected 1 oat product"),
     (lambda r: r['products'][0]['product_id'] == 'P003', "should be P003 Organic Oats")])

test("search by keyword 'oil' returns 3 products",
    {"action": "search_products", "keyword": "oil"},
    [(lambda r: r['count'] == 3, "expected 3 oil products")])

test("search by keyword 'protein' returns 3 products (incl quinoa description)",
    {"action": "search_products", "keyword": "protein"},
    [(lambda r: r['count'] == 3, "expected 3 protein products"),
     (lambda r: any(p['product_id'] == 'P014' for p in r['products']), "should include P014"),
     (lambda r: any(p['product_id'] == 'P015' for p in r['products']), "should include P015"),
     (lambda r: any(p['product_id'] == 'P008' for p in r['products']), "quinoa has protein in description")])

test("search by keyword 'elephant' returns 0 products (out of scope)",
    {"action": "search_products", "keyword": "elephant"},
    [(lambda r: r['count'] == 0, "expected 0 results for elephant")])

test("search with no keyword returns all 19 products",
    {"action": "search_products"},
    [(lambda r: r['count'] == 19, "expected all 19 products")])


# ════════════════════════════════════════════════════════════════
# TEST GROUP 2: search_products — price filtering
# ════════════════════════════════════════════════════════════════
print("\n💰 Group 2: search_products — price filtering")

test("search honey under $20 returns 3 products (excludes Manuka $34.99)",
    {"action": "search_products", "keyword": "honey", "max_price": 20},
    [(lambda r: r['count'] == 3, "expected 3 honey products under $20"),
     (lambda r: all(p['price'] <= 20 for p in r['products']), "all prices should be <= 20")])

test("search under $10 returns budget products only",
    {"action": "search_products", "max_price": 10},
    [(lambda r: r['count'] > 0, "expected some products under $10"),
     (lambda r: all(p['price'] <= 10 for p in r['products']), "all prices should be <= 10")])

test("search under $5 returns 0 products",
    {"action": "search_products", "max_price": 5},
    [(lambda r: r['count'] == 0, "expected 0 products under $5 (cheapest is $5.99)")])

test("search all products under $35 returns all 19",
    {"action": "search_products", "max_price": 35},
    [(lambda r: r['count'] == 19, "expected all 19 products under $35")])


# ════════════════════════════════════════════════════════════════
# TEST GROUP 3: search_products — organic filtering
# ════════════════════════════════════════════════════════════════
print("\n🌿 Group 3: search_products — organic filtering")

test("search organic only returns 11 products",
    {"action": "search_products", "is_organic": True},
    [(lambda r: r['count'] == 11, "expected 11 organic products"),
     (lambda r: all(p['is_organic'] == True for p in r['products']), "all results should be organic")])

test("search non-organic returns 8 products",
    {"action": "search_products", "is_organic": False},
    [(lambda r: r['count'] == 8, "expected 8 non-organic products"),
     (lambda r: all(p['is_organic'] == False for p in r['products']), "all results should be non-organic")])

test("search organic honey under $20 returns 3 products",
    {"action": "search_products", "keyword": "honey", "is_organic": True, "max_price": 20},
    [(lambda r: r['count'] == 3, "expected 3 organic honey products under $20"),
     (lambda r: all(p['is_organic'] == True for p in r['products']), "all should be organic"),
     (lambda r: all(p['price'] <= 20 for p in r['products']), "all prices should be <= 20")])

test("search organic + non-existent keyword returns 0",
    {"action": "search_products", "keyword": "tiger", "is_organic": True},
    [(lambda r: r['count'] == 0, "expected 0 results for organic tiger")])


# ════════════════════════════════════════════════════════════════
# TEST GROUP 4: get_product_rating
# ════════════════════════════════════════════════════════════════
print("\n⭐ Group 4: get_product_rating")

test("P001 Organic Raw Honey avg rating ~4.62 with 4 reviews",
    {"action": "get_product_rating", "product_id": "P001"},
    [(lambda r: r['review_count'] == 4, "expected 4 reviews"),
     (lambda r: 4.5 <= r['average_rating'] <= 4.7, "expected avg ~4.62")])

test("P013 Manuka Honey avg rating ~4.83 with 3 reviews",
    {"action": "get_product_rating", "product_id": "P013"},
    [(lambda r: r['review_count'] == 3, "expected 3 reviews"),
     (lambda r: r['average_rating'] >= 4.5, "expected high rating >= 4.5")])

test("P002 Coconut Oil avg rating ~3.83 with 3 reviews",
    {"action": "get_product_rating", "product_id": "P002"},
    [(lambda r: r['review_count'] == 3, "expected 3 reviews"),
     (lambda r: 3.5 <= r['average_rating'] <= 4.0, "expected avg ~3.83")])

test("non-existent product returns 0 rating and 0 reviews",
    {"action": "get_product_rating", "product_id": "P999"},
    [(lambda r: r['review_count'] == 0, "expected 0 reviews"),
     (lambda r: r['average_rating'] == 0, "expected 0 rating")])


# ════════════════════════════════════════════════════════════════
# TEST GROUP 5: place_order
# ════════════════════════════════════════════════════════════════
print("\n🛒 Group 5: place_order")

test("place order for P001 Organic Raw Honey succeeds",
    {"action": "place_order", "product_id": "P001"},
    [(lambda r: r['success'] == True, "order should succeed"),
     (lambda r: 'order_id' in r, "should return order_id"),
     (lambda r: r['product'] == 'Organic Raw Honey', "product name should match"),
     (lambda r: r['price'] == 15.99, "price should be 15.99")])

test("place order for P018 Dark Chocolate succeeds",
    {"action": "place_order", "product_id": "P018"},
    [(lambda r: r['success'] == True, "order should succeed"),
     (lambda r: r['price'] == 5.99, "price should be 5.99")])

test("place order for non-existent product fails gracefully",
    {"action": "place_order", "product_id": "P999"},
    [(lambda r: r['success'] == False, "order should fail"),
     (lambda r: 'error' in r, "should return error message")])


# ════════════════════════════════════════════════════════════════
# TEST GROUP 6: edge cases
# ════════════════════════════════════════════════════════════════
print("\n🔧 Group 6: edge cases")

test("unknown action returns error",
    {"action": "unknown_action"},
    [(lambda r: 'error' in r, "should return error for unknown action")])

test("search with empty keyword returns all products",
    {"action": "search_products", "keyword": ""},
    [(lambda r: r['count'] == 19, "empty keyword should return all 19 products")])

test("search category 'grains' returns oats and quinoa",
    {"action": "search_products", "keyword": "grains"},
    [(lambda r: r['count'] == 2, "expected 2 grain products")])

test("search 'matcha' returns matcha powder",
    {"action": "search_products", "keyword": "matcha"},
    [(lambda r: r['count'] == 1, "expected 1 matcha product"),
     (lambda r: r['products'][0]['product_id'] == 'P017', "should be P017 Matcha Powder")])


# ════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════
total = passed + failed
print(f"\n{'='*50}")
print(f"TEST RESULTS: {passed}/{total} passed")
if errors:
    print(f"FAILED TESTS:")
    for e in errors:
        print(f"  ❌ {e}")
else:
    print("✅ All tests passed!")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
