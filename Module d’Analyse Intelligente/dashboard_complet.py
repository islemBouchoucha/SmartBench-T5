import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import numpy as np
from streamlit_option_menu import option_menu

# ============================================================================
# CONFIGURATION DE LA PAGE - STYLE PROFESSIONNEL
# ============================================================================
st.set_page_config(
    page_title="Sagemcom - Banc de Test Intelligent",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONNALISÉ - CHARTE GRAPHIQUE SAGEMCOM
# ============================================================================
st.markdown("""
<style>
    /* Palette de couleurs Sagemcom */
    :root {
        --sagemcom-blue: #004B87;
        --sagemcom-light-blue: #0072B0;
        --sagemcom-dark-blue: #002D5A;
        --sagemcom-orange: #F58220;
        --sagemcom-green: #00A651;
        --sagemcom-red: #E61E2A;
        --sagemcom-gray: #6D6E71;
        --sagemcom-light-gray: #F0F2F5;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(90deg, #004B87 0%, #0072B0 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,75,135,0.3);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: 1px;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.8) !important;
        margin: 0 !important;
        font-size: 1.1rem;
    }
    
    /* Cartes KPI */
    .kpi-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #004B87;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .kpi-label {
        color: #6D6E71;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-value {
        color: #004B87;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.3rem 0 0 0;
    }
    
    .kpi-delta {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .kpi-delta.positive {
        color: #00A651;
    }
    
    .kpi-delta.negative {
        color: #E61E2A;
    }
    
    /* Status badges */
    .badge-pass {
        background: #00A651;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .badge-fail {
        background: #E61E2A;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    .badge-warning {
        background: #F58220;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    /* Section titles */
    .section-title {
        color: #004B87;
        font-size: 1.3rem;
        font-weight: 600;
        border-bottom: 3px solid #F58220;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #F8FAFC;
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Table */
    .dataframe {
        font-size: 0.9rem !important;
    }
    
    .dataframe thead tr th {
        background: #004B87 !important;
        color: white !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCTIONS
# ============================================================================
@st.cache_data(ttl=5)
def charger_donnees():
    """Charge les données depuis SQLite"""
    try:
        conn = sqlite3.connect("base_production.db")
        df = pd.read_sql_query("SELECT * FROM Historique_Tests ORDER BY id DESC", conn)
        conn.close()
        
        if not df.empty and 'mesures_brutes' in df.columns:
            mesures_df = df['mesures_brutes'].apply(
                lambda x: pd.Series(json.loads(x)) if x and x != '{}' else pd.Series()
            )
            df = pd.concat([df, mesures_df], axis=1)
        
        # Conversion des dates
        if 'date_heure' in df.columns:
            df['date_heure'] = pd.to_datetime(df['date_heure'])
        
        return df
    except Exception as e:
        st.error(f"Erreur de chargement: {e}")
        return pd.DataFrame()

def get_stats(df):
    """Calcule les statistiques"""
    if df.empty:
        return {}
    
    total = len(df)
    failures = len(df[df['statut_ia'] == 'FAIL'])
    passes = total - failures
    
    return {
        'total': total,
        'passes': passes,
        'failures': failures,
        'taux_defaut': (failures / total * 100) if total > 0 else 0,
        'score_moyen': df['score_risque'].mean() if 'score_risque' in df else 0,
        'score_max': df['score_risque'].max() if 'score_risque' in df else 0,
        'score_min': df['score_risque'].min() if 'score_risque' in df else 0,
        'pass_rate': (passes / total * 100) if total > 0 else 0,
    }

def create_gauge(score):
    """Crée un gauge pour le score de risque"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Score de Risque", 'font': {'size': 14}},
        delta = {'reference': 50, 'increasing': {'color': "#E61E2A"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#6D6E71"},
            'bar': {'color': "#004B87"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#6D6E71",
            'steps': [
                {'range': [0, 30], 'color': '#00A651'},
                {'range': [30, 70], 'color': '#F58220'},
                {'range': [70, 100], 'color': '#E61E2A'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    # Logo Sagemcom (texte)
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0; border-bottom: 2px solid #004B87;">
        <h1 style="color: #004B87; font-size: 1.8rem; margin: 0;">🏭 SAGEMCOM</h1>
        <p style="color: #6D6E71; font-size: 0.9rem; margin: 0;">Banc de Test Intelligent</p>
        <p style="color: #6D6E71; font-size: 0.8rem; margin: 0;">TF GTW T5 - Version 1.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    menu = option_menu(
        menu_title=None,
        options=["Dashboard", "Analyse Détaillée", "Historique", "Configuration"],
        icons=["speedometer2", "graph-up-arrow", "clock-history", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#004B87", "font-size": "18px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "#004B87"},
        }
    )
    
    st.markdown("---")
    
    # Filtres
    st.markdown("### 🔍 Filtres")
    
    periode = st.selectbox(
        "📅 Période",
        ["Tout l'historique", "24h", "7 jours", "30 jours", "Ce mois"]
    )
    
    statut_filtre = st.multiselect(
        "📊 Statut",
        options=['PASS', 'FAIL'],
        default=['PASS', 'FAIL']
    )
    
    score_range = st.slider(
        "🎯 Score de risque",
        min_value=0,
        max_value=100,
        value=(0, 100),
        step=5
    )
    
    auto_refresh = st.toggle("🔄 Auto-refresh", value=True)
    if auto_refresh:
        st.caption("⏱️ Mise à jour toutes les 5 secondes")
    
    if st.button("🔄 Rafraîchir", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# ============================================================================
# CHARGEMENT DES DONNÉES
# ============================================================================
df = charger_donnees()

if df.empty:
    st.warning("⚠️ Aucune donnée disponible. Commencez les tests !")
    st.stop()

# Application des filtres
if not df.empty:
    # Filtre période
    now = datetime.now()
    if periode == "24h":
        df = df[df['date_heure'] > (now - timedelta(hours=24))]
    elif periode == "7 jours":
        df = df[df['date_heure'] > (now - timedelta(days=7))]
    elif periode == "30 jours":
        df = df[df['date_heure'] > (now - timedelta(days=30))]
    elif periode == "Ce mois":
        df = df[df['date_heure'].dt.month == now.month]
    
    # Filtre statut
    if statut_filtre:
        df = df[df['statut_ia'].isin(statut_filtre)]
    
    # Filtre score
    if 'score_risque' in df.columns:
        df = df[(df['score_risque'] >= score_range[0]) & 
                (df['score_risque'] <= score_range[1])]

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>📊 Banc de Test Intelligent TF GTW T5</h1>
    <p>Supervision en temps réel · Contrôle qualité automatisé · IA intégrée</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# KPI CARDS
# ============================================================================
stats = get_stats(df)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📦 Cartes testées</div>
        <div class="kpi-value">{stats.get('total', 0)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #00A651;">
        <div class="kpi-label">✅ Taux de conformité</div>
        <div class="kpi-value" style="color: #00A651;">{stats.get('pass_rate', 0):.1f}%</div>
        <div class="kpi-delta positive">↑ {stats.get('passes', 0)} cartes OK</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #E61E2A;">
        <div class="kpi-label">❌ Taux de défaut</div>
        <div class="kpi-value" style="color: #E61E2A;">{stats.get('taux_defaut', 0):.1f}%</div>
        <div class="kpi-delta negative">⚠️ {stats.get('failures', 0)} cartes FAIL</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #F58220;">
        <div class="kpi-label">📊 Score de risque moyen</div>
        <div class="kpi-value" style="color: #F58220;">{stats.get('score_moyen', 0):.1f}%</div>
        <div class="kpi-delta">Max: {stats.get('score_max', 0):.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    derniere = df.iloc[0] if not df.empty else None
    if derniere is not None:
        status_class = "badge-pass" if derniere['statut_ia'] == 'PASS' else "badge-fail"
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #004B87;">
            <div class="kpi-label">🕐 Dernier test</div>
            <div style="margin: 0.3rem 0;">
                <span class="{status_class}">{derniere['statut_ia']}</span>
            </div>
            <div style="font-size: 0.85rem; color: #6D6E71;">
                Score: {derniere.get('score_risque', 0):.1f}%
            </div>
            <div style="font-size: 0.75rem; color: #6D6E71;">
                {derniere['identifiant_carte']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# SECTION: ANALYSE PRINCIPALE
# ============================================================================
st.markdown('<div class="section-title">📈 Analyse des performances</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Graphique d'évolution
    if not df.empty and 'date_heure' in df.columns and 'score_risque' in df.columns:
        df_plot = df.copy().sort_values('date_heure')
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Ligne des scores
        colors = df_plot['statut_ia'].map({'PASS': '#00A651', 'FAIL': '#E61E2A'})
        
        fig.add_trace(
            go.Scatter(
                x=df_plot['date_heure'],
                y=df_plot['score_risque'],
                mode='lines+markers',
                name='Score de risque',
                line=dict(color='#004B87', width=2),
                marker=dict(size=8, color=colors, symbol='circle'),
                hovertemplate='<b>%{text}</b><br>' +
                              'Score: %{y:.1f}%<br>' +
                              'Date: %{x}<br>',
                text=df_plot['identifiant_carte']
            )
        )
        
        # Seuil d'alerte
        fig.add_hline(
            y=70, 
            line_dash="dash", 
            line_color="#E61E2A",
            annotation_text="🔴 Seuil critique",
            annotation_position="top right"
        )
        fig.add_hline(
            y=50,
            line_dash="dash",
            line_color="#F58220",
            annotation_text="⚠️ Seuil d'alerte",
            annotation_position="top right"
        )
        
        # Zone de risque
        fig.add_hrect(
            y0=70, y1=100,
            fillcolor="#E61E2A",
            opacity=0.1,
            line_width=0,
            annotation_text="Zone critique"
        )
        
        fig.update_layout(
            height=400,
            template='plotly_white',
            xaxis_title="Date",
            yaxis_title="Score de risque (%)",
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Gauge du score moyen
    fig_gauge = create_gauge(stats.get('score_moyen', 0))
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Distribution des statuts
    if not df.empty:
        pie_data = df['statut_ia'].value_counts()
        fig_pie = go.Figure(data=[go.Pie(
            labels=pie_data.index,
            values=pie_data.values,
            marker=dict(colors=['#00A651', '#E61E2A']),
            textposition='inside',
            textinfo='percent+label',
            hole=0.4,
            showlegend=False
        )])
        fig_pie.update_layout(
            height=180,
            margin=dict(l=10, r=10, t=20, b=20),
            template='plotly_white',
            title_text="Répartition PASS/FAIL",
            title_font=dict(size=12)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ============================================================================
# SECTION: ANALYSE DES MESURES
# ============================================================================
st.markdown('<div class="section-title">🔬 Analyse détaillée des mesures</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📊 Boxplot des mesures")
    colonnes_mesures = ['Tension (V)', 'Courant (mA)', 'Gain mes1 (dB)', 
                       'Gain mes2 (dB)', 'Gain mes3 (dB)', 'Puissance (W)', 
                       'RMS (Vrms)', "Température('C)"]
    
    cols_existantes = [col for col in colonnes_mesures if col in df.columns]
    
    if cols_existantes:
        fig = go.Figure()
        for col in cols_existantes[:4]:  # Afficher 4 premières
            fig.add_trace(go.Box(
                y=df[col],
                name=col,
                boxmean='sd',
                marker_color='#004B87'
            ))
        
        fig.update_layout(
            height=350,
            template='plotly_white',
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis_title="Valeur"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### 📋 Statistiques des mesures")
    if cols_existantes:
        stats_df = df[cols_existantes].describe().round(3)
        st.dataframe(
            stats_df.style.background_gradient(cmap='Blues', subset=['mean', '50%']),
            use_container_width=True,
            height=350
        )

with col3:
    st.markdown("#### 🎯 Corrélation")
    if len(cols_existantes) > 1:
        corr = df[cols_existantes].corr()
        
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            title="Matrice de corrélation"
        )
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# SECTION: DERNIERS TESTS
# ============================================================================
st.markdown('<div class="section-title">🔄 Derniers tests effectués</div>', unsafe_allow_html=True)

# Tableau stylisé
if not df.empty:
    df_display = df.head(20)[['identifiant_carte', 'date_heure', 'statut_ia', 
                              'score_risque'] + cols_existantes[:3] if cols_existantes else []].copy()
    
    if 'date_heure' in df_display.columns:
        df_display['date_heure'] = df_display['date_heure'].dt.strftime('%d/%m/%Y %H:%M')
    
    # Style conditionnel
    def style_status(val):
        if val == 'PASS':
            return 'background-color: #00A65120; color: #00A651; font-weight: bold;'
        return 'background-color: #E61E2A20; color: #E61E2A; font-weight: bold;'
    
    def style_score(val):
        if val <= 30:
            return 'background-color: #00A65120; color: #00A651;'
        elif val <= 70:
            return 'background-color: #F5822020; color: #F58220;'
        return 'background-color: #E61E2A20; color: #E61E2A;'
    
    styled_df = df_display.style.applymap(style_status, subset=['statut_ia'])
    if 'score_risque' in df_display.columns:
        styled_df = styled_df.applymap(style_score, subset=['score_risque'])
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=300,
        column_config={
            "identifiant_carte": "🆔 Carte",
            "date_heure": "📅 Date/Heure",
            "statut_ia": "📊 Statut",
            "score_risque": "🎯 Score",
        }
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div style="text-align: center; color: #6D6E71; font-size: 0.8rem; padding: 1rem 0;">
        <strong>🏭 Sagemcom</strong> · Banc de Test Intelligent TF GTW T5<br>
        Version 1.0 · {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br>
        <span style="font-size: 0.7rem;">Système de supervision par Intelligence Artificielle</span>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# AUTO-REFRESH
# ============================================================================
if auto_refresh:
    import time
    time.sleep(5)
    st.rerun()