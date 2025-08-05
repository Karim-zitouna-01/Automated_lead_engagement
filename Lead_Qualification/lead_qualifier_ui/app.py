import streamlit as st
import requests
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# === Configuration de la page ===
st.set_page_config(
    page_title="Qualification de Leads B2B", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Thème personnalisé bleu marine moderne ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1e3a5f 50%, #2c5282 100%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    /* Remove white header */
    .stApp > header {
        background: transparent !important;
    }
    
    .stApp > header .stApp-header {
        background: transparent !important;
    }

    .stSidebar {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
        border-right: 2px solid #4a5568;
    }

    .stSidebar .stSidebar-content {
        background: transparent;
    }

    /* Remove any white backgrounds */
    .main .block-container {
        padding-top: 1rem;
        background: transparent;
    }

    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }

    .hero-title {
        background: linear-gradient(90deg, #63b3ed, #4299e1, #3182ce);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }

    .hero-subtitle {
        color: #cbd5e0;
        font-size: 1.2rem;
        font-weight: 300;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Cards et containers */
    .custom-card {
        background: rgba(45, 55, 72, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(74, 85, 104, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        border-color: rgba(99, 179, 237, 0.5);
    }

    /* Métriques personnalisées */
    .metric-container {
        background: linear-gradient(135deg, #4299e1, #3182ce);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(66, 153, 225, 0.3);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }

    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    /* Classifications des leads */
    .hot-lead {
        background: linear-gradient(135deg, #f56565, #e53e3e);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(245, 101, 101, 0.4);
        animation: pulse-hot 2s infinite;
    }

    .cold-lead {
        background: linear-gradient(135deg, #718096, #4a5568);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(113, 128, 150, 0.3);
    }

    @keyframes pulse-hot {
        0%, 100% { box-shadow: 0 4px 15px rgba(245, 101, 101, 0.4); }
        50% { box-shadow: 0 4px 25px rgba(245, 101, 101, 0.6); }
    }

    /* Justifications */
    .justification {
        background: rgba(45, 55, 72, 0.8);
        border-left: 4px solid #4299e1;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Company header */
    .company-header {
        background: linear-gradient(90deg, rgba(66, 153, 225, 0.2), rgba(49, 130, 206, 0.1));
        border: 1px solid rgba(66, 153, 225, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1.5rem 0 1rem 0;
    }

    .company-name {
        font-size: 1.5rem;
        font-weight: 600;
        color: #63b3ed;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Sidebar styling */
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #63b3ed !important;
    }

    .stSidebar .stFileUploader label {
        color: #e2e8f0 !important;
        font-weight: 500;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4299e1, #3182ce);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #3182ce, #2c5282);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(66, 153, 225, 0.4);
    }

    /* File uploader */
    .stFileUploader {
        background: rgba(45, 55, 72, 0.5);
        border: 2px dashed rgba(99, 179, 237, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    /* Error and warning messages */
    .stAlert {
        border-radius: 12px;
        border: none;
    }

    /* Dividers */
    .stDivider {
        border-color: rgba(74, 85, 104, 0.3) !important;
        margin: 2rem 0;
    }

    /* DataFrames */
    .stDataFrame {
        background: rgba(45, 55, 72, 0.8);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Progress indicators */
    .progress-ring {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(99, 179, 237, 0.3);
        border-top: 4px solid #63b3ed;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Score indicators */
    .score-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# === Hero Section ===
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">🧠 B2B Lead Qualification Tool</h1>
   
</div>
""", unsafe_allow_html=True)

st.markdown("""
    ## 🚀 Ready to Get Started?
    
    **Simply upload your files in the sidebar and click "Start Qualification" to begin analyzing your leads with AI-powered precision.**
    

    ---
   
    """)
# === Sidebar améliorée ===
with st.sidebar:
    st.markdown("### 📥 Configuration")
    
    st.markdown("#### 📊 Ideal Customer Profile (ICP)")
    icp_file = st.file_uploader(
        "Upload your ICP file",
        type="json",
        help="JSON file containing your ideal customer definition"
    )
    
    st.markdown("#### 📋 Lead Reports")
    lead_files = st.file_uploader(
        "Upload your lead reports",
        type="txt",
        accept_multiple_files=True,
        help="One or more .txt files containing lead information"
    )
    
    st.markdown("---")
    
    if st.button("🚀 Start Qualification", type="primary"):
        if not icp_file or not lead_files:
            st.error("❗ Please upload both ICP and at least one lead report.")
        else:
            with st.spinner("🔄 Processing leads..."):
                # Sauvegarde de l'ICP
                os.makedirs("data", exist_ok=True)
                icp_data = json.load(icp_file)
                with open("data/icp.json", "w", encoding="utf-8") as f:
                    json.dump(icp_data, f, indent=2, ensure_ascii=False)

                results = []
                progress_bar = st.progress(0)
                
                for i, lead_file in enumerate(lead_files):
                    files = {"file": (lead_file.name, lead_file.read(), "text/plain")}
                    try:
                        response = requests.post("http://localhost:8000/api/process_lead", files=files)
                        if response.status_code == 200:
                            results.append(response.json())
                        else:
                            st.warning(f"⚠️ Error for `{lead_file.name}` : {response.json().get('detail')}")
                    except Exception as e:
                        st.error(f"❌ API Error : {str(e)}")
                    
                    progress_bar.progress((i + 1) / len(lead_files))
                
                st.session_state['results'] = results

# === Affichage des résultats ===
if 'results' in st.session_state and st.session_state['results']:
    results = st.session_state['results']
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Qualification Dashboard")
    
    # Création du DataFrame
    df = pd.DataFrame([{
        "Company": res["company"],
        "Score": res["scores"]["final_score"],
        "Classification": res["classification"].upper(),
        "Justification": res["justification"]
    } for res in results])

    # Métriques principales
    count_hot = (df["Classification"] == "HOT").sum()
    count_cold = (df["Classification"] == "COLD").sum()
    count_total = len(df)
    percent_hot = round((count_hot / count_total) * 100, 1)
    avg_score = round(df["Score"].mean(), 1)

    # Affichage des métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">🔥 {count_hot}</div>
            <div class="metric-label">HOT Leads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">❄️ {count_cold}</div>
            <div class="metric-label">COLD Leads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{percent_hot}%</div>
            <div class="metric-label">Conversion Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{avg_score}</div>
            <div class="metric-label">Average Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Graphiques
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # Graphique en secteurs
        fig_pie = px.pie(
            df,
            names="Classification",
            title="🎯 Classification Distribution",
            color="Classification",
            color_discrete_map={
                "HOT": "#f56565",
                "COLD": "#718096"
            },
            hole=0.4
        )
        
        fig_pie.update_traces(
            textfont_color='white',
            textfont_size=14,
            textposition="outside"
        )
        
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16,
            title_x=0.5,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # Graphique des scores
        fig_bar = px.bar(
            df,
            x="Company",
            y="Score",
            color="Classification",
            title="📈 Scores by Company",
            color_discrete_map={
                "HOT": "#f56565",
                "COLD": "#718096"
            }
        )
        
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16,
            title_x=0.5,
            xaxis_title="Companies",
            yaxis_title="Score (/100)"
        )
        
        fig_bar.update_traces(texttemplate='%{y}', textposition='outside')
        
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Liste détaillée des leads
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("## 📋 Qualified Leads Details")
    
    for index, row in df.iterrows():
        is_hot = row["Classification"] == "HOT"
        icon = "🔥" if is_hot else "❄️"
        css_class = "hot-lead" if is_hot else "cold-lead"
        
        st.markdown(f"""
        <div class="company-header">
            <div class="company-name">🏢 {row['Company']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(
                f'<div class="{css_class}">{icon} {row["Classification"]}</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f'<div class="score-badge">📊 Score: <strong>{row["Score"]}/100</strong></div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            f'<div class="justification">💡 <strong>Analysis:</strong><br>{row["Justification"]}</div>',
            unsafe_allow_html=True
        )
        
        st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Page d'accueil simplifiée
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)