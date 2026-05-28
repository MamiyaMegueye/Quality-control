"""
auth.py — Page de connexion SISTA QC.
Design compact, colore, identifiants par defaut : sista26 / 1234
"""

import os
import hmac
import base64
import streamlit as st


def _get_users():
    """Recupere les utilisateurs autorises (st.secrets ou defaut)."""
    try:
        if "users" in st.secrets:
            return dict(st.secrets["users"])
    except Exception:
        pass
    raw = os.environ.get("USERS_JSON", "")
    if raw:
        try:
            import json
            return json.loads(raw)
        except Exception:
            pass
    # Identifiants par defaut
    return {"sista26": "1234"}


def _logo_b64():
    if os.path.exists("logo_sista.png"):
        with open("logo_sista.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def _render_login_styles():
    """CSS de la page de connexion : compact, colore, moderne."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Spline+Sans:wght@400;500;600&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(239,199,26,0.18) 0%, transparent 35%),
            radial-gradient(circle at 85% 80%, rgba(46,117,182,0.18) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(139,92,246,0.10) 0%, transparent 50%),
            linear-gradient(135deg, #F4F7FA 0%, #E8EEF5 100%) !important;
        min-height: 100vh;
    }

    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }

    html, body { font-family: 'Spline Sans', sans-serif; }

    /* Carte de connexion compacte */
    .sista-login-card {
        max-width: 380px;
        margin: 1.5rem auto 0;
        background: #ffffff;
        border-radius: 20px;
        box-shadow:
            0 20px 50px rgba(13,27,44,0.15),
            0 8px 20px rgba(13,27,44,0.08);
        overflow: hidden;
        position: relative;
    }
    .sista-login-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0;
        height: 5px;
        background: linear-gradient(90deg, #EFC71A 0%, #D4AC0D 50%, #EFC71A 100%);
    }

    /* En-tete compact avec degrade */
    .sista-login-header {
        background: linear-gradient(135deg, #0D1B2C 0%, #13263D 50%, #1E3A5C 100%);
        padding: 22px 28px 18px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .sista-login-header::after {
        content: '';
        position: absolute;
        right: -40px; top: -40px;
        width: 130px; height: 130px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(239,199,26,0.25), transparent 70%);
    }
    .sista-login-header::before {
        content: '';
        position: absolute;
        left: -30px; bottom: -50px;
        width: 110px; height: 110px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(46,117,182,0.30), transparent 70%);
    }
    .sista-login-header img {
        height: 52px;
        margin-bottom: 8px;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.35));
        position: relative;
        z-index: 2;
    }
    .sista-login-header h1 {
        font-family: 'Sora', sans-serif;
        color: #fff;
        font-size: 1.1rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.01em;
        position: relative;
        z-index: 2;
    }
    .sista-login-header h1 span { color: #EFC71A; }
    .sista-login-header p {
        color: rgba(255,255,255,0.65);
        font-size: 0.62rem;
        margin: 3px 0 0;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 500;
        position: relative;
        z-index: 2;
    }

    /* Corps du formulaire compact */
    .sista-login-body label {
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important;
        color: #13263D !important;
        font-size: 0.78rem !important;
    }
    .sista-login-body .stTextInput input,
    div[data-testid="stForm"] .stTextInput input {
        border-radius: 10px !important;
        border: 1.5px solid #E5E7EB !important;
        padding: 9px 12px !important;
        font-size: 0.88rem !important;
        font-family: 'Spline Sans', sans-serif !important;
        background: #FAFBFC !important;
        transition: 0.2s;
    }
    div[data-testid="stForm"] .stTextInput input:focus {
        border-color: #EFC71A !important;
        background: #fff !important;
        box-shadow: 0 0 0 3px rgba(239,199,26,0.15) !important;
    }

    /* Bouton stylise */
    .stFormSubmitButton button {
        background: linear-gradient(135deg, #13263D 0%, #1E3A5C 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-family: 'Sora', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        width: 100% !important;
        margin-top: 10px !important;
        box-shadow: 0 4px 12px rgba(13,27,44,0.25);
        transition: all 0.2s;
        letter-spacing: 0.02em;
    }
    .stFormSubmitButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(13,27,44,0.35);
        color: #EFC71A !important;
    }
    .stFormSubmitButton button:active {
        transform: translateY(0);
    }

    /* Footer carte */
    .sista-login-footer {
        max-width: 380px;
        margin: 14px auto 0;
        text-align: center;
        padding: 14px 20px;
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(6px);
        border-radius: 14px;
        color: #6B7280;
        font-size: 0.7rem;
        font-family: 'Spline Sans', sans-serif;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(13,27,44,0.04);
    }
    .sista-login-footer b { color: #13263D; }

    /* Badges colores en bas (decoratifs) */
    .sista-decor {
        max-width: 380px;
        margin: 12px auto 0;
        display: flex;
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
    }
    .sista-pill {
        background: #fff;
        padding: 5px 11px;
        border-radius: 999px;
        font-size: 0.68rem;
        font-weight: 600;
        color: #5F5E5A;
        box-shadow: 0 2px 6px rgba(13,27,44,0.06);
        border: 1px solid rgba(13,27,44,0.05);
    }
    .sista-pill.green { color: #065F46; background: #ECFDF5; border-color: #A7F3D0; }
    .sista-pill.blue  { color: #1E40AF; background: #DBEAFE; border-color: #BFDBFE; }
    .sista-pill.gold  { color: #92400E; background: #FEF3C7; border-color: #FDE68A; }

    /* Forcer la largeur compacte du form Streamlit */
    div[data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        max-width: 380px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)


def _render_login_form():
    """Affiche la page de connexion stylisee."""
    _render_login_styles()
    logo = _logo_b64()

    # En-tete carte
    st.markdown(f"""
    <div class="sista-login-card">
      <div class="sista-login-header">
        {f'<img src="data:image/png;base64,{logo}" alt="SISTA"/>' if logo else ''}
        <h1>SISTA <span>QC</span></h1>
        <p>Connexion securisee</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Formulaire centre via colonnes
    col_l, col_c, col_r = st.columns([1, 1.4, 1])
    with col_c:
        st.markdown('<div class="sista-login-body">', unsafe_allow_html=True)
        with st.form("sista_login_form", clear_on_submit=False):
            username = st.text_input("Nom d'utilisateur",
                                     placeholder="  ")
            password = st.text_input("Mot de passe",
                                     type="password",
                                     placeholder="••••••••")
            submitted = st.form_submit_button("Se connecter")

            if submitted:
                users = _get_users()
                if (username in users
                        and hmac.compare_digest(str(password), str(users[username]))):
                    st.session_state["sista_authenticated"] = True
                    st.session_state["sista_username"] = username
                    st.rerun()
                else:
                    st.markdown(
                        '<div style="background:#FEE2E2;color:#991B1B;padding:9px 12px;'
                        'border-radius:8px;font-size:0.82rem;margin-top:10px;'
                        'border-left:3px solid #EF4444;text-align:center;">'
                        'Identifiants incorrects</div>',
                        unsafe_allow_html=True,
                    )
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer + badges decoratifs
    st.markdown("""
    <div class="sista-login-footer">
      <b>SISTA Consult Mauritanie</b><br>
      <span style="font-size:0.65rem;color:#9CA3AF">
       
      </span>
    </div>

    """, unsafe_allow_html=True)


def check_password():
    """A appeler en debut de l'app. Renvoie True si connecte."""
    if st.session_state.get("sista_authenticated"):
        return True
    _render_login_form()
    return False


def logout_button(label="Se deconnecter"):
    """Bouton de deconnexion."""
    if st.button(label, key="sista_logout"):
        for k in ("sista_authenticated", "sista_username"):
            st.session_state.pop(k, None)
        st.rerun()


def current_user():
    """Renvoie le nom de l'utilisateur connecte."""
    return st.session_state.get("sista_username", "")