"""
app.py — SISTA QC : Plateforme de Controle Qualite automatise des enquetes.
Moteur IA — API1 ou API2 au choix de l'utilisateur.
Lancer : streamlit run app.py
"""

import os
import io
import html as html_lib
import base64
import tempfile
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------
#  Chargement des cles API depuis le fichier .env (a la racine du projet)
# ----------------------------------------------------------------------

def _load_env_file():
    """Lit un fichier .env simple (KEY=VALUE) et injecte dans os.environ."""
    env_path = ".env"
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value:
                    os.environ.setdefault(key, value)
    except Exception:
        pass


_load_env_file()

from core.loader import load_file
from core.profiler import profile_dataset
from core.qc_basic import run_basic_qc, build_enqueteur_summary, global_stats
from core import ai_agent

# ----------------------------------------------------------------------
#  Configuration
# ----------------------------------------------------------------------

st.set_page_config(page_title="SISTA QC — Controle Qualite",
                   page_icon="logo_sista.png", layout="wide",
                   initial_sidebar_state="collapsed")

NAVY = "#13263D"
NAVY_DEEP = "#0D1B2C"
GOLD = "#EFC71A"
GOLD_DEEP = "#D4AC0D"
GREEN = "#10B981"
GREEN_SOFT = "#ECFDF5"
GREEN_DARK = "#065F46"
RED = "#EF4444"
RED_SOFT = "#FEE2E2"
RED_DARK = "#991B1B"
ORANGE = "#F97316"
ORANGE_SOFT = "#FFEDD5"
ORANGE_DARK = "#9A3412"
BLUE = "#3B82F6"
BLUE_SOFT = "#DBEAFE"
BLUE_DARK = "#1E40AF"
PURPLE = "#8B5CF6"
PURPLE_SOFT = "#EDE9FE"
PURPLE_DARK = "#5B21B6"
TEAL = "#14B8A6"
TEAL_SOFT = "#CCFBF1"
TEAL_DARK = "#115E59"
GRAY = "#6B7280"
GRAY_SOFT = "#F3F4F6"
BORDER = "#E5E7EB"


def _logo_b64():
    if os.path.exists("logo_sista.png"):
        with open("logo_sista.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


LOGO = _logo_b64()

# ----------------------------------------------------------------------
#  CSS
# ----------------------------------------------------------------------

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Spline+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

  html, body, [class*="css"] {{ font-family: 'Spline Sans', sans-serif; }}
  h1,h2,h3,h4 {{ font-family: 'Sora', sans-serif; }}

  section[data-testid="stSidebar"] {{ display: none !important; }}
  [data-testid="collapsedControl"] {{ display: none !important; }}
  #MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}

  .stApp {{ background: #F4F7FA; }}
  .block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px;
  }}

  /* HEADER */
  .top-header {{
    background: linear-gradient(115deg, {NAVY_DEEP} 0%, {NAVY} 60%, #1E3A5C 120%);
    border-radius: 14px; padding: 18px 28px; margin-bottom: 20px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 8px 24px rgba(13,27,44,0.18);
  }}
  .top-header-left {{ display: flex; align-items: center; gap: 18px; }}
  .top-header img {{ height: 54px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.25)); }}
  .top-header .divider {{ width: 1px; height: 42px; background: rgba(255,255,255,0.22); }}
  .top-header h1 {{
    color: #fff; font-size: 1.45rem; margin: 0;
    font-weight: 800; letter-spacing: -0.01em;
  }}
  .top-header h1 span {{ color: {GOLD}; }}
  .top-header .subtitle {{
    color: rgba(255,255,255,0.65); font-size: 0.72rem; margin: 3px 0 0;
    text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500;
  }}
  .api-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 16px; border-radius: 20px;
    font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.82rem;
    border: 1px solid rgba(255,255,255,0.15);
  }}
  .api-badge.active {{ background: rgba(16,185,129,0.15); color: #6EE7B7; }}
  .api-badge.inactive {{ background: rgba(239,68,68,0.12); color: #FCA5A5; }}
  .api-badge .dot {{ width: 8px; height: 8px; border-radius: 50%; }}
  .api-badge.active .dot {{ background: #10B981; }}
  .api-badge.inactive .dot {{ background: #EF4444; }}

  /* STEPPER */
  .stepper {{
    background: #fff; border-radius: 14px; padding: 20px 28px; margin-bottom: 20px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 2px 10px rgba(13,27,44,0.05); border: 1px solid {BORDER};
  }}
  .step-item {{ display: flex; align-items: center; gap: 12px; flex: 0 0 auto; }}
  .step-circle {{
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.95rem;
  }}
  .step-active .step-circle {{ background: {NAVY}; color: #fff; }}
  .step-done .step-circle {{ background: {GREEN}; color: #fff; }}
  .step-todo .step-circle {{ background: {GRAY_SOFT}; color: {GRAY}; }}
  .step-label {{ font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.95rem; }}
  .step-active .step-label {{ color: {NAVY}; }}
  .step-done .step-label {{ color: {GREEN}; }}
  .step-todo .step-label {{ color: {GRAY}; }}
  .step-line {{ flex: 1; height: 2px; background: {BORDER}; margin: 0 16px; }}
  .step-line.done {{ background: {GREEN}; }}

  /* Boutons de navigation du stepper : visibles mais discrets */
  div[data-testid="column"] button[kind="secondary"][data-testid*="navstep"],
  button[data-testid^="stBaseButton-secondary"][aria-label*=" a"] {{
    background: transparent !important;
    color: {NAVY} !important;
    border: 1px dashed {BORDER} !important;
    font-size: 0.78rem !important;
    padding: 6px 12px !important;
    opacity: 0.65;
  }}

  /* ALERTE */
  .alert-error {{
    background: {RED_SOFT}; border: 1px solid #FECACA; border-radius: 12px;
    padding: 16px 20px; margin-bottom: 20px;
  }}
  .alert-error .content {{ color: {RED_DARK}; font-size: 0.88rem; word-break: break-word; }}

  /* CARD */
  .main-card {{
    background: #fff; border-radius: 14px; padding: 28px 32px;
    box-shadow: 0 2px 14px rgba(13,27,44,0.06); border: 1px solid {BORDER};
    margin-bottom: 20px;
  }}
  .main-card h3 {{ color: {NAVY}; margin: 0 0 6px; font-size: 1.2rem; font-weight: 700; }}
  .main-card .desc {{ color: {GRAY}; font-size: 0.9rem; margin: 0 0 22px; }}

  /* UPLOAD */
  .upload-zone {{
    border: 2px dashed {BORDER}; border-radius: 14px; padding: 32px 24px;
    text-align: center; background: #FAFBFC; margin-bottom: 14px;
  }}
  .upload-zone.required {{ border-color: {GREEN}; background: {GREEN_SOFT}; }}
  .upload-zone.filled {{ border-color: {GREEN}; background: {GREEN_SOFT}; border-style: solid; }}
  .upload-icon {{
    width: 56px; height: 56px; border-radius: 14px; margin: 0 auto 14px;
    display: flex; align-items: center; justify-content: center; font-size: 1.7rem;
  }}
  .upload-icon.green {{ background: rgba(16,185,129,0.15); color: {GREEN}; }}
  .upload-icon.gold  {{ background: rgba(212,172,13,0.15); color: {GOLD_DEEP}; }}
  .upload-title {{ font-weight: 700; font-size: 1.05rem; color: {NAVY}; margin: 0 0 4px; }}
  .upload-hint {{ color: {GRAY}; font-size: 0.82rem; margin: 0 0 10px; }}
  .upload-badge {{
    display: inline-block; padding: 4px 12px; border-radius: 12px;
    font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.7rem;
    text-transform: uppercase;
  }}
  .upload-badge.required {{ background: rgba(16,185,129,0.18); color: {GREEN_DARK}; }}
  .upload-badge.optional {{ background: rgba(212,172,13,0.18); color: {NAVY}; }}
  .upload-filename {{ margin-top: 12px; font-size: 0.85rem; color: {NAVY}; font-weight: 500; }}
  .upload-meta {{ font-size: 0.78rem; color: {GRAY}; }}

  [data-testid="stFileUploaderDropzone"] {{
    background: #fff; border: 1.5px solid {BORDER}; border-radius: 10px;
    padding: 8px; min-height: auto;
  }}
  [data-testid="stFileUploaderDropzone"] button {{
    background: {NAVY} !important; color: #fff !important;
    border-radius: 8px !important; font-weight: 600 !important;
  }}

  /* INPUTS */
  .stTextInput input, .stNumberInput input, .stTextArea textarea {{
    background: #fff; border: 1.5px solid {BORDER}; border-radius: 10px;
    padding: 10px 14px;
  }}
  .stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {NAVY};
  }}
  .stTextInput label, .stNumberInput label, .stSlider label, .stRadio label,
  .stTextArea label, .stSelectbox label {{
    font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.85rem; color: {NAVY} !important;
  }}

  /* BUTTONS */
  .stButton button {{
    background: {NAVY}; color: #fff !important; border: none; border-radius: 11px;
    font-family: 'Sora', sans-serif; font-weight: 600; padding: 12px 24px;
  }}
  .stButton button:hover {{ background: {NAVY_DEEP}; color: {GOLD} !important; }}

  .stDownloadButton button {{
    background: {GREEN} !important; color: #fff !important; border-radius: 11px;
    font-family: 'Sora', sans-serif; font-weight: 600;
  }}
  .stDownloadButton button:hover {{ background: {GREEN_DARK} !important; }}

  /* METRICS */
  .mcard {{
    border-radius: 14px; padding: 18px 20px; color: #fff;
    position: relative; overflow: hidden;
  }}
  .mcard .v {{ font-family: 'Sora', sans-serif; font-size: 1.9rem; font-weight: 800; line-height: 1; }}
  .mcard .l {{ font-size: 0.78rem; opacity: 0.92; margin-top: 6px; font-weight: 500; }}
  .m-navy {{ background: linear-gradient(135deg, #1E3A5C, {NAVY}); }}
  .m-gold {{ background: linear-gradient(135deg, #F3D44E, {GOLD_DEEP}); color: {NAVY}; }}
  .m-gold .v {{ color: {NAVY}; }}
  .m-red  {{ background: linear-gradient(135deg, #F26172, #C9303F); }}
  .m-green{{ background: linear-gradient(135deg, #2BD39A, #16A077); }}
  .m-blue {{ background: linear-gradient(135deg, #4FA3E0, #2E75B6); }}
  .m-purple {{ background: linear-gradient(135deg, #A78BFA, #7C3AED); }}

  /* TABLEAU APERCU COLORE */
  .var-table {{
    background: #fff; border-radius: 12px; overflow: hidden;
    border: 1px solid {BORDER}; box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    margin-bottom: 16px;
  }}
  .var-table table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  .var-table thead tr {{ background: linear-gradient(135deg, #F1F5F9, #E2E8F0); }}
  .var-table th {{
    padding: 12px 14px; text-align: left; font-family: 'Sora', sans-serif;
    font-weight: 700; font-size: 0.75rem; text-transform: uppercase;
    letter-spacing: 0.05em; color: {NAVY}; border-bottom: 2px solid {BORDER};
  }}
  .var-table td {{ padding: 10px 14px; border-bottom: 1px solid {BORDER}; vertical-align: middle; }}
  .var-table tbody tr:hover {{ background: #FAFBFC; }}
  .var-table tbody tr:last-child td {{ border-bottom: none; }}

  .var-name {{
    display: inline-block; background: {BLUE_SOFT}; color: {BLUE_DARK};
    padding: 4px 10px; border-radius: 6px;
    font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 0.82rem;
  }}
  .type-badge {{
    display: inline-block; padding: 3px 10px; border-radius: 6px;
    font-size: 0.74rem; font-weight: 600;
  }}
  .type-numeric    {{ background: {ORANGE_SOFT}; color: {ORANGE_DARK}; }}
  .type-text       {{ background: {PURPLE_SOFT}; color: {PURPLE_DARK}; }}
  .type-date       {{ background: {TEAL_SOFT}; color: {TEAL_DARK}; }}
  .type-categorical{{ background: #FCE7F3; color: #9D174D; }}
  .type-boolean    {{ background: #FEF3C7; color: #92400E; }}
  .type-other      {{ background: {GRAY_SOFT}; color: {GRAY}; }}

  .fill-badge {{
    display: inline-block; padding: 3px 10px; border-radius: 6px;
    font-size: 0.78rem; font-weight: 600; min-width: 50px; text-align: center;
  }}
  .fill-high {{ background: {GREEN_SOFT}; color: {GREEN_DARK}; }}
  .fill-mid  {{ background: {ORANGE_SOFT}; color: {ORANGE_DARK}; }}
  .fill-low  {{ background: {RED_SOFT}; color: {RED_DARK}; }}

  .var-legend {{
    display: flex; gap: 14px; flex-wrap: wrap; padding: 10px 16px;
    background: #F8FAFC; border-radius: 10px; margin-bottom: 14px;
    font-size: 0.78rem; color: {GRAY};
  }}
  .var-legend .item {{ display: inline-flex; align-items: center; gap: 6px; }}
  .var-legend .swatch {{
    display: inline-block; width: 12px; height: 12px; border-radius: 3px;
  }}

  /* CARTES CAS DETECTES */
  .cas-grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 14px; margin-top: 14px;
  }}
  .cas-card {{
    background: #fff; border: 1px solid {BORDER}; border-radius: 12px;
    padding: 14px 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    transition: all 0.2s;
  }}
  .cas-card:hover {{ box-shadow: 0 4px 14px rgba(0,0,0,0.08); transform: translateY(-1px); }}
  .cas-card.high {{ border-left: 4px solid {RED}; }}
  .cas-card.med  {{ border-left: 4px solid {ORANGE}; }}
  .cas-card.low  {{ border-left: 4px solid {BLUE}; }}

  .cas-header {{
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 10px;
  }}
  .cas-severity {{
    display: inline-block; padding: 3px 10px; border-radius: 6px;
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
  }}
  .cas-severity.high {{ background: {RED_SOFT}; color: {RED_DARK}; }}
  .cas-severity.med  {{ background: {ORANGE_SOFT}; color: {ORANGE_DARK}; }}
  .cas-severity.low  {{ background: {BLUE_SOFT}; color: {BLUE_DARK}; }}
  .cas-ligne {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;
    color: {GRAY}; font-weight: 500;
  }}
  .cas-titre {{
    font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.95rem;
    color: {NAVY}; margin: 0 0 10px;
  }}
  .cas-valeurs {{
    background: {GRAY_SOFT}; border-radius: 8px; padding: 10px 12px;
    margin-bottom: 10px; font-size: 0.82rem;
  }}
  .cas-valeur-row {{ display: flex; justify-content: space-between; padding: 3px 0; }}
  .cas-valeur-key {{
    color: {GRAY}; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;
  }}
  .cas-valeur-val {{ color: {NAVY}; font-weight: 600; }}
  .cas-explain {{
    font-size: 0.78rem; color: {GRAY}; margin: 0 0 6px; line-height: 1.5;
  }}
  .cas-explain strong {{ color: {NAVY}; }}
  .cas-enqueteur {{
    margin-top: 10px; padding-top: 10px; border-top: 1px solid {BORDER};
    font-size: 0.8rem; color: {NAVY}; font-weight: 600;
  }}
  .cas-enqueteur span.label {{ color: {GRAY}; font-weight: 500; font-size: 0.75rem; }}

  /* Carte API selector */
  .api-selector {{
    background: #F8FAFC; border-radius: 10px; padding: 14px 18px;
    margin-bottom: 16px; border: 1px solid {BORDER};
  }}

  .qc-card {{
    background: #fff; border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
    border-left: 5px solid #2E75B6; box-shadow: 0 2px 6px rgba(20,51,82,0.05);
  }}
  .qc-card.high {{ border-left-color: {RED}; }}
  .qc-card.med  {{ border-left-color: {GOLD}; }}
  .qc-card.low  {{ border-left-color: {BLUE}; }}
  .qc-card.ok   {{ border-left-color: {GREEN}; }}

  .stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: transparent; }}
  .stTabs [data-baseweb="tab"] {{
    background: #fff; border-radius: 11px 11px 0 0; padding: 10px 18px;
    font-family: 'Sora', sans-serif; font-weight: 600;
    border: 1px solid {BORDER}; border-bottom: none;
  }}
  .stTabs [aria-selected="true"] {{ background: {NAVY}; color: #fff !important; }}

  h2, h3 {{ color: {NAVY}; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
#  Etat de session
# ----------------------------------------------------------------------

ss = st.session_state
for key in ["loaded", "profile", "results", "mp",
            "ai_results", "ai_comment", "ai_metrics",
            "data_file_obj", "dict_file_obj", "form_file_obj", "api_error",
            "api1_status", "api2_status"]:
    ss.setdefault(key, None)

ss.setdefault("params", {"duree_min": 18, "iqr_k": 1.5, "missing_seuil": 50})
ss.setdefault("survey_type", "")
ss.setdefault("survey_description", "")
ss.setdefault("survey_population", "")
ss.setdefault("survey_eligibility", "")
ss.setdefault("api1_key", os.environ.get("ANTHROPIC_API_KEY", ""))
ss.setdefault("api2_key", os.environ.get("GROQ_API_KEY", ""))
ss.setdefault("selected_api", "api1")
ss.setdefault("current_step", 1)

# ----------------------------------------------------------------------
#  HEADER
# ----------------------------------------------------------------------

api1_active = bool(ss.api1_key) and ss.api1_key.startswith("sk-ant-")
api2_active = bool(ss.api2_key) and ss.api2_key.startswith("gsk_")
any_active = api1_active or api2_active
badge_cls = "active" if any_active else "inactive"
badge_txt = "IA active" if any_active else "IA inactive"

logo_html = f'<img src="data:image/png;base64,{LOGO}" alt="SISTA"/>' if LOGO else ''

st.markdown(f"""
<div class="top-header">
  <div class="top-header-left">
    {logo_html}
    <div class="divider"></div>
    <div>
      <h1>Controle Qualite <span>QC</span></h1>
      <div class="subtitle">SISTA Consult Mauritanie</div>
    </div>
  </div>
  <div class="api-badge {badge_cls}">
    <span class="dot"></span> {badge_txt}
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
#  STEPPER
# ----------------------------------------------------------------------

STEPS = [(1, "Importer"), (2, "Detecter"), (3, "Rapport QC")]


def step_status(idx):
    if idx == ss.current_step: return "step-active"
    elif idx < ss.current_step: return "step-done"
    else: return "step-todo"


stepper_html = '<div class="stepper">'
for i, (num, label) in enumerate(STEPS):
    cls = step_status(num)
    circle_content = "v" if cls == "step-done" else str(num)
    stepper_html += (
        f'<div class="step-item {cls}">'
        f'<div class="step-circle">{circle_content}</div>'
        f'<div class="step-label">{label}</div>'
        f'</div>'
    )
    if i < len(STEPS) - 1:
        line_cls = "done" if num < ss.current_step else ""
        stepper_html += f'<div class="step-line {line_cls}"></div>'
stepper_html += '</div>'
st.markdown(stepper_html, unsafe_allow_html=True)

# Boutons de navigation (cacher mais cliquables via colonnes etroites)
nav_cols = st.columns(3)
for i, (num, label) in enumerate(STEPS):
    with nav_cols[i]:
        if st.button(f"  {label}", key=f"navstep_{num}",
                     use_container_width=True):
            ss.current_step = num
            st.rerun()

# Bandeau info colore selon l'etape courante
INFO_BANDS = {
    1: {
        "icon": "📂",
        "title": "Etape 1 — Importer",
        "msg": "Pour de meilleurs resultats, importez aussi le dictionnaire des variables et remplissez la description de l'enquete. L'IA pourra ainsi mieux comprendre le contexte metier.",
        "grad": "linear-gradient(135deg, #EEEDFE 0%, #E1F5EE 50%, #FAEEDA 100%)",
        "icon_bg": "#3C3489",
    },
    2: {
        "icon": "🔍",
        "title": "Etape 2 — Detecter",
        "msg": "Trois onglets disponibles : Apercu (profilage colore), QC basique (tests automatiques) et QC intelligent (regles generees par l'IA). Tous les resultats peuvent etre exportes.",
        "grad": "linear-gradient(135deg, #E6F1FB 0%, #EAF3DE 50%, #FAEEDA 100%)",
        "icon_bg": "#0C447C",
    },
    3: {
        "icon": "📊",
        "title": "Etape 3 — Rapport QC",
        "msg": "Classement des enqueteurs selon le nombre et la gravite des anomalies. Ce bilan vous aide a identifier les agents a former ou a remplacer en priorite.",
        "grad": "linear-gradient(135deg, #FAEEDA 0%, #FCEBEB 50%, #EEEDFE 100%)",
        "icon_bg": "#A32D2D",
    },
}
band = INFO_BANDS.get(ss.current_step, INFO_BANDS[1])
st.markdown(f"""
<div style="background:{band['grad']};
            border-radius:14px; padding:14px 20px; margin:8px 0 20px 0;
            border:1px solid {BORDER};
            display:flex; align-items:center; gap:16px;
            box-shadow:0 2px 8px rgba(13,27,44,0.04);">
  <div style="background:{band['icon_bg']}; color:#fff; border-radius:10px;
              width:48px; height:48px; display:flex; align-items:center;
              justify-content:center; flex-shrink:0; font-size:22px;
              box-shadow:0 3px 8px rgba(0,0,0,0.15);">
    {band['icon']}
  </div>
  <div style="flex:1;">
    <p style="font-family:'Sora',sans-serif; font-size:14px; font-weight:700;
              color:{NAVY}; margin:0 0 2px;">{band['title']}</p>
    <p style="font-size:13px; color:#5F5E5A; margin:0; line-height:1.5;">{band['msg']}</p>
  </div>
</div>
""", unsafe_allow_html=True)

if ss.api_error:
    st.markdown(f'<div class="alert-error"><div class="content">{html_lib.escape(str(ss.api_error))}</div></div>',
                unsafe_allow_html=True)


# ----------------------------------------------------------------------
#  Utilitaires
# ----------------------------------------------------------------------

def _save_upload(uploaded):
    suffix = os.path.splitext(uploaded.name)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getbuffer())
    tmp.close()
    return tmp.name


def metric(col, cls, val, lab):
    col.markdown(f'<div class="mcard {cls}"><div class="v">{val}</div>'
                 f'<div class="l">{lab}</div></div>', unsafe_allow_html=True)


def divider(icon="◆"):
    """Separateur visuel elegant : ligne degradee avec icone centrale."""
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:14px;
                margin:14px 0; padding:0 4px;">
      <div style="flex:1; height:2px;
                  background:linear-gradient(90deg,
                    transparent 0%,
                    {GOLD} 30%,
                    {NAVY} 60%,
                    {PURPLE} 100%);
                  border-radius:2px; opacity:0.55;"></div>
      <div style="color:{GOLD_DEEP}; font-size:14px; font-weight:700;
                  background:#fff; padding:4px 10px; border-radius:50%;
                  border:1.5px solid {GOLD};
                  box-shadow:0 2px 6px rgba(212,172,13,0.15);">
        {icon}
      </div>
      <div style="flex:1; height:2px;
                  background:linear-gradient(90deg,
                    {PURPLE} 0%,
                    {NAVY} 40%,
                    {GOLD} 70%,
                    transparent 100%);
                  border-radius:2px; opacity:0.55;"></div>
    </div>
    """, unsafe_allow_html=True)


def fmt_size(n):
    if n < 1024: return f"{n} B"
    if n < 1024 * 1024: return f"{n/1024:.1f} KB"
    return f"{n/1024/1024:.1f} MB"


def _type_class(t):
    t = (t or "").lower()
    if any(k in t for k in ["num", "int", "float", "decimal"]): return "type-numeric"
    if any(k in t for k in ["date", "time", "datetime"]): return "type-date"
    if any(k in t for k in ["cat", "factor", "enum"]): return "type-categorical"
    if any(k in t for k in ["bool", "logical"]): return "type-boolean"
    if any(k in t for k in ["str", "text", "object", "char"]): return "type-text"
    return "type-other"


def _fill_class(rate):
    if rate >= 80: return "fill-high"
    if rate >= 40: return "fill-mid"
    return "fill-low"


def render_var_table(variables):
    def esc(x):
        return html_lib.escape(str(x), quote=True)

    rows = []
    for v in variables:
        name = esc(v["name"])
        label = esc((v["label"] or "")[:60])
        vtype = esc(v["type"])
        fill = v["fill_rate"]
        uniq = v["uniques"]
        examples = esc(", ".join(str(e) for e in v["examples"][:2])[:50])
        type_cls = _type_class(v["type"])
        fill_cls = _fill_class(fill)
        row = (
            f'<tr>'
            f'<td><span class="var-name">{name}</span></td>'
            f'<td style="color:{NAVY};">{label}</td>'
            f'<td><span class="type-badge {type_cls}">{vtype}</span></td>'
            f'<td><span class="fill-badge {fill_cls}">{fill}%</span></td>'
            f'<td style="color:{GRAY}; font-family:\'JetBrains Mono\', monospace; font-size:0.82rem;">{uniq}</td>'
            f'<td style="color:{GRAY}; font-size:0.78rem;">{examples}</td>'
            f'</tr>'
        )
        rows.append(row)

    legend = (
        f'<div class="var-legend">'
        f'<span class="item"><span class="swatch" style="background:{ORANGE_SOFT}"></span> Numerique</span>'
        f'<span class="item"><span class="swatch" style="background:{PURPLE_SOFT}"></span> Texte</span>'
        f'<span class="item"><span class="swatch" style="background:{TEAL_SOFT}"></span> Date</span>'
        f'<span class="item"><span class="swatch" style="background:#FCE7F3"></span> Categoriel</span>'
        f'<span class="item"><span class="swatch" style="background:{GREEN_SOFT}"></span> &gt;=80%</span>'
        f'<span class="item"><span class="swatch" style="background:{ORANGE_SOFT}"></span> 40-80%</span>'
        f'<span class="item"><span class="swatch" style="background:{RED_SOFT}"></span> &lt;40%</span>'
        f'</div>'
    )
    table = (
        '<div class="var-table"><table>'
        '<thead><tr>'
        '<th>Variable</th><th>Libelle</th><th>Type</th>'
        '<th>Remplissage</th><th>Uniques</th><th>Exemples</th>'
        '</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        '</table></div>'
    )
    return legend + table


def render_cas_card(cas, num):
    def esc(x):
        return html_lib.escape(str(x), quote=True)

    sev = cas.get("_severite", "low")
    sev_label = {"high": "Gravite haute", "med": "Gravite moyenne",
                 "low": "Gravite faible"}[sev]

    valeurs_html = ""
    val_dict = cas.get("_valeurs_dict", {})
    if val_dict:
        val_rows = []
        for k, v in val_dict.items():
            val_rows.append(
                f'<div class="cas-valeur-row">'
                f'<span class="cas-valeur-key">{esc(k)}</span>'
                f'<span class="cas-valeur-val">{esc(v)}</span>'
                f'</div>'
            )
        valeurs_html = f'<div class="cas-valeurs">{"".join(val_rows)}</div>'

    pourquoi = esc(cas.get("_pourquoi", ""))
    action = esc(cas.get("_action", ""))
    regle = esc(cas.get("Regle", ""))
    enqueteur = esc(cas.get("Enqueteur", "Inconnu"))
    ligne = cas.get("_index", "?")

    pourquoi_block = (f'<p class="cas-explain"><strong>Pourquoi :</strong> {pourquoi}</p>'
                      if pourquoi else '')
    action_block = (f'<p class="cas-explain"><strong>Action :</strong> {action}</p>'
                    if action else '')

    return (
        f'<div class="cas-card {sev}">'
        f'<div class="cas-header">'
        f'<span class="cas-severity {sev}">{sev_label}</span>'
        f'<span class="cas-ligne">Cas #{num} | Ligne {ligne}</span>'
        f'</div>'
        f'<p class="cas-titre">{regle}</p>'
        f'{valeurs_html}{pourquoi_block}{action_block}'
        f'<div class="cas-enqueteur">'
        f'<span class="label">Enqueteur :</span> {enqueteur}'
        f'</div>'
        f'</div>'
    )


def build_export_excel(cas_list, rules):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if cas_list:
            df_cas = pd.DataFrame([{
                "Cas N": i + 1,
                "Ligne": c["_index"],
                "Gravite": {"high": "Haute", "med": "Moyenne",
                            "low": "Faible"}.get(c["_severite"], ""),
                "Enqueteur": c["Enqueteur"],
                "Regle": c["Regle"],
                "Colonnes concernees": c["Colonnes_concernees"],
                "Valeurs en cause": c["Valeurs"],
                "Pourquoi": c.get("_pourquoi", ""),
                "Cause probable": c.get("_cause", ""),
                "Action recommandee": c.get("_action", ""),
            } for i, c in enumerate(cas_list)])
            df_cas.to_excel(writer, sheet_name="Cas detectes", index=False)

        if cas_list:
            df_enq = pd.DataFrame(cas_list)
            synth = df_enq.groupby("Enqueteur").agg(
                Nb_anomalies=("_index", "count"),
                Regles_distinctes=("Regle", "nunique"),
            ).reset_index().sort_values("Nb_anomalies", ascending=False)
            synth.to_excel(writer, sheet_name="Synthese enqueteurs", index=False)

        if rules:
            df_rules = pd.DataFrame([{
                "N": i + 1,
                "Description": r.get("description", ""),
                "Expression": r.get("expression", ""),
                "Pourquoi": r.get("pourquoi", ""),
                "Cause": r.get("cause", ""),
                "Action": r.get("action", ""),
            } for i, r in enumerate(rules)])
            df_rules.to_excel(writer, sheet_name="Regles IA", index=False)

    return output.getvalue()


# ======================================================================
#  ETAPE 1 — IMPORTER
# ======================================================================

if ss.current_step == 1:
    # Carte upload
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("""
    <h3>Importer les fichiers</h3>
    <p class="desc">La base est obligatoire. Le dictionnaire et le questionnaire ameliorent fortement la qualite des regles generees par l'IA.</p>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    # === Colonne 1 : Base de donnees (REQUIS) ===
    with col_a:
        data_filled = ss.data_file_obj is not None
        zone_cls = "filled" if data_filled else "required"
        if data_filled:
            fname = html_lib.escape(ss.data_file_obj.name, quote=True)
            fsize = fmt_size(len(ss.data_file_obj.getbuffer()))
            inner = (f'<div class="upload-icon green">v</div>'
                     f'<div class="upload-title">Base de donnees</div>'
                     f'<div class="upload-hint">Fichier de l\'enquete</div>'
                     f'<span class="upload-badge required">Requis</span>'
                     f'<div class="upload-filename">{fname}</div>'
                     f'<div class="upload-meta">{fsize}</div>')
        else:
            inner = ('<div class="upload-icon green">F</div>'
                     '<div class="upload-title">Base de donnees</div>'
                     '<div class="upload-hint">.xlsx, .csv, .sav, .dta</div>'
                     '<span class="upload-badge required">Requis</span>')
        st.markdown(f'<div class="upload-zone {zone_cls}">{inner}</div>',
                    unsafe_allow_html=True)
        data_file = st.file_uploader("Choisir la base",
            type=["csv", "tsv", "txt", "xlsx", "xls", "sav", "dta", "sas7bdat"],
            key="upl_data", label_visibility="collapsed")
        if data_file is not None:
            ss.data_file_obj = data_file

    # === Colonne 2 : Dictionnaire (OPTIONNEL) ===
    with col_b:
        dict_filled = ss.dict_file_obj is not None
        zone_cls = "filled" if dict_filled else ""
        if dict_filled:
            fname = html_lib.escape(ss.dict_file_obj.name, quote=True)
            fsize = fmt_size(len(ss.dict_file_obj.getbuffer()))
            inner = (f'<div class="upload-icon green">v</div>'
                     f'<div class="upload-title">Dictionnaire</div>'
                     f'<div class="upload-hint">Libelles / modalites</div>'
                     f'<span class="upload-badge optional">Optionnel</span>'
                     f'<div class="upload-filename">{fname}</div>'
                     f'<div class="upload-meta">{fsize}</div>')
        else:
            inner = ('<div class="upload-icon gold">D</div>'
                     '<div class="upload-title">Dictionnaire</div>'
                     '<div class="upload-hint">.xlsx, .csv</div>'
                     '<span class="upload-badge optional">Optionnel</span>')
        st.markdown(f'<div class="upload-zone {zone_cls}">{inner}</div>',
                    unsafe_allow_html=True)
        dict_file = st.file_uploader("Choisir le dictionnaire",
            type=["csv", "xlsx", "xls"], key="upl_dict", label_visibility="collapsed")
        if dict_file is not None:
            ss.dict_file_obj = dict_file

    # === Colonne 3 : Questionnaire / Form Kobo (OPTIONNEL) ===
    with col_c:
        form_filled = ss.form_file_obj is not None
        zone_cls = "filled" if form_filled else ""
        if form_filled:
            fname = html_lib.escape(ss.form_file_obj.name, quote=True)
            fsize = fmt_size(len(ss.form_file_obj.getbuffer()))
            inner = (f'<div class="upload-icon green">v</div>'
                     f'<div class="upload-title">Questionnaire</div>'
                     f'<div class="upload-hint">Form Kobo / PDF</div>'
                     f'<span class="upload-badge optional">Optionnel</span>'
                     f'<div class="upload-filename">{fname}</div>'
                     f'<div class="upload-meta">{fsize}</div>')
        else:
            inner = ('<div class="upload-icon gold">Q</div>'
                     '<div class="upload-title">Questionnaire</div>'
                     '<div class="upload-hint">XLSForm Kobo / PDF</div>'
                     '<span class="upload-badge optional">Optionnel</span>')
        st.markdown(f'<div class="upload-zone {zone_cls}">{inner}</div>',
                    unsafe_allow_html=True)
        form_file = st.file_uploader("Choisir le questionnaire",
            type=["xlsx", "xls", "pdf", "txt", "docx"],
            key="upl_form", label_visibility="collapsed")
        if form_file is not None:
            ss.form_file_obj = form_file

    st.markdown('</div>', unsafe_allow_html=True)

    # Separateur visuel elegant entre les cartes
    divider("◆")

    # ===== Carte Configuration IA =====
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("""
    <h3>Configuration de l'IA</h3>
    <p class="desc">Choisissez le moteur IA a utiliser. Les cles sont chargees automatiquement depuis le fichier .env.</p>
    """, unsafe_allow_html=True)

    # Selecteur API (labels neutres)
    ss.selected_api = st.radio(
        "Moteur IA",
        options=["api1", "api2"],
        format_func=lambda x: {"api1": "API 1", "api2": "API 2"}[x],
        index=0 if ss.selected_api == "api1" else 1,
        horizontal=True,
    )

    # Statut des cles chargees (sans afficher la valeur)
    current_key = ss.api1_key if ss.selected_api == "api1" else ss.api2_key
    current_label = "API 1" if ss.selected_api == "api1" else "API 2"
    key_prefix = "sk-ant-" if ss.selected_api == "api1" else "gsk_"
    key_loaded = bool(current_key) and current_key.startswith(key_prefix)

    if key_loaded:
        # Statut + bouton test sur la meme ligne
        col_s, col_b = st.columns([3, 1])
        with col_s:
            st.markdown(f"""
            <div style="background:{GREEN_SOFT}; border:1px solid #A7F3D0;
                        border-radius:10px; padding:10px 16px; margin-top:4px;
                        display:flex; align-items:center; gap:10px;">
              <span style="background:{GREEN}; color:#fff; border-radius:50%;
                           width:24px; height:24px; display:inline-flex;
                           align-items:center; justify-content:center;
                           font-weight:700; font-size:14px;">✓</span>
              <span style="color:{GREEN_DARK}; font-weight:600; font-size:0.9rem;">
                Cle {current_label} chargee depuis .env</span>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Tester la connexion", key=f"test_{ss.selected_api}",
                         use_container_width=True):
                with st.spinner("Test..."):
                    ok, msg = ai_agent.test_api_key(ss.selected_api, current_key)
                    if ss.selected_api == "api1":
                        ss.api1_status = (ok, msg)
                    else:
                        ss.api2_status = (ok, msg)

        status = ss.api1_status if ss.selected_api == "api1" else ss.api2_status
        if status:
            ok, msg = status
            (st.success if ok else st.error)(msg)
    else:
        st.markdown(f"""
        <div style="background:{RED_SOFT}; border:1px solid #FECACA;
                    border-radius:10px; padding:12px 16px; margin-top:4px;">
          <span style="color:{RED_DARK}; font-weight:600; font-size:0.9rem;">
            Cle {current_label} non trouvee dans .env</span><br>
          <span style="color:{GRAY}; font-size:0.82rem;">
            Ajoutez la ligne <code>{'ANTHROPIC_API_KEY=sk-ant-...' if ss.selected_api == 'api1' else 'GROQ_API_KEY=gsk_...'}</code>
            dans le fichier .env a la racine du projet, puis redemarrez l'application.</span>
        </div>
        """, unsafe_allow_html=True)

    # Contexte enquête — section enrichie
    st.markdown("<br>", unsafe_allow_html=True)

    # Sous-titre stylé
    st.markdown(f"""
    <div style="background:linear-gradient(90deg, {PURPLE_SOFT}, {BLUE_SOFT});
                border-left:4px solid {PURPLE}; border-radius:0 8px 8px 0;
                padding:10px 14px; margin-bottom:14px;">
      <p style="font-family:'Sora',sans-serif; font-weight:700; color:{NAVY};
                margin:0; font-size:0.95rem;">
        Contexte de l'enquete
      </p>
      <p style="color:{GRAY}; font-size:0.78rem; margin:2px 0 0;">
        Plus les informations sont riches, meilleures sont les regles generees par l'IA.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Type d'enquete avec liste deroulante + saisie libre
    TYPES_ENQUETE = [
        "(Selectionner ou saisir)",
        "PDM - Post-Distribution Monitoring",
        "EFSA - Securite alimentaire",
        "HEA - Household Economy Approach",
        "WASH - Eau, hygiene, assainissement",
        "MSNA - Besoins multi-sectoriels",
        "Education / scolarisation",
        "Protection / GBV",
        "Sante / nutrition",
        "Cash / transferts monetaires",
        "Livelihood / moyens de subsistance",
        "Recensement / RGPH",
        "Etude de marche / commerce",
        "Etude bancaire / microfinance",
        "Enquete satisfaction client",
        "Autre (preciser ci-dessous)",
    ]

    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        type_choice = st.selectbox(
            "Type d'enquete",
            options=TYPES_ENQUETE,
            index=0,
            help="Selectionnez le type le plus proche, ou choisissez 'Autre' pour saisir manuellement."
        )
    with col_t2:
        type_custom = st.text_input(
            "Ou saisie libre",
            value=ss.survey_type if ss.survey_type and ss.survey_type not in TYPES_ENQUETE else "",
            placeholder="ex : PDM HCR Mauritanie 2026",
        )

    # Logique : si custom rempli, on l'utilise, sinon on prend la dropdown
    if type_custom:
        ss.survey_type = type_custom
    elif type_choice and type_choice != "(Selectionner ou saisir)":
        ss.survey_type = type_choice
    else:
        ss.survey_type = ""

    # Description / objectifs
    ss.survey_description = st.text_area(
        "Description et objectifs de l'enquete",
        value=ss.survey_description,
        placeholder="",
        height=110,
        help="Plus la description est detaillee, plus l'IA generera des regles pertinentes.",
    )

    # Population cible
    ss.survey_population = st.text_area(
        "Population cible",
        value=ss.survey_population,
        placeholder=""
                    "",
        height=80,
        help="",
    )

    

    st.markdown('</div>', unsafe_allow_html=True)

    # Separateur avant le bouton final
    divider("▼")

    # Bouton Analyser
    col_btn = st.columns([3, 1, 3])
    with col_btn[1]:
        if st.button("Analyser le fichier", use_container_width=True):
            if ss.data_file_obj is None:
                st.warning("Veuillez d'abord importer une base de donnees.")
            else:
                with st.spinner("Lecture et analyse du fichier..."):
                    try:
                        data_path = _save_upload(ss.data_file_obj)
                        dict_path = _save_upload(ss.dict_file_obj) if ss.dict_file_obj else None
                        loaded = load_file(data_path, dict_path)
                        profile = profile_dataset(loaded)
                        results, mp = run_basic_qc(loaded, profile, params=ss.params)
                        ss.loaded, ss.profile, ss.results, ss.mp = loaded, profile, results, mp
                        ss.ai_results, ss.ai_comment = None, None
                        ss.loaded.meta["survey_type"] = ss.survey_type
                        ss.api_error = None
                        ss.current_step = 2
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")


# ======================================================================
#  ETAPE 2 — DETECTER
# ======================================================================

elif ss.current_step == 2:
    if not ss.loaded:
        st.warning("Veuillez d'abord importer un fichier.")
        if st.button("Retour"):
            ss.current_step = 1
            st.rerun()
    else:
        loaded, profile, results, mp = ss.loaded, ss.profile, ss.results, ss.mp
        summary = profile["summary"]

        tab1, tab2, tab3 = st.tabs([
            "Apercu & profilage",
            "QC basique",
            "QC intelligent"
        ])

        # ============================================================
        # ONGLET 1 — APERCU
        # ============================================================
        with tab1:
            st.markdown(f"#### {loaded.meta['filename']}")
            cols = st.columns(5)
            metric(cols[0], "m-navy", summary["n_rows"], "Lignes")
            metric(cols[1], "m-blue", summary["n_vars"], "Variables")
            metric(cols[2], "m-gold", summary["n_numeric"], "Numeriques")
            metric(cols[3], "m-purple", summary["n_categorical"], "Categorielles")
            metric(cols[4], "m-green", f"{summary['global_fill_rate']}%", "Remplissage")

            st.markdown("##### Detail des variables")
            st.markdown(render_var_table(profile["variables"]), unsafe_allow_html=True)

            with st.expander("Apercu des donnees (20 lignes)"):
                st.dataframe(loaded.df.head(20), use_container_width=True)

        # ============================================================
        # ONGLET 2 — QC basique
        # ============================================================
        with tab2:
            stats = global_stats(profile, results)
            cols = st.columns(4)
            metric(cols[0], "m-navy", stats["questionnaires"], "Questionnaires")
            metric(cols[1], "m-red", stats["incoherences"], "Incoherences")
            metric(cols[2], "m-blue", stats["tests"], "Tests")
            metric(cols[3], "m-gold", stats["tests_alertes"], "Tests avec alertes")

            st.markdown("<br>", unsafe_allow_html=True)

            # Repartition visuelle des resultats par severite
            n_high = sum(1 for r in results if r["severite"] == "high")
            n_med  = sum(1 for r in results if r["severite"] == "med")
            n_low  = sum(1 for r in results if r["severite"] == "low")
            n_ok   = sum(1 for r in results if r["severite"] == "ok")

            st.markdown(f"""
            <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin-bottom:18px;">
              <div style="background:linear-gradient(135deg, #FCEBEB, #F7C1C1);
                          border-radius:12px; padding:14px; text-align:center;
                          border-left:4px solid {RED};">
                <p style="font-family:'Sora',sans-serif; font-size:1.8rem; font-weight:800;
                          color:{RED_DARK}; margin:0; line-height:1;">{n_high}</p>
                <p style="font-size:0.78rem; color:{RED_DARK}; margin:6px 0 0;
                          text-transform:uppercase; letter-spacing:0.05em; font-weight:600;">
                  Tests critiques</p>
              </div>
              <div style="background:linear-gradient(135deg, #FAEEDA, #FAC775);
                          border-radius:12px; padding:14px; text-align:center;
                          border-left:4px solid #EF9F27;">
                <p style="font-family:'Sora',sans-serif; font-size:1.8rem; font-weight:800;
                          color:{ORANGE_DARK}; margin:0; line-height:1;">{n_med}</p>
                <p style="font-size:0.78rem; color:{ORANGE_DARK}; margin:6px 0 0;
                          text-transform:uppercase; letter-spacing:0.05em; font-weight:600;">
                  A surveiller</p>
              </div>
              <div style="background:linear-gradient(135deg, #E6F1FB, #B5D4F4);
                          border-radius:12px; padding:14px; text-align:center;
                          border-left:4px solid {BLUE};">
                <p style="font-family:'Sora',sans-serif; font-size:1.8rem; font-weight:800;
                          color:{BLUE_DARK}; margin:0; line-height:1;">{n_low}</p>
                <p style="font-size:0.78rem; color:{BLUE_DARK}; margin:6px 0 0;
                          text-transform:uppercase; letter-spacing:0.05em; font-weight:600;">
                  Faible risque</p>
              </div>
              <div style="background:linear-gradient(135deg, #EAF3DE, #C0DD97);
                          border-radius:12px; padding:14px; text-align:center;
                          border-left:4px solid #639922;">
                <p style="font-family:'Sora',sans-serif; font-size:1.8rem; font-weight:800;
                          color:{GREEN_DARK}; margin:0; line-height:1;">{n_ok}</p>
                <p style="font-size:0.78rem; color:{GREEN_DARK}; margin:6px 0 0;
                          text-transform:uppercase; letter-spacing:0.05em; font-weight:600;">
                  Tests OK</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### Detail des tests executes")

            order = {"high": 0, "med": 1, "low": 2, "ok": 3}
            # Configuration visuelle par severite
            SEV_STYLE = {
                "high": {"bg": "#FCEBEB", "border": RED,        "txt": RED_DARK,
                         "icon": "⚠", "label": "CRITIQUE"},
                "med":  {"bg": "#FAEEDA", "border": "#EF9F27",  "txt": ORANGE_DARK,
                         "icon": "⚡", "label": "ATTENTION"},
                "low":  {"bg": "#E6F1FB", "border": BLUE,       "txt": BLUE_DARK,
                         "icon": "ℹ",  "label": "INFO"},
                "ok":   {"bg": "#EAF3DE", "border": "#639922",  "txt": GREEN_DARK,
                         "icon": "✓",  "label": "OK"},
            }

            for r in sorted(results, key=lambda x: (order[x["severite"]], -x["n_cas"])):
                sev = r["severite"]
                style = SEV_STYLE[sev]
                titre_safe = html_lib.escape(r["titre"], quote=True)

                # Carte resume colore avant l'expander
                st.markdown(f"""
                <div style="background:{style['bg']};
                            border-left:4px solid {style['border']};
                            border-radius:0 10px 10px 0;
                            padding:12px 16px; margin-bottom:4px;
                            display:flex; align-items:center; gap:14px;">
                  <div style="background:#fff; border-radius:50%;
                              width:36px; height:36px; display:flex;
                              align-items:center; justify-content:center;
                              color:{style['txt']}; font-size:18px; font-weight:700;
                              box-shadow:0 2px 4px rgba(0,0,0,0.08); flex-shrink:0;">
                    {style['icon']}
                  </div>
                  <div style="flex:1;">
                    <p style="font-family:'Sora',sans-serif; font-weight:700;
                              font-size:0.95rem; color:{style['txt']}; margin:0;">
                      {titre_safe}</p>
                    <p style="font-size:0.78rem; color:{style['txt']}; opacity:0.85;
                              margin:2px 0 0;">{r['n_cas']} cas detectes</p>
                  </div>
                  <span style="background:#fff; color:{style['txt']};
                               padding:5px 14px; border-radius:8px;
                               font-family:'Sora',sans-serif; font-size:0.7rem;
                               font-weight:700; letter-spacing:0.05em;
                               box-shadow:0 1px 3px rgba(0,0,0,0.08);">
                    {style['label']}</span>
                </div>
                """, unsafe_allow_html=True)

                # Expander avec les details (sans icon dans le titre pour eviter le doublon)
                with st.expander(f"Voir les details — {r['titre']}",
                                 expanded=(sev == "high")):
                    e = r["explication"]
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.markdown(f"""
                        <div style="background:{PURPLE_SOFT}; border-radius:8px;
                                    padding:10px 12px; height:100%;">
                          <p style="font-size:0.7rem; color:{PURPLE_DARK};
                                    text-transform:uppercase; letter-spacing:0.05em;
                                    font-weight:700; margin:0 0 4px;">Pourquoi</p>
                          <p style="font-size:0.85rem; color:{NAVY}; margin:0;">
                            {html_lib.escape(e['pourquoi'])}</p>
                        </div>""", unsafe_allow_html=True)
                    with col_b:
                        st.markdown(f"""
                        <div style="background:{ORANGE_SOFT}; border-radius:8px;
                                    padding:10px 12px; height:100%;">
                          <p style="font-size:0.7rem; color:{ORANGE_DARK};
                                    text-transform:uppercase; letter-spacing:0.05em;
                                    font-weight:700; margin:0 0 4px;">Cause</p>
                          <p style="font-size:0.85rem; color:{NAVY}; margin:0;">
                            {html_lib.escape(e['cause'])}</p>
                        </div>""", unsafe_allow_html=True)
                    with col_c:
                        st.markdown(f"""
                        <div style="background:{GREEN_SOFT}; border-radius:8px;
                                    padding:10px 12px; height:100%;">
                          <p style="font-size:0.7rem; color:{GREEN_DARK};
                                    text-transform:uppercase; letter-spacing:0.05em;
                                    font-weight:700; margin:0 0 4px;">Action</p>
                          <p style="font-size:0.85rem; color:{NAVY}; margin:0;">
                            {html_lib.escape(e['action'])}</p>
                        </div>""", unsafe_allow_html=True)

                    if r["lignes"]:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("**Cas detectes :**")
                        raw = pd.DataFrame(r["lignes"])
                        show_cols = [c for c in raw.columns
                                     if not c.startswith("_") or c == "_index"]
                        disp = raw[show_cols].rename(columns={"_index": "Ligne"})
                        if "_probleme" in raw.columns:
                            disp["Probleme"] = raw["_probleme"].values
                        st.dataframe(disp, use_container_width=True, hide_index=True)

        # ============================================================
        # ONGLET 3 — QC INTELLIGENT
        # ============================================================
        with tab3:
            # Bandeau de l'API active
            api_label = "API 1" if ss.selected_api == "api1" else "API 2"
            api_key = ss.api1_key if ss.selected_api == "api1" else ss.api2_key
            key_prefix = "sk-ant-" if ss.selected_api == "api1" else "gsk_"

            st.markdown(f'<div class="api-selector">'
                       f'<b>Moteur IA actif :</b> {api_label} '
                       f'<span style="color:{GRAY};font-size:0.85rem;">'
                       f'(vous pouvez changer ce choix a l\'etape 1)</span>'
                       f'</div>', unsafe_allow_html=True)

            st.markdown("L'IA lit les variables, leurs libelles, le dictionnaire et la "
                       "description pour generer des regles de coherence logique adaptees. "
                       "Si le fichier est volumineux, l'analyse se fait en plusieurs lots. "
                       "Les regles sont ensuite executees sur **100% du fichier**.")

            if not api_key:
                st.warning(f"Renseignez votre cle pour {api_label} a l'etape 1.")
            elif not api_key.startswith(key_prefix):
                st.error(f"Cle invalide pour {api_label}. Verifiez votre saisie.")
            else:
                if st.button(f"Generer et executer les regles avec {api_label}"):
                    progress_box = st.empty()
                    progress_log = []

                    def progress_cb(msg):
                        progress_log.append(msg)
                        progress_box.info(" | ".join(progress_log[-3:]))

                    with st.spinner(f"Analyse intelligente en cours via {api_label}..."):
                        try:
                            # Extraire le contenu du questionnaire si fourni
                            form_content = ""
                            if ss.form_file_obj is not None:
                                try:
                                    fname = ss.form_file_obj.name.lower()
                                    if fname.endswith((".xlsx", ".xls")):
                                        # Form Kobo XLSForm : lire feuille survey
                                        form_path = _save_upload(ss.form_file_obj)
                                        try:
                                            df_form = pd.read_excel(form_path,
                                                                    sheet_name="survey")
                                        except Exception:
                                            df_form = pd.read_excel(form_path)
                                        # Garder colonnes pertinentes
                                        keep_cols = [c for c in df_form.columns
                                                     if any(k in c.lower() for k in
                                                            ["type", "name", "label",
                                                             "constraint", "relevant",
                                                             "calculation", "required"])]
                                        form_content = df_form[keep_cols].head(150).to_string(
                                            max_colwidth=80, index=False)[:4000]
                                    elif fname.endswith(".txt"):
                                        form_content = ss.form_file_obj.getvalue().decode(
                                            "utf-8", errors="ignore")[:4000]
                                except Exception as fe:
                                    form_content = f"(Formulaire non lisible : {fe})"

                            rules, comment, metrics = ai_agent.generate_rules(
                                ss.selected_api, api_key, profile,
                                loaded.var_labels, loaded.value_labels,
                                survey_type=ss.survey_type,
                                survey_description=ss.survey_description,
                                survey_population=ss.survey_population,
                                survey_eligibility=ss.survey_eligibility,
                                form_content=form_content,
                                df=loaded.df,
                                progress_callback=progress_cb,
                            )
                            progress_cb("Execution des regles sur le fichier complet...")
                            ai_res = ai_agent.run_rules(loaded.df, rules, mp)
                            ss.ai_results = {"rules": rules, "result": ai_res}
                            ss.ai_comment = comment
                            ss.ai_metrics = metrics
                            ss.api_error = None
                            progress_box.empty()
                            st.success(f"Analyse terminee : {len(rules)} regles generees, "
                                       f"{ai_res['n_cas']} cas detectes.")
                        except Exception as e:
                            err = str(e)
                            for term in ["Anthropic", "anthropic", "Claude", "claude",
                                         "Groq", "groq", "sk-ant", "gsk_"]:
                                err = err.replace(term, "API")
                            ss.api_error = f"Erreur du moteur IA : {err[:300]}"
                            st.rerun()

                if ss.ai_results:
                    if ss.ai_metrics:
                        m = ss.ai_metrics
                        mc = st.columns(4)
                        metric(mc[0], "m-blue", f"{m['duration']}s", "Duree totale")
                        metric(mc[1], "m-gold", m.get("n_batches", 1), "Lots traites")
                        metric(mc[2], "m-purple", m.get("n_vars_analysed", "?"), "Variables analysees")
                        metric(mc[3], "m-green", m["n_rules"], "Regles generees")

                    if ss.ai_comment:
                        st.info(ss.ai_comment)

                    rules = ss.ai_results["rules"]
                    res = ss.ai_results["result"]

                    with st.expander(f"Voir les {len(rules)} regles generees par l'IA",
                                     expanded=False):
                        for i, r in enumerate(rules, 1):
                            n_cas_regle = res["cas_par_regle"].get(i-1, 0)
                            desc = html_lib.escape(r.get("description", ""), quote=True)
                            st.markdown(
                                f'<div class="qc-card med">'
                                f'<b>Regle {i}</b> — {desc}<br>'
                                f'<span style="color:{GRAY};font-size:0.82rem;">'
                                f'{n_cas_regle} cas detectes</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                    st.markdown(f"### {res['n_cas']} cas detectes")

                    if res["lignes"]:
                        excel_data = build_export_excel(res["lignes"], rules)

                        col_dl, col_view = st.columns([2, 3])
                        with col_dl:
                            st.download_button(
                                label="Exporter en Excel",
                                data=excel_data,
                                file_name=f"sista_qc_{loaded.meta['filename']}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True,
                            )
                        with col_view:
                            view_mode = st.radio(
                                "Mode d'affichage",
                                ["Cartes visuelles", "Tableau de donnees"],
                                horizontal=True,
                                label_visibility="collapsed"
                            )

                        if view_mode == "Cartes visuelles":
                            cards_html = '<div class="cas-grid">'
                            for i, cas in enumerate(res["lignes"], 1):
                                cards_html += render_cas_card(cas, i)
                            cards_html += '</div>'
                            st.markdown(cards_html, unsafe_allow_html=True)
                        else:
                            df_view = pd.DataFrame([{
                                "Cas N": i + 1,
                                "Ligne": c["_index"],
                                "Gravite": {"high": "Haute", "med": "Moyenne",
                                            "low": "Faible"}[c["_severite"]],
                                "Enqueteur": c["Enqueteur"],
                                "Regle": c["Regle"],
                                "Colonnes": c["Colonnes_concernees"],
                                "Valeurs en cause": c["Valeurs"],
                                "Action": c.get("_action", ""),
                            } for i, c in enumerate(res["lignes"])])
                            st.dataframe(df_view, use_container_width=True, hide_index=True)
                    else:
                        st.success("Aucune incoherence detectee. Bravo !")


# ======================================================================
#  ETAPE 3 — RAPPORT QC
# ======================================================================

elif ss.current_step == 3:
    if not ss.loaded:
        st.warning("Veuillez d'abord importer et analyser un fichier.")
        if st.button("Retour"):
            ss.current_step = 1
            st.rerun()
    else:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown("""
        <h3>Bilan par enqueteur</h3>
        <p class="desc">Classement selon le nombre et la gravite des anomalies.</p>
        """, unsafe_allow_html=True)

        all_results = list(ss.results)
        if ss.ai_results:
            all_results.append(ss.ai_results["result"])
        summary_enq = build_enqueteur_summary(all_results, ss.mp)

        if not summary_enq:
            st.info("Aucune colonne enqueteur detectee.")
        else:
            n_high = sum(1 for e in summary_enq if e["niveau"] == "high")
            n_med = sum(1 for e in summary_enq if e["niveau"] == "med")
            n_low = sum(1 for e in summary_enq if e["niveau"] == "low")

            cols = st.columns(4)
            metric(cols[0], "m-navy", len(summary_enq), "Enqueteurs")
            metric(cols[1], "m-red", n_high, "Risque eleve")
            metric(cols[2], "m-gold", n_med, "Risque modere")
            metric(cols[3], "m-green", n_low, "Risque faible")

            for e in summary_enq:
                sev = e["niveau"]
                label = {"high": "RISQUE ELEVE", "med": "RISQUE MODERE",
                         "low": "RISQUE FAIBLE"}[sev]
                nom_safe = html_lib.escape(str(e["nom"]), quote=True)
                details_raw = " | ".join(f"{t} ({n})" for t, n in e["par_test"].items())
                details = html_lib.escape(details_raw, quote=True)
                st.markdown(
                    f'<div class="qc-card {sev}"><b>{nom_safe} — {label}</b> '
                    f'<span style="color:{NAVY};font-weight:700">'
                    f'({e["total"]} anomalies)</span><br>'
                    f'<span style="font-size:0.82rem;color:#5A6A7A">{details}</span></div>',
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)
