import streamlit as st
import pandas as pd
import requests
import json
import io
import time

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Katrium SEO Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header { padding: 1.5rem 0 1rem; border-bottom: 1px solid rgba(0,0,0,0.08); margin-bottom: 2rem; }
.step-card { background: #fafafa; border: 1px solid #e8e8e8; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; }
.step-header { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.step-num { width: 28px; height: 28px; border-radius: 50%; background: #f0f0f0; border: 1px solid #d0d0d0; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; color: #444; flex-shrink: 0; }
.info-banner { background: #f0f7ff; border: 1px solid #b3d4ff; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #1a4a7a; margin-bottom: 12px; }
.success-banner { background: #f0fff4; border: 1px solid #b3ffd6; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #1a5c3a; }
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 1rem 0; }
.metric-box { background: #fafafa; border: 1px solid #e8e8e8; border-radius: 10px; padding: 1rem; text-align: center; }
.metric-label { font-size: 12px; color: #888; margin-bottom: 4px; }
.metric-value { font-size: 24px; font-weight: 600; }
.red { color: #e53e3e; }
.green { color: #38a169; }
.blue { color: #3182ce; }
.orange { color: #dd6b20; }
.tag-p1 { background: #fff5f5; color: #c53030; border: 1px solid #fed7d7; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-p2 { background: #fffaf0; color: #c05621; border: 1px solid #fbd38d; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-p3 { background: #fffff0; color: #744210; border: 1px solid #f6e05e; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.tag-p4 { background: #f7fafc; color: #4a5568; border: 1px solid #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    backend_url = st.text_input(
        "Backend URL",
        placeholder="https://xxxx.ngrok.io",
        help="The ngrok URL from your running Colab backend"
    )

    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get a free key at console.groq.com"
    )

    if backend_url:
        try:
            r = requests.get(f"{backend_url.rstrip('/')}/health", timeout=5)
            if r.status_code == 200:
                st.success("✅ Backend connected")
            else:
                st.error("❌ Backend unreachable")
        except:
            st.error("❌ Cannot reach backend")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
**Katrium SEO Intelligence Tool**
Automated SEO audit and AI content brief generation.

**Pipeline:**
- BERT semantic clustering
- Cannibalization detection
- WordPress API classification
- CPS + intent scoring
- LSI gap analysis
- RAG + Llama 3.3 briefs

*PFE Internship — April–July 2026*
""")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🔍 Katrium SEO Intelligence")
st.markdown("**Automated SEO audit · Intent classification · AI content briefs**")
st.markdown('</div>', unsafe_allow_html=True)

# ── INSTRUCTIONS ──────────────────────────────────────────────────────────────
with st.expander("📖 How to use this tool — read before starting", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
**Step 1 — Prepare your files**
Export from Google Search Console:
- Go to **Performance → Search Results**
- Click the **Queries** tab → Export CSV
- Click the **Pages** tab → Export CSV

You only need these 2 files.
""")
    with col2:
        st.markdown("""
**Step 2 — Start the backend**
Open the Colab notebook (link below), add your Groq API key, and run it.
It will display a public URL (ngrok). Paste that URL in the sidebar.

The backend handles all heavy computation — BERT, scraping, AI generation.
""")
    with col3:
        st.markdown("""
**Step 3 — Run the analysis**
Upload your 2 CSV files, enter your Groq API key, and click **Run Analysis**.

The tool will automatically:
- Detect dead pages & gaps
- Classify intent (SERVICE/INFORMATIVE)
- Generate AI content briefs
- Export action CSV files
""")

    st.info("⏱️ Full analysis takes approximately **5–8 minutes** depending on the number of queries and competitor pages to scrape.")

st.markdown("---")

# ── STEP 1 — UPLOAD ───────────────────────────────────────────────────────────
st.header("① Upload GSC Exports")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Queries.csv**")
    st.caption("From GSC → Performance → Queries → Export")
    queries_file = st.file_uploader("Upload Queries.csv", type=["csv"], label_visibility="collapsed")
    if queries_file:
        try:
            q_preview = pd.read_csv(queries_file)
            queries_file.seek(0)
            st.success(f"✅ {len(q_preview):,} queries loaded")
            st.dataframe(q_preview.head(3), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")

with col2:
    st.markdown("**Pages.csv**")
    st.caption("From GSC → Performance → Pages → Export")
    pages_file = st.file_uploader("Upload Pages.csv", type=["csv"], label_visibility="collapsed")
    if pages_file:
        try:
            p_preview = pd.read_csv(pages_file)
            pages_file.seek(0)
            st.success(f"✅ {len(p_preview):,} pages loaded")
            st.dataframe(p_preview.head(3), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")

st.markdown("---")

# ── STEP 2 — RUN ANALYSIS ─────────────────────────────────────────────────────
st.header("② Run Analysis")

if not backend_url:
    st.warning("⚠️ Enter the backend URL in the sidebar before running the analysis.")
elif not groq_api_key:
    st.warning("⚠️ Enter your Groq API key in the sidebar.")
elif not queries_file or not pages_file:
    st.warning("⚠️ Upload both CSV files above before running.")
else:
    if st.button("🚀 Run Full Analysis", type="primary", use_container_width=True):
        with st.spinner("Sending files to backend..."):
            try:
                queries_file.seek(0)
                pages_file.seek(0)

                response = requests.post(
                    f"{backend_url.rstrip('/')}/analyze",
                    files={
                        'queries': ('queries.csv', queries_file.read(), 'text/csv'),
                        'pages':   ('pages.csv',   pages_file.read(),  'text/csv'),
                    },
                    data={'groq_api_key': groq_api_key},
                    timeout=30
                )

                if response.status_code == 200:
                    st.session_state['analysis_started'] = True
                    st.success("✅ Analysis started! Tracking progress below...")
                else:
                    st.error(f"Backend error: {response.text}")

            except Exception as e:
                st.error(f"Connection error: {e}")

# ── PROGRESS TRACKING ─────────────────────────────────────────────────────────
if st.session_state.get('analysis_started') and backend_url:
    st.markdown("---")
    st.subheader("Analysis Progress")

    progress_placeholder = st.empty()
    bar_placeholder      = st.progress(0)
    status_placeholder   = st.empty()
    results_placeholder  = st.empty()

    poll_count = 0
    while poll_count < 200:
        try:
            # Check progress
            prog_resp = requests.get(f"{backend_url.rstrip('/')}/progress", timeout=5)
            if prog_resp.status_code == 200:
                prog = prog_resp.json()
                pct  = max(0, min(100, int(prog.get('pct', 0))))
                step = prog.get('step', '')

                bar_placeholder.progress(pct / 100)
                progress_placeholder.markdown(f"**{pct}%** — {step}")

                if pct == -1:
                    status_placeholder.error(f"❌ Analysis failed: {step}")
                    break

            # Check results
            res_resp = requests.get(f"{backend_url.rstrip('/')}/results", timeout=10)
            if res_resp.status_code == 200:
                res_data = res_resp.json()
                if res_data.get('status') == 'done':
                    bar_placeholder.progress(1.0)
                    progress_placeholder.markdown("**100%** — Analysis complete!")
                    st.session_state['results'] = res_data['results']
                    st.session_state['analysis_started'] = False
                    st.rerun()

        except:
            pass

        time.sleep(4)
        poll_count += 1

# ── STEP 3 — RESULTS ─────────────────────────────────────────────────────────
if st.session_state.get('results'):
    results = st.session_state['results']
    summary = results.get('summary', {})

    st.markdown("---")
    st.header("③ Results & Insights")

    # ── KPIs ─────────────────────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Lost clicks/month", f"{summary.get('total_lost_clicks',0):,}", help="Estimated monthly clicks lost due to low CTR on informative pages")
    with col2:
        st.metric("Dead pages", summary.get('dead_pages', 0), help="Pages with 0 clicks and 100+ impressions")
    with col3:
        st.metric("Gaps detected", summary.get('gaps_detected', 0), help="Queries without a relevant landing page")
    with col4:
        st.metric("Cannibalization", summary.get('cannibalization_queries', 0), help="Queries where multiple pages compete")
    with col5:
        st.metric("Content briefs", summary.get('content_briefs', 0), help="AI-generated content briefs for gap pages")

    # ── Priority distribution ─────────────────────────────────────────────────
    pc = summary.get('priority_counts', {})
    if pc:
        st.subheader("Priority Distribution")
        pcols = st.columns(4)
        for i, (prio, color) in enumerate([
            ('P1-CRITICAL', '🔴'),
            ('P2-HIGH', '🟠'),
            ('P3-MEDIUM', '🟡'),
            ('P4-LOW', '⚪')
        ]):
            with pcols[i]:
                st.metric(f"{color} {prio}", pc.get(prio, 0))

    # ── Tabs for detailed results ─────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Top Opportunities",
        "💀 Dead Pages",
        "↪️ Redirect Plan",
        "🔑 LSI Terms",
        "📄 Content Briefs",
        "📥 Export"
    ])

    with tab1:
        st.subheader("Top 20 Priority Opportunities")
        opps = results.get('top_opportunities', [])
        if opps:
            opps_df = pd.DataFrame(opps)
            st.dataframe(opps_df, use_container_width=True, hide_index=True)
        else:
            st.info("No opportunity data available.")

    with tab2:
        st.subheader(f"Dead Pages ({summary.get('dead_pages',0)} total)")
        dead = results.get('dead_pages', [])
        if dead:
            dead_df = pd.DataFrame(dead)
            st.dataframe(dead_df, use_container_width=True, hide_index=True)
        else:
            st.info("No dead pages detected.")

    with tab3:
        st.subheader(f"301 Redirect Plan ({summary.get('redirect_actions',0)} actions)")
        redir = results.get('redirect_plan', [])
        if redir:
            redir_df = pd.DataFrame(redir)
            st.dataframe(redir_df, use_container_width=True, hide_index=True)
        else:
            st.info("No redirects needed.")

    with tab4:
        st.subheader(f"LSI Semantic Gap ({summary.get('lsi_terms',0)} terms)")
        lsi = results.get('lsi_terms', [])
        if lsi:
            lsi_df = pd.DataFrame(lsi)
            st.dataframe(lsi_df, use_container_width=True, hide_index=True)
        else:
            st.info("No LSI data available.")

    with tab5:
        st.subheader(f"AI Content Briefs ({summary.get('content_briefs',0)} pages)")
        briefs = results.get('content_briefs', [])
        if briefs:
            for brief in briefs:
                p_icon = {'P1-CRITICAL':'🔴','P2-HIGH':'🟠','P3-MEDIUM':'🟡','P4-LOW':'⚪'}.get(brief.get('priority',''),'⚪')
                lang_flag = '🇫🇮' if brief.get('language') == 'FI' else '🇬🇧'
                with st.expander(f"{p_icon} [{brief.get('priority','')}] {brief.get('query','').upper()} {lang_flag}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        t_ok = '✅' if 55 <= brief.get('title_len',0) <= 60 else '⚠️'
                        m_ok = '✅' if 150 <= brief.get('meta_len',0) <= 160 else '⚠️'
                        st.markdown(f"**Slug:** `{brief.get('slug','')}`")
                        st.markdown(f"**Intent:** {brief.get('intent','')} · **CPS:** {brief.get('cps','')} · **{brief.get('impressions',0):,} impressions**")
                        st.markdown(f"**{t_ok} Title ({brief.get('title_len',0)}c):** {brief.get('title_tag','')}")
                        st.markdown(f"**{m_ok} Meta ({brief.get('meta_len',0)}c):** {brief.get('meta_description','')}")
                        st.markdown(f"**Target words:** {brief.get('word_count_target','')}")
                        st.markdown(f"**CTA:** {brief.get('cta','')}")
                        st.markdown(f"**Schema:** {brief.get('schema','')}")
                        lsi_list = brief.get('lsi_to_integrate',[])
                        if isinstance(lsi_list, list):
                            st.markdown(f"**LSI:** {' · '.join(lsi_list)}")
                    with c2:
                        h_struct = brief.get('h_structure',[])
                        if isinstance(h_struct, list):
                            st.markdown("**Content structure:**")
                            for item in h_struct[:6]:
                                if isinstance(item, dict):
                                    st.markdown(f"**H2:** {item.get('h2','')}")
                                    for h3 in item.get('h3s',[])[:3]:
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;↳ {h3}")
                    notes = brief.get('seo_notes','')
                    if notes:
                        st.info(f"💡 {notes}")
        else:
            st.info("No content briefs generated yet.")

    with tab6:
        st.subheader("Export Action Files")
        st.markdown("Download all results as ready-to-use CSV files.")

        col1, col2, col3 = st.columns(3)

        with col1:
            briefs = results.get('content_briefs',[])
            if briefs:
                briefs_export = []
                for b in briefs:
                    h_flat = ' | '.join([f"H2: {i.get('h2','')} → {', '.join(i.get('h3s',[]))}" for i in b.get('h_structure',[]) if isinstance(i,dict)])
                    lsi_flat = ', '.join(b.get('lsi_to_integrate',[])) if isinstance(b.get('lsi_to_integrate',[]),list) else ''
                    briefs_export.append({
                        'Priority': b.get('priority',''), 'Query': b.get('query',''),
                        'Intent': b.get('intent',''), 'CPS': b.get('cps',''),
                        'Impressions': b.get('impressions',''), 'Position': b.get('position',''),
                        'Language': b.get('language',''), 'Slug': b.get('slug',''),
                        'Title_Tag': b.get('title_tag',''), 'Title_Len': b.get('title_len',''),
                        'Meta_Description': b.get('meta_description',''), 'Meta_Len': b.get('meta_len',''),
                        'Word_Count_Target': b.get('word_count_target',''),
                        'H_Structure': h_flat, 'LSI_Terms': lsi_flat,
                        'CTA': b.get('cta',''), 'Schema': b.get('schema',''),
                        'SEO_Notes': b.get('seo_notes','')
                    })
                csv = pd.DataFrame(briefs_export).to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 Content Briefs CSV", csv,
                    file_name="katrium_content_briefs.csv", mime="text/csv", type="primary")

        with col2:
            redir = results.get('redirect_plan',[])
            if redir:
                csv = pd.DataFrame(redir).to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 Redirect Plan CSV", csv,
                    file_name="katrium_redirect_plan.csv", mime="text/csv")

        with col3:
            opps = results.get('top_opportunities',[])
            if opps:
                csv = pd.DataFrame(opps).to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 Priority Opportunities CSV", csv,
                    file_name="katrium_opportunities.csv", mime="text/csv")

        # Full JSON export
        st.markdown("---")
        full_json = json.dumps(results, ensure_ascii=False, indent=2)
        st.download_button("📥 Full Results JSON", full_json,
            file_name="katrium_full_results.json", mime="application/json")

        st.success("✅ Analysis complete — all files ready for download")

