"""
P07 Shopping Agent — Conversation / Short-term Memory Test Suite
Tests multi-turn conversations via AgentCore Runtime
Run: python3 ph1/tests/test_agent_conversation.py
"""
import boto3
import json
import uuid
import time
import sys

RUNTIME_ARN = 'arn:aws:bedrock-agentcore:us-east-1:759802535955:runtime/p07ShoppingAgent_p07ShoppingAgent-MZZ0obEJqS'
REGION      = 'us-east-1'

client = boto3.client('bedrock-agentcore', region_name=REGION)

# ── Test runner ──────────────────────────────────────────────────
passed = 0
failed = 0
errors = []

def invoke(prompt, session_id):
    """Invoke AgentCore Runtime and return text response."""
    payload = json.dumps({"prompt": prompt}).encode()
    response = client.invoke_agent_runtime(
        agentRuntimeArn=RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=payload,
        qualifier="DEFAULT"
    )
    raw = response['response'].read().decode('utf-8')

    # Try SSE format first (data: {...})
    text_chunks = []
    for line in raw.split('\n'):
        if line.startswith('data: '):
            try:
                event_data = json.loads(line[6:])
                event = event_data.get('event', {})
                delta = event.get('contentBlockDelta', {}).get('delta', {})
                text = delta.get('text', '')
                if text:
                    text_chunks.append(text)
            except json.JSONDecodeError:
                continue

    if text_chunks:
        return ''.join(text_chunks)

    # Try direct JSON response
    try:
        data = json.loads(raw)
        if isinstance(data, str):
            return data
        return data.get('text', data.get('content', raw))
    except json.JSONDecodeError:
        pass

    # Return raw text directly
    return raw.strip()

def new_session():
    """Generate a unique session ID."""
    raw = str(uuid.uuid4()).replace('-', '') + str(uuid.uuid4()).replace('-', '')
    return raw[:40]

def test(name, fn):
    """Run a test function and track results."""
    global passed, failed
    try:
        fn()
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
# TEST GROUP 1: Basic search and response
# ════════════════════════════════════════════════════════════════
print("\n🔍 Group 1: Basic search")

def test_honey_search():
    session = new_session()
    response = invoke("Find organic honey under $20", session)
    assert "honey" in response.lower(), f"Expected honey in response, got: {response[:200]}"
    assert any(p in response for p in ["P001", "P005", "P007", "$15.99", "$18.99", "$19.99"]), \
        "Expected product details in response"

test("search returns honey products", test_honey_search)

def test_out_of_scope():
    session = new_session()
    response = invoke("I want to buy an elephant", session)
    assert any(word in response.lower() for word in [
        "couldn't find", "no products", "not found", "don't have",
        "don't carry", "specialize", "not available", "can't help",
        "outside", "only carry", "elephant", "don't sell"
    ]), f"Expected out-of-scope handling, got: {response[:200]}"

test("out of scope query handled gracefully", test_out_of_scope)

def test_rating_shown():
    session = new_session()
    response = invoke("Find oats with reviews", session)
    assert any(word in response.lower() for word in ["rating", "review", "/5"]), \
        f"Expected rating info in response, got: {response[:200]}"

test("ratings shown in search results", test_rating_shown)


# ════════════════════════════════════════════════════════════════
# TEST GROUP 2: Short-term memory — order by item number
# ════════════════════════════════════════════════════════════════
print("\n🧠 Group 2: Short-term memory — order by item number")

def test_order_item1():
    session = new_session()
    # Turn 1: search
    response1 = invoke("Find organic honey under $20 with 4 plus rating", session)
    assert "honey" in response1.lower(), "Turn 1 should return honey products"
    time.sleep(1)
    # Turn 2: order by item number
    response2 = invoke("Order item 1", session)
    assert any(word in response2.lower() for word in ["order", "placed", "confirmed", "success"]), \
        f"Expected order confirmation, got: {response2[:200]}"
    assert "honey" in response2.lower(), \
        f"Expected honey in order confirmation, got: {response2[:200]}"

test("order item 1 after search (short-term memory)", test_order_item1)

def test_order_item2():
    session = new_session()
    # Turn 1: search
    response1 = invoke("Find organic honey under $20 with 4 plus rating", session)
    assert "honey" in response1.lower(), "Turn 1 should return honey products"
    time.sleep(1)
    # Turn 2: order item 2
    response2 = invoke("Order item 2", session)
    assert any(word in response2.lower() for word in ["order", "placed", "confirmed", "success"]), \
        f"Expected order confirmation, got: {response2[:200]}"

test("order item 2 after search (short-term memory)", test_order_item2)

def test_no_order_without_search():
    session = new_session()
    # Try to order without searching first
    response = invoke("Order item 1", session)
    # Agent should ask to search first, not place a random order
    assert not any(word in response.lower() for word in ["order placed", "order confirmed", "order id"]), \
        f"Agent should not place order without prior search, got: {response[:200]}"

test("agent refuses order without prior search", test_no_order_without_search)


# ════════════════════════════════════════════════════════════════
# TEST GROUP 3: Short-term memory — multi-turn context
# ════════════════════════════════════════════════════════════════
print("\n💬 Group 3: Multi-turn context retention")

def test_followup_question():
    session = new_session()
    # Turn 1: search
    response1 = invoke("Find protein powder", session)
    assert "protein" in response1.lower(), "Turn 1 should return protein products"
    time.sleep(1)
    # Turn 2: follow-up question about results
    response2 = invoke("Which one is organic?", session)
    assert any(word in response2.lower() for word in ["organic", "whey", "P014"]), \
        f"Agent should remember protein search results, got: {response2[:200]}"

test("agent remembers previous search in follow-up", test_followup_question)

def test_price_followup():
    session = new_session()
    # Turn 1: search
    response1 = invoke("Show me all honey products", session)
    assert "honey" in response1.lower(), "Turn 1 should return honey"
    time.sleep(1)
    # Turn 2: filter previous results
    response2 = invoke("Which ones are under $20?", session)
    assert any(word in response2.lower() for word in ["honey", "$15", "$18", "$19", "under"]), \
        f"Agent should filter from previous results, got: {response2[:200]}"

test("agent applies filter to previous search results", test_price_followup)


# ════════════════════════════════════════════════════════════════
# TEST GROUP 4: Session isolation
# ════════════════════════════════════════════════════════════════
print("\n🔒 Group 4: Session isolation")

def test_sessions_isolated():
    session1 = new_session()
    session2 = new_session()

    # Session 1: search honey
    invoke("Find organic honey under $20", session1)
    time.sleep(1)

    # Session 2: try to order without searching
    response2 = invoke("Order item 1", session2)

    # Session 2 should NOT know about session 1's search
    assert not any(word in response2.lower() for word in ["order placed", "order confirmed", "order id"]), \
        f"Session 2 should not have Session 1 context, got: {response2[:200]}"

test("different sessions are isolated", test_sessions_isolated)

def test_order_confirmation_details():
    session = new_session()
    # Turn 1: search
    invoke("Find oats", session)
    time.sleep(1)
    # Turn 2: order
    response2 = invoke("Order item 1", session)
    assert any(word in response2.lower() for word in ["order", "oat", "price", "$"]), \
        f"Order confirmation should include product and price, got: {response2[:200]}"

test("order confirmation includes product details", test_order_confirmation_details)


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
