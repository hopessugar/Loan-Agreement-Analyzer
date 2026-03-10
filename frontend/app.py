import streamlit as st
import requests
import json
import os

# ── PAGE CONFIG ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mifos Loan Analyzer",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── STYLES ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --navy:      #0A0E27;
    --navy2:     #141B3D;
    --navy3:     #1A2347;
    --accent:    #6366F1;
    --accent2:   #818CF8;
    --accent3:   #4F46E5;
    --success:   #10B981;
    --warning:   #F59E0B;
    --danger:    #EF4444;
    --white:     #F9FAFB;
    --gray100:   #F3F4F6;
    --gray200:   #E5E7EB;
    --gray300:   #D1D5DB;
    --gray400:   #9CA3AF;
    --gray500:   #6B7280;
    --gray600:   #4B5563;
    --gray700:   #374151;
    --card:      #1E2749;
    --card-hover: #252D54;
    --border:    #2D3659;
    --shadow:    rgba(99, 102, 241, 0.1);
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy2) 100%) !important;
    color: var(--white) !important;
}

#MainMenu, footer, header, .stDeployButton { display: none !important; }

.block-container {
    padding: 24px 48px 48px 48px !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
}

/* MAIN WRAPPER */
.main-wrapper {
    padding: 0;
}

/* APP SHELL */
.app-shell {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 0 48px 0;
}

/* NAVBAR */
.navbar {
    background: linear-gradient(135deg, rgba(20, 27, 61, 0.95) 0%, rgba(26, 35, 71, 0.95) 100%);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    padding: 0 0;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    margin: -24px -48px 12px -48px;
    padding: 0 48px;
    max-width: calc(100% + 96px);
}
.nav-left { display: flex; align-items: center; gap: 20px; }
.nav-logo {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; font-weight: 800; color: white;
    box-shadow: 0 8px 24px var(--shadow);
    transition: transform 0.3s ease;
}
.nav-logo:hover { transform: translateY(-2px); }
.nav-title { 
    font-size: 20px; 
    font-weight: 700; 
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, var(--white) 0%, var(--gray200) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.nav-sub { 
    font-size: 12px; 
    color: var(--gray400); 
    letter-spacing: 0.5px; 
    text-transform: uppercase; 
    font-weight: 600;
}
.nav-badge {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(129, 140, 248, 0.15) 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: var(--accent2);
    padding: 8px 20px;
    border-radius: 24px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

/* MAIN CONTENT */
.main-wrap { margin: 0 auto; }

.layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr);
    gap: 32px;
    margin-top: 28px;
}

.panel {
    background: linear-gradient(135deg, rgba(30, 39, 73, 0.6) 0%, rgba(26, 35, 71, 0.4) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 32px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.panel:hover {
    transform: translateY(-4px);
    box-shadow: 0 24px 72px rgba(0, 0, 0, 0.5);
}

.panel-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 24px;
}

.panel-title {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: var(--white);
}

.panel-sub {
    font-size: 14px;
    color: var(--gray400);
    margin-top: 6px;
    line-height: 1.6;
}

.pill {
    padding: 8px 16px;
    border-radius: 999px;
    border: 1px solid rgba(99, 102, 241, 0.3);
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(129, 140, 248, 0.1) 100%);
    color: var(--accent2);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    white-space: nowrap;
    text-transform: uppercase;
}

.hint {
    padding: 16px 20px;
    border-radius: 16px;
    border: 1px dashed rgba(99, 102, 241, 0.3);
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(129, 140, 248, 0.05) 100%);
    color: var(--gray300);
    font-size: 13px;
    line-height: 1.7;
    margin-top: 20px;
}

.hint code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--accent2);
    background: rgba(99, 102, 241, 0.1);
    padding: 2px 8px;
    border-radius: 6px;
}

.hero-title {
    font-size: 48px;
    font-weight: 800;
    margin: -12px 0 8px 0;
    letter-spacing: -1.5px;
    line-height: 1.1;
}
.hero-title span { 
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 16px;
    color: var(--gray400);
    margin-bottom: 24px;
    max-width: 700px;
    line-height: 1.7;
    font-weight: 400;
}

/* SECTION LABEL */
.sec-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent2);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.sec-label::before {
    content: '';
    width: 24px; height: 3px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent2) 100%);
    border-radius: 3px;
    display: inline-block;
}

/* DIVIDER */
.divider {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 40px 0 24px;
}
.divider-text {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--gray400);
    white-space: nowrap;
}
.divider-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, var(--border), transparent);
}

/* STATS */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 32px;
}
.stat-box {
    background: linear-gradient(135deg, var(--card) 0%, var(--navy3) 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    transition: all 0.3s ease;
}
.stat-box:hover {
    transform: translateY(-4px);
    border-color: var(--accent);
    box-shadow: 0 12px 32px rgba(99, 102, 241, 0.2);
}
.stat-icon {
    width: 56px; height: 56px;
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; flex-shrink: 0;
}
.stat-num {
    font-size: 32px; font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
    letter-spacing: -1px;
}
.stat-lbl { 
    font-size: 12px; 
    color: var(--gray400); 
    margin-top: 6px; 
    font-weight: 500;
}

/* SUMMARY */
.summary-box {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(129, 140, 248, 0.05) 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.summary-box::before {
    content: '';
    position: absolute;
    top: -100px; right: -100px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
    pointer-events: none;
}
.summary-label {
    font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--accent2); margin-bottom: 16px;
}
.summary-text {
    font-size: 16px; line-height: 1.8;
    color: var(--gray200); position: relative; z-index: 1;
    font-weight: 400;
}

/* MATH CHECK */
.math-box {
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 32px;
    border: 1px solid;
    display: flex;
    align-items: flex-start;
    gap: 20px;
}
.math-box.pass { 
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(16, 185, 129, 0.05) 100%); 
    border-color: rgba(16, 185, 129, 0.3); 
}
.math-box.fail { 
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(239, 68, 68, 0.05) 100%); 
    border-color: rgba(239, 68, 68, 0.3); 
}
.math-box.skip { 
    background: linear-gradient(135deg, rgba(107, 114, 128, 0.08) 0%, rgba(107, 114, 128, 0.05) 100%); 
    border-color: rgba(107, 114, 128, 0.2); 
}
.math-icon { font-size: 32px; flex-shrink: 0; }
.math-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.math-detail { font-size: 14px; color: var(--gray400); line-height: 1.6; }
.math-nums {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px; color: var(--gray300);
    margin-top: 12px;
    background: rgba(0,0,0,0.3);
    padding: 10px 16px; border-radius: 10px;
    display: inline-block;
}

/* ENTITY GRID */
.ent-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 32px;
}
.ent-card {
    background: linear-gradient(135deg, var(--card) 0%, var(--navy3) 100%);
    border: 1px solid var(--border);
    border-left: 3px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    transition: all 0.3s ease;
}
.ent-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}
.ent-card.ok   { border-left-color: var(--accent); }
.ent-card.warn { border-left-color: var(--warning); background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, var(--navy3) 100%); }
.ent-card.null { border-left-color: var(--border); opacity: 0.5; }
.ent-name {
    font-size: 11px; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--gray400); margin-bottom: 12px;
}
.ent-val {
    font-size: 22px; font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    color: var(--white); margin-bottom: 14px;
    word-break: break-word;
    letter-spacing: -0.5px;
}
.ent-val.na {
    font-size: 14px; font-style: italic;
    color: var(--gray500);
    font-family: 'Inter', sans-serif; font-weight: 400;
}
.conf-bar { background: rgba(255,255,255,0.08); border-radius: 6px; height: 4px; margin-bottom: 8px; }
.conf-fill { height: 4px; border-radius: 6px; }
.conf-row {
    display: flex; justify-content: space-between;
    font-size: 11px; color: var(--gray400);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
}
.ent-flag { font-size: 12px; color: var(--warning); margin-top: 12px; line-height: 1.6; }
.ent-src {
    font-size: 11px; color: var(--gray500);
    font-family: 'JetBrains Mono', monospace;
    background: rgba(0,0,0,0.3);
    border-left: 2px solid var(--accent);
    padding: 10px 14px; border-radius: 0 10px 10px 0;
    margin-top: 12px; line-height: 1.6;
}

/* WHATSAPP */
.wa-box {
    background: linear-gradient(135deg, var(--card) 0%, var(--navy3) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px 32px;
}
.wa-pre {
    background: var(--navy);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px; color: var(--gray300);
    line-height: 2; white-space: pre-wrap;
    margin-top: 16px;
}
.wa-count { 
    font-size: 12px; 
    color: var(--gray400); 
    text-align: right; 
    margin-top: 10px; 
    font-family: 'JetBrains Mono', monospace; 
    font-weight: 500;
}

/* STREAMLIT OVERRIDES */
.stTextArea > label {
    font-family: 'Inter', sans-serif !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--accent2) !important;
}
.stTextArea textarea {
    background: rgba(10, 14, 39, 0.6) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 16px !important;
    color: var(--gray200) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    line-height: 1.8 !important;
    padding: 20px !important;
    transition: all 0.3s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15) !important;
    background: rgba(10, 14, 39, 0.8) !important;
}
.stTextArea textarea::placeholder { color: var(--gray600) !important; }

.stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 18px 48px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4) !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 32px rgba(99, 102, 241, 0.6) !important;
    background: linear-gradient(135deg, var(--accent2) 0%, var(--accent) 100%) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    padding: 8px 4px 16px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    border: 1px solid var(--border);
    background: rgba(10, 14, 39, 0.4);
    color: var(--gray400);
    font-size: 13px;
    padding: 12px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(99, 102, 241, 0.1);
    border-color: rgba(99, 102, 241, 0.3);
}

.stTabs [aria-selected="true"] {
    border-color: var(--accent) !important;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(129, 140, 248, 0.1) 100%) !important;
    color: var(--white) !important;
}

.stAlert { border-radius: 14px !important; }
div[data-testid="stSpinner"] > div { border-top-color: var(--accent2) !important; }

/* RESPONSIVE */
@media (max-width: 1024px) {
    .navbar {
        padding: 0 32px;
        margin-bottom: 20px;
    }
    .app-shell {
        max-width: 100%;
        padding: 0 32px 40px 32px;
    }
    .layout {
        grid-template-columns: minmax(0, 1fr);
    }
    .hero-title {
        font-size: 36px;
    }
}

@media (max-width: 768px) {
    .navbar {
        padding: 0 24px;
        height: 72px;
        margin-bottom: 16px;
    }
    .app-shell {
        padding: 0 24px 32px 24px;
    }
    .hero-title { font-size: 32px; }
    .hero-sub { font-size: 14px; }
    .stats-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .ent-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .panel {
        padding: 24px;
    }
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ────────────────────────────────────────────────────────

def conf_color(score):
    if score is None: return "#6B7280"
    if score >= 0.75: return "#10B981"
    if score >= 0.50: return "#F59E0B"
    return "#EF4444"

def fmt_name(name):
    return name.replace("_", " ").title()

def render_entity_card(name, data):
    if not isinstance(data, dict):
        return ""
    value      = data.get("value")
    confidence = data.get("confidence")
    flag       = data.get("flag")
    source     = data.get("source_clause") or ""
    currency   = data.get("currency") or ""

    if value is None:
        return f"""
        <div class="ent-card null">
          <div class="ent-name">{fmt_name(name)}</div>
          <div class="ent-val na">Not found</div>
        </div>"""

    card_cls = "warn" if flag else "ok"

    # Format value nicely: add currency for money fields and '%' for rate fields.
    money_fields = {
        "loan_amount",
        "monthly_payment",
        "total_cost",
        "late_fee",
        "processing_fee",
        "insurance_fee",
        "administrative_fee",
        "other_fee",
    }
    percent_fields = {"interest_rate", "penalty_interest", "prepayment_penalty"}

    val_disp: str
    if name in money_fields:
        curr = currency or "Rs."
        val_disp = f"{curr} {value}"
    elif name == "repayment_duration":
        unit = data.get("unit") or ""
        unit_str = f" {unit}" if unit else ""
        val_disp = f"{value}{unit_str}"
    elif name in percent_fields:
        # Ensure there is exactly one '%' suffix
        text = str(value)
        val_disp = text if text.endswith("%") else f"{text}%"
    else:
        val_disp = f"{currency} {value}".strip() if currency else str(value)
    conf_pct = int((confidence or 0) * 100)
    color    = conf_color(confidence)
    # We keep the internal flag information for validation, but do not render
    # the warning text in the UI for a cleaner display.
    flag_html = ""
    src_text  = str(source)[:100] + ("…" if len(str(source)) > 100 else "")
    src_html  = f'<div class="ent-src">"{src_text}"</div>' if source else ""

    return f"""
    <div class="ent-card {card_cls}">
      <div class="ent-name">{fmt_name(name)}</div>
      <div class="ent-val">{val_disp}</div>
      <div class="conf-bar"><div class="conf-fill" style="width:{conf_pct}%;background:{color};"></div></div>
      <div class="conf-row"><span>Confidence</span><span style="color:{color};font-weight:600;">{conf_pct}%</span></div>
      {flag_html}
      {src_html}
    </div>"""


# ── NAVBAR ─────────────────────────────────────────────────────────
st.markdown("""
<div class="main-wrapper">
<div class="navbar">
  <div class="nav-left">
    <div class="nav-logo">S</div>
    <div>
      <div class="nav-title">Loan Agreement Analyzer</div>
      <div class="nav-sub"></div>
    </div>
  </div>
  <div class="nav-badge">GSoC 2026 · Prototype</div>
</div>
</div>
""", unsafe_allow_html=True)


# ── BODY ───────────────────────────────────────────────────────────
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="app-shell">', unsafe_allow_html=True)
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

st.markdown("""
<div class="hero-title">Loan Agreement <span>Analyzer</span></div>
<div class="hero-sub">Paste a loan agreement to extract key financial terms, validate numbers, and highlight borrower risks. The backend runs locally and uses an LLM for structured extraction.</div>
""", unsafe_allow_html=True)

# Layout: left input panel + right results panel
left, right = st.columns([1.05, 1.45], gap="large")

with left:
    st.markdown("""
    <div class="panel">
      <div class="panel-head">
        <div>
          <div class="panel-title">Contract input</div>
          <div class="panel-sub">Paste the full agreement text. Longer, well-formatted contracts give better results.</div>
        </div>
        <div class="pill">Local</div>
      </div>
    """, unsafe_allow_html=True)

    contract_text = st.text_area(
        label="LOAN AGREEMENT TEXT",
        placeholder=(
            "Paste the full loan agreement here...\n\n"
            "CLAUSE 1 - LOAN AMOUNT\n"
            "The Lender agrees to disburse a principal loan amount of Rs. 50,000...\n\n"
            "CLAUSE 2 - INTEREST RATE\n"
            "Interest shall be charged at 24% per annum flat rate..."
        ),
        height=360
    )

    run = st.button("🔍  Analyze Contract", use_container_width=True)

    st.markdown("""
      <div class="hint">
        Tip: include the repayment clause, due dates, fees, and default section.  
        Backend should be reachable at <code>http://127.0.0.1:8000</code>.
      </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="panel">
      <div class="panel-head">
        <div>
          <div class="panel-title">Results</div>
          <div class="panel-sub">Summary, validation, risk score, and extracted terms.</div>
        </div>
        <div class="pill">v1</div>
      </div>
    """, unsafe_allow_html=True)

    if run:
        if not contract_text or len(contract_text.strip()) < 50:
            st.error("Please paste a loan agreement with at least 50 characters.")
        else:
            with st.spinner("Analyzing contract — this may take 20–40 seconds..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/analyze",
                        json={"text": contract_text},
                        timeout=120
                    )

                    if resp.status_code == 200:
                        data       = resp.json()
                        entities   = data.get("entities", {})
                        math_check = data.get("math_check", {})
                        fin_sum    = data.get("financial_summary", {}) or {}
                        risk       = data.get("risk_analysis", {}) or {}
                        default_ev = data.get("default_events", []) or []
                        summary    = data.get("summary", "")
                        seg_count  = data.get("segment_count", 0)

                        found   = [e for e in entities.values() if isinstance(e, dict) and e.get("value") is not None]
                        flagged = [e for e in found if e.get("flag")]
                        avg_conf = sum(e.get("confidence") or 0 for e in found) / len(found) if found else 0

                        tab_overview, tab_terms, tab_risk, tab_raw = st.tabs(
                            ["Overview", "Key terms", "Risks & defaults", "Raw JSON"]
                        )

                        with tab_overview:
                            st.markdown(f"""
                            <div class="stats-row">
                              <div class="stat-box">
                                <div class="stat-icon" style="background:linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(129, 140, 248, 0.15));">📋</div>
                                <div><div class="stat-num">{seg_count}</div><div class="stat-lbl">Contract clauses</div></div>
                              </div>
                              <div class="stat-box">
                                <div class="stat-icon" style="background:linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.1));">✅</div>
                                <div><div class="stat-num">{len(found)}<span style="font-size:16px;color:var(--gray400)">/13</span></div><div class="stat-lbl">Entities found</div></div>
                              </div>
                              <div class="stat-box">
                                <div class="stat-icon" style="background:linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.1));">⚠️</div>
                                <div><div class="stat-num" style="color:{'#F59E0B' if flagged else '#10B981'}">{len(flagged)}</div><div class="stat-lbl">Flagged items</div></div>
                              </div>
                              <div class="stat-box">
                                <div class="stat-icon" style="background:linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(129, 140, 248, 0.15));">🎯</div>
                                <div><div class="stat-num" style="color:{conf_color(avg_conf)}">{int(avg_conf*100)}%</div><div class="stat-lbl">Avg confidence</div></div>
                              </div>
                            </div>
                            """, unsafe_allow_html=True)

                            if fin_sum or risk:
                                fs_html = ""
                                if fin_sum:
                                    la = fin_sum.get("loan_amount")
                                    tr = fin_sum.get("total_repayment")
                                    ti = fin_sum.get("total_interest")
                                    er = fin_sum.get("effective_interest_pct")
                                    parts = []
                                    if la is not None:
                                        parts.append(f"Loan: Rs. {la:,.2f}")
                                    if tr is not None:
                                        parts.append(f"Total repayable: Rs. {tr:,.2f}")
                                    if ti is not None:
                                        parts.append(f"Total interest: Rs. {ti:,.2f}")
                                    if er is not None:
                                        parts.append(f"Effective interest: {er:.2f}%")
                                    fs_html = " · ".join(parts)

                                rk_html = ""
                                if risk:
                                    rs = risk.get("score")
                                    factors = risk.get("factors") or []
                                    factors_str = "; ".join(factors)
                                    rk_html = f"Risk score: {rs}/10"
                                    if factors_str:
                                        rk_html += f" — {factors_str}"

                                if fs_html or rk_html:
                                    st.markdown(f"""
                                    <div class="risk-box">
                                      {fs_html}<br/>{rk_html}
                                    </div>
                                    """, unsafe_allow_html=True)

                            if summary:
                                st.markdown(f"""
                                <div class="summary-box">
                                  <div class="summary-label">📝 Plain Language Summary</div>
                                  <div class="summary-text">{summary}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            math = math_check or {}
                            consistent = math.get("is_consistent")
                            reason     = math.get("reason", "")
                            calc       = math.get("calculated_total")
                            stated     = math.get("stated_total")
                            diff       = math.get("difference_pct")

                            if consistent is True:
                                cls, icon, title = "pass", "✅", "Math Check — Passed"
                            elif consistent is False:
                                cls, icon, title = "fail", "❌", "Math Check — Discrepancy Detected"
                            else:
                                cls, icon, title = "skip", "➖", "Math Check — Skipped (missing values)"

                            nums_html = ""
                            if calc and stated:
                                nums_html = f'<div class="math-nums">Calculated: {calc:,.2f} &nbsp;|&nbsp; Stated: {stated:,.2f} &nbsp;|&nbsp; Diff: {diff}%</div>'

                            st.markdown(f"""
                            <div class="math-box {cls}">
                              <div class="math-icon">{icon}</div>
                              <div>
                                <div class="math-title">{title}</div>
                                <div class="math-detail">{reason}</div>
                                {nums_html}
                              </div>
                            </div>
                            """, unsafe_allow_html=True)

                        with tab_terms:
                            st.markdown("""
                            <div class="divider">
                              <div class="divider-text">Extracted Financial Terms</div>
                              <div class="divider-line"></div>
                            </div>
                            """, unsafe_allow_html=True)

                            items = list(entities.items())
                            cols  = st.columns(3)
                            for i, (name, edata) in enumerate(items):
                                with cols[i % 3]:
                                    st.markdown(render_entity_card(name, edata), unsafe_allow_html=True)

                        with tab_risk:
                            st.markdown("""
                            <div class="divider">
                              <div class="divider-text">Defaults & Risks</div>
                              <div class="divider-line"></div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Risk score + factors
                            if isinstance(risk, dict) and (risk.get("score") is not None or risk.get("factors")):
                                rs = risk.get("score")
                                factors = risk.get("factors") or []
                                factors_str = "; ".join(str(x) for x in factors if x)
                                st.markdown(f"""
                                <div class="risk-box">
                                  <strong>Risk score:</strong> {rs}/10<br/>
                                  <span style="color:var(--muted);font-size:12px;line-height:1.6;">
                                    {factors_str if factors_str else "No major risk factors detected."}
                                  </span>
                                </div>
                                """, unsafe_allow_html=True)

                            # Collateral
                            collateral = entities.get("collateral") if isinstance(entities, dict) else None
                            if isinstance(collateral, dict) and collateral.get("present"):
                                desc = collateral.get("description") or "Collateral mentioned"
                                st.write(f"**Secured / collateral:** {desc}")

                            if default_ev:
                                st.write("**Events of default (detected):**")
                                for ev in default_ev:
                                    if isinstance(ev, dict):
                                        st.write(f"- {ev.get('trigger','')}")
                            else:
                                st.write("No explicit default events detected.")

                            # Conditional fee clauses (logic preserved)
                            fee_names = ["late_fee", "penalty_interest", "prepayment_penalty", "processing_fee"]
                            conditional_lines = []
                            for fn in fee_names:
                                fee_obj = entities.get(fn) if isinstance(entities, dict) else None
                                if isinstance(fee_obj, dict):
                                    logic = fee_obj.get("logic")
                                    if logic:
                                        conditional_lines.append(f"- **{fmt_name(fn)}**: {logic}")
                            if conditional_lines:
                                st.write("**Conditional fees (as written):**")
                                st.markdown("\n".join(conditional_lines))

                            st.markdown("""
                            <div class="divider">
                              <div class="divider-text">WhatsApp / SMS Summary</div>
                              <div class="divider-line"></div>
                            </div>
                            """, unsafe_allow_html=True)

                            loan = entities.get("loan_amount") or {}
                            intr = entities.get("interest_rate") or {}
                            emi  = entities.get("monthly_payment") or {}
                            dur  = entities.get("repayment_duration") or {}
                            fee  = entities.get("processing_fee") or {}

                            loan_val = loan.get("value")
                            loan_curr = loan.get("currency") or "Rs."
                            loan_str = f"{loan_curr} {loan_val}" if loan_val is not None else "Not specified"

                            intr_val = intr.get("value")
                            intr_type = intr.get("type")
                            if intr_val is not None:
                                intr_str = f"{intr_val}%"
                                if intr_type:
                                    intr_str += f" ({intr_type})"
                            else:
                                intr_str = "Not specified"

                            emi_val = emi.get("value")
                            dur_val = dur.get("value")
                            dur_unit = dur.get("unit") or "months"
                            if emi_val is not None and dur_val is not None:
                                emi_str = f"{emi_val} × {dur_val} {dur_unit}"
                            else:
                                emi_str = "Not specified"

                            fee_val = fee.get("value")
                            fee_str = str(fee_val) if fee_val is not None else "Not specified"

                            wa = (
                                f"📋 LOAN SUMMARY\n"
                                f"━━━━━━━━━━━━━━━━\n"
                                f"💰 Amount: {loan_str}\n"
                                f"📈 Interest: {intr_str}\n"
                                f"📅 EMI: {emi_str}\n"
                                f"🧾 Processing fee: {fee_str}\n"
                                f"⚠️ Flagged items: {len(flagged)}\n"
                                f"━━━━━━━━━━━━━━━━\n"
                                f"Powered by Mifos X LLM Analyzer"
                            )

                            st.markdown(f"""
                            <div class="wa-box">
                              <div class="sec-label">Message Preview</div>
                              <div class="wa-pre">{wa}</div>
                              <div class="wa-count">{len(wa)} characters</div>
                            </div>
                            """, unsafe_allow_html=True)

                        with tab_raw:
                            st.json(data)

                    else:
                        try:
                            err = resp.json().get("detail", resp.text)
                        except Exception:
                            err = resp.text
                        st.error(f"Backend error {resp.status_code}: {err}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure FastAPI is running: `python -m uvicorn backend.main:app --reload --port 8000`")
                except requests.exceptions.Timeout:
                    st.error("⏱ Request timed out — model is loading. Wait 30 seconds and try again.")
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

    else:
        st.markdown("""
        <div class="hint">
          Click <strong>Analyze Contract</strong> to generate a summary, validation, risk score, and extracted terms.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # panel

st.markdown('</div>', unsafe_allow_html=True)  # main-wrap
st.markdown('</div>', unsafe_allow_html=True)  # app-shell
st.markdown('</div>', unsafe_allow_html=True)  # main-wrapper