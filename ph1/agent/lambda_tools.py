"""
P07 Shopping Agent — Lambda Tools
4 tools: search_products, get_product_rating, place_order, search_by_image
Deploy as a single Lambda function with action routing
"""
import json
import boto3
import uuid
from decimal import Decimal
from datetime import datetime, timezone
import base64

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
bedrock  = boto3.client('bedrock-runtime', region_name='us-east-1')

PRODUCTS_TABLE = 'p07-ph1-shopping-agent-dev-products'
REVIEWS_TABLE  = 'p07-ph1-shopping-agent-dev-reviews'
ORDERS_TABLE   = 'p07-ph1-shopping-agent-dev-orders'
MODEL_ID       = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def search_products(keyword=None, max_price=None, is_organic=None):
    """Search products by keyword, price, and organic filter."""
    table = dynamodb.Table(PRODUCTS_TABLE)
    response = table.scan()
    items = response.get('Items', [])

    # Filter by keyword
    if keyword:
        kw = keyword.lower()
        items = [
            i for i in items
            if kw in i.get('name', '').lower()
            or kw in i.get('description', '').lower()
            or kw in i.get('category', '').lower()
        ]

    # Filter by max_price
    if max_price is not None:
        items = [i for i in items if float(i.get('price', 0)) <= float(max_price)]

    # Filter by is_organic
    if is_organic is not None:
        items = [i for i in items if i.get('is_organic') == is_organic]

    return {
        'products': items,
        'count': len(items)
    }


def get_product_rating(product_id):
    """Get average rating and review count for a product."""
    table = dynamodb.Table(REVIEWS_TABLE)
    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('product_id').eq(product_id)
    )
    reviews = response.get('Items', [])

    if not reviews:
        return {'product_id': product_id, 'average_rating': 0, 'review_count': 0}

    avg = sum(float(r.get('rating', 0)) for r in reviews) / len(reviews)
    return {
        'product_id': product_id,
        'average_rating': round(avg, 2),
        'review_count': len(reviews)
    }


def place_order(product_id):
    """Place an order for a product."""
    # Get product details
    products_table = dynamodb.Table(PRODUCTS_TABLE)
    response = products_table.get_item(Key={'product_id': product_id})
    product = response.get('Item')

    if not product:
        return {'success': False, 'error': f'Product {product_id} not found'}

    # Insert order
    orders_table = dynamodb.Table(ORDERS_TABLE)
    order_id = str(uuid.uuid4())
    order = {
        'order_id': order_id,
        'product_id': product_id,
        'name': product.get('name'),
        'price': product.get('price'),
        'ordered_at': datetime.now(timezone.utc).isoformat()
    }
    orders_table.put_item(Item=order)

    return {
        'success': True,
        'order_id': order_id,
        'product': product.get('name'),
        'price': float(product.get('price', 0)),
        'message': f"Order placed successfully for {product.get('name')} at ${float(product.get('price', 0)):.2f}"
    }


def search_by_image(image_base64, media_type='image/jpeg'):
    """Describe a product image and search for similar products."""
    # Call Bedrock vision to describe the image
    body = json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 300,
        'messages': [{
            'role': 'user',
            'content': [
                {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': media_type,
                        'data': image_base64
                    }
                },
                {
                    'type': 'text',
                    'text': '''Look at this product image. Extract its key attributes and return a JSON object with exactly these fields:
{
  "product_type": "main product type (e.g. honey, oats, oil)",
  "search_query": "best 1-2 word keyword to search for this product",
  "is_organic": true or false based on visual cues,
  "description": "brief description of what you see"
}
Return only the JSON object, no other text.'''
                }
            ]
        }]
    })

    response = bedrock.invoke_model(modelId=MODEL_ID, body=body)
    result = json.loads(response['body'].read())
    text = result['content'][0]['text'].strip()

    try:
        image_info = json.loads(text)
    except json.JSONDecodeError:
        image_info = {'search_query': 'product', 'is_organic': None}

    # Search products using extracted query
    search_result = search_products(
        keyword=image_info.get('search_query', 'product'),
        is_organic=image_info.get('is_organic')
    )

    return {
        'image_description': image_info.get('description', ''),
        'search_query_used': image_info.get('search_query', ''),
        'products': search_result['products'],
        'count': search_result['count']
    }


def lambda_handler(event, context):
    """Route to the correct tool based on action parameter."""
    action = event.get('action')

    try:
        if action == 'search_products':
            result = search_products(
                keyword=event.get('keyword'),
                max_price=event.get('max_price'),
                is_organic=event.get('is_organic')
            )
        elif action == 'get_product_rating':
            result = get_product_rating(event['product_id'])
        elif action == 'place_order':
            result = place_order(event['product_id'])
        elif action == 'search_by_image':
            result = search_by_image(
                image_base64=event['image_base64'],
                media_type=event.get('media_type', 'image/jpeg')
            )
        else:
            result = {'error': f'Unknown action: {action}'}

        return {
            'statusCode': 200,
            'body': json.dumps(result, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
