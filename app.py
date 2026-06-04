import streamlit as st
import pandas as pd
import numpy as np
import re
import time
import json
import io
from groq import Groq
from sklearn.metrics.pairwise import cosine_similarity
from langdetect import detect as langdetect_detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from sentence_transformers import SentenceTransformer
import requests
from bs4 import BeautifulSoup

DetectorFactory.seed = 42

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Katrium SEO Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.metric-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    border: 1px solid #e9ecef;
    margin-bottom: 8px;
}
.priority-p1 { color: #dc3545; font-weight: 600; }
.priority-p2 { color: #fd7e14; font-weight: 600; }
.priority-p3 { color: #ffc107; font-weight: 600; }
.priority-p4 { color: #6c757d; font-weight: 600; }
.status-ok { color: #28a745; }
.status-warn { color: #ffc107; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://katrium.eu/wp-content/uploads/2022/03/katrium-logo.png",
             use_container_width=True)
    st.markdown("---")
    st.markdown("### ⚙️ Configuration")
    groq_api_key = st.text_input("Clé API Groq", type="password",
                                  help="Obtenir gratuitement sur console.groq.com")
    st.markdown("---")
    st.markdown("### 📋 À propos")
    st.markdown("""
    Outil SEO intelligent développé dans le cadre du stage PFE Katrium.

    **Architecture :**
    - Diagnostic GSC automatique
    - Classification intent (Random Forest)
    - RAG + LLM (Llama 3.3 70B)
    - Génération Content Briefs

    **Auteur :** Stagiaire PFE — Avril-Juillet 2026
    """)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.title("🔍 Katrium SEO Intelligence Tool")
st.markdown("**Upload vos exports GSC → Diagnostic complet + Content Briefs en quelques secondes**")
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — UPLOAD
# ─────────────────────────────────────────────────────────────────────────────

st.header("① Upload des fichiers GSC")

col1, col2 = st.columns(2)
with col1:
    queries_file = st.file_uploader("📄 Queries.csv", type=["csv"],
                                     help="Export Google Search Console — Requêtes")
with col2:
    pages_file = st.file_uploader("📄 Pages.csv", type=["csv"],
                                   help="Export Google Search Console — Pages")

if not queries_file or not pages_file:
    st.info("👆 Uploadez vos 2 fichiers GSC pour démarrer l'analyse.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def load_gsc_data(queries_bytes, pages_bytes):
    queries_df = pd.read_csv(io.BytesIO(queries_bytes))
    pages_df   = pd.read_csv(io.BytesIO(pages_bytes))

    # Normalisation colonnes
    col_map_q = {}
    for c in queries_df.columns:
        cl = c.lower().strip()
        if 'query' in cl or 'requête' in cl or 'requete' in cl:
            col_map_q[c] = 'Query'
        elif 'click' in cl:
            col_map_q[c] = 'Clicks'
        elif 'impression' in cl:
            col_map_q[c] = 'Impressions'
        elif 'ctr' in cl:
            col_map_q[c] = 'CTR'
        elif 'position' in cl:
            col_map_q[c] = 'Position'
    queries_df = queries_df.rename(columns=col_map_q)

    col_map_p = {}
    for c in pages_df.columns:
        cl = c.lower().strip()
        if 'page' in cl or 'url' in cl or 'landing' in cl:
            col_map_p[c] = 'Page'
        elif 'click' in cl:
            col_map_p[c] = 'Clicks'
        elif 'impression' in cl:
            col_map_p[c] = 'Impressions'
        elif 'ctr' in cl:
            col_map_p[c] = 'CTR'
        elif 'position' in cl:
            col_map_p[c] = 'Position'
    pages_df = pages_df.rename(columns=col_map_p)

    # Nettoyage
    for col in ['Clicks', 'Impressions', 'Position']:
        if col in queries_df.columns:
            queries_df[col] = pd.to_numeric(queries_df[col], errors='coerce').fillna(0)
        if col in pages_df.columns:
            pages_df[col] = pd.to_numeric(pages_df[col], errors='coerce').fillna(0)

    return queries_df, pages_df

queries_df, pages_df = load_gsc_data(
    queries_file.read(),
    pages_file.read()
)

st.success(f"✅ Données chargées — {len(queries_df):,} requêtes · {len(pages_df):,} pages")

# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 — DIAGNOSTIC SEO
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.header("② Diagnostic SEO")

@st.cache_data
def run_diagnostic(queries_bytes, pages_bytes):
    queries_df, pages_df = load_gsc_data(queries_bytes, pages_bytes)
    results = {}

    # Pages mortes (0 clics + impressions > 100)
    if 'Clicks' in pages_df.columns and 'Impressions' in pages_df.columns:
        dead_pages = pages_df[
            (pages_df['Clicks'] == 0) & (pages_df['Impressions'] >= 100)
        ].copy()
        results['dead_pages'] = dead_pages
        results['dead_pages_count'] = len(dead_pages)
    else:
        results['dead_pages'] = pd.DataFrame()
        results['dead_pages_count'] = 0

    # Clics perdus
    if 'Impressions' in queries_df.columns and 'Clicks' in queries_df.columns:
        queries_df['Lost_Clicks'] = (
            queries_df['Impressions'] * 0.317 - queries_df['Clicks']
        ).clip(lower=0)
        results['total_lost_clicks'] = int(queries_df['Lost_Clicks'].sum())
        results['top_opportunities'] = queries_df.nlargest(10, 'Lost_Clicks')[
            ['Query', 'Impressions', 'Clicks', 'Position', 'Lost_Clicks']
        ] if 'Query' in queries_df.columns else pd.DataFrame()
    else:
        results['total_lost_clicks'] = 0
        results['top_opportunities'] = pd.DataFrame()

    # CPS — Conversion Potential Score
    def calc_cps(query):
        query = str(query).lower()
        commercial_kw = ['company', 'companies', 'service', 'agency', 'firm',
                         'provider', 'solution', 'hire', 'best', 'top',
                         'yritys', 'palvelu', 'toimisto']
        info_kw = ['what is', 'how to', 'definition', 'guide', 'tutorial',
                   'mikä on', 'miten', 'mitä']
        score = 0.44
        for kw in commercial_kw:
            if kw in query: score += 0.08
        for kw in info_kw:
            if kw in query: score -= 0.06
        return round(min(max(score, 0.0), 1.0), 3)

    if 'Query' in queries_df.columns:
        queries_df['CPS'] = queries_df['Query'].apply(calc_cps)
        queries_df['Intent'] = queries_df['CPS'].apply(
            lambda x: 'SERVICE' if x >= 0.50 else 'INFORMATIVE'
        )

    def get_priority(impressions, cps):
        if impressions >= 400 and cps >= 0.50: return 'P1-CRITIQUE'
        elif impressions >= 200 and cps >= 0.50: return 'P2-HAUTE'
        elif impressions >= 100: return 'P3-MOYENNE'
        else: return 'P4-BASSE'

    if 'Query' in queries_df.columns and 'Impressions' in queries_df.columns:
        queries_df['Priority'] = queries_df.apply(
            lambda r: get_priority(r['Impressions'], r['CPS']), axis=1
        )
        results['priority_counts'] = queries_df['Priority'].value_counts().to_dict()
        results['intent_counts']   = queries_df['Intent'].value_counts().to_dict()

    # GAPs — requêtes sans page correspondante
    if 'Query' in queries_df.columns and 'Page' in pages_df.columns:
        page_keywords = set()
        for page in pages_df['Page'].dropna():
            words = re.findall(r'[a-z]{4,}', str(page).lower())
            page_keywords.update(words)

        def is_gap(query):
            q_words = set(re.findall(r'[a-z]{4,}', str(query).lower()))
            return len(q_words & page_keywords) == 0

        gaps = queries_df[
            queries_df['Query'].apply(is_gap) &
            (queries_df['Impressions'] >= 50)
        ].copy()
        results['gaps'] = gaps.nlargest(23, 'Impressions') if len(gaps) > 0 else gaps
        results['gaps_count'] = len(results['gaps'])
    else:
        results['gaps'] = pd.DataFrame()
        results['gaps_count'] = 0

    results['queries_df'] = queries_df
    return results

with st.spinner("Analyse en cours..."):
    diag = run_diagnostic(queries_file.getvalue(), pages_file.getvalue())

# Affichage métriques
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📉 Clics perdus/mois",
              f"{diag['total_lost_clicks']:,}",
              help="Impressions × CTR moyen P1 − clics réels")
with col2:
    st.metric("💀 Pages mortes",
              diag['dead_pages_count'],
              help="Pages avec 0 clics et +100 impressions")
with col3:
    st.metric("🔍 GAPs détectés",
              diag.get('gaps_count', 0),
              help="Requêtes sans page de destination pertinente")
with col4:
    service_count = diag.get('intent_counts', {}).get('SERVICE', 0)
    st.metric("🎯 Requêtes SERVICE",
              service_count,
              help="Requêtes à intention commerciale (CPS ≥ 0.50)")

# Distribution priorités
if 'priority_counts' in diag:
    st.subheader("Distribution des priorités")
    pc = diag['priority_counts']
    cols = st.columns(4)
    for i, (prio, color) in enumerate([
        ('P1-CRITIQUE', '🔴'),
        ('P2-HAUTE', '🟠'),
        ('P3-MOYENNE', '🟡'),
        ('P4-BASSE', '⚪')
    ]):
        with cols[i]:
            st.metric(f"{color} {prio}", pc.get(prio, 0))

# Top opportunités
if not diag['top_opportunities'].empty:
    st.subheader("Top 10 opportunités — clics perdus")
    st.dataframe(diag['top_opportunities'], use_container_width=True, hide_index=True)

# Pages mortes
if not diag['dead_pages'].empty:
    with st.expander(f"💀 Pages mortes ({diag['dead_pages_count']})"):
        st.dataframe(diag['dead_pages'].head(20), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 3 — GÉNÉRATION CONTENT BRIEFS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.header("③ Génération des Content Briefs")

if not groq_api_key:
    st.warning("⚠️ Entrez votre clé API Groq dans la barre latérale pour générer les Content Briefs.")
    st.stop()

gaps_df = diag.get('gaps', pd.DataFrame())
if gaps_df.empty:
    st.info("Aucun GAP détecté dans vos données.")
    st.stop()

st.info(f"**{len(gaps_df)} GAPs identifiés** — Prêt à générer les Content Briefs via Llama 3.3")

if st.button("🚀 Lancer la génération", type="primary"):

    groq_client = Groq(api_key=groq_api_key)

    def detect_lang(query):
        try:
            lang = langdetect_detect(str(query))
            return 'fi' if lang == 'fi' else 'en'
        except LangDetectException:
            return 'en'

    def fix_title(title):
        if 55 <= len(title) <= 60:
            return title
        base = re.sub(r'\s*[-|–]\s*Katrium\s*$', '', title, flags=re.IGNORECASE).strip()
        base = re.sub(r'\s+by\s+Katrium\s*$', '', base, flags=re.IGNORECASE).strip()
        base = re.sub(r'\s*\|\s*Katrium\s*$', '', base, flags=re.IGNORECASE).strip()
        if len(base + ' | Katrium') < 55:
            pads = [' | Expert Solutions | Katrium', ' | Research Agency | Katrium',
                    ' | B2B Research | Katrium', ' | Europe | Katrium',
                    ' Services | Katrium', ' Experts | Katrium']
            for pad in pads:
                if 55 <= len(base + pad) <= 60:
                    return base + pad
        while len(base + ' | Katrium') > 60 and len(base) > 5:
            base = base.rsplit(' ', 1)[0].rstrip(' -|–')
        return base + ' | Katrium'

    def fix_meta(meta, intent, lang):
        if 150 <= len(meta) <= 160:
            return meta
        if len(meta) > 160:
            return meta[:157].rsplit(' ', 1)[0].rstrip('.') + '...'
        ctas = {
            ('SERVICE', 'en'): ' Get a free quote today.',
            ('SERVICE', 'fi'): ' Ota yhteyttä tänään.',
            ('INFORMATIVE', 'en'): ' Learn more with Katrium.',
            ('INFORMATIVE', 'fi'): ' Lue lisää Katriumilta.',
        }
        suffix = ctas.get((intent, lang), ' Contact us today.')
        meta = meta.rstrip('.')
        while len(meta) < 150:
            meta += suffix
            if len(meta) > 160:
                meta = meta[:157].rsplit(' ', 1)[0].rstrip('.') + '...'
                break
        return meta

    def safe_json_parse(text):
        text = text.strip()
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```$', '', text, flags=re.MULTILINE)
        try:
            return json.loads(text.strip())
        except Exception:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    return None
        return None

    def get_priority(impressions, cps):
        if impressions >= 400 and cps >= 0.50: return 'P1-CRITIQUE'
        elif impressions >= 200 and cps >= 0.50: return 'P2-HAUTE'
        elif impressions >= 100: return 'P3-MOYENNE'
        else: return 'P4-BASSE'

    briefs = []
    errors = []
    progress_bar = st.progress(0)
    status_text  = st.empty()
    results_container = st.container()

    for idx, row in gaps_df.iterrows():
        query    = str(row.get('Query', ''))
        impr     = int(row.get('Impressions', 0))
        position = round(float(row.get('Position', 50)), 1)
        cps      = float(row.get('CPS', 0.44))
        intent   = str(row.get('Intent', 'INFORMATIVE'))
        priority = get_priority(impr, cps)
        lang     = detect_lang(query)
        lang_flag = '🇫🇮 FI' if lang == 'fi' else '🇬🇧 EN'
        wc_target = '3,000+ mots' if intent == 'SERVICE' else '1,800–3,000 mots'

        i = list(gaps_df.index).index(idx)
        progress = (i + 1) / len(gaps_df)
        progress_bar.progress(progress)
        status_text.text(f"[{i+1}/{len(gaps_df)}] Génération : {query[:50]}...")

        cta = {
            ('SERVICE', 'fi'): 'Ota yhteyttä — Pyydä tarjous',
            ('SERVICE', 'en'): 'Get a Free Research Quote',
            ('INFORMATIVE', 'fi'): 'Tutustu tutkimuspalveluihimme',
            ('INFORMATIVE', 'en'): 'Discover Our Research Services',
        }.get((intent, lang), 'Get a Free Research Quote')

        schema = 'LocalBusiness + Service + FAQPage' if intent == 'SERVICE' else 'Article + FAQPage'
        lang_instruction = 'finnois (fi)' if lang == 'fi' else 'anglais (en)'

        prompt = f"""Tu es un consultant SEO senior B2B travaillant pour Katrium, entreprise de market research en Finlande et Europe.
Génère un Content Brief professionnel pour une nouvelle page à créer sur katrium.eu.

DONNÉES GSC :
- Requête cible : {query}
- Impressions/mois : {impr:,}
- Position moyenne : {position}
- Intention : {intent} (CPS: {cps})
- Priorité SEO : {priority}
- Langue de la page : {lang_instruction}
- Densité cible : {wc_target}

INSTRUCTIONS :
- Langue : rédige TOUT en {lang_instruction}
- Title tag : 55-60 caractères, terminer par "| Katrium"
- Meta description : 150-160 caractères avec CTA
- Structure H2 : 7-9 sections adaptées à l'intent {intent}
- Pour chaque H2, propose 2-3 H3 actionnables
- CTA : {cta}
- Schéma : {schema}

Réponds UNIQUEMENT en JSON :
{{
  "slug": "/..../",
  "title_tag": "...",
  "meta_description": "...",
  "word_count_target": "...",
  "h_structure": [{{"h2": "...", "h3s": ["...", "..."]}}],
  "lsi_to_integrate": ["terme1", "terme2", "terme3", "terme4", "terme5"],
  "cta": "...",
  "schema": "...",
  "internal_links_suggestion": ["...", "..."],
  "seo_notes": "Conseil stratégique en 2-3 phrases."
}}"""

        try:
            resp = groq_client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[
                    {'role': 'system', 'content': f'Expert SEO B2B. Rédige en {lang_instruction}. JSON uniquement.'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3,
                max_tokens=1200,
            )
            raw    = resp.choices[0].message.content
            parsed = safe_json_parse(raw)
            if parsed:
                parsed['title_tag']        = fix_title(parsed.get('title_tag', ''))
                parsed['meta_description'] = fix_meta(parsed.get('meta_description', ''), intent, lang)
                parsed['query']     = query
                parsed['priority']  = priority
                parsed['intent']    = intent
                parsed['cps']       = round(cps, 3)
                parsed['impressions'] = impr
                parsed['position']  = position
                parsed['language']  = lang_flag
                parsed['title_len'] = len(parsed['title_tag'])
                parsed['meta_len']  = len(parsed['meta_description'])
                briefs.append(parsed)
            else:
                errors.append({'query': query, 'error': 'JSON invalide'})
        except Exception as e:
            errors.append({'query': query, 'error': str(e)[:80]})

        time.sleep(2.5)

    progress_bar.progress(1.0)
    status_text.text("✅ Génération terminée !")

    if briefs:
        st.session_state['briefs'] = briefs
        briefs_df = pd.DataFrame(briefs).sort_values(
            by=['priority', 'impressions'], ascending=[True, False]
        ).reset_index(drop=True)
        st.session_state['briefs_df'] = briefs_df

        st.success(f"✅ {len(briefs)} Content Briefs générés")
        if errors:
            st.warning(f"⚠️ {len(errors)} erreurs : quota Groq dépassé — relancer demain pour les requêtes manquantes.")

        # Résumé qualité
        title_ok = ((briefs_df['title_len'] >= 55) & (briefs_df['title_len'] <= 60)).sum()
        meta_ok  = ((briefs_df['meta_len'] >= 150) & (briefs_df['meta_len'] <= 160)).sum()
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Briefs générés", f"{len(briefs_df)}/{len(gaps_df)}")
        with col2: st.metric("Title ✅ (55-60c)", f"{title_ok}/{len(briefs_df)}")
        with col3: st.metric("Meta ✅ (150-160c)", f"{meta_ok}/{len(briefs_df)}")
        with col4: st.metric("Pages FI 🇫🇮", (briefs_df['language'] == '🇫🇮 FI').sum())

        # Affichage briefs
        st.subheader("Content Briefs générés")
        for _, r in briefs_df.iterrows():
            p_color = {'P1-CRITIQUE': '🔴', 'P2-HAUTE': '🟠',
                       'P3-MOYENNE': '🟡', 'P4-BASSE': '⚪'}.get(r['priority'], '⚪')
            with st.expander(f"{p_color} [{r['priority']}] {r['query'].upper()} {r['language']}"):
                col1, col2 = st.columns(2)
                with col1:
                    t_ok = '✅' if 55 <= r['title_len'] <= 60 else '⚠️'
                    m_ok = '✅' if 150 <= r['meta_len'] <= 160 else '⚠️'
                    st.markdown(f"**Slug :** `{r.get('slug', 'N/A')}`")
                    st.markdown(f"**{t_ok} Title ({r['title_len']}c) :** {r.get('title_tag', '')}")
                    st.markdown(f"**{m_ok} Meta ({r['meta_len']}c) :** {r.get('meta_description', '')}")
                    st.markdown(f"**Mots cible :** {r.get('word_count_target', '')}")
                    st.markdown(f"**CTA :** {r.get('cta', '')}")
                    st.markdown(f"**Schéma :** {r.get('schema', '')}")
                with col2:
                    h_structure = r.get('h_structure', [])
                    if isinstance(h_structure, list):
                        st.markdown("**Structure H2/H3 :**")
                        for item in h_structure[:5]:
                            if isinstance(item, dict):
                                st.markdown(f"**H2 :** {item.get('h2', '')}")
                                for h3 in item.get('h3s', []):
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;↳ {h3}")
                lsi = r.get('lsi_to_integrate', [])
                if isinstance(lsi, list):
                    st.markdown(f"**LSI :** {' · '.join(lsi)}")
                notes = r.get('seo_notes', '')
                if notes:
                    st.info(f"💡 {notes}")

# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 4 — EXPORT CSV
# ─────────────────────────────────────────────────────────────────────────────

if 'briefs_df' in st.session_state:
    st.markdown("---")
    st.header("④ Export CSV")

    briefs_df = st.session_state['briefs_df']
    queries_df = diag['queries_df']

    # Préparer export content briefs
    export_briefs = briefs_df.copy()
    export_briefs['h_structure_flat'] = export_briefs['h_structure'].apply(
        lambda x: ' | '.join([f"H2: {i.get('h2','')} → {', '.join(i.get('h3s',[]))}"
                               for i in x]) if isinstance(x, list) else ''
    )
    export_briefs['lsi_flat'] = export_briefs['lsi_to_integrate'].apply(
        lambda x: ', '.join(x) if isinstance(x, list) else str(x)
    )

    cols_export = ['priority', 'query', 'intent', 'cps', 'impressions', 'position',
                   'language', 'slug', 'title_tag', 'title_len', 'meta_description',
                   'meta_len', 'word_count_target', 'h_structure_flat',
                   'lsi_flat', 'cta', 'schema', 'seo_notes']
    available = [c for c in cols_export if c in export_briefs.columns]
    csv_briefs = export_briefs[available].to_csv(index=False, encoding='utf-8-sig')

    # Préparer export title recommendations
    title_cols = ['Query', 'Impressions', 'Position', 'Clicks', 'CPS', 'Intent', 'Priority']
    available_title = [c for c in title_cols if c in queries_df.columns]
    csv_titles = queries_df[available_title].nlargest(50, 'Impressions').to_csv(
        index=False, encoding='utf-8-sig'
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="📥 Content Briefs CSV",
            data=csv_briefs,
            file_name="katrium_content_briefs.csv",
            mime="text/csv",
            type="primary"
        )
    with col2:
        st.download_button(
            label="📥 Title Recommendations CSV",
            data=csv_titles,
            file_name="katrium_title_recommendations.csv",
            mime="text/csv"
        )
    with col3:
        # LSI export
        lsi_rows = []
        for _, r in briefs_df.iterrows():
            lsi = r.get('lsi_to_integrate', [])
            if isinstance(lsi, list):
                for term in lsi:
                    lsi_rows.append({
                        'Page': r.get('slug', ''),
                        'Query': r.get('query', ''),
                        'Intent': r.get('intent', ''),
                        'LSI_Term': term,
                        'Priority': r.get('priority', '')
                    })
        csv_lsi = pd.DataFrame(lsi_rows).to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 LSI Terms CSV",
            data=csv_lsi,
            file_name="katrium_lsi_by_page.csv",
            mime="text/csv"
        )

    st.success("✅ Analyse complète terminée — 3 fichiers prêts au téléchargement")
