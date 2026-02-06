import os
import json
import requests
import streamlit as st

# ----------------------------
# HCLTech-branded Streamlit UI
# ----------------------------

st.set_page_config(
    page_title="HCLTech | License Analysis AI Agent",
    page_icon="🤖",
    layout="centered",
)

# ---- Config (use Streamlit Cloud Secrets) ----
DO_AGENT_ENDPOINT = st.secrets.get("DO_AGENT_ENDPOINT", os.getenv("DO_AGENT_ENDPOINT", "")).rstrip("/")
DO_AGENT_API_KEY = st.secrets.get("DO_AGENT_API_KEY", os.getenv("DO_AGENT_API_KEY", ""))
# Optional, kept for parity with your original files (not strictly required by the /chat/completions call)
AGENT_ID = st.secrets.get("AGENT_ID", os.getenv("AGENT_ID", ""))

if not DO_AGENT_ENDPOINT:
    st.error("Missing DO_AGENT_ENDPOINT. Add it in Streamlit Secrets or environment variables.")
    st.stop()

# ---- Styling (cool, modern gradients) ----
st.markdown(
    """
    <style>
      :root{
        --bg1:#071B34;
        --bg2:#0B5ED7;
        --card: rgba(255,255,255,.92);
        --ink:#0b1f3a;
        --muted:#5c6b7a;

        --teal:#18c4c4;
        --cyan:#22d3ee;
        --sky:#38bdf8;

        --lav:#bba7ff;
        --violet:#7c3aed;
        --purple:#a78bfa;

        --indigo:#4f46e5;
        --deep:#2e1065;
      }

      /* app background */
      .stApp {
        background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
      }

      /* main container */
      section.main > div{
        max-width: 980px;
      }

      /* header card */
      .hcl-header{
        background: var(--card);
        border-radius: 18px;
        padding: 22px 22px;
        box-shadow: 0 14px 38px rgba(0,0,0,.18);
        border: 1px solid rgba(255,255,255,.35);
        backdrop-filter: blur(10px);
        margin-bottom: 14px;
      }
      .hcl-row{
        display:flex; align-items:center; gap:14px; flex-wrap:wrap;
      }
      .hcl-title{
        font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
        font-weight: 750;
        letter-spacing: .2px;
        color: var(--ink);
        margin: 0;
        line-height: 1.2;
      }
      .hcl-subtitle{
        color: var(--muted);
        margin: 2px 0 0 0;
        font-size: 0.98rem;
      }
      .hcl-badge{
        display:inline-flex;
        align-items:center;
        gap:8px;
        font-weight:650;
        color: #083344;
        background: linear-gradient(90deg, rgba(24,196,196,.18), rgba(56,189,248,.18));
        border: 1px solid rgba(34,211,238,.35);
        padding: 6px 10px;
        border-radius: 999px;
        font-size: .85rem;
      }

      /* chat container look */
      div[data-testid="stChatMessage"]{
        background: var(--card);
        border-radius: 16px;
        padding: 10px 12px;
        box-shadow: 0 10px 22px rgba(0,0,0,.14);
        border: 1px solid rgba(255,255,255,.35);
      }

      /* user messages slightly tinted */
      div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: linear-gradient(90deg, rgba(34,211,238,.10), rgba(167,139,250,.10));
        border: 1px solid rgba(124,58,237,.18);
      }

      /* input area */
      .stChatInput > div{
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,.35) !important;
        box-shadow: 0 12px 26px rgba(0,0,0,.14) !important;
      }

      /* sidebar card */
      .hcl-side{
        background: rgba(255,255,255,.90);
        border: 1px solid rgba(255,255,255,.35);
        border-radius: 16px;
        padding: 14px 14px;
        box-shadow: 0 12px 28px rgba(0,0,0,.14);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Header ----
logo_path = os.path.join("assets", "hcltech_logo.png")  # add your official logo file here
col_logo, col_text = st.columns([1, 6], vertical_alignment="center")
with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        # graceful fallback so the app runs even before the logo is added
        st.markdown(
            "<div class='hcl-badge'>🟦 HCLTech</div>",
            unsafe_allow_html=True,
        )

with col_text:
    st.markdown(
        """
        <div class="hcl-header">
          <div class="hcl-row">
            <div>
              <h1 class="hcl-title">License Analysis AI Agent</h1>
              <p class="hcl-subtitle">Automated software license compliance and risk assessment</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---- Sidebar: quick actions + config status ----
with st.sidebar:
    st.markdown("<div class='hcl-side'>", unsafe_allow_html=True)
    st.markdown("### Quick Actions")
    PROMPTS = {
    # Core analysis
    "Analyze software license agreement":
        "I have a software license agreement that needs comprehensive analysis. "
        "Please examine it for key terms, obligations, risks, and provide recommendations "
        "for approval or rejection. Include details on licensing model, restrictions, "
        "compliance requirements, and any red flags.",

    "Identify compliance risks and red flags":
        "Please identify all compliance risks and red flags in the software license agreement. "
        "Focus on potential legal, financial, and operational risks that could impact our organization. "
        "Highlight any problematic clauses that need attention.",

    "Extract key legal and business terms":
        "Extract and summarize all key legal and business terms from this software license agreement. "
        "Include pricing, payment terms, duration, termination conditions, liability clauses, "
        "intellectual property rights, and data handling provisions.",

    "Review liability & indemnification":
        "Review and analyze all liability and indemnification clauses in this software license agreement. "
        "Assess the risk exposure and provide recommendations on acceptable vs. problematic liability terms.",

    "Analyze data protection requirements":
        "Analyze the data protection and privacy requirements in this software license agreement. "
        "Review data handling provisions, security requirements, and compliance with regulations "
        "like GDPR, CCPA, etc.",

    "Approval / rejection recommendation":
        "Based on the software license agreement provided, please give a clear approval or rejection "
        "recommendation. Include your reasoning, risk assessment, and any conditions or modifications "
        "that would make the license acceptable.",

    # --- DEMO / ADVANCED REASONING ---
    "Conflict detection (SAP audit rights)":
        "Are there any conflicting audit rights in the SAP agreements or amendments? "
        "Identify each conflicting clause, cite the relevant documents, and explain the nature of the conflict.",

    "Precedence reasoning (SAP audit terms)":
        "Which SAP audit terms apply, and why? "
        "Analyze order-of-precedence language across the base agreement and amendments, "
        "and explain any unresolved ambiguity.",

    "Calculation (SAP first-year cost)":
        "What is the total first-year cost of the SAP licenses including maintenance? "
        "Show your calculations and clearly state any assumptions.",

    "Risk analysis (SAP indirect access)":
        "What is the financial risk if SAP finds indirect access during an audit? "
        "Consider penalties, retroactive license fees, and maintenance exposure.",

    "Cross-license comparison (pricing escalation)":
        "Compare pricing escalation risk between the SAP license and the GitHub Copilot license. "
        "Identify escalation clauses, caps, compounding effects, and long-term cost exposure."
   }
    selected = st.selectbox("Insert a standard prompt", ["—"] + list(PROMPTS.keys()))
    if selected != "—":
        st.session_state["draft_prompt"] = PROMPTS[selected]
        st.success("Prompt loaded into the input (below).")

    st.divider()
    st.markdown("### Connection")
    st.caption(f"Endpoint: `{DO_AGENT_ENDPOINT}`")
    st.caption(f"API key: `{'✅ set' if bool(DO_AGENT_API_KEY) else '❌ missing'}`")
    st.caption(f"Agent ID: `{AGENT_ID or '—'}`")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Session state ----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I’m your AI agent for software license analysis.\n\n"
                "Share contract text (or paste key clauses) and I’ll help with:\n"
                "- License compliance assessment\n"
                "- Risk analysis & recommendations\n"
                "- Term extraction (liability, IP, termination, data protection)\n"
                "- Plain-English clause interpretation"
            )
        }
    ]

if "draft_prompt" not in st.session_state:
    st.session_state["draft_prompt"] = ""

# ---- Render chat history ----
for m in st.session_state.messages:
    with st.chat_message("assistant" if m["role"] == "assistant" else "user"):
        st.markdown(m["content"])

# ---- Input ----
default_text = st.session_state.get("draft_prompt", "")
user_input = st.chat_input("Type your license analysis question or paste contract text here…", key="chat_input")

# Streamlit chat_input can't be prefilled; we provide a helper text area when a standard prompt is selected
if default_text:
    st.info("A standard prompt is loaded. Click **Send loaded prompt** or edit it below.")
    edited = st.text_area("Loaded prompt (editable):", value=default_text, height=140)
    col_a, col_b = st.columns([1,1])
    with col_a:
        send_loaded = st.button("Send loaded prompt", type="primary")
    with col_b:
        clear_loaded = st.button("Clear loaded prompt")
    if clear_loaded:
        st.session_state["draft_prompt"] = ""
        st.rerun()
    if send_loaded:
        user_input = edited
        st.session_state["draft_prompt"] = ""

def call_agent_api(message: str) -> str:
    """
    Calls the DigitalOcean Agent chat completion endpoint.
    Uses a minimal OpenAI-compatible payload.
    """
    if not DO_AGENT_API_KEY:
        return "Missing DO_AGENT_API_KEY. Add it in Streamlit Secrets to enable the backend call."

    url = f"{DO_AGENT_ENDPOINT}/api/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": message}],
        "stream": False,
        "include_functions_info": True,
        "include_retrieval_info": True,
        "include_guardrails_info": True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DO_AGENT_API_KEY}"
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if not r.ok:
        # include helpful details but avoid dumping secrets
        return f"API error: {r.status_code} {r.reason}\n\n{r.text[:1200]}"

    data = r.json()
    # Try standard OpenAI format
    if isinstance(data, dict) and data.get("choices"):
        msg = data["choices"][0].get("message", {})
        if msg.get("content"):
            return msg["content"]
        if msg.get("reasoning_content"):
            return msg["reasoning_content"]

    # Fallbacks
    for k in ("message", "content", "response"):
        if isinstance(data, dict) and data.get(k):
            return str(data[k])

    return "Received a response, but couldn’t recognize the payload format."

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing…"):
            reply = call_agent_api(user_input)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ---- Footer ----
st.caption("© 2026 HCLTech — License Analysis AI Agent")
