"""
Sagemcom - Intelligent Test Bench (TF GTW T5)
==============================================
Quality-supervision console for production test data, AI-scored.

Version : 3.0 — corporate / instrumentation-panel redesign
Run     : streamlit run dashboard_sagemcom.py
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_option_menu import option_menu

# ============================================================================
# 1. CONFIGURATION
# ============================================================================

APP_NAME = "SAGEMCOM"
APP_LINE = "Intelligent Test Bench"
APP_UNIT = "TF GTW T5"
APP_VERSION = "3.0"

DB_PATH = "base_production.db"
TABLE_NAME = "Historique_Tests"
LOGO_PATH = "logo.png"  # optionnel : déposer un logo réel à côté du script

# --- Design tokens ---------------------------------------------------------
# Palette neutre / industrielle, dérivée de l'identité Sagemcom mais désaturée
# pour un rendu "console de mesure" plutôt que "application grand public".
C = {
    "bg": "#F5F6F8",
    "surface": "#FFFFFF",
    "border": "#E2E5EA",
    "ink": "#1B2430",
    "ink_soft": "#5B6472",
    "navy": "#0A3D62",
    "navy_soft": "#DCE7EF",
    "steel": "#3E5468",
    "success": "#1E7F4C",
    "success_bg": "#E5F3EA",
    "danger": "#B3261E",
    "danger_bg": "#FBEAE9",
    "warning": "#B15C00",
    "warning_bg": "#FBF0DF",
}

THRESHOLD_ALERT = 50
THRESHOLD_CRITICAL = 70

MEASURE_COLUMNS = [
    "Tension (V)", "Courant (mA)", "Gain mes1 (dB)", "Gain mes2 (dB)",
    "Gain mes3 (dB)", "Puissance (W)", "RMS (Vrms)", "Température('C)",
]

st.set_page_config(page_title=f"{APP_NAME} · {APP_LINE}", page_icon="▪", layout="wide",
                    initial_sidebar_state="expanded")

# ============================================================================
# 2. I18N — bilingue FR / EN
# ============================================================================

TXT = {
    "fr": {
        "nav": ["Tableau de bord", "Analyse détaillée", "Historique", "Configuration"],
        "filters": "FILTRES",
        "period": "Période",
        "period_opts": {"all": "Historique complet", "24h": "24 heures", "7d": "7 jours",
                         "30d": "30 jours", "month": "Ce mois-ci"},
        "status": "Statut",
        "score_range": "Score de risque",
        "search": "Recherche",
        "search_ph": "Identifiant de carte",
        "auto_refresh": "Actualisation automatique",
        "interval": "Intervalle",
        "refresh_now": "Actualiser",
        "updated": "Dernière lecture",
        "live": "EN LIGNE",
        "offline": "HORS LIGNE",
        "kpi_total": "Cartes testées",
        "kpi_pass": "Taux de conformité",
        "kpi_fail": "Taux de défaut",
        "kpi_score": "Score de risque moyen",
        "kpi_last": "Dernier test",
        "ok_units": "unités conformes",
        "fail_units": "unités en défaut",
        "max_lbl": "maximum",
        "sec_perf": "Analyse des performances",
        "sec_measures": "Analyse des mesures",
        "sec_table": "Journal des tests",
        "no_data": "Aucune donnée n'a encore été enregistrée pour ce banc de test.",
        "no_data_filtered": "Aucun enregistrement ne correspond aux filtres sélectionnés.",
        "export": "Exporter le journal (CSV)",
        "distribution": "Distribution des mesures",
        "stats_desc": "Statistiques descriptives",
        "correlation": "Matrice de corrélation",
        "no_measures": "Aucune mesure exploitable dans le jeu de données actuel.",
        "need_2": "Deux mesures minimum sont nécessaires pour une corrélation.",
        "gauge_title": "Score moyen",
        "critical": "Seuil critique",
        "alert": "Seuil d'alerte",
        "pie_title": "Répartition PASS / FAIL",
        "col_card": "Identifiant",
        "col_dt": "Horodatage",
        "col_status": "Statut",
        "col_score": "Score",
        "db_missing": "Base de données introuvable :",
        "db_error": "Erreur de lecture de la base :",
        "waiting": "En attente des premiers résultats du banc de test.",
        "footer": "Supervision qualité par intelligence artificielle — Document interne, diffusion restreinte.",
        "next_refresh": "Prochaine lecture dans {s}s",
    },
    "en": {
        "nav": ["Dashboard", "Detailed Analysis", "History", "Configuration"],
        "filters": "FILTERS",
        "period": "Period",
        "period_opts": {"all": "Full history", "24h": "24 hours", "7d": "7 days",
                         "30d": "30 days", "month": "This month"},
        "status": "Status",
        "score_range": "Risk score",
        "search": "Search",
        "search_ph": "Board identifier",
        "auto_refresh": "Auto-refresh",
        "interval": "Interval",
        "refresh_now": "Refresh",
        "updated": "Last read",
        "live": "LIVE",
        "offline": "OFFLINE",
        "kpi_total": "Boards tested",
        "kpi_pass": "Pass rate",
        "kpi_fail": "Fail rate",
        "kpi_score": "Average risk score",
        "kpi_last": "Last test",
        "ok_units": "passing units",
        "fail_units": "failing units",
        "max_lbl": "maximum",
        "sec_perf": "Performance analysis",
        "sec_measures": "Measurement analysis",
        "sec_table": "Test log",
        "no_data": "No data has been recorded for this test bench yet.",
        "no_data_filtered": "No record matches the selected filters.",
        "export": "Export log (CSV)",
        "distribution": "Measurement distribution",
        "stats_desc": "Descriptive statistics",
        "correlation": "Correlation matrix",
        "no_measures": "No usable measurement in the current dataset.",
        "need_2": "At least two measurements are required for a correlation.",
        "gauge_title": "Average score",
        "critical": "Critical threshold",
        "alert": "Alert threshold",
        "pie_title": "PASS / FAIL breakdown",
        "col_card": "Identifier",
        "col_dt": "Timestamp",
        "col_status": "Status",
        "col_score": "Score",
        "db_missing": "Database not found:",
        "db_error": "Database read error:",
        "waiting": "Waiting for the first test results.",
        "footer": "AI-driven quality supervision — Internal document, restricted distribution.",
        "next_refresh": "Next read in {s}s",
    },
}


def t(key: str) -> str:
    return TXT[st.session_state.get("lang", "fr")][key]


# ============================================================================
# 3. STYLE
# ============================================================================

def inject_css() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

            html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {C['ink']}; }}
            .stApp {{ background: {C['bg']}; }}

            h1, h2, h3, .brand, .nav-link {{ font-family: 'IBM Plex Sans', sans-serif; }}
            .mono {{ font-family: 'IBM Plex Mono', monospace; }}

            #MainMenu, footer {{ visibility: hidden; }}

            /* ---- Top bar ---- */
            .topbar {{
                display: flex; justify-content: space-between; align-items: center;
                background: {C['navy']};
                padding: 1.1rem 1.6rem;
                border-radius: 6px;
                margin-bottom: 1.4rem;
            }}
            .topbar .brand {{
                color: #FFFFFF; font-size: 1.15rem; font-weight: 700;
                letter-spacing: 2.5px; margin: 0;
            }}
            .topbar .subline {{
                color: #AFC4D6; font-size: 0.82rem; margin-top: 2px;
                letter-spacing: 0.3px;
            }}
            .topbar .status {{
                display: flex; align-items: center; gap: 0.5rem;
                color: #DCE7EF; font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem;
                letter-spacing: 1px;
            }}
            .pulse-dot {{
                width: 8px; height: 8px; border-radius: 50%;
                background: #35C46A; box-shadow: 0 0 0 rgba(53,196,106,0.5);
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(53,196,106,0.55); }}
                70% {{ box-shadow: 0 0 0 6px rgba(53,196,106,0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(53,196,106,0); }}
            }}
            .pulse-dot.off {{ background: {C['ink_soft']}; animation: none; }}

            /* ---- KPI cards ---- */
            .kpi {{
                background: {C['surface']};
                border: 1px solid {C['border']};
                border-radius: 6px;
                padding: 1rem 1.15rem;
                height: 100%;
            }}
            .kpi-label {{
                color: {C['ink_soft']}; font-size: 0.72rem; font-weight: 600;
                text-transform: uppercase; letter-spacing: 0.9px;
            }}
            .kpi-value {{
                font-family: 'IBM Plex Mono', monospace;
                color: {C['ink']}; font-size: 1.9rem; font-weight: 600;
                margin: 0.25rem 0 0.15rem 0; line-height: 1;
            }}
            .kpi-sub {{ font-size: 0.78rem; color: {C['ink_soft']}; font-family: 'IBM Plex Mono', monospace; }}
            .kpi-sub.pos {{ color: {C['success']}; }}
            .kpi-sub.neg {{ color: {C['danger']}; }}
            .kpi-bar {{ width: 28px; height: 3px; border-radius: 2px; margin-bottom: 0.5rem; }}

            /* ---- Status tags (square, technical, not pill-shaped) ---- */
            .tag {{
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.72rem; font-weight: 600; letter-spacing: 0.6px;
                padding: 0.15rem 0.5rem; border-radius: 3px; display: inline-block;
            }}
            .tag-pass {{ background: {C['success_bg']}; color: {C['success']}; }}
            .tag-fail {{ background: {C['danger_bg']}; color: {C['danger']}; }}
            .tag-na   {{ background: {C['bg']}; color: {C['ink_soft']}; }}

            /* ---- Section headers ---- */
            .sec {{
                display: flex; align-items: baseline; gap: 0.6rem;
                margin: 1.6rem 0 0.9rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid {C['border']};
            }}
            .sec .idx {{
                font-family: 'IBM Plex Mono', monospace; color: {C['navy']};
                font-size: 0.78rem; font-weight: 600; border: 1px solid {C['navy']};
                border-radius: 3px; padding: 0.05rem 0.4rem;
            }}
            .sec .title {{ font-size: 1.05rem; font-weight: 600; color: {C['ink']}; }}

            .panel {{
                background: {C['surface']}; border: 1px solid {C['border']};
                border-radius: 6px; padding: 1rem 1.1rem;
            }}
            .info-banner {{
                background: {C['navy_soft']}; border-left: 3px solid {C['navy']};
                padding: 0.75rem 1rem; border-radius: 4px;
                color: {C['steel']}; font-size: 0.88rem; margin-bottom: 1rem;
            }}

            .dataframe thead tr th {{
                background: {C['navy']} !important; color: white !important;
                font-family: 'IBM Plex Mono', monospace !important; font-size: 0.78rem !important;
                font-weight: 500 !important; letter-spacing: 0.4px;
            }}

            section[data-testid="stSidebar"] {{ background: {C['surface']}; border-right: 1px solid {C['border']}; }}
            section[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem; }}

            .side-label {{
                font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
                font-weight: 600; color: {C['ink_soft']}; letter-spacing: 1px;
                margin: 1rem 0 0.3rem 0;
            }}

            .footer-line {{
                text-align: center; color: {C['ink_soft']}; font-size: 0.76rem;
                padding: 1.2rem 0 0.6rem 0; letter-spacing: 0.2px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# 4. DATA LAYER
# ============================================================================

@dataclass
class LoadResult:
    df: pd.DataFrame
    error: Optional[str] = None


def _safe_json_parse(raw) -> dict:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


@st.cache_data(ttl=5, show_spinner=False)
def charger_donnees(db_path: str, table_name: str) -> LoadResult:
    db_file = Path(db_path)
    if not db_file.exists():
        return LoadResult(pd.DataFrame(), error=f"{t('db_missing')} {db_path}")

    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY id DESC", conn)
    except Exception as exc:  # noqa: BLE001
        return LoadResult(pd.DataFrame(), error=f"{t('db_error')} {exc}")

    if df.empty:
        return LoadResult(df)

    if "mesures_brutes" in df.columns:
        parsed = df["mesures_brutes"].apply(_safe_json_parse).apply(pd.Series)
        df = pd.concat([df.drop(columns=["mesures_brutes"]), parsed], axis=1)

    if "date_heure" in df.columns:
        df["date_heure"] = pd.to_datetime(df["date_heure"], errors="coerce")
    if "score_risque" in df.columns:
        df["score_risque"] = pd.to_numeric(df["score_risque"], errors="coerce")

    for col in ("statut_ia", "score_risque", "identifiant_carte", "date_heure"):
        if col not in df.columns:
            df[col] = np.nan

    return LoadResult(df)


def appliquer_filtres(df: pd.DataFrame, periode_key: str, statuts: list[str],
                       score_range: tuple[int, int], recherche: str) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = df.copy()
    now = datetime.now()
    deltas = {"24h": timedelta(hours=24), "7d": timedelta(days=7), "30d": timedelta(days=30)}

    if periode_key in deltas and "date_heure" in filtered.columns:
        filtered = filtered[filtered["date_heure"] > (now - deltas[periode_key])]
    elif periode_key == "month" and "date_heure" in filtered.columns:
        filtered = filtered[filtered["date_heure"].dt.month == now.month]

    if statuts and "statut_ia" in filtered.columns:
        filtered = filtered[filtered["statut_ia"].isin(statuts)]

    if "score_risque" in filtered.columns:
        filtered = filtered[
            filtered["score_risque"].between(score_range[0], score_range[1], inclusive="both")
            | filtered["score_risque"].isna()
        ]

    if recherche and "identifiant_carte" in filtered.columns:
        filtered = filtered[filtered["identifiant_carte"].astype(str).str.contains(recherche, case=False, na=False)]

    return filtered


def calculer_statistiques(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total": 0, "passes": 0, "failures": 0, "taux_defaut": 0.0,
                "pass_rate": 0.0, "score_moyen": 0.0, "score_max": 0.0, "score_min": 0.0}

    total = len(df)
    failures = int((df["statut_ia"] == "FAIL").sum())
    passes = total - failures
    score_series = df["score_risque"].dropna()

    return {
        "total": total, "passes": passes, "failures": failures,
        "taux_defaut": (failures / total * 100) if total else 0.0,
        "pass_rate": (passes / total * 100) if total else 0.0,
        "score_moyen": float(score_series.mean()) if not score_series.empty else 0.0,
        "score_max": float(score_series.max()) if not score_series.empty else 0.0,
        "score_min": float(score_series.min()) if not score_series.empty else 0.0,
    }


# ============================================================================
# 5. CHARTS
# ============================================================================

def creer_gauge(score: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(score, 1),
        domain={"x": [0, 1], "y": [0, 1]},
        number={"font": {"family": "IBM Plex Mono", "size": 30, "color": C["ink"]}, "suffix": "%"},
        title={"text": t("gauge_title"), "font": {"size": 12, "family": "IBM Plex Sans", "color": C["ink_soft"]}},
        delta={"reference": THRESHOLD_ALERT, "increasing": {"color": C["danger"]}, "decreasing": {"color": C["success"]}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": C["ink_soft"]},
            "bar": {"color": C["navy"]},
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": C["border"],
            "steps": [
                {"range": [0, THRESHOLD_ALERT], "color": C["success_bg"]},
                {"range": [THRESHOLD_ALERT, THRESHOLD_CRITICAL], "color": C["warning_bg"]},
                {"range": [THRESHOLD_CRITICAL, 100], "color": C["danger_bg"]},
            ],
            "threshold": {"line": {"color": C["danger"], "width": 3}, "thickness": 0.75, "value": THRESHOLD_ALERT},
        },
    ))
    fig.update_layout(height=230, margin=dict(l=20, r=20, t=40, b=10),
                       paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"))
    return fig


def creer_courbe_evolution(df: pd.DataFrame) -> go.Figure:
    df_plot = df.dropna(subset=["date_heure"]).sort_values("date_heure")
    colors = df_plot["statut_ia"].map({"PASS": C["success"], "FAIL": C["danger"]}).fillna(C["ink_soft"])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=df_plot["date_heure"], y=df_plot["score_risque"], mode="lines+markers",
        name="Score", line=dict(color=C["navy"], width=1.6),
        marker=dict(size=6, color=colors, symbol="circle", line=dict(width=0)),
        hovertemplate="<b>%{text}</b><br>Score: %{y:.1f}%<br>%{x}<extra></extra>",
        text=df_plot["identifiant_carte"],
    ))
    fig.add_hline(y=THRESHOLD_CRITICAL, line_dash="dot", line_color=C["danger"], line_width=1,
                  annotation_text=t("critical"), annotation_font=dict(size=10, color=C["danger"]),
                  annotation_position="top right")
    fig.add_hline(y=THRESHOLD_ALERT, line_dash="dot", line_color=C["warning"], line_width=1,
                  annotation_text=t("alert"), annotation_font=dict(size=10, color=C["warning"]),
                  annotation_position="top right")
    fig.add_hrect(y0=THRESHOLD_CRITICAL, y1=100, fillcolor=C["danger"], opacity=0.05, line_width=0)

    fig.update_layout(
        height=380, template="plotly_white", xaxis_title=None, yaxis_title="Score (%)",
        hovermode="x unified", showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family="Inter", color=C["ink_soft"], size=11),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor=C["border"])
    return fig


def creer_camembert_statuts(df: pd.DataFrame) -> go.Figure:
    counts = df["statut_ia"].value_counts()
    color_map = {"PASS": C["success"], "FAIL": C["danger"]}
    fig = go.Figure(data=[go.Pie(
        labels=counts.index, values=counts.values,
        marker=dict(colors=[color_map.get(l, C["ink_soft"]) for l in counts.index],
                    line=dict(color="white", width=2)),
        textposition="inside", textinfo="percent", textfont=dict(family="IBM Plex Mono", size=11, color="white"),
        hole=0.55, showlegend=True,
    )])
    fig.update_layout(
        height=190, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, font=dict(size=10, family="Inter")),
        font=dict(family="Inter"),
    )
    return fig


# ============================================================================
# 6. SIDEBAR
# ============================================================================

def render_sidebar() -> dict:
    with st.sidebar:
        logo_file = Path(LOGO_PATH)
        if logo_file.exists():
            st.image(str(logo_file), use_container_width=True)
        else:
            st.markdown(
                f"""<div style="padding:0.4rem 0 1rem 0; border-bottom:1px solid {C['border']}; margin-bottom:0.8rem;">
                <div style="font-family:'IBM Plex Sans',sans-serif; font-weight:700; font-size:1.05rem;
                            letter-spacing:2px; color:{C['navy']};">{APP_NAME}</div>
                <div style="font-size:0.75rem; color:{C['ink_soft']};">{APP_LINE} · {APP_UNIT}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        lang_choice = st.radio("Language", options=["FR", "EN"], horizontal=True, label_visibility="collapsed")
        st.session_state["lang"] = "fr" if lang_choice == "FR" else "en"

        menu = option_menu(
            menu_title=None,
            options=t("nav"),
            icons=["bar-chart-line", "graph-up", "clock-history", "sliders"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": C["navy"], "font-size": "15px"},
                "nav-link": {"font-size": "13.5px", "text-align": "left", "margin": "1px 0",
                             "--hover-color": C["bg"]},
                "nav-link-selected": {"background-color": C["navy_soft"], "color": C["navy"], "font-weight": "600"},
            },
        )

        st.markdown(f'<div class="side-label">{t("filters")}</div>', unsafe_allow_html=True)

        period_map = t("period_opts")
        periode_label = st.selectbox(t("period"), options=list(period_map.values()))
        periode_key = next(k for k, v in period_map.items() if v == periode_label)

        statut_filtre = st.multiselect(t("status"), options=["PASS", "FAIL"], default=["PASS", "FAIL"])
        score_range = st.slider(t("score_range"), min_value=0, max_value=100, value=(0, 100), step=5)
        recherche = st.text_input(t("search"), placeholder=t("search_ph"))

        st.markdown(f'<div class="side-label">{t("updated")}</div>', unsafe_allow_html=True)
        auto_refresh = st.toggle(t("auto_refresh"), value=False)
        refresh_interval = 10
        if auto_refresh:
            refresh_interval = st.select_slider(t("interval"), options=[5, 10, 15, 30, 60], value=10)

        if st.button(t("refresh_now"), use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown(
            f'<div class="mono" style="font-size:0.72rem; color:{C["ink_soft"]}; margin-top:0.8rem;">'
            f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
            unsafe_allow_html=True,
        )

        return {
            "menu": menu, "periode_key": periode_key, "statut_filtre": statut_filtre,
            "score_range": score_range, "recherche": recherche,
            "auto_refresh": auto_refresh, "refresh_interval": refresh_interval,
        }


# ============================================================================
# 7. PAGE SECTIONS
# ============================================================================

def render_topbar(is_live: bool) -> None:
    dot_class = "pulse-dot" if is_live else "pulse-dot off"
    status_text = t("live") if is_live else t("offline")
    st.markdown(
        f"""
        <div class="topbar">
            <div>
                <p class="brand">{APP_NAME}</p>
                <p class="subline">{APP_LINE} — {APP_UNIT}</p>
            </div>
            <div class="status">
                <span class="{dot_class}"></span>{status_text}
                &nbsp;·&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(index: str, title: str) -> None:
    st.markdown(f'<div class="sec"><span class="idx">{index}</span><span class="title">{title}</span></div>',
                unsafe_allow_html=True)


def render_kpis(df: pd.DataFrame, stats: dict) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""<div class="kpi"><div class="kpi-bar" style="background:{C['navy']};"></div>
            <div class="kpi-label">{t('kpi_total')}</div>
            <div class="kpi-value">{stats['total']}</div></div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div class="kpi"><div class="kpi-bar" style="background:{C['success']};"></div>
            <div class="kpi-label">{t('kpi_pass')}</div>
            <div class="kpi-value">{stats['pass_rate']:.1f}%</div>
            <div class="kpi-sub pos">↑ {stats['passes']} {t('ok_units')}</div></div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""<div class="kpi"><div class="kpi-bar" style="background:{C['danger']};"></div>
            <div class="kpi-label">{t('kpi_fail')}</div>
            <div class="kpi-value">{stats['taux_defaut']:.1f}%</div>
            <div class="kpi-sub neg">↓ {stats['failures']} {t('fail_units')}</div></div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""<div class="kpi"><div class="kpi-bar" style="background:{C['warning']};"></div>
            <div class="kpi-label">{t('kpi_score')}</div>
            <div class="kpi-value">{stats['score_moyen']:.1f}%</div>
            <div class="kpi-sub">{t('max_lbl')} {stats['score_max']:.1f}%</div></div>""", unsafe_allow_html=True)

    with col5:
        if not df.empty:
            derniere = df.iloc[0]
            statut = derniere.get("statut_ia", "N/A")
            tag_class = {"PASS": "tag-pass", "FAIL": "tag-fail"}.get(statut, "tag-na")
            score_val = derniere.get("score_risque", np.nan)
            score_txt = f"{score_val:.1f}%" if pd.notna(score_val) else "N/A"
            carte = derniere.get("identifiant_carte", "N/A")
            st.markdown(f"""<div class="kpi"><div class="kpi-bar" style="background:{C['steel']};"></div>
                <div class="kpi-label">{t('kpi_last')}</div>
                <div style="margin:0.35rem 0;"><span class="tag {tag_class}">{statut}</span></div>
                <div class="kpi-sub">{score_txt} · {carte}</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="kpi"><div class="kpi-label">{t('kpi_last')}</div>
                <div class="kpi-sub">—</div></div>""", unsafe_allow_html=True)


def render_analyse_performances(df: pd.DataFrame, stats: dict) -> None:
    section_title("01", t("sec_perf"))
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        if not df.empty and {"date_heure", "score_risque"}.issubset(df.columns) and df["score_risque"].notna().any():
            st.plotly_chart(creer_courbe_evolution(df), use_container_width=True)
        else:
            st.markdown(f'<div class="info-banner">{t("no_data_filtered")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.plotly_chart(creer_gauge(stats["score_moyen"]), use_container_width=True)
        if not df.empty and df["statut_ia"].notna().any():
            st.plotly_chart(creer_camembert_statuts(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_analyse_mesures(df: pd.DataFrame) -> list[str]:
    section_title("02", t("sec_measures"))
    cols_existantes = [c for c in MEASURE_COLUMNS if c in df.columns and df[c].notna().any()]

    if not cols_existantes:
        st.markdown(f'<div class="info-banner">{t("no_measures")}</div>', unsafe_allow_html=True)
        return []

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'<div class="panel"><b style="font-size:0.85rem;">{t("distribution")}</b>', unsafe_allow_html=True)
        fig = go.Figure()
        for col in cols_existantes[:4]:
            fig.add_trace(go.Box(y=df[col], name=col, boxmean="sd", marker_color=C["navy"],
                                  line=dict(color=C["steel"], width=1)))
        fig.update_layout(height=330, template="plotly_white", showlegend=False,
                           margin=dict(l=10, r=10, t=15, b=10), yaxis_title=None,
                           font=dict(family="Inter", size=10, color=C["ink_soft"]),
                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        fig.update_yaxes(gridcolor=C["border"])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="panel"><b style="font-size:0.85rem;">{t("stats_desc")}</b><br><br>', unsafe_allow_html=True)
        stats_df = df[cols_existantes].describe().round(3)
        try:
            styled = stats_df.style.background_gradient(cmap="Blues", subset=["mean", "50%"])
        except Exception:  # noqa: BLE001
            styled = stats_df
        st.dataframe(styled, use_container_width=True, height=310)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="panel"><b style="font-size:0.85rem;">{t("correlation")}</b>', unsafe_allow_html=True)
        if len(cols_existantes) > 1:
            corr = df[cols_existantes].corr()
            fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
            fig.update_layout(height=330, margin=dict(l=10, r=10, t=15, b=10),
                               font=dict(family="Inter", size=9, color=C["ink_soft"]),
                               paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f'<div class="info-banner">{t("need_2")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_table(df: pd.DataFrame, cols_mesures: list[str]) -> None:
    section_title("03", t("sec_table"))

    if df.empty:
        st.markdown(f'<div class="info-banner">{t("no_data_filtered")}</div>', unsafe_allow_html=True)
        return

    colonnes = [c for c in (["identifiant_carte", "date_heure", "statut_ia", "score_risque"] + cols_mesures[:3])
                if c in df.columns]
    df_display = df.head(20)[colonnes].copy()
    if "date_heure" in df_display.columns:
        df_display["date_heure"] = df_display["date_heure"].dt.strftime("%Y-%m-%d %H:%M")

    def style_status(val):
        if val == "PASS":
            return f"background-color:{C['success_bg']}; color:{C['success']}; font-weight:600;"
        if val == "FAIL":
            return f"background-color:{C['danger_bg']}; color:{C['danger']}; font-weight:600;"
        return ""

    def style_score(val):
        if pd.isna(val):
            return ""
        if val <= THRESHOLD_ALERT:
            return f"background-color:{C['success_bg']}; color:{C['success']};"
        if val <= THRESHOLD_CRITICAL:
            return f"background-color:{C['warning_bg']}; color:{C['warning']};"
        return f"background-color:{C['danger_bg']}; color:{C['danger']};"

    styler = df_display.style
    apply_fn = getattr(styler, "map", None) or styler.applymap
    if "statut_ia" in df_display.columns:
        styler = apply_fn(style_status, subset=["statut_ia"])
    if "score_risque" in df_display.columns:
        apply_fn2 = getattr(styler, "map", None) or styler.applymap
        styler = apply_fn2(style_score, subset=["score_risque"])

    st.dataframe(
        styler, use_container_width=True, height=300,
        column_config={
            "identifiant_carte": t("col_card"),
            "date_heure": t("col_dt"),
            "statut_ia": t("col_status"),
            "score_risque": st.column_config.NumberColumn(t("col_score"), format="%.1f%%"),
        },
    )

    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(t("export"), data=csv_data,
                        file_name=f"sagemcom_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv")


def render_footer() -> None:
    st.markdown(
        f'<div class="footer-line">{APP_NAME} · {APP_LINE} {APP_UNIT} · v{APP_VERSION} — {t("footer")}</div>',
        unsafe_allow_html=True,
    )


# ============================================================================
# 8. ENTRY POINT
# ============================================================================

def main() -> None:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "fr"

    inject_css()
    filtres = render_sidebar()

    result = charger_donnees(DB_PATH, TABLE_NAME)
    render_topbar(is_live=result.error is None and not result.df.empty)

    if result.error:
        st.error(result.error)
        st.markdown(f'<div class="info-banner">{t("waiting")}</div>', unsafe_allow_html=True)
        st.stop()

    if result.df.empty:
        st.markdown(f'<div class="info-banner">{t("no_data")}</div>', unsafe_allow_html=True)
        st.stop()

    df = appliquer_filtres(result.df, filtres["periode_key"], filtres["statut_filtre"],
                            filtres["score_range"], filtres["recherche"])

    if df.empty:
        st.markdown(f'<div class="info-banner">{t("no_data_filtered")}</div>', unsafe_allow_html=True)
        render_footer()
        st.stop()

    stats = calculer_statistiques(df)

    render_kpis(df, stats)
    st.markdown("<br>", unsafe_allow_html=True)
    render_analyse_performances(df, stats)
    cols_mesures = render_analyse_mesures(df)
    render_table(df, cols_mesures)
    render_footer()

    if filtres["auto_refresh"]:
        st.caption(t("next_refresh").format(s=filtres["refresh_interval"]))
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=filtres["refresh_interval"] * 1000, key="auto_refresh_timer")
        except ImportError:
            import time
            time.sleep(filtres["refresh_interval"])
            st.rerun()


if __name__ == "__main__":
    main()