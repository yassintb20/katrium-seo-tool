import streamlit as st
import pandas as pd
import requests
import json
import time

st.set_page_config(
    page_title="Katrium SEO Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Page background ── */
.stApp { background: #0d1117; }
.main .block-container { padding: 1.5rem 2.5rem 3rem; max-width: 1400px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #111927 100%);
    border-right: 1px solid #1e2d40;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Typography ── */
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #111927;
    border: 1px solid #1e2d40;
    border-radius: 12px;
    padding: 1rem 1.2rem !important;
    transition: border-color 0.2s, transform 0.2s;
}
[data-testid="stMetric"]:hover {
    border-color: #1d6fcc;
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] { color: #6b7ea3 !important; font-size: 0.78rem !important; font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #e6edf3 !important; font-family: 'Space Grotesk', sans-serif; font-size: 2rem !important; font-weight: 700; }
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    letter-spacing: 0.02em;
    border-radius: 8px;
    border: none;
    transition: all 0.2s;
    cursor: pointer;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d6fcc 0%, #1558a8 100%) !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(29, 111, 204, 0.35);
    padding: 0.65rem 1.5rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2279dd 0%, #1a62bb 100%) !important;
    box-shadow: 0 6px 24px rgba(29, 111, 204, 0.5);
    transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
    background: #111927 !important;
    color: #8ba3c7 !important;
    border: 1px solid #1e2d40 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #1a2840 !important;
    color: #e6edf3 !important;
    border-color: #2a4060 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] { background: transparent; }
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    color: #6b7ea3 !important;
    padding: 0.6rem 1.2rem !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #58a6ff !important;
    border-bottom: 2px solid #58a6ff !important;
}
button[data-baseweb="tab"]:hover {
    color: #e6edf3 !important;
    background: #111927 !important;
}
[data-testid="stTabContent"] { background: transparent; padding-top: 1rem; }

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: #111927 !important;
    border: 1px solid #1e2d40 !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-size: 0.88rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus { border-color: #1d6fcc !important; box-shadow: 0 0 0 3px rgba(29,111,204,0.15) !important; }
.stTextInput > div > div > input::placeholder { color: #4a5568 !important; }
.stTextInput label { color: #8ba3c7 !important; font-size: 0.8rem !important; font-weight: 500; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #111927 !important;
    border: 1.5px dashed #1e2d40 !important;
    border-radius: 10px !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: #1d6fcc !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
[data-testid="stDataFrame"] table { background: #111927; color: #c9d1d9; }
[data-testid="stDataFrame"] th { background: #0d1117 !important; color: #58a6ff !important; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.7rem 0.9rem !important; }
[data-testid="stDataFrame"] td { border-color: #1e2d40 !important; padding: 0.6rem 0.9rem !important; font-size: 0.84rem; }
[data-testid="stDataFrame"] tr:hover td { background: #1a2840 !important; }

/* ── Expander ── */
details { background: #111927 !important; border: 1px solid #1e2d40 !important; border-radius: 10px !important; margin-bottom: 0.6rem !important; transition: border-color 0.2s; }
details:hover { border-color: #2a4060 !important; }
details summary { padding: 0.8rem 1rem !important; color: #c9d1d9 !important; font-weight: 500 !important; font-size: 0.9rem !important; cursor: pointer; }
details[open] { border-color: #1d6fcc !important; }

/* ── Progress bar ── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #1d6fcc, #58a6ff) !important;
    border-radius: 6px !important;
    transition: width 0.5s ease !important;
}
[data-testid="stProgress"] > div { background: #1e2d40 !important; border-radius: 6px !important; height: 8px !important; }

/* ── Alerts ── */
[data-testid="stAlert"] { border-radius: 10px !important; border-left-width: 3px !important; font-size: 0.88rem !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: #111927 !important;
    border: 1px solid #1e2d40 !important;
    color: #58a6ff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s;
    width: 100%;
}
.stDownloadButton > button:hover {
    background: #1a2840 !important;
    border-color: #1d6fcc !important;
    transform: translateY(-1px);
}

/* ── Custom components ── */
.kpi-banner {
    display: flex; gap: 1rem; margin: 1.5rem 0;
    animation: fadeInUp 0.5s ease;
}
.kpi-card {
    flex: 1; background: #111927;
    border: 1px solid #1e2d40; border-radius: 12px;
    padding: 1.2rem 1.4rem;
    transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
}
.kpi-card:hover { border-color: #1d6fcc; transform: translateY(-3px); box-shadow: 0 8px 24px rgba(29,111,204,0.18); }
.kpi-card .kpi-label { color: #6b7ea3; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem; }
.kpi-card .kpi-value { color: #e6edf3; font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; line-height: 1; }
.kpi-card .kpi-sub { color: #6b7ea3; font-size: 0.76rem; margin-top: 0.3rem; }

.kpi-critical .kpi-value { color: #ff7b72; }
.kpi-warning .kpi-value { color: #e3b341; }
.kpi-info .kpi-value { color: #58a6ff; }
.kpi-success .kpi-value { color: #56d364; }

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem; font-weight: 600;
    color: #e6edf3; margin-bottom: 0.2rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.section-sub { color: #6b7ea3; font-size: 0.82rem; margin-bottom: 1rem; }

.step-header {
    background: linear-gradient(135deg, #111927 0%, #0d1117 100%);
    border: 1px solid #1e2d40; border-radius: 14px;
    padding: 1.4rem 1.8rem; margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
}
.step-header::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #1d6fcc, #58a6ff);
}
.step-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem; font-weight: 700;
    color: #1d6fcc; text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.step-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem; font-weight: 700; color: #e6edf3;
}

.priority-badge {
    display: inline-block; padding: 0.2rem 0.65rem;
    border-radius: 5px; font-size: 0.72rem;
    font-weight: 700; letter-spacing: 0.04em;
}
.p1 { background: rgba(255,123,114,0.15); color: #ff7b72; border: 1px solid rgba(255,123,114,0.3); }
.p2 { background: rgba(227,179,65,0.15); color: #e3b341; border: 1px solid rgba(227,179,65,0.3); }
.p3 { background: rgba(88,166,255,0.12); color: #58a6ff; border: 1px solid rgba(88,166,255,0.25); }
.p4 { background: rgba(107,126,163,0.15); color: #6b7ea3; border: 1px solid rgba(107,126,163,0.3); }

.brief-card {
    background: #0d1117; border: 1px solid #1e2d40;
    border-radius: 12px; padding: 1.4rem;
    margin-bottom: 0.8rem; transition: border-color 0.2s;
}
.brief-card:hover { border-color: #2a4060; }
.brief-card .tag {
    display: inline-block; padding: 0.18rem 0.55rem;
    border-radius: 5px; font-size: 0.72rem; font-weight: 600;
    margin-right: 0.4rem; margin-bottom: 0.5rem;
}
.tag-service { background: rgba(255,123,114,0.12); color: #ff7b72; border: 1px solid rgba(255,123,114,0.25); }
.tag-info { background: rgba(86,211,100,0.12); color: #56d364; border: 1px solid rgba(86,211,100,0.25); }
.tag-fi { background: rgba(88,166,255,0.1); color: #79c0ff; border: 1px solid rgba(88,166,255,0.2); }
.tag-en { background: rgba(107,126,163,0.12); color: #8ba3c7; border: 1px solid rgba(107,126,163,0.25); }

.upload-zone {
    background: #111927; border: 1.5px dashed #1e2d40;
    border-radius: 12px; padding: 1.5rem;
    transition: border-color 0.2s, background 0.2s;
    text-align: center;
}
.upload-zone:hover { border-color: #1d6fcc; background: #0f1e33; }
.upload-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.upload-label { color: #8ba3c7; font-size: 0.88rem; font-weight: 500; margin-bottom: 0.3rem; }
.upload-hint { color: #4a5568; font-size: 0.78rem; }

.sidebar-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem; font-weight: 700;
    color: #e6edf3; letter-spacing: -0.01em;
    margin-bottom: 0.2rem;
}
.sidebar-sub { color: #6b7ea3; font-size: 0.78rem; margin-bottom: 1.5rem; }

.connected-badge {
    display: flex; align-items: center; gap: 0.5rem;
    background: rgba(86,211,100,0.1); border: 1px solid rgba(86,211,100,0.3);
    border-radius: 8px; padding: 0.55rem 0.9rem;
    color: #56d364; font-size: 0.82rem; font-weight: 600;
}
.connected-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #56d364; animation: pulse 2s infinite;
}
.error-badge {
    display: flex; align-items: center; gap: 0.5rem;
    background: rgba(255,123,114,0.1); border: 1px solid rgba(255,123,114,0.3);
    border-radius: 8px; padding: 0.55rem 0.9rem;
    color: #ff7b72; font-size: 0.82rem; font-weight: 600;
}

.divider {
    height: 1px; background: #1e2d40;
    margin: 1.4rem 0; border: none;
}

.how-step {
    background: #111927; border: 1px solid #1e2d40;
    border-radius: 10px; padding: 1.2rem;
    text-align: center; transition: border-color 0.2s, transform 0.2s;
}
.how-step:hover { border-color: #2a4060; transform: translateY(-2px); }
.how-step .how-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem; font-weight: 700; color: #1d6fcc;
    line-height: 1; margin-bottom: 0.5rem;
}
.how-step .how-title { color: #e6edf3; font-weight: 600; font-size: 0.88rem; margin-bottom: 0.4rem; }
.how-step .how-desc { color: #6b7ea3; font-size: 0.8rem; line-height: 1.5; }

.hero-banner {
    background: linear-gradient(135deg, #0d1117 0%, #111927 50%, #0d1623 100%);
    border: 1px solid #1e2d40; border-radius: 16px;
    padding: 2.5rem 2.5rem 2rem;
    margin-bottom: 2rem; position: relative; overflow: hidden;
    animation: fadeInUp 0.6s ease;
}
.hero-banner::after {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 220px; height: 220px; border-radius: 50%;
    background: radial-gradient(circle, rgba(29,111,204,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-size: 0.72rem; font-weight: 700;
    color: #1d6fcc; text-transform: uppercase; letter-spacing: 0.12em;
    margin-bottom: 0.6rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem; font-weight: 700; color: #e6edf3;
    line-height: 1.15; margin-bottom: 0.8rem;
}
.hero-title span { color: #58a6ff; }
.hero-desc { color: #8ba3c7; font-size: 0.92rem; line-height: 1.65; max-width: 540px; }

.results-header {
    background: linear-gradient(135deg, #111927 0%, #0d1117 100%);
    border: 1px solid #1e2d40; border-radius: 14px;
    padding: 1.5rem 2rem; margin-bottom: 1.5rem;
}
.results-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem; font-weight: 700; color: #e6edf3; margin-bottom: 0.4rem;
}
.results-sub { color: #6b7ea3; font-size: 0.85rem; }

.opportunity-row {
    background: #111927; border: 1px solid #1e2d40;
    border-radius: 10px; padding: 0.9rem 1.2rem;
    margin-bottom: 0.5rem; display: flex;
    align-items: center; gap: 1rem;
    transition: border-color 0.2s, transform 0.15s;
}
.opportunity-row:hover { border-color: #1d6fcc; transform: translateX(3px); }

.pill {
    display: inline-block; padding: 0.15rem 0.6rem;
    border-radius: 20px; font-size: 0.72rem; font-weight: 600;
}

.export-card {
    background: #111927; border: 1px solid #1e2d40;
    border-radius: 12px; padding: 1.5rem;
    text-align: center; transition: border-color 0.2s, transform 0.2s;
}
.export-card:hover { border-color: #1d6fcc; transform: translateY(-2px); }
.export-icon { font-size: 2rem; margin-bottom: 0.6rem; }
.export-title { color: #e6edf3; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.3rem; }
.export-desc { color: #6b7ea3; font-size: 0.78rem; margin-bottom: 1rem; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.loading-bar {
    height: 3px;
    background: linear-gradient(90deg, #0d1117 0%, #1d6fcc 50%, #0d1117 100%);
    background-size: 200% 100%;
    animation: shimmer 1.6s infinite;
    border-radius: 3px; margin-bottom: 1rem;
}

.stat-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.65rem 0; border-bottom: 1px solid #1e2d40;
}
.stat-row:last-child { border-bottom: none; }
.stat-label { color: #8ba3c7; font-size: 0.84rem; }
.stat-value { color: #e6edf3; font-weight: 600; font-size: 0.88rem; }

.redirect-row {
    background: #111927; border-left: 3px solid #1d6fcc;
    border-radius: 0 8px 8px 0; padding: 0.8rem 1.1rem;
    margin-bottom: 0.5rem; font-size: 0.84rem;
}
.redirect-from { color: #ff7b72; font-family: 'Space Grotesk', monospace; font-size: 0.82rem; }
.redirect-arrow { color: #6b7ea3; margin: 0 0.4rem; }
.redirect-to { color: #56d364; font-family: 'Space Grotesk', monospace; font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">📊 Katrium SEO</div>
    <div class="sidebar-sub">Intelligence Platform · M1+M2+M3</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div style="color:#8ba3c7;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.8rem;">Configuration</div>', unsafe_allow_html=True)

    backend_url = st.text_input(
        "Backend URL (ngrok)",
        placeholder="https://xxxx.ngrok-free.app",
        help="Copy the ngrok URL from your Colab notebook"
    )
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Free at console.groq.com — used to generate AI content briefs"
    )
    serpapi_key = st.text_input(
        "SerpApi Key",
        type="password",
        placeholder="serpapi key...",
        help="serpapi.com — detects P1 competitors dynamically each month"
    )

    if backend_url:
        try:
            r = requests.get(f"{backend_url.rstrip('/')}/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                st.markdown(f"""
                <div class="connected-badge">
                    <div class="connected-dot"></div>
                    Backend connected
                </div>
                <div style="color:#6b7ea3;font-size:0.74rem;margin-top:0.5rem;margin-left:0.2rem;">
                    Pipeline: {data.get('pipeline','M1+M2+M3')}<br>
                    Model: paraphrase-multilingual-MiniLM
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-badge">⚠ Backend unreachable</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div class="error-badge">⚠ Cannot reach backend</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div style="color:#8ba3c7;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">Analysis Settings</div>', unsafe_allow_html=True)

    max_briefs = st.slider(
        "Max Content Briefs to generate",
        min_value=5,
        max_value=149,
        value=30,
        step=5,
        help="More briefs = better coverage but longer analysis time. 30 briefs ≈ 5 min · 149 briefs ≈ 30 min"
    )
    st.markdown(f'<div style="color:#6b7ea3;font-size:0.74rem;margin-top:-0.3rem;">⏱ Estimated time: ~{max_briefs // 6} min for briefs generation</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if backend_url:
        if st.button("📊 Load existing results", help="Load results from a previous analysis", use_container_width=True):
            try:
                res_data = requests.get(f"{backend_url.rstrip('/')}/results", timeout=10).json()
                if res_data.get('status') == 'done':
                    st.session_state['results'] = res_data['results']
                    st.session_state['analysis_started'] = False
                    st.rerun()
                else:
                    st.warning("No results yet — run an analysis first.")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.76rem;color:#4a5568;line-height:1.8;">
        <div style="color:#6b7ea3;font-weight:600;margin-bottom:0.5rem;font-size:0.74rem;text-transform:uppercase;letter-spacing:0.05em;">Pipeline</div>
        <div>● BERT Clustering (6 pillars)</div>
        <div>● WordPress API classification</div>
        <div>● CPS via BERT centroids</div>
        <div>● Random Forest vs SVM</div>
        <div>● LSI TF-IDF + BERT 0.40</div>
        <div>● SerpApi dynamic competitors</div>
        <div>● RAG + Llama 3.3 70B</div>
        <div style="margin-top:1rem;color:#4a5568;font-size:0.72rem;">PFE Internship · Katrium · 2026</div>
    </div>
    """, unsafe_allow_html=True)

# ── HERO BANNER ───────────────────────────────────────────────────────────────
if not st.session_state.get('results'):
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-eyebrow">Katrium SEO Intelligence</div>
        <div class="hero-title">Your SEO data.<br><span>Fully automated.</span></div>
        <div class="hero-desc">
            Upload two CSV files from Google Search Console and get a complete audit in minutes —
            competitor intelligence, content gaps, AI-written briefs, and a prioritized action plan.
            No technical knowledge required.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── HOW IT WORKS ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("01", "Export from GSC", "Performance → Queries → Export CSV\nPerformance → Pages → Export CSV"),
        ("02", "Start Colab backend", "Open the notebook · Run all cells\nCopy the ngrok URL → paste in sidebar"),
        ("03", "Upload & analyse", "Upload your 2 CSV files below\nClick Run Full Analysis · Wait ~20 min"),
        ("04", "Download results", "View all insights in the tabs below\nDownload 3 ready-to-use CSV files"),
    ]
    for col, (num, title, desc) in zip([c1,c2,c3,c4], steps):
        with col:
            st.markdown(f"""
            <div class="how-step">
                <div class="how-num">{num}</div>
                <div class="how-title">{title}</div>
                <div class="how-desc">{desc.replace(chr(10),'<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── STEP 1 — UPLOAD ───────────────────────────────────────────────────────────
st.markdown("""
<div class="step-header">
    <div class="step-number">Step 1</div>
    <div class="step-title">Upload GSC Exports</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div style="color:#8ba3c7;font-size:0.82rem;font-weight:600;margin-bottom:0.5rem;">
        📄 Queries.csv <span style="color:#4a5568;font-weight:400;">— GSC → Performance → Queries → Export</span>
    </div>
    """, unsafe_allow_html=True)
    queries_file = st.file_uploader("Upload Queries.csv", type=["csv"], label_visibility="collapsed")
    if queries_file:
        try:
            q_preview = pd.read_csv(queries_file)
            queries_file.seek(0)
            st.markdown(f"""
            <div style="background:#0d2a1a;border:1px solid rgba(86,211,100,0.3);border-radius:8px;
                        padding:0.6rem 1rem;color:#56d364;font-size:0.82rem;font-weight:600;margin-bottom:0.6rem;">
                ✓ {len(q_preview):,} queries loaded
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(q_preview.head(4), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")

with col2:
    st.markdown("""
    <div style="color:#8ba3c7;font-size:0.82rem;font-weight:600;margin-bottom:0.5rem;">
        📄 Pages.csv <span style="color:#4a5568;font-weight:400;">— GSC → Performance → Pages → Export</span>
    </div>
    """, unsafe_allow_html=True)
    pages_file = st.file_uploader("Upload Pages.csv", type=["csv"], label_visibility="collapsed")
    if pages_file:
        try:
            p_preview = pd.read_csv(pages_file)
            pages_file.seek(0)
            st.markdown(f"""
            <div style="background:#0d2a1a;border:1px solid rgba(86,211,100,0.3);border-radius:8px;
                        padding:0.6rem 1rem;color:#56d364;font-size:0.82rem;font-weight:600;margin-bottom:0.6rem;">
                ✓ {len(p_preview):,} pages loaded
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(p_preview.head(4), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── STEP 2 — RUN ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="step-header">
    <div class="step-number">Step 2</div>
    <div class="step-title">Run Full Analysis</div>
</div>
""", unsafe_allow_html=True)

ready = backend_url and groq_api_key and serpapi_key and queries_file and pages_file

if not backend_url:
    st.markdown('<div style="color:#e3b341;font-size:0.85rem;padding:0.8rem;background:rgba(227,179,65,0.08);border:1px solid rgba(227,179,65,0.2);border-radius:8px;">⚠ Enter the backend URL in the sidebar</div>', unsafe_allow_html=True)
elif not groq_api_key:
    st.markdown('<div style="color:#e3b341;font-size:0.85rem;padding:0.8rem;background:rgba(227,179,65,0.08);border:1px solid rgba(227,179,65,0.2);border-radius:8px;">⚠ Enter your Groq API key in the sidebar</div>', unsafe_allow_html=True)
elif not serpapi_key:
    st.markdown('<div style="color:#e3b341;font-size:0.85rem;padding:0.8rem;background:rgba(227,179,65,0.08);border:1px solid rgba(227,179,65,0.2);border-radius:8px;">⚠ Enter your SerpApi key in the sidebar</div>', unsafe_allow_html=True)
elif not queries_file or not pages_file:
    st.markdown('<div style="color:#e3b341;font-size:0.85rem;padding:0.8rem;background:rgba(227,179,65,0.08);border:1px solid rgba(227,179,65,0.2);border-radius:8px;">⚠ Upload both CSV files above</div>', unsafe_allow_html=True)

if ready:
    col_run, col_check = st.columns([3, 1])
    with col_run:
        run_clicked = st.button("🚀  Run Full Analysis  —  M1 + M2 + M3", type="primary", use_container_width=True)
    with col_check:
        if st.button("↺  Check results", use_container_width=True):
            try:
                res_data = requests.get(f"{backend_url.rstrip('/')}/results", timeout=10).json()
                if res_data.get('status') == 'done':
                    st.session_state['results'] = res_data['results']
                    st.session_state['analysis_started'] = False
                    st.rerun()
                else:
                    st.info("Analysis still running…")
            except Exception as e:
                st.error(f"Error: {e}")

    if run_clicked:
        with st.spinner("Sending files to backend…"):
            try:
                queries_file.seek(0); pages_file.seek(0)
                response = requests.post(
                    f"{backend_url.rstrip('/')}/analyze",
                    files={
                        'queries': ('queries.csv', queries_file.read(), 'text/csv'),
                        'pages':   ('pages.csv',   pages_file.read(),  'text/csv'),
                    },
                    data={
                        'groq_api_key': groq_api_key,
                        'serpapi_key':  serpapi_key,
                        'max_briefs':   str(max_briefs)
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    st.session_state['analysis_started'] = True
                    st.session_state['results'] = None
                    st.rerun()
                else:
                    st.error(f"Backend error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# ── PROGRESS ─────────────────────────────────────────────────────────────────
if st.session_state.get('analysis_started') and backend_url:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="loading-bar"></div>', unsafe_allow_html=True)

    try:
        prog = requests.get(f"{backend_url.rstrip('/')}/progress", timeout=5).json()
        pct  = max(0, min(100, int(prog.get('pct', 0))))
        step = prog.get('step', 'Processing…')

        col_pct, col_step = st.columns([1, 5])
        with col_pct:
            st.markdown(f'<div style="font-family:Space Grotesk,sans-serif;font-size:2.5rem;font-weight:700;color:#58a6ff;line-height:1;">{pct}%</div>', unsafe_allow_html=True)
        with col_step:
            st.markdown(f'<div style="color:#e6edf3;font-weight:500;font-size:0.9rem;padding-top:0.8rem;">{step}</div>', unsafe_allow_html=True)
            st.progress(pct / 100)

        if pct == -1:
            st.error(f"❌ Pipeline error: {step}")
            st.session_state['analysis_started'] = False
        elif pct == 100:
            res_data = requests.get(f"{backend_url.rstrip('/')}/results", timeout=10).json()
            if res_data.get('status') == 'done':
                st.session_state['results'] = res_data['results']
                st.session_state['analysis_started'] = False
                st.rerun()
    except:
        st.markdown('<div style="color:#6b7ea3;font-size:0.84rem;">Connecting to backend…</div>', unsafe_allow_html=True)

    st.markdown('<div style="color:#6b7ea3;font-size:0.78rem;margin-top:0.5rem;">Auto-refreshing every 5 seconds. Full analysis takes 20–25 minutes.</div>', unsafe_allow_html=True)
    time.sleep(5)
    st.rerun()

# ── RESULTS ───────────────────────────────────────────────────────────────────
if st.session_state.get('results'):
    results = st.session_state['results']
    summary = results.get('summary', {})

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Results header ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="results-header">
        <div class="results-title">📊 Analysis Results</div>
        <div class="results-sub">
            {summary.get('total_queries',0):,} queries · {summary.get('total_pages',0):,} pages ·
            {summary.get('mr_cluster_queries',0)} in Market Research cluster ·
            Model: {summary.get('rf_model','Random Forest')} (F1: {summary.get('rf_f1',0):.3f})
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Row 1 — Critical metrics ────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: st.metric("📉 Lost clicks/month", f"{summary.get('total_lost_clicks',0):,}", help="Clicks lost because informative pages have lower CTR than service pages")
    with k2: st.metric("💀 Dead pages", summary.get('dead_pages_0_clicks', summary.get('dead_pages',0)), delta="Needs fixing", delta_color="inverse")
    with k3: st.metric("🔍 Content gaps", summary.get('gaps_detected',0), help="Queries with no relevant landing page")
    with k4: st.metric("⚠️ Cannibalization", summary.get('cannibalization_queries',0), help="Queries competing across multiple pages")
    with k5: st.metric("📝 AI briefs", summary.get('content_briefs',0), help="Content briefs generated by Llama 3.3")

    # ── KPI Row 2 ────────────────────────────────────────────────────────────
    k6, k7, k8, k9 = st.columns(4)
    with k6: st.metric("🎯 MR cluster", summary.get('mr_cluster_queries',0), help="Queries in the Market Research semantic cluster")
    with k7: st.metric("🔑 LSI terms", summary.get('lsi_semantic_terms', summary.get('lsi_terms',0)), help="Semantic terms missing vs competitors (BERT filtered)")
    with k8: st.metric("↪️ Redirects", summary.get('redirect_actions',0), help="301 redirect actions identified")
    with k9:
        rf_f1 = summary.get('rf_f1', 0)
        st.metric("🤖 RF F1-score", f"{rf_f1:.3f}", help=f"Best model: {summary.get('rf_model','RF')} — {summary.get('svm_f1',0):.3f} SVM")

    # ── Priority distribution ─────────────────────────────────────────────
    pd_dist = summary.get('priority_distribution', {})
    if pd_dist:
        st.markdown('<div style="margin-top:1rem;margin-bottom:0.4rem;color:#8ba3c7;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Priority Distribution</div>', unsafe_allow_html=True)
        p1,p2,p3,p4 = st.columns(4)
        with p1: st.metric("🔴 CRITIQUE", pd_dist.get('P1-CRITIQUE', pd_dist.get('🔴 CRITIQUE',0)))
        with p2: st.metric("🟠 HAUTE", pd_dist.get('P2-HAUTE', pd_dist.get('🟠 HAUTE',0)))
        with p3: st.metric("🟡 MOYENNE", pd_dist.get('P3-MOYENNE', pd_dist.get('🟡 MOYENNE',0)))
        with p4: st.metric("🟢 BASSE", pd_dist.get('P4-BASSE', pd_dist.get('🟢 BASSE',0)))

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── TABS ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎯 Opportunities", "💀 Dead Pages", "↪️ Redirects",
        "🔑 LSI Terms", "📄 Content Briefs", "🌐 Competitors", "📥 Export"
    ])

    # ── TAB 1 — Opportunities ───────────────────────────────────────────────
    with tab1:
        opps = results.get('priority_opportunities', results.get('top_opportunities', []))
        st.markdown(f'<div class="section-title">🎯 Top Priority Opportunities <span style="color:#6b7ea3;font-size:0.82rem;font-weight:400;margin-left:0.5rem;">({len(opps)} queries)</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Ranked by Priority Score = CPS × log(impressions) × 1/position. Focus on 🔴 CRITIQUE first.</div>', unsafe_allow_html=True)

        if opps:
            intent_col = summary.get('intent_distribution', {})
            if intent_col:
                ic1, ic2 = st.columns(2)
                with ic1: st.metric("SERVICE queries", intent_col.get('SERVICE',0))
                with ic2: st.metric("INFORMATIVE queries", intent_col.get('INFORMATIVE',0))
            st.dataframe(pd.DataFrame(opps), use_container_width=True, hide_index=True)

        qw = results.get('quick_wins', [])
        if qw:
            st.markdown('<div class="section-title" style="margin-top:1.5rem;">⚡ Quick Wins — Page 2</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Positions 10–20 with 100+ impressions — one optimization away from Page 1.</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(qw), use_container_width=True, hide_index=True)

        new_opps = results.get('new_content_opportunities', [])
        if new_opps:
            st.markdown('<div class="section-title" style="margin-top:1.5rem;">✨ New Content Opportunities</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">SERVICE queries (CPS ≥ 0.50) with no good landing page (Best Fit < 0.70).</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(new_opps), use_container_width=True, hide_index=True)

    # ── TAB 2 — Dead Pages ──────────────────────────────────────────────────
    with tab2:
        dead = results.get('dead_pages', [])
        diag = results.get('diagnostic_m1', {})
        st.markdown(f'<div class="section-title">💀 Dead Pages <span style="color:#ff7b72;margin-left:0.5rem;">{len(dead)} pages</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Pages with 0 clicks but 100+ impressions — Google is showing them but they are broken or empty.</div>', unsafe_allow_html=True)

        if diag:
            d1,d2,d3,d4 = st.columns(4)
            with d1: st.metric("Dead classified", diag.get('dead_count',0))
            with d2: st.metric("SERVICE pages", diag.get('service_count',0))
            with d3: st.metric("INFORMATIVE", diag.get('info_count',0))
            with d4: st.metric("Potential clicks", f"{diag.get('total_potential',0):,}", help=f"Lost: {diag.get('total_lost',0):,} clicks/month")

        if dead:
            st.markdown("""
            <div style="background:rgba(255,123,114,0.08);border:1px solid rgba(255,123,114,0.2);
                        border-radius:8px;padding:0.8rem 1rem;color:#ff7b72;font-size:0.84rem;margin-bottom:1rem;">
                ⚠️ <strong>Action required:</strong> Recreate or restore these pages — each one is losing clicks every day.
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(dead), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div style="color:#56d364;font-size:0.88rem;padding:1rem;">✓ No dead pages detected.</div>', unsafe_allow_html=True)

    # ── TAB 3 — Redirects ───────────────────────────────────────────────────
    with tab3:
        redir = results.get('redirect_plan', [])
        cannibal = results.get('cannibalization_detail', [])
        st.markdown(f'<div class="section-title">↪️ 301 Redirect Plan <span style="color:#58a6ff;margin-left:0.5rem;">{len(redir)} actions</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">0-click pages redirected to the strongest page in the same language (detected via langdetect on URL slug).</div>', unsafe_allow_html=True)

        if redir:
            st.markdown("""
            <div style="background:rgba(29,111,204,0.08);border:1px solid rgba(29,111,204,0.2);
                        border-radius:8px;padding:0.8rem 1rem;color:#58a6ff;font-size:0.84rem;margin-bottom:1rem;">
                💡 <strong>How to implement:</strong> In WordPress, use the Redirection plugin or add rules in .htaccess.
                Each row = one 301 redirect to add.
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(redir), use_container_width=True, hide_index=True)

        if cannibal:
            st.markdown('<div class="section-title" style="margin-top:1.5rem;">⚠️ Cannibalization Detail</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(cannibal), use_container_width=True, hide_index=True)

        cannibal_summary = results.get('summary_cannibalization', [])
        if cannibal_summary:
            st.markdown('<div class="section-title" style="margin-top:1.5rem;">📊 Cannibalization Summary</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(cannibal_summary), use_container_width=True, hide_index=True)

    # ── TAB 4 — LSI Terms ───────────────────────────────────────────────────
    with tab4:
        lsi = results.get('lsi_semantic_gap', results.get('lsi_terms', []))
        lsi_page = results.get('lsi_tfidf_per_page', [])
        st.markdown(f'<div class="section-title">🔑 LSI Semantic Gap <span style="color:#58a6ff;margin-left:0.5rem;">{len(lsi)} terms</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Terms with high TF-IDF score in competitor pages but absent from katrium.eu — filtered by BERT similarity ≥ 0.40 to the Market Research centroid.</div>', unsafe_allow_html=True)

        if lsi:
            st.markdown("""
            <div style="background:rgba(88,166,255,0.07);border:1px solid rgba(88,166,255,0.18);
                        border-radius:8px;padding:0.8rem 1rem;color:#79c0ff;font-size:0.84rem;margin-bottom:1rem;">
                💡 <strong>How to use:</strong> Integrate these terms naturally in your H2 headings and body content.
                Higher GAP Score = higher priority.
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(lsi), use_container_width=True, hide_index=True)

        if lsi_page:
            st.markdown('<div class="section-title" style="margin-top:1.5rem;">📄 Missing Vocabulary — Per Page</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Terms present in your GSC queries but absent from each page content (TF-IDF analysis).</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(lsi_page).head(100), use_container_width=True, hide_index=True)

    # ── TAB 5 — Content Briefs ──────────────────────────────────────────────
    with tab5:
        briefs = results.get('content_briefs', [])
        st.markdown(f'<div class="section-title">📄 AI Content Briefs <span style="color:#58a6ff;margin-left:0.5rem;">{len(briefs)} pages to create</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Generated by Groq Llama 3.3 70B using RAG with real competitor pages + LSI terms. Each brief is a complete blueprint for a new page on katrium.eu.</div>', unsafe_allow_html=True)

        if briefs:
            p_colors = {'P1-CRITIQUE':('#ff7b72','p1'), 'P2-HAUTE':('#e3b341','p2'), 'P3-MOYENNE':('#58a6ff','p3'), 'P4-BASSE':('#6b7ea3','p4'),
                       'P1-CRITICAL':('#ff7b72','p1'), 'P2-HIGH':('#e3b341','p2'), 'P3-MEDIUM':('#58a6ff','p3'), 'P4-LOW':('#6b7ea3','p4')}
            for brief in briefs:
                prio = brief.get('priority','')
                color, cls = p_colors.get(prio, ('#6b7ea3','p4'))
                intent = brief.get('intent','')
                lang_raw = brief.get('language','EN')
                lang = '🇫🇮' if 'FI' in str(lang_raw) else '🇬🇧'
                t_len = brief.get('title_len', len(brief.get('title_tag','')))
                m_len = brief.get('meta_len', len(brief.get('meta_description','')))
                t_ok = '✅' if 55 <= t_len <= 60 else '⚠️'
                m_ok = '✅' if 150 <= m_len <= 160 else '⚠️'

                with st.expander(f"{lang}  {prio}  —  {brief.get('query','').title()}  ·  {brief.get('impressions',0):,} impr/mo"):
                    # Action type
                    is_gap_brief = brief.get('is_gap', True)
                    action_type  = brief.get('action_type', 'GAP_NEW_PAGE' if is_gap_brief else 'WINNER_OPTIMIZATION')
                    is_gap_brief = 'GAP' in str(action_type)
                    action_label = '🆕 NEW PAGE TO CREATE' if is_gap_brief else '✏️ EXISTING PAGE TO OPTIMIZE'
                    action_color = 'rgba(255,123,114,0.15)' if is_gap_brief else 'rgba(88,166,255,0.12)'
                    action_border= 'rgba(255,123,114,0.3)' if is_gap_brief else 'rgba(88,166,255,0.25)'
                    action_text  = '#ff7b72' if is_gap_brief else '#58a6ff'
                    page_katrium = brief.get('page_katrium', '')

                    c1, c2 = st.columns([3, 2])
                    with c1:
                        page_line = ''
                        if not is_gap_brief and page_katrium:
                            page_line = f'<div style="color:#6b7ea3;font-size:0.78rem;margin-bottom:0.6rem;">Current page: <span style="color:#8ba3c7;font-family:monospace;">{page_katrium}</span></div>'
                        st.markdown(f"""
                        <div style="margin-bottom:0.8rem;">
                            <span style="background:{action_color};color:{action_text};border:1px solid {action_border};padding:0.2rem 0.65rem;border-radius:5px;font-size:0.72rem;font-weight:700;margin-right:0.4rem;">{action_label}</span>
                            <span class="tag {'tag-service' if intent=='SERVICE' else 'tag-info'}">{intent}</span>
                            <span class="tag {'tag-fi' if 'FI' in str(lang_raw) else 'tag-en'}">{lang} {'Finnish' if 'FI' in str(lang_raw) else 'English'}</span>
                            <span style="color:#6b7ea3;font-size:0.78rem;">CPS: {brief.get('cps','')} · Position: {brief.get('position','')}</span>
                        </div>
                        {page_line}
                        <div style="background:#0d1117;border-radius:8px;padding:1rem;margin-bottom:0.8rem;border:1px solid #1e2d40;">
                            <div style="color:#6b7ea3;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem;">Slug URL</div>
                            <div style="color:#58a6ff;font-family:monospace;font-size:0.86rem;">{brief.get('slug','')}</div>
                        </div>
                        <div style="background:#0d1117;border-radius:8px;padding:1rem;margin-bottom:0.8rem;border:1px solid #1e2d40;">
                            <div style="color:#6b7ea3;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem;">{t_ok} Title Tag ({t_len} chars)</div>
                            <div style="color:#e6edf3;font-size:0.88rem;font-weight:600;">{brief.get('title_tag','')}</div>
                        </div>
                        <div style="background:#0d1117;border-radius:8px;padding:1rem;margin-bottom:0.8rem;border:1px solid #1e2d40;">
                            <div style="color:#6b7ea3;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem;">H1 — Main Heading</div>
                            <div style="color:#e6edf3;font-size:0.9rem;font-weight:600;">{brief.get('h1','— generated in brief —')}</div>
                        </div>
                        <div style="background:#0d1117;border-radius:8px;padding:1rem;margin-bottom:0.8rem;border:1px solid #1e2d40;">
                            <div style="color:#6b7ea3;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem;">{m_ok} Meta Description ({m_len} chars)</div>
                            <div style="color:#c9d1d9;font-size:0.84rem;line-height:1.55;">{brief.get('meta_description','')}</div>
                        </div>
                        <div style="display:flex;gap:1rem;font-size:0.82rem;flex-wrap:wrap;">
                            <div><span style="color:#6b7ea3;">Target words:</span> <span style="color:#e6edf3;">{brief.get('word_count_target','')}</span></div>
                            <div><span style="color:#6b7ea3;">CTA:</span> <span style="color:#e6edf3;">{brief.get('cta','')}</span></div>
                            <div><span style="color:#6b7ea3;">Schema:</span> <span style="color:#e6edf3;">{brief.get('schema','')}</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Target Keywords
                        kw_list = brief.get('keywords', [])
                        if isinstance(kw_list, list) and kw_list:
                            kw_pills = ' '.join([f'<span class="pill" style="background:rgba(227,179,65,0.12);color:#e3b341;border:1px solid rgba(227,179,65,0.25);font-size:0.72rem;padding:0.25rem 0.7rem;">{k}</span>' for k in kw_list])
                            st.markdown(f'<div style="margin-top:0.8rem;"><span style="color:#6b7ea3;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">🎯 Target Keywords</span><br><div style="margin-top:0.4rem;">{kw_pills}</div></div>', unsafe_allow_html=True)

                        # LSI Terms
                        lsi_list = brief.get('lsi_to_integrate',[])
                        if isinstance(lsi_list, list) and lsi_list:
                            pills = ' '.join([f'<span class="pill" style="background:rgba(88,166,255,0.1);color:#79c0ff;border:1px solid rgba(88,166,255,0.2);">{t}</span>' for t in lsi_list])
                            st.markdown(f'<div style="margin-top:0.8rem;"><span style="color:#6b7ea3;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">LSI Terms to integrate</span><br><div style="margin-top:0.4rem;">{pills}</div></div>', unsafe_allow_html=True)

                    with c2:
                        h_struct = brief.get('h_structure',[])
                        if isinstance(h_struct, list) and h_struct:
                            st.markdown('<div style="color:#6b7ea3;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.6rem;">Content Structure</div>', unsafe_allow_html=True)
                            for item in h_struct[:8]:
                                if isinstance(item, dict):
                                    st.markdown(f'<div style="color:#e6edf3;font-weight:600;font-size:0.84rem;margin-bottom:0.2rem;">▸ {item.get("h2","")}</div>', unsafe_allow_html=True)
                                    for h3 in item.get('h3s',[])[:3]:
                                        st.markdown(f'<div style="color:#8ba3c7;font-size:0.78rem;margin-left:1rem;margin-bottom:0.1rem;">↳ {h3}</div>', unsafe_allow_html=True)

                        internal_links = brief.get('internal_links_suggestion', [])
                        if isinstance(internal_links, list) and internal_links:
                            st.markdown('<div style="color:#6b7ea3;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-top:1rem;margin-bottom:0.4rem;">🔗 Internal Links</div>', unsafe_allow_html=True)
                            for link in internal_links[:4]:
                                st.markdown(f'<div style="color:#58a6ff;font-size:0.78rem;font-family:monospace;margin-bottom:0.2rem;">→ {link}</div>', unsafe_allow_html=True)

                    notes = brief.get('seo_notes','')
                    if notes:
                        st.markdown(f"""
                        <div style="background:rgba(86,211,100,0.07);border:1px solid rgba(86,211,100,0.2);
                                    border-radius:8px;padding:0.75rem 1rem;color:#7ee787;
                                    font-size:0.82rem;margin-top:0.8rem;line-height:1.5;">
                            💡 {notes}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#6b7ea3;font-size:0.88rem;padding:1rem;">No content briefs generated — check that SerpApi returned results and GAPs were detected.</div>', unsafe_allow_html=True)

        title_recs = results.get('title_recommendations', [])
        if title_recs:
            st.markdown('<div class="section-title" style="margin-top:1.5rem;">✏️ Title & Meta Recommendations — Existing Pages</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Optimized titles (55–60 chars) and meta descriptions (150–160 chars) for your current pages.</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(title_recs), use_container_width=True, hide_index=True)

    # ── TAB 6 — Competitors ─────────────────────────────────────────────────
    with tab6:
        top5 = summary.get('top5_competitors', [])
        serp_credits = summary.get('serpapi_credits_used', 0)
        st.markdown(f'<div class="section-title">🌐 P1 Competitor Intelligence <span style="color:#58a6ff;margin-left:0.5rem;">{serp_credits} SerpApi credits used</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Competitors detected dynamically from Google P1 this month via SerpApi. BERT similarity = url_to_text(Katrium page) vs url_to_text(competitor URL).</div>', unsafe_allow_html=True)

        if top5:
            st.markdown(f"""
            <div style="background:rgba(29,111,204,0.07);border:1px solid rgba(29,111,204,0.18);
                        border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;">
                <div style="color:#6b7ea3;font-size:0.74rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Top 5 Competitors Detected This Month</div>
                <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
                    {"".join([f'<span class="pill" style="background:rgba(88,166,255,0.12);color:#79c0ff;border:1px solid rgba(88,166,255,0.25);font-size:0.82rem;padding:0.3rem 0.8rem;">{d}</span>' for d in top5])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        comp_analysis = results.get('competitors_analysis', [])
        if comp_analysis:
            st.markdown('<div class="section-sub" style="margin-bottom:0.6rem;">Content metrics per competitor</div>', unsafe_allow_html=True)
            comp_df = pd.DataFrame(comp_analysis)
            display_cols = [c for c in ['name','domain','url','word_count','h2_count','h3_count','da'] if c in comp_df.columns]
            if display_cols:
                st.dataframe(comp_df[display_cols], use_container_width=True, hide_index=True)

        serp_sum = results.get('serp_summary', [])
        if serp_sum:
            st.markdown('<div class="section-title" style="margin-top:1.5rem;">BERT Similarity — Katrium vs P1 Google</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(serp_sum), use_container_width=True, hide_index=True)

        main_df_data = results.get('main_df', [])
        if main_df_data:
            with st.expander("Full mapping: query → Katrium page → P1 competitor"):
                st.dataframe(pd.DataFrame(main_df_data), use_container_width=True, hide_index=True)

    # ── TAB 7 — Export ──────────────────────────────────────────────────────
    with tab7:
        st.markdown('<div class="section-title">📥 Download Action Files</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">All files are UTF-8 encoded and ready to open in Excel or Google Sheets.</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

        # Row 1 — Primary exports
        e1, e2, e3 = st.columns(3)
        with e1:
            st.markdown("""
            <div class="export-card">
                <div class="export-icon">📄</div>
                <div class="export-title">Content Briefs</div>
                <div class="export-desc">All AI-generated briefs with H2 structure, LSI terms, CTA, schema</div>
            </div>
            """, unsafe_allow_html=True)
            briefs = results.get('content_briefs', [])
            if briefs:
                export_b = []
                for b in briefs:
                    h_flat = ' | '.join([f"H2: {i.get('h2','')} → {', '.join(i.get('h3s',[]))}" for i in b.get('h_structure',[]) if isinstance(i,dict)])
                    lsi_flat = ', '.join(b.get('lsi_to_integrate',[])) if isinstance(b.get('lsi_to_integrate',[]),list) else ''
                    export_b.append({'Priority':b.get('priority',''),'Query':b.get('query',''),'Intent':b.get('intent',''),'CPS':b.get('cps',''),'Impressions':b.get('impressions',''),'Language':b.get('language',''),'Slug':b.get('slug',''),'Title_Tag':b.get('title_tag',''),'Title_Len':b.get('title_len',''),'Meta_Description':b.get('meta_description',''),'Meta_Len':b.get('meta_len',''),'Word_Count_Target':b.get('word_count_target',''),'H_Structure':h_flat,'LSI_Terms':lsi_flat,'CTA':b.get('cta',''),'Schema':b.get('schema',''),'SEO_Notes':b.get('seo_notes','')})
                st.download_button("📥 katrium_content_briefs.csv", pd.DataFrame(export_b).to_csv(index=False, encoding='utf-8-sig'), file_name="katrium_content_briefs.csv", mime="text/csv", type="primary", use_container_width=True)
            else:
                st.markdown('<div style="color:#4a5568;font-size:0.8rem;text-align:center;padding:0.5rem;">No briefs available</div>', unsafe_allow_html=True)

        with e2:
            st.markdown("""
            <div class="export-card">
                <div class="export-icon">↪️</div>
                <div class="export-title">Redirect Plan</div>
                <div class="export-desc">301 redirects to implement — source URL → winner URL by language</div>
            </div>
            """, unsafe_allow_html=True)
            redir = results.get('redirect_plan', [])
            if redir:
                st.download_button("📥 katrium_redirect_plan.csv", pd.DataFrame(redir).to_csv(index=False, encoding='utf-8-sig'), file_name="katrium_redirect_plan.csv", mime="text/csv", use_container_width=True)
            else:
                st.markdown('<div style="color:#4a5568;font-size:0.8rem;text-align:center;padding:0.5rem;">No redirects available</div>', unsafe_allow_html=True)

        with e3:
            st.markdown("""
            <div class="export-card">
                <div class="export-icon">✏️</div>
                <div class="export-title">Title Recommendations</div>
                <div class="export-desc">Optimized title tags and meta descriptions for existing pages</div>
            </div>
            """, unsafe_allow_html=True)
            title_recs = results.get('title_recommendations', [])
            if title_recs:
                st.download_button("📥 katrium_title_recommendations.csv", pd.DataFrame(title_recs).to_csv(index=False, encoding='utf-8-sig'), file_name="katrium_title_recommendations.csv", mime="text/csv", use_container_width=True)
            else:
                st.markdown('<div style="color:#4a5568;font-size:0.8rem;text-align:center;padding:0.5rem;">No recommendations available</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

        # Row 2 — Secondary exports
        e4, e5, e6 = st.columns(3)
        with e4:
            opps = results.get('priority_opportunities', results.get('top_opportunities', []))
            if opps:
                st.download_button("📥 Priority opportunities CSV", pd.DataFrame(opps).to_csv(index=False, encoding='utf-8-sig'), file_name="katrium_opportunities.csv", mime="text/csv", use_container_width=True)
        with e5:
            lsi_export = results.get('export_lsi', results.get('lsi_semantic_gap', []))
            if lsi_export:
                st.download_button("📥 LSI terms CSV", pd.DataFrame(lsi_export).to_csv(index=False, encoding='utf-8-sig'), file_name="katrium_lsi_terms.csv", mime="text/csv", use_container_width=True)
        with e6:
            st.download_button("📥 Full results JSON", json.dumps(results, ensure_ascii=False, indent=2), file_name="katrium_full_results.json", mime="application/json", use_container_width=True)

        st.markdown("""
        <div style="background:rgba(86,211,100,0.07);border:1px solid rgba(86,211,100,0.2);
                    border-radius:10px;padding:1rem 1.2rem;margin-top:1rem;
                    color:#7ee787;font-size:0.84rem;line-height:1.6;">
            ✓ All files are ready. Open in Excel or Google Sheets — UTF-8 BOM encoded for correct display.
        </div>
        """, unsafe_allow_html=True)
