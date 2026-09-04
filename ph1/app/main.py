"""
P07 Shopping Agent — Streamlit UI
AWS-native rebuild of Dhaval Patel's LangChain Shopping Agent
"""
import streamlit as st
import boto3
import json
import uuid
import base64
import os
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

RUNTIME_ARN = os.getenv('AGENTCORE_RUNTIME_ARN', '')
AWS_REGION   = os.getenv('AWS_REGION', 'us-east-1')

st.set_page_config(page_title="AI Shopping Agent", page_icon="🛒", layout="wide")

# ── Sidebar ──────────────────────────────────────────────────────
st.sidebar.title("🛒 AI Shopping Agent")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["Shopping Agent", "How it works", "Architecture", "About"])
st.sidebar.markdown("---")
st.sidebar.caption("Built on AWS · Powered by AgentCore")
st.sidebar.caption("Strands Agents · DynamoDB · Bedrock")


def invoke_agent(prompt, session_id, image_base64=None, media_type="image/jpeg"):
    client = boto3.client('bedrock-agentcore', region_name=AWS_REGION)
    payload = {"prompt": prompt}
    if image_base64:
        payload["image_base64"] = image_base64
        payload["media_type"] = media_type

    response = client.invoke_agent_runtime(
        agentRuntimeArn=RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=json.dumps(payload).encode(),
        qualifier="DEFAULT"
    )
    raw = response['response'].read().decode('utf-8')

    # Try SSE format
    chunks = []
    for line in raw.split('\n'):
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
                text = data.get('event', {}).get('contentBlockDelta', {}).get('delta', {}).get('text', '')
                if text:
                    chunks.append(text)
            except:
                continue
    if chunks:
        return ''.join(chunks)

    # Direct response
    try:
        return json.loads(raw) if isinstance(json.loads(raw), str) else raw.strip()
    except:
        return raw.strip()


def new_session():
    raw = str(uuid.uuid4()).replace('-', '') + str(uuid.uuid4()).replace('-', '')
    return raw[:40]


def resize_image(uploaded_file, max_size=(512, 512)):
    img = Image.open(uploaded_file)
    if img.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    img.thumbnail(max_size, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# ── Init session state ───────────────────────────────────────────
if 'session_id' not in st.session_state:
    st.session_state.session_id = new_session()
if 'messages' not in st.session_state:
    st.session_state.messages = []


# ════════════════════════════════════════════════════════════════
# PAGE 1: Shopping Agent
# ════════════════════════════════════════════════════════════════
if page == "Shopping Agent":
    st.title("🛒 AI Shopping Agent")
    st.subheader("Find products, check ratings, and place orders in natural language")
    st.markdown("---")

    # Image upload
    st.sidebar.markdown("### 📸 Image Search")
    uploaded_file = st.sidebar.file_uploader(
        "Upload a product image",
        type=['jpg', 'jpeg', 'png'],
        key="image_uploader"
    )

    if uploaded_file:
        st.sidebar.image(uploaded_file, caption="Uploaded image", width=200)
        if st.sidebar.button("🔍 Find Similar Products", type="primary"):
            import io
            uploaded_file.seek(0)
            image_base64 = resize_image(io.BytesIO(uploaded_file.read()))
            media_type = "image/jpeg"
            with st.spinner("Analyzing image and searching products..."):
                response = invoke_agent(
                    "Find similar products to this image",
                    st.session_state.session_id,
                    image_base64=image_base64,
                    media_type=media_type
                )
            st.session_state.messages.append({"role": "user", "content": "🖼️ [Image uploaded] Find similar products"})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    # Example prompts
    if not st.session_state.messages:
        st.markdown("### 💡 Try asking:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🍯 Find organic honey under $20"):
                st.session_state.pending = "Find organic honey under $20 with 4+ rating"
            if st.button("🌾 Show me organic oats"):
                st.session_state.pending = "Find organic oats"
        with col2:
            if st.button("💪 Protein powder options"):
                st.session_state.pending = "Find protein powder"
            if st.button("📊 What is my budget?"):
                st.session_state.pending = "Show me all products under $15"

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle button click
    if 'pending' in st.session_state:
        prompt = st.session_state.pop('pending')
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Searching products..."):
                response = invoke_agent(prompt, st.session_state.session_id)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Chat input
    if prompt := st.chat_input("Search products, check ratings, or place an order..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                response = invoke_agent(prompt, st.session_state.session_id)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Session controls
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Session: {st.session_state.session_id[:16]}...")
    with col2:
        if st.button("🔄 New Session"):
            st.session_state.messages = []
            st.session_state.session_id = new_session()
            st.rerun()


# ════════════════════════════════════════════════════════════════
# PAGE 2: How it works
# ════════════════════════════════════════════════════════════════
elif page == "How it works":
    st.title("How it works")
    st.markdown("---")
    st.markdown("""
    This is an AWS-native rebuild of [Dhaval Patel's LangChain Shopping Agent](https://www.youtube.com/watch?v=D74el9mvNak) from Codebasics.

    **What you can do:**
    - Search products by keyword, price, organic filter
    - Get average ratings from customer reviews
    - Place orders by item number
    - Upload an image to find similar products
    - Handle out-of-scope queries gracefully

    **How it's different from Dhaval's version:**
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Dhaval's version (LangChain)**")
        st.markdown("""
        - LangChain agent framework
        - SQLite local database
        - Groq vision model
        - Local execution
        - No observability
        """)
    with col2:
        st.markdown("**Our version (AWS-native)**")
        st.markdown("""
        - Strands Agents framework
        - DynamoDB (serverless, cloud-native)
        - Bedrock Claude Haiku 4.5 (multimodal)
        - AgentCore Runtime (managed, scalable)
        - CloudWatch logs
        """)

    st.markdown("---")
    st.markdown("### Short-term memory")
    st.markdown("""
    AgentCore Runtime maintains conversation context within a session via `session_id`.
    When you say "Order item 2", the agent remembers the previous search results.
    This is AgentCore's built-in short-term memory — no extra configuration needed.
    """)


# ════════════════════════════════════════════════════════════════
# PAGE 3: Architecture
# ════════════════════════════════════════════════════════════════
elif page == "Architecture":
    st.title("Architecture")
    st.markdown("---")
    st.markdown("""
    ### AWS-native Shopping Agent Pipeline

    ```
    Streamlit (local)
      └── boto3 invoke_agent_runtime
            └── AgentCore Runtime (CDK deployed)
                  └── Strands Agent (Claude Haiku 4.5)
                        ├── search_products()    → Lambda → DynamoDB products
                        ├── get_product_rating() → Lambda → DynamoDB reviews
                        ├── place_order()        → Lambda → DynamoDB orders
                        └── search_by_image()    → Lambda → Bedrock vision
    ```
    """)

    diagram_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'architecture-ph1.png')
    if os.path.exists(diagram_path):
        st.image(diagram_path)
    else:
        st.info("📐 Architecture diagram: ph1/docs/architecture-ph1.png")

    st.markdown("---")
    st.markdown("### Component breakdown")
    components = {
        "Streamlit (local)": "Chat UI + image uploader. Sends prompts to AgentCore Runtime via boto3. Preserves session_id across turns for short-term memory.",
        "AgentCore Runtime (CDK)": "Managed container runtime. Hosts Strands agent. Maintains session context (short-term memory) via session_id. Auto-scales.",
        "Strands Agent (Claude Haiku 4.5)": "Autonomous agent. Decides which tool to call based on user query. Handles multi-turn conversations via AgentCore session.",
        "Lambda (4 tools)": "Single Lambda function with action routing: search_products, get_product_rating, place_order, search_by_image. Serverless, cost-efficient.",
        "DynamoDB (3 tables)": "products, reviews, orders. PAY_PER_REQUEST billing. Cloud-native replacement for Dhaval's SQLite.",
        "Bedrock vision": "Claude Haiku 4.5 multimodal. Used inside search_by_image Lambda to identify product from uploaded image.",
    }
    for name, desc in components.items():
        with st.expander(f"**{name}**"):
            st.markdown(desc)


# ════════════════════════════════════════════════════════════════
# PAGE 4: About
# ════════════════════════════════════════════════════════════════
elif page == "About":
    st.title("About this project")
    st.markdown("---")
    st.markdown("""
    ### Gen AI on AWS — Portfolio Project 7

    An AWS-native rebuild of [Dhaval Patel's LangChain Shopping Agent](https://www.youtube.com/watch?v=D74el9mvNak) from [Codebasics](https://www.youtube.com/@codebasics).

    **Credit:** Original concept by Dhaval Patel / Codebasics. Rebuilt on AWS-native stack as a portfolio exercise.

    [View on GitHub](https://github.com/prk-gen-ai-aws/genai-aws-p07-shopping-agent)

    ---
    ### What's new vs Dhaval's version

    | Feature | Dhaval (LangChain) | Our version (AWS) |
    |---|---|---|
    | Agent framework | LangChain | Strands Agents |
    | Database | SQLite (local) | DynamoDB (serverless) |
    | Vision model | Groq Llama | Bedrock Claude Haiku 4.5 |
    | Runtime | Local Python | AgentCore Runtime |
    | Short-term memory | Python list | AgentCore session |
    | Tools | Local functions | Lambda (serverless) |

    ---
    ### Products available
    19 products across 8 categories: Honey, Oils, Grains, Nut Butters, Seeds, Protein, Beverages, Snacks

    ---
    > Part of an ongoing series exploring Gen AI on AWS.
    > Browse all projects: https://github.com/prk-gen-ai-aws
    """)
