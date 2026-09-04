"""
P07 Shopping Agent — Strands Agent with AgentCore Runtime
AWS-native rebuild of Dhaval Patel's LangChain Shopping Agent
Tools: search_products, get_product_rating, place_order, search_by_image
"""
import json
import base64
import os
import asyncio
from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# ── Config ──────────────────────────────────────────────────────
import boto3
LAMBDA_NAME = os.environ.get('LAMBDA_TOOLS_NAME', 'p07-ph1-shopping-agent-dev-tools')
AWS_REGION  = os.environ.get('AWS_REGION', 'us-east-1')
MODEL_ID    = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'

lambda_client = boto3.client('lambda', region_name=AWS_REGION)

def invoke_lambda(payload: dict) -> dict:
    """Invoke the Lambda tools function."""
    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        Payload=json.dumps(payload).encode()
    )
    result = json.loads(response['Payload'].read())
    return json.loads(result['body'])

# ── Tools ────────────────────────────────────────────────────────

@tool
def search_products(keyword: str = None, max_price: float = None, is_organic: bool = None) -> str:
    """
    Search for products in the store by keyword, price, and organic filter.

    Use this tool when the user wants to find or browse products.
    Call this BEFORE get_product_rating to find product IDs.

    Args:
        keyword: Search term to match against product name, description, or category.
                 Examples: "honey", "oats", "oil", "chocolate", "protein"
        max_price: Maximum price filter in USD. Example: 20.0 for "under $20"
        is_organic: Filter for organic products only (True) or non-organic only (False).
                    Leave as None to return both.

    Returns:
        JSON string with list of matching products including product_id, name, category,
        price, description, and is_organic flag.
    """
    payload = {"action": "search_products"}
    if keyword:
        payload["keyword"] = keyword
    if max_price is not None:
        payload["max_price"] = max_price
    if is_organic is not None:
        payload["is_organic"] = is_organic

    result = invoke_lambda(payload)
    return json.dumps(result)


@tool
def get_product_rating(product_id: str) -> str:
    """
    Get the average customer rating and review count for a specific product.

    Use this tool after search_products to get ratings for found products.
    Always call this for each candidate product when user asks for rated products.

    Args:
        product_id: The product ID from search_products results. Example: "P001"

    Returns:
        JSON string with product_id, average_rating (0-5), and review_count.
    """
    result = invoke_lambda({"action": "get_product_rating", "product_id": product_id})
    return json.dumps(result)


@tool
def place_order(product_id: str) -> str:
    """
    Place an order for a specific product.

    IMPORTANT: Only call this tool when the user EXPLICITLY confirms they want to order.
    Never place an order without user confirmation.
    Never guess a product_id — always use the exact ID from search_products results.

    Args:
        product_id: The exact product ID to order. Example: "P001"

    Returns:
        JSON string with order confirmation including order_id, product name, and price.
    """
    result = invoke_lambda({"action": "place_order", "product_id": product_id})
    return json.dumps(result)


@tool
def search_by_image(image_base64: str, media_type: str = "image/jpeg") -> str:
    """
    Search for products similar to an uploaded image using multimodal AI.

    Use this tool when the user uploads an image and wants to find similar products.
    The tool uses Claude's vision capabilities to identify the product in the image
    and then searches the store for similar items.

    Args:
        image_base64: Base64 encoded image string
        media_type: Image MIME type. One of: "image/jpeg", "image/png", "image/webp"

    Returns:
        JSON string with image description, search query used, and matching products.
    """
    result = invoke_lambda({
        "action": "search_by_image",
        "image_base64": image_base64,
        "media_type": media_type
    })
    return json.dumps(result)


# ── System Prompt ────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a helpful AI shopping assistant for an organic health food store.
You help customers find products, check ratings, and place orders.

## Tools available:
- search_products: Find products by keyword, price, or organic filter
- get_product_rating: Get average rating and review count for a product
- place_order: Place an order for a product
- search_by_image: Find products similar to an uploaded image

## Rules for TEXT search:
1. Call search_products with the appropriate filters
2. For each result, call get_product_rating to get ratings
3. Filter by user's minimum rating if specified
4. Present qualified products as a numbered list with:
   - Product name and ID
   - Price
   - Rating (x/5 from N reviews)
   - Organic status
5. Ask if they want to order any item

## Rules for IMAGE search:
1. Call search_by_image with the provided image_base64 and media_type
2. Present found products as a numbered list
3. Call get_product_rating for each product found
4. Ask if they want to order any item

## Rules for ORDERING:
1. NEVER place an order unless the user EXPLICITLY confirms (e.g. "order item 1", "yes place the order")
2. NEVER guess a product_id — use exact IDs from search results
3. After ordering, confirm with order ID and price

## Rules for OUT OF SCOPE queries:
1. If user asks for products not in our store, say you couldn't find matching products
2. If user asks non-shopping questions, politely redirect to shopping

## Formatting:
- Use emojis sparingly for a friendly tone 🛒
- Keep responses concise and scannable
- Always show price with $ sign — NEVER use backtick for prices
- Show ratings as x.x/5 (N reviews)
"""

# ── AgentCore App ────────────────────────────────────────────────
# Agent in GLOBAL scope — conversation history persists across invocations
app = BedrockAgentCoreApp()

_model = BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION)
_agent = Agent(
    model=_model,
    system_prompt=SYSTEM_PROMPT,
    tools=[search_products, get_product_rating, place_order, search_by_image],
    callback_handler=None
)

@app.entrypoint
async def agent_entrypoint(payload: dict) -> str:
    """Agent entrypoint for AgentCore Runtime."""
    prompt = payload.get("prompt", "")
    image_base64 = payload.get("image_base64")
    media_type = payload.get("media_type", "image/jpeg")

    if image_base64:
        # Pass image as proper multimodal message
        messages = [{
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": media_type.split("/")[-1],
                        "source": {
                            "bytes": base64.b64decode(image_base64)
                        }
                    }
                },
                {
                    "text": prompt
                }
            ]
        }]
        response = await _agent.invoke_async(messages)
    else:
        response = await _agent.invoke_async(prompt)

    return str(response)


if __name__ == "__main__":
    app.run()
