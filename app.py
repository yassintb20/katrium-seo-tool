import streamlit as st
import pandas as pd
import requests
import json
import time

st.set_page_config(
    page_title="Katrium SEO Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")
    backend_url = st.text_input(
        "🔗 Backend URL (ngrok)",
        placeholder="https://xxxx.ngrok-free.app",
    )
    groq_api_key = st.text_input(
        "🔑 Groq API Key",
        type="password",
        placeholder="gsk_...",
    )
    if backend_url:
        try:
            r = requests.get(f"{backend_url.rstrip('/')}/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                st.success("✅ Backend connected")
                st.caption(f"Pipeline: {data.get('pipeline','M1+M2+M3')}")
                st.caption(f"Model: {data.get('bert','BERT')}")
            else:
                st.error("❌ Backend unreachable")
        except:
            st.error("❌ Cannot reach backend")

    st.markdown("---")

    # ── Bouton pour charger résultats existants ────────────────────────────
    if backend_url:
        if st.button("📊 Load existing results", help="Load results from a previous analysis already done in Colab"):
            try:
                res_data = requests.get(f"{backend_url.rstrip('/')}/results", timeout=10).json()
                if res_data.get('status') == 'done':
                    st.session_state['results'] = res_data['results']
                    st.session_state['analysis_started'] = False
                    st.success("✅ Results loaded!")
                    st.rerun()
                else:
                    st.warning("No results available yet — run an analysis first.")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("""
**Katrium SEO Intelligence**

Pipeline M1+M2+M3:
- BERT clustering (6 pillars)
- WordPress API classification
- CPS via BERT centroids
- Random Forest intent
- LSI TF-IDF + BERT (0.40)
- RAG + Llama 3.3 70B

*PFE Internship — Katrium — 2026*
""")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🔍 Katrium SEO Intelligence")
st.markdown("**Automated SEO audit · BERT clustering · CPS classification · AI content briefs**")
st.markdown("---")

# ── HOW IT WORKS ──────────────────────────────────────────────────────────────
with st.expander("📖 How to use this tool", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**① Export from GSC**\n\nPerformance → Queries → Export CSV\nPerformance → Pages → Export CSV")
    with col2:
        st.markdown("**② Start Colab backend**\n\nRun the notebook cells\nCopy ngrok URL → paste in sidebar")
    with col3:
        st.markdown("**③ Run analysis**\n\nUpload 2 CSV files\nClick Run Full Analysis\nWait 5–8 minutes")
    with col4:
        st.markdown("**④ View results**\n\nClick **Load existing results** in sidebar\nDownload CSV files")
    st.info("⏱️ After analysis completes, click **Load existing results** in the sidebar to display results.")

st.markdown("---")

# ── STEP 1 — UPLOAD ───────────────────────────────────────────────────────────
st.header("① Upload GSC Exports")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**📄 Queries.csv**")
    st.caption("GSC → Performance → Queries → Export CSV")
    queries_file = st.file_uploader("Upload Queries.csv", type=["csv"], label_visibility="collapsed")
    if queries_file:
        try:
            q_preview = pd.read_csv(queries_file)
            queries_file.seek(0)
            st.success(f"✅ {len(q_preview):,} queries loaded")
            st.dataframe(q_preview.head(3), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    st.markdown("**📄 Pages.csv**")
    st.caption("GSC → Performance → Pages → Export CSV")
    pages_file = st.file_uploader("Upload Pages.csv", type=["csv"], label_visibility="collapsed")
    if pages_file:
        try:
            p_preview = pd.read_csv(pages_file)
            pages_file.seek(0)
            st.success(f"✅ {len(p_preview):,} pages loaded")
            st.dataframe(p_preview.head(3), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")

# ── STEP 2 — RUN ANALYSIS ─────────────────────────────────────────────────────
st.header("② Run Full Analysis")

if not backend_url:
    st.warning("⚠️ Enter the backend URL in the sidebar.")
elif not groq_api_key:
    st.warning("⚠️ Enter your Groq API key in the sidebar.")
elif not queries_file or not pages_file:
    st.warning("⚠️ Upload both CSV files above.")
else:
    col_run, col_status = st.columns([2, 1])
    with col_run:
        run_clicked = st.button("🚀 Run Full Analysis", type="primary", use_container_width=True)
    with col_status:
        # Check if results already available
        if st.button("📊 Check & Load Results", use_container_width=True):
            try:
                res_data = requests.get(f"{backend_url.rstrip('/')}/results", timeout=10).json()
                if res_data.get('status') == 'done':
                    st.session_state['results'] = res_data['results']
                    st.session_state['analysis_started'] = False
                    st.rerun()
                else:
                    st.info("No results yet.")
            except Exception as e:
                st.error(f"Error: {e}")

    if run_clicked:
        with st.spinner("Sending files to Colab backend..."):
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
                    st.session_state['results'] = None
                    st.success("✅ Analysis started in Colab! Monitor progress below.")
                    st.rerun()
                else:
                    st.error(f"Backend error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# ── PROGRESS TRACKING ─────────────────────────────────────────────────────────
if st.session_state.get('analysis_started') and backend_url:
    st.markdown("---")
    st.subheader("⚙️ Analysis Progress")
    st.caption("Auto-updates every 5 seconds. When complete, results will load automatically.")

    bar    = st.progress(0)
    status = st.empty()
    note   = st.info("💡 If the page doesn't update automatically after 100%, click **Check & Load Results** above.")

    try:
        prog = requests.get(f"{backend_url.rstrip('/')}/progress", timeout=5).json()
        pct  = max(0, min(100, int(prog.get('pct', 0))))
        step = prog.get('step', '')
        bar.progress(pct / 100)
        status.markdown(f"**{pct}%** — {step}")

        if pct == 100:
            # Try to load results immediately
            res_data = requests.get(f"{backend_url.rstrip('/')}/results", timeout=10).json()
            if res_data.get('status') == 'done':
                st.session_state['results'] = res_data['results']
                st.session_state['analysis_started'] = False
                st.rerun()
        elif pct == -1:
            st.error(f"❌ Pipeline error: {step}")
            st.session_state['analysis_started'] = False
    except:
        pass

    # Auto-refresh every 5 seconds
    time.sleep(5)
    st.rerun()

# ── RESULTS ───────────────────────────────────────────────────────────────────
if st.session_state.get('results'):
    results = st.session_state['results']
    summary = results.get('summary', {})

    st.markdown("---")
    st.header("③ Results & Insights")

    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("📉 Lost clicks/month", f"{summary.get('total_lost_clicks',0):,}")
    with col2: st.metric("💀 Dead pages", summary.get('dead_pages', 0))
    with col3: st.metric("🔍 Gaps detected", summary.get('gaps_detected', 0))
    with col4: st.metric("⚠️ Cannibalization", summary.get('cannibalization_queries', 0))
    with col5: st.metric("📝 Content briefs", summary.get('content_briefs', 0))

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("🤖 RF F1-Score", f"{summary.get('rf_f1_score',0):.4f}")
    with col2: st.metric("🔑 LSI terms", summary.get('lsi_terms', 0))
    with col3: st.metric("🎯 MR cluster", summary.get('mr_cluster_queries', 0))

    pd_dist = summary.get('priority_distribution', {})
    if pd_dist:
        st.subheader("Priority Distribution")
        pcols = st.columns(4)
        for i, (p, icon) in enumerate([('P1-CRITICAL','🔴'),('P2-HIGH','🟠'),('P3-MEDIUM','🟡'),('P4-LOW','⚪')]):
            with pcols[i]: st.metric(f"{icon} {p}", pd_dist.get(p, 0))

    intent_counts = summary.get('intent_counts', {})
    if intent_counts:
        st.subheader("Intent Distribution (Random Forest)")
        ic = st.columns(2)
        with ic[0]: st.metric("🔴 SERVICE", intent_counts.get('SERVICE', 0))
        with ic[1]: st.metric("🟢 INFORMATIVE", intent_counts.get('INFORMATIVE', 0))

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Top Opportunities", "💀 Dead Pages", "↪️ Redirect Plan",
        "🔑 LSI Terms", "📄 Content Briefs", "📥 Export"
    ])

    with tab1:
        st.subheader("Top 20 Priority Opportunities")
        st.caption("Priority Score = CPS × log(impressions) × 1/position (M2-S3)")
        opps = results.get('top_opportunities', [])
        if opps:
            st.dataframe(pd.DataFrame(opps), use_container_width=True, hide_index=True)
        else:
            st.info("No data.")

    with tab2:
        st.subheader(f"Dead Pages ({summary.get('dead_pages',0)})")
        st.caption("0 clicks + 100+ impressions — immediate action required")
        dead = results.get('dead_pages', [])
        if dead:
            st.dataframe(pd.DataFrame(dead), use_container_width=True, hide_index=True)
        else:
            st.info("No dead pages detected.")

    with tab3:
        st.subheader(f"301 Redirect Plan ({summary.get('redirect_actions',0)} actions)")
        st.caption("0-click pages → winner (langdetect on URL slug)")
        redir = results.get('redirect_plan', [])
        if redir:
            st.dataframe(pd.DataFrame(redir), use_container_width=True, hide_index=True)
        else:
            st.info("No redirects needed.")

    with tab4:
        st.subheader(f"LSI Semantic Gap ({summary.get('lsi_terms',0)} terms)")
        st.caption("TF-IDF competitors vs Katrium → BERT filter threshold 0.40")
        lsi = results.get('lsi_terms', [])
        if lsi:
            st.dataframe(pd.DataFrame(lsi), use_container_width=True, hide_index=True)
        else:
            st.info("No LSI data.")

    with tab5:
        st.subheader(f"AI Content Briefs ({summary.get('content_briefs',0)} pages)")
        st.caption("Generated by Llama 3.3 70B — RAG with competitor pages + LSI terms")
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
                            for item in h_struct[:7]:
                                if isinstance(item, dict):
                                    st.markdown(f"**H2:** {item.get('h2','')}")
                                    for h3 in item.get('h3s',[])[:3]:
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;↳ {h3}")
                    notes = brief.get('seo_notes','')
                    if notes:
                        st.info(f"💡 {notes}")
        else:
            st.info("No content briefs generated.")

    with tab6:
        st.subheader("📥 Export Action Files")
        c1, c2, c3 = st.columns(3)
        with c1:
            briefs = results.get('content_briefs',[])
            if briefs:
                export = []
                for b in briefs:
                    h_flat = ' | '.join([f"H2: {i.get('h2','')} → {', '.join(i.get('h3s',[]))}" for i in b.get('h_structure',[]) if isinstance(i,dict)])
                    lsi_flat = ', '.join(b.get('lsi_to_integrate',[])) if isinstance(b.get('lsi_to_integrate',[]),list) else ''
                    export.append({
                        'Priority':b.get('priority',''),'Query':b.get('query',''),
                        'Intent':b.get('intent',''),'CPS':b.get('cps',''),
                        'Impressions':b.get('impressions',''),'Language':b.get('language',''),
                        'Slug':b.get('slug',''),'Title_Tag':b.get('title_tag',''),
                        'Title_Len':b.get('title_len',''),'Meta_Description':b.get('meta_description',''),
                        'Meta_Len':b.get('meta_len',''),'Word_Count_Target':b.get('word_count_target',''),
                        'H_Structure':h_flat,'LSI_Terms':lsi_flat,
                        'CTA':b.get('cta',''),'Schema':b.get('schema',''),
                        'SEO_Notes':b.get('seo_notes','')
                    })
                st.download_button("📥 Content Briefs CSV",
                    pd.DataFrame(export).to_csv(index=False, encoding='utf-8-sig'),
                    file_name="katrium_content_briefs.csv", mime="text/csv", type="primary")
        with c2:
            redir = results.get('redirect_plan',[])
            if redir:
                st.download_button("📥 Redirect Plan CSV",
                    pd.DataFrame(redir).to_csv(index=False, encoding='utf-8-sig'),
                    file_name="katrium_redirect_plan.csv", mime="text/csv")
        with c3:
            opps = results.get('top_opportunities',[])
            if opps:
                st.download_button("📥 Priority Opportunities CSV",
                    pd.DataFrame(opps).to_csv(index=False, encoding='utf-8-sig'),
                    file_name="katrium_opportunities.csv", mime="text/csv")
        st.markdown("---")
        title_recs = results.get('title_recommendations',[])
        if title_recs:
            st.download_button("📥 Title Recommendations CSV",
                pd.DataFrame(title_recs).to_csv(index=False, encoding='utf-8-sig'),
                file_name="katrium_title_recommendations.csv", mime="text/csv")
        st.download_button("📥 Full Results JSON",
            json.dumps(results, ensure_ascii=False, indent=2),
            file_name="katrium_full_results.json", mime="application/json")
        st.success("✅ All files ready for download")
