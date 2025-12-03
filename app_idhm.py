# app_idhm.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    layout="wide",
    page_title="Dashboard IDHM vs Maternidade",
    page_icon="👶",
    initial_sidebar_state="expanded"
)

# =============================================================================
# NOVAS CORES - TEMA CLARO MODERNO
# =============================================================================
# Cores principais
CORES = {
    "fundo": "#FAF7F3",           # Off-white quente
    "texto_principal": "#1F3A5F", # Azul profundo
    "detalhes_ui": "#E8DCCF",     # Off-white secundário
    "grafico_idhm": "#5DA9E9",    # Azul claro
    "grafico_maes": "#F4B6C2",    # Rosa claro suave
    "alertas": "#FFD166",         # Amarelo suave
    "destaques": "#FF9F1C",       # Amarelo mais forte
    "grid_lines": "#E8DCCF",      # Grid lines
    "tooltip": "#1F3A5F",         # Tooltip
    "branco": "#FFFFFF",
    "cinza_claro": "#F0F0F0",
    "cinza_medio": "#D0D0D0",
    "cinza_escuro": "#888888"
}

# Cores das regiões (versão clara)
REGIAO_CORES = {
    'NORTE': '#FF6B6B',        # Vermelho suave
    'NORDESTE': '#FFA726',     # Laranja suave
    'CENTRO-OESTE': '#4CAF50', # Verde suave
    'SUDESTE': '#42A5F5',      # Azul suave
    'SUL': '#AB47BC',          # Roxo suave
    'Outro': '#78909C'         # Cinza azulado
}

# =============================================================================
# CSS ESTILO CLARO MODERNO
# =============================================================================
st.markdown(f"""
<style>
    /* Tema claro moderno */
    .stApp {{
        background: {CORES['fundo']} !important;
    }}
    
    /* Cards de métricas com gradiente azul suave */
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, {CORES['grafico_idhm']}15, {CORES['grafico_maes']}15);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 2px solid {CORES['detalhes_ui']};
        margin: 10px;
    }}
    
    div[data-testid="stMetric"] label {{
        color: {CORES['texto_principal']} !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {CORES['texto_principal']} !important;
        font-size: 32px !important;
        font-weight: bold !important;
    }}
    
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
        color: {CORES['destaques']} !important;
        font-weight: 600 !important;
    }}
    
    /* Títulos e headers */
    h1, h2, h3, h4 {{
        color: {CORES['texto_principal']} !important;
        font-weight: 700 !important;
    }}
    
    h1 {{
        background: linear-gradient(90deg, {CORES['grafico_idhm']}, {CORES['grafico_maes']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        margin-bottom: 10px !important;
    }}
    
    /* Sidebar claro */
    [data-testid="stSidebar"] {{
        background: {CORES['branco']} !important;
        border-right: 2px solid {CORES['detalhes_ui']};
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
    }}
    
    /* Labels dos filtros */
    .stSelectbox label, .stSlider label, .stRadio label {{
        color: {CORES['texto_principal']} !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 14px !important;
    }}
    
    /* Containers e boxes */
    .stAlert {{
        background: linear-gradient(135deg, {CORES['alertas']}20, {CORES['destaques']}10);
        border-left: 4px solid {CORES['alertas']};
        border-radius: 10px;
        color: {CORES['texto_principal']} !important;
    }}
    
    /* Tabelas */
    [data-testid="stDataFrame"] {{
        background: {CORES['branco']} !important;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid {CORES['detalhes_ui']};
    }}
    
    /* Botões */
    .stButton > button {{
        background: linear-gradient(135deg, {CORES['grafico_idhm']}, {CORES['grafico_idhm']}CC) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 8px rgba(93, 169, 233, 0.2) !important;
        padding: 10px 25px !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(93, 169, 233, 0.3) !important;
        background: linear-gradient(135deg, {CORES['grafico_idhm']}CC, {CORES['grafico_idhm']}) !important;
    }}
    
    /* Inputs e selects */
    .stSelectbox > div > div {{
        background: {CORES['branco']} !important;
        border: 2px solid {CORES['detalhes_ui']} !important;
        border-radius: 8px !important;
        color: {CORES['texto_principal']} !important;
    }}
    
    .stSlider [role="slider"] {{
        background: {CORES['grafico_idhm']} !important;
    }}
    
    /* Destaque para estado selecionado */
    .highlight-state {{
        background: linear-gradient(135deg, {CORES['grafico_idhm']}15, {CORES['grafico_maes']}15) !important;
        color: {CORES['texto_principal']} !important;
        font-weight: bold !important;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        border: 2px solid {CORES['detalhes_ui']};
    }}
    
    /* Cards de análise */
    .analysis-card {{
        background: {CORES['branco']};
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border-left: 5px solid {CORES['grafico_idhm']};
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        color: {CORES['texto_principal']};
    }}
    
    /* Scrollbar customizada */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {CORES['detalhes_ui']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, {CORES['grafico_idhm']}, {CORES['grafico_maes']});
        border-radius: 5px;
    }}
    
    /* Ícones grandes */
    .big-icon {{
        font-size: 3rem;
        color: {CORES['grafico_idhm']};
        text-align: center;
        display: block;
        margin-bottom: 15px;
    }}
    
    /* Tags de região */
    .tag-norte {{ background: linear-gradient(135deg, {REGIAO_CORES['NORTE']}40, {REGIAO_CORES['NORTE']}20); color: {REGIAO_CORES['NORTE']}; }}
    .tag-nordeste {{ background: linear-gradient(135deg, {REGIAO_CORES['NORDESTE']}40, {REGIAO_CORES['NORDESTE']}20); color: {REGIAO_CORES['NORDESTE']}; }}
    .tag-centro-oeste {{ background: linear-gradient(135deg, {REGIAO_CORES['CENTRO-OESTE']}40, {REGIAO_CORES['CENTRO-OESTE']}20); color: {REGIAO_CORES['CENTRO-OESTE']}; }}
    .tag-sudeste {{ background: linear-gradient(135deg, {REGIAO_CORES['SUDESTE']}40, {REGIAO_CORES['SUDESTE']}20); color: {REGIAO_CORES['SUDESTE']}; }}
    .tag-sul {{ background: linear-gradient(135deg, {REGIAO_CORES['SUL']}40, {REGIAO_CORES['SUL']}20); color: {REGIAO_CORES['SUL']}; }}
    
    .region-tag {{
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
        margin: 2px;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 1px solid currentColor;
    }}
    
    /* Separadores */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, {CORES['grafico_idhm']}, {CORES['grafico_maes']});
        margin: 30px 0;
        opacity: 0.3;
    }}
    
    /* Tabs personalizadas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        background-color: {CORES['detalhes_ui']};
        padding: 5px;
        border-radius: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        color: {CORES['texto_principal']};
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {CORES['branco']} !important;
        color: {CORES['texto_principal']} !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    
    /* Plotly theme modifications */
    .js-plotly-plot .plotly .modebar {{
        background: transparent !important;
    }}
    
    /* Tooltip styling */
    .hovertext {{
        background-color: {CORES['tooltip']} !important;
        color: white !important;
        border: 1px solid {CORES['detalhes_ui']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
@st.cache_data
def load_data():
    """Carrega e prepara os dados"""
    try:
        # Carregar seus dados
        df = pd.read_csv('dados_normalizados/comparacao_idhm_idade_mae.csv')
        
        # Criar IDHM geral se necessário
        if 'IDHM' not in df.columns:
            if all(col in df.columns for col in ['IDHM_Educacao', 'IDHM_Renda', 'IDHM_Longevidade']):
                df['IDHM'] = df[['IDHM_Educacao', 'IDHM_Renda', 'IDHM_Longevidade']].mean(axis=1)
        
        # Adicionar região
        regioes = {
            'NORTE': ['Acre', 'Amapá', 'Amazonas', 'Pará', 'Rondônia', 'Roraima', 'Tocantins'],
            'NORDESTE': ['Alagoas', 'Bahia', 'Ceará', 'Maranhão', 'Paraíba', 'Pernambuco', 
                        'Piauí', 'Rio Grande do Norte', 'Sergipe'],
            'CENTRO-OESTE': ['Distrito Federal', 'Goiás', 'Mato Grosso', 'Mato Grosso do Sul'],
            'SUDESTE': ['Espírito Santo', 'Minas Gerais', 'Rio de Janeiro', 'São Paulo'],
            'SUL': ['Paraná', 'Rio Grande do Sul', 'Santa Catarina']
        }
        
        df['Regiao'] = df['Estado'].apply(
            lambda x: next((regiao for regiao, estados in regioes.items() if x in estados), 'Outro')
        )
        
        # Ordenar faixas etárias
        faixa_order = [
            'Menor de 10 anos', '10-14 anos', '15-19 anos', '20-24 anos',
            '25-29 anos', '30-34 anos', '35-39 anos', '40-44 anos',
            'Outras idades', 'Idade ignorada'
        ]
        
        # Converter para categoria ordenada
        df['Faixa_Etaria'] = pd.Categorical(df['Faixa_Etaria'], categories=faixa_order, ordered=True)
        
        st.success(f"✅ Dados carregados: {len(df)} registros")
        
        return df, regioes
        
    except FileNotFoundError:
        st.error("❌ Arquivo 'dados_normalizados/comparacao_idhm_idade_mae.csv' não encontrado!")
        st.info("""
        **Solução:**
        1. Certifique-se que o arquivo está na pasta `dados_normalizados/`
        2. O nome deve ser exatamente: `comparacao_idhm_idade_mae.csv`
        3. Verifique a estrutura do seu projeto:
        ```
        trabalho_modelagem/
        ├── app_idhm.py          # Este arquivo
        ├── dados_normalizados/
        │   └── comparacao_idhm_idade_mae.csv
        └── requirements.txt
        ```
        """)
        st.stop()
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.stop()

def get_region_color(regiao):
    """Retorna cor para cada região"""
    return REGIAO_CORES.get(regiao, CORES['cinza_escuro'])

def format_number(num):
    """Formata números para exibição"""
    if pd.isna(num):
        return "N/A"
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.0f}k"
    else:
        return f"{num:.0f}"

# =============================================================================
# CARREGAR DADOS
# =============================================================================
df, regioes = load_data()

# Extrair listas para filtros
anos_disponiveis = sorted(df['Ano'].unique())
estados_disponiveis = sorted(df['Estado'].unique())
faixas_disponiveis = sorted(df['Faixa_Etaria'].cat.categories)
regioes_disponiveis = sorted(df['Regiao'].unique())

# =============================================================================
# SIDEBAR - FILTROS
# =============================================================================
with st.sidebar:
    st.markdown('<div class="big-icon">🎛️</div>', unsafe_allow_html=True)
    st.markdown(f"### 🔍 Filtros de Análise")
    
    # Filtro de Ano
    selected_year = st.selectbox(
        "Selecione o Ano",
        anos_disponiveis,
        index=len(anos_disponiveis)-1  # Último ano por padrão
    )
    
    # Filtro de Faixa Etária
    selected_faixa = st.selectbox(
        "Selecione a Faixa Etária",
        faixas_disponiveis,
        index=2  # 15-19 anos por padrão
    )
    
    # Filtro de Região
    selected_regiao = st.selectbox(
        "Selecione a Região",
        ['TODAS'] + regioes_disponiveis
    )
    
    # Filtro de Estado (depende da região)
    if selected_regiao == 'TODAS':
        estados_filtrados = estados_disponiveis
    else:
        estados_filtrados = [e for e in estados_disponiveis if e in regioes.get(selected_regiao, [])]
    
    selected_estado = st.selectbox(
        "Selecione o Estado (opcional)",
        ['TODOS'] + estados_filtrados
    )
    
    # Filtro de IDHM
    st.markdown("---")
    st.markdown("### 📊 Filtros de IDHM")
    
    min_idhm = float(df['IDHM'].min())
    max_idhm = float(df['IDHM'].max())
    
    idhm_range = st.slider(
        "Faixa de IDHM",
        min_value=min_idhm,
        max_value=max_idhm,
        value=(min_idhm, max_idhm),
        step=0.01,
        format="%.3f"
    )
    
    # Botões de ação
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📥 Exportar", use_container_width=True):
            st.info("Funcionalidade de exportação em desenvolvimento")
    
    # Estatísticas rápidas
    st.markdown("---")
    st.markdown("### 📈 Estatísticas Rápidas")
    
    dados_filtrados = df[
        (df['Ano'] == selected_year) & 
        (df['Faixa_Etaria'] == selected_faixa) &
        (df['IDHM'].between(idhm_range[0], idhm_range[1]))
    ]
    
    if selected_estado != 'TODOS':
        dados_filtrados = dados_filtrados[dados_filtrados['Estado'] == selected_estado]
    elif selected_regiao != 'TODAS':
        dados_filtrados = dados_filtrados[dados_filtrados['Regiao'] == selected_regiao]
    
    if not dados_filtrados.empty:
        media_percentual = dados_filtrados['Percentual'].mean()
        media_idhm = dados_filtrados['IDHM'].mean()
        correlacao = dados_filtrados['Percentual'].corr(dados_filtrados['IDHM'])
        
        st.metric("Média % Mães", f"{media_percentual:.1f}%")
        st.metric("IDHM Médio", f"{media_idhm:.3f}")
        st.metric("Correlação", f"{correlacao:.3f}")

# =============================================================================
# NOVO: ABAS PRINCIPAIS
# =============================================================================
tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📋 Relatórios Avançados"])

# =============================================================================
# TAB 1: DASHBOARD PRINCIPAL (conteúdo original)
# =============================================================================
with tab1:
    # TÍTULO PRINCIPAL
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='font-size: 3rem; margin-bottom: 10px;'>
            👶 Dashboard IDHM vs Maternidade 💼
        </h1>
        <p style='font-size: 1.3rem; color: #5DA9E9; font-weight: 500;'>
            Análise da Relação entre Desenvolvimento Humano e Padrões de Maternidade
        </p>
        <p style='font-size: 0.9rem; color: #888; margin-top: 10px;'>
            Período: {}-{} | {} Estados | {} Faixas Etárias
        </p>
    </div>
    """.format(
        df['Ano'].min(), df['Ano'].max(),
        df['Estado'].nunique(),
        df['Faixa_Etaria'].nunique()
    ), unsafe_allow_html=True)

    st.markdown("---")

    # =============================================================================
    # SEÇÃO 1: KPIs PRINCIPAIS
    # =============================================================================
    st.markdown(f"""
    <h2 style='text-align: center; margin-bottom: 30px;'>
        📊 Indicadores Principais - {selected_faixa}
    </h2>
    """, unsafe_allow_html=True)

    # Filtrar dados para os KPIs
    dados_kpi = df[
        (df['Ano'] == selected_year) & 
        (df['Faixa_Etaria'] == selected_faixa) &
        (df['IDHM'].between(idhm_range[0], idhm_range[1]))
    ]

    if selected_estado != 'TODOS':
        dados_kpi = dados_kpi[dados_kpi['Estado'] == selected_estado]
    elif selected_regiao != 'TODAS':
        dados_kpi = dados_kpi[dados_kpi['Regiao'] == selected_regiao]

    if not dados_kpi.empty:
        # Calcular estatísticas
        max_percentual = dados_kpi['Percentual'].max()
        min_percentual = dados_kpi['Percentual'].min()
        media_percentual = dados_kpi['Percentual'].mean()
        media_idhm = dados_kpi['IDHM'].mean()
        correlacao = dados_kpi['Percentual'].corr(dados_kpi['IDHM'])
        
        # Estado com maior e menor percentual
        estado_max = dados_kpi.loc[dados_kpi['Percentual'].idxmax(), 'Estado']
        estado_min = dados_kpi.loc[dados_kpi['Percentual'].idxmin(), 'Estado']
        
        # Exibir KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'<div class="big-icon" style="color: {CORES["grafico_idhm"]}">📈</div>', unsafe_allow_html=True)
            st.metric(
                "Média % Mães",
                f"{media_percentual:.1f}%",
                help="Média do percentual de mães nesta faixa etária"
            )
        
        with col2:
            st.markdown(f'<div class="big-icon" style="color: {CORES["grafico_idhm"]}">🎯</div>', unsafe_allow_html=True)
            st.metric(
                "IDHM Médio",
                f"{media_idhm:.3f}",
                help="Média do IDHM Geral"
            )
        
        with col3:
            st.markdown(f'<div class="big-icon" style="color: {CORES["destaques"]}">🔗</div>', unsafe_allow_html=True)
            color = "normal" if correlacao < 0 else "inverse"
            st.metric(
                "Correlação",
                f"{correlacao:.3f}",
                delta="Negativa" if correlacao < 0 else "Positiva",
                delta_color=color,
                help="Relação entre IDHM e % de mães"
            )
        
        with col4:
            st.markdown(f'<div class="big-icon" style="color: {CORES["grafico_maes"]}">🏆</div>', unsafe_allow_html=True)
            st.metric(
                "Amplitude",
                f"{max_percentual - min_percentual:.1f}%",
                help="Diferença entre maior e menor percentual"
            )
        
        # Estados destaque
        col5, col6 = st.columns(2)
        
        with col5:
            with st.container():
                st.markdown('<div class="highlight-state">', unsafe_allow_html=True)
                st.markdown(f"**🎯 MAIOR %: {estado_max}**")
                st.markdown(f"`{max_percentual:.1f}%` de mães {selected_faixa}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col6:
            with st.container():
                st.markdown('<div class="highlight-state">', unsafe_allow_html=True)
                st.markdown(f"**📉 MENOR %: {estado_min}**")
                st.markdown(f"`{min_percentual:.1f}%` de mães {selected_faixa}")
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # =============================================================================
    # SEÇÃO 2: GRÁFICO DE CORRELAÇÃO INTERATIVO
    # =============================================================================
    st.markdown("""
    <h2 style='text-align: center; margin: 30px 0;'>
        📈 Correlação IDHM vs % Mães
    </h2>
    """, unsafe_allow_html=True)

    if not dados_kpi.empty:
        # Criar gráfico de correlação
        fig_corr = px.scatter(
            dados_kpi,
            x='IDHM',
            y='Percentual',
            color='Regiao',
            hover_data=['Estado', 'IDHM_Educacao', 'IDHM_Renda', 'IDHM_Longevidade'],
            size='Percentual',
            size_max=25,
            color_discrete_map={regiao: get_region_color(regiao) for regiao in regioes_disponiveis},
            labels={
                'IDHM': 'IDHM Geral (0-1)',
                'Percentual': f'% Mães {selected_faixa}',
                'Regiao': 'Região'
            },
            title=f'Relação entre IDHM e Maternidade {selected_faixa} ({selected_year})'
        )
        
        # Personalizar layout para tema claro
        fig_corr.update_layout(
            template='plotly_white',
            title_font=dict(size=20, family='Arial', color=CORES['texto_principal']),
            title_x=0.05,
            xaxis=dict(
                title=dict(text='<b>IDHM Geral</b>', font=dict(size=16, color=CORES['texto_principal'])),
                gridcolor=CORES['grid_lines'],
                linecolor=CORES['detalhes_ui'],
                zerolinecolor=CORES['detalhes_ui'],
                tickfont=dict(color=CORES['texto_principal'])
            ),
            yaxis=dict(
                title=dict(text=f'<b>% Mães {selected_faixa}</b>', font=dict(size=16, color=CORES['texto_principal'])),
                gridcolor=CORES['grid_lines'],
                linecolor=CORES['detalhes_ui'],
                zerolinecolor=CORES['detalhes_ui'],
                tickfont=dict(color=CORES['texto_principal'])
            ),
            hoverlabel=dict(
                bgcolor=CORES['tooltip'],
                font_size=12,
                font_family="Arial",
                font_color="white"
            ),
            height=600,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor=CORES['branco']
        )
        
        # Adicionar linha de tendência com nova cor
        z = np.polyfit(dados_kpi['IDHM'], dados_kpi['Percentual'], 1)
        p = np.poly1d(z)
        x_range = np.linspace(dados_kpi['IDHM'].min(), dados_kpi['IDHM'].max(), 100)
        
        fig_corr.add_trace(
            go.Scatter(
                x=x_range,
                y=p(x_range),
                mode='lines',
                name='Linha de Tendência',
                line=dict(color=CORES['destaques'], width=3, dash='dash'),
                showlegend=True
            )
        )
        
        # Destacar estado selecionado
        if selected_estado != 'TODOS' and selected_estado in dados_kpi['Estado'].values:
            estado_data = dados_kpi[dados_kpi['Estado'] == selected_estado].iloc[0]
            fig_corr.add_annotation(
                x=estado_data['IDHM'],
                y=estado_data['Percentual'],
                text=f"<b>{selected_estado}</b>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=CORES['destaques'],
                font=dict(size=14, color=CORES['destaques']),
                bgcolor=CORES['branco'],
                bordercolor=CORES['destaques'],
                borderwidth=2,
                borderpad=4
            )
        
        st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")

    # ... [Restante do conteúdo da TAB 1 - manter todas as outras seções originais] ...
    # Continuar com as outras seções (Ranking, Evolução Temporal, Análise por Faixa Etária, etc.)

# =============================================================================
# TAB 2: RELATÓRIOS AVANÇADOS
# =============================================================================
with tab2:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 10px;'>
            📋 Relatórios Avançados
        </h1>
        <p style='font-size: 1.2rem; color: #5DA9E9; font-weight: 500;'>
            Análises detalhadas e relatórios personalizados
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # =============================================================================
    # SEÇÃO 1: RELATÓRIO DE ANÁLISE POR ESTADO
    # =============================================================================
    st.markdown("### 📊 Relatório por Estado")
    
    col_rel1, col_rel2 = st.columns([1, 2])
    
    with col_rel1:
        estado_relatorio = st.selectbox(
            "Selecione o Estado para o Relatório",
            ['TODOS'] + estados_disponiveis,
            key="estado_relatorio"
        )
        
        ano_relatorio = st.selectbox(
            "Ano para Análise",
            anos_disponiveis,
            index=len(anos_disponiveis)-1,
            key="ano_relatorio"
        )
        
        gerar_relatorio = st.button("📄 Gerar Relatório Completo", use_container_width=True)
    
    with col_rel2:
        st.markdown("#### 📝 Conteúdo do Relatório")
        st.markdown("""
        O relatório completo incluirá:
        
        1. **Análise Demográfica:**
           - Distribuição por faixa etária
           - Evolução temporal
           - Comparação com média nacional
        
        2. **Indicadores de IDHM:**
           - Componentes (Educação, Renda, Longevidade)
           - Posição no ranking estadual
           - Evolução histórica
        
        3. **Correlações e Tendências:**
           - Relação IDHM vs maternidade
           - Padrões regionais
           - Projeções futuras
        
        4. **Recomendações:**
           - Políticas públicas específicas
           - Áreas prioritárias de intervenção
           - Boas práticas identificadas
        """)
    
    if gerar_relatorio:
        with st.spinner("Gerando relatório..."):
            # Filtrar dados para o relatório
            if estado_relatorio == 'TODOS':
                dados_relatorio = df[df['Ano'] == ano_relatorio]
                titulo = f"Relatório Nacional - {ano_relatorio}"
            else:
                dados_relatorio = df[
                    (df['Estado'] == estado_relatorio) & 
                    (df['Ano'] == ano_relatorio)
                ]
                titulo = f"Relatório {estado_relatorio} - {ano_relatorio}"
            
            if not dados_relatorio.empty:
                # Criar relatório
                st.markdown(f"### {titulo}")
                
                # Métricas principais
                col_r1, col_r2, col_r3 = st.columns(3)
                
                with col_r1:
                    st.metric(
                        "Total de Registros",
                        len(dados_relatorio)
                    )
                
                with col_r2:
                    media_perc = dados_relatorio['Percentual'].mean()
                    st.metric(
                        "Média % Mães",
                        f"{media_perc:.1f}%"
                    )
                
                with col_r3:
                    media_idhm = dados_relatorio['IDHM'].mean()
                    st.metric(
                        "IDHM Médio",
                        f"{media_idhm:.3f}"
                    )
                
                # Gráfico de distribuição por faixa etária
                st.markdown("#### 📈 Distribuição por Faixa Etária")
                dados_faixas_agrupado = dados_relatorio.groupby('Faixa_Etaria').agg({
                    'Percentual': 'mean',
                    'IDHM': 'mean'
                }).reset_index()
                
                fig_dist = px.bar(
                    dados_faixas_agrupado,
                    x='Faixa_Etaria',
                    y='Percentual',
                    color='Percentual',
                    color_continuous_scale=[CORES['grafico_idhm'], CORES['grafico_maes']],
                    title=f'Distribuição Média por Faixa Etária - {ano_relatorio}'
                )
                
                fig_dist.update_layout(
                    template='plotly_white',
                    xaxis_title="Faixa Etária",
                    yaxis_title="% Mães (Média)",
                    height=400
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Análise de correlação
                st.markdown("#### 🔗 Análise de Correlação")
                
                # Calcular correlações para cada faixa
                correlacoes = {}
                for faixa in faixas_disponiveis:
                    dados_faixa = dados_relatorio[dados_relatorio['Faixa_Etaria'] == faixa]
                    if len(dados_faixa) > 1:
                        corr = dados_faixa['Percentual'].corr(dados_faixa['IDHM'])
                        if not pd.isna(corr):
                            correlacoes[faixa] = corr
                
                if correlacoes:
                    df_corr = pd.DataFrame(list(correlacoes.items()), columns=['Faixa_Etaria', 'Correlação'])
                    df_corr = df_corr.sort_values('Correlação', ascending=False)
                    
                    fig_corr_faixas = px.bar(
                        df_corr,
                        x='Faixa_Etaria',
                        y='Correlação',
                        color='Correlação',
                        color_continuous_scale=['red', 'yellow', 'green'],
                        title='Correlação IDHM vs % Mães por Faixa Etária'
                    )
                    
                    fig_corr_faixas.update_layout(
                        template='plotly_white',
                        height=400,
                        xaxis_tickangle=45
                    )
                    
                    st.plotly_chart(fig_corr_faixas, use_container_width=True)
                
                # Recomendações baseadas nos dados
                st.markdown("#### 🎯 Recomendações Específicas")
                
                # Identificar faixas problemáticas
                faixas_alta = dados_faixas_agrupado[dados_faixas_agrupado['Percentual'] > 20]
                faixas_baixa = dados_faixas_agrupado[dados_faixas_agrupado['Percentual'] < 5]
                
                if not faixas_alta.empty:
                    st.warning("**⚠️ Atenção - Faixas com Alta Maternidade:**")
                    for _, row in faixas_alta.iterrows():
                        st.markdown(f"- **{row['Faixa_Etaria']}**: {row['Percentual']:.1f}% de mães")
                
                if not faixas_baixa.empty:
                    st.success("**✅ Faixas Bem Controladas:**")
                    for _, row in faixas_baixa.iterrows():
                        st.markdown(f"- **{row['Faixa_Etaria']}**: {row['Percentual']:.1f}% de mães")
                
                # Botão para download do relatório
                st.markdown("---")
                st.markdown("### 📥 Exportar Relatório")
                
                # Gerar relatório em formato texto
                relatorio_completo = f"""
                RELATÓRIO DE ANÁLISE - {titulo}
                {'='*50}
                
                Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                
                RESUMO ESTATÍSTICO:
                {'-'*30}
                • Total de registros analisados: {len(dados_relatorio)}
                • Média % de mães: {media_perc:.1f}%
                • IDHM médio: {media_idhm:.3f}
                • Faixas etárias analisadas: {len(faixas_disponiveis)}
                
                DISTRIBUIÇÃO POR FAIXA ETÁRIA:
                {'-'*30}
                """
                
                for _, row in dados_faixas_agrupado.iterrows():
                    relatorio_completo += f"• {row['Faixa_Etaria']}: {row['Percentual']:.1f}% de mães (IDHM: {row['IDHM']:.3f})\n"
                
                relatorio_completo += f"""
                
                CORRELAÇÕES IDENTIFICADAS:
                {'-'*30}
                """
                
                for faixa, corr in correlacoes.items():
                    classificacao = "FORTE NEGATIVA" if corr < -0.7 else \
                                  "MODERADA NEGATIVA" if corr < -0.5 else \
                                  "FRACA NEGATIVA" if corr < -0.3 else \
                                  "FRACA POSITIVA" if corr < 0.3 else \
                                  "MODERADA POSITIVA" if corr < 0.7 else "FORTE POSITIVA"
                    relatorio_completo += f"• {faixa}: {corr:.3f} ({classificacao})\n"
                
                relatorio_completo += f"""
                
                RECOMENDAÇÕES:
                {'-'*30}
                """
                
                if not faixas_alta.empty:
                    relatorio_completo += "**PRIORIDADES DE INTERVENÇÃO:**\n"
                    for _, row in faixas_alta.iterrows():
                        relatorio_completo += f"- Implementar programas específicos para {row['Faixa_Etaria']}\n"
                
                relatorio_completo += f"""
                
                ---
                Relatório gerado automaticamente pelo Dashboard IDHM vs Maternidade
                """
                
                st.download_button(
                    label="📄 Baixar Relatório Completo (TXT)",
                    data=relatorio_completo,
                    file_name=f"relatorio_{estado_relatorio.replace(' ', '_')}_{ano_relatorio}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    
    st.markdown("---")
    
    # =============================================================================
    # SEÇÃO 2: ANÁLISE COMPARATIVA ENTRE ESTADOS
    # =============================================================================
    st.markdown("### 📊 Análise Comparativa")
    
    estados_comparar = st.multiselect(
        "Selecione Estados para Comparar",
        estados_disponiveis,
        default=estados_disponiveis[:3] if len(estados_disponiveis) >= 3 else estados_disponiveis,
        key="estados_comparar"
    )
    
    ano_comparacao = st.selectbox(
        "Ano para Comparação",
        anos_disponiveis,
        index=len(anos_disponiveis)-1,
        key="ano_comparacao"
    )
    
    if estados_comparar and len(estados_comparar) >= 2:
        dados_comparacao = df[
            (df['Estado'].isin(estados_comparar)) & 
            (df['Ano'] == ano_comparacao) &
            (df['Faixa_Etaria'] == selected_faixa)
        ]
        
        if not dados_comparacao.empty:
            # Gráfico de comparação
            fig_comp = px.bar(
                dados_comparacao,
                x='Estado',
                y='Percentual',
                color='Regiao',
                color_discrete_map=REGIAO_CORES,
                hover_data=['IDHM', 'Regiao'],
                title=f'Comparação entre Estados - {selected_faixa} ({ano_comparacao})'
            )
            
            fig_comp.update_layout(
                template='plotly_white',
                xaxis_title="Estado",
                yaxis_title=f"% Mães {selected_faixa}",
                height=500
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Tabela comparativa
            st.markdown("#### 📋 Tabela Comparativa")
            
            dados_tabela = dados_comparacao[['Estado', 'Regiao', 'Percentual', 'IDHM']].sort_values('Percentual', ascending=False)
            st.dataframe(
                dados_tabela.style.background_gradient(
                    subset=['Percentual', 'IDHM'],
                    cmap='Blues'
                ),
                use_container_width=True
            )
    
    st.markdown("---")
    
    # =============================================================================
    # SEÇÃO 3: RELATÓRIO DE TENDÊNCIAS
    # =============================================================================
    st.markdown("### 📈 Análise de Tendências")
    
    # Selecionar período para análise de tendência
    ano_inicio, ano_fim = st.select_slider(
        "Período para Análise de Tendência",
        options=anos_disponiveis,
        value=(anos_disponiveis[0], anos_disponiveis[-1])
    )
    
    # Selecionar métrica para análise
    metrica_tendencia = st.radio(
        "Métrica para Análise de Tendência",
        ["Percentual de Mães", "IDHM Geral", "Ambos"],
        horizontal=True
    )
    
    if st.button("🔍 Analisar Tendências", use_container_width=True):
        # Filtrar dados para o período
        dados_tendencia = df[
            (df['Ano'] >= ano_inicio) & 
            (df['Ano'] <= ano_fim) &
            (df['Faixa_Etaria'] == selected_faixa)
        ]
        
        if selected_estado != 'TODOS':
            dados_tendencia = dados_tendencia[dados_tendencia['Estado'] == selected_estado]
        elif selected_regiao != 'TODAS':
            dados_tendencia = dados_tendencia[dados_tendencia['Regiao'] == selected_regiao]
        
        if not dados_tendencia.empty:
            # Agrupar por ano
            tendencia_agrupada = dados_tendencia.groupby('Ano').agg({
                'Percentual': 'mean',
                'IDHM': 'mean'
            }).reset_index()
            
            # Criar gráfico de tendência
            fig_tendencia = go.Figure()
            
            if metrica_tendencia in ["Percentual de Mães", "Ambos"]:
                fig_tendencia.add_trace(go.Scatter(
                    x=tendencia_agrupada['Ano'],
                    y=tendencia_agrupada['Percentual'],
                    mode='lines+markers',
                    name='% Mães',
                    line=dict(color=CORES['grafico_maes'], width=3),
                    marker=dict(size=8, color=CORES['grafico_maes'])
                ))
            
            if metrica_tendencia in ["IDHM Geral", "Ambos"]:
                fig_tendencia.add_trace(go.Scatter(
                    x=tendencia_agrupada['Ano'],
                    y=tendencia_agrupada['IDHM'],
                    mode='lines+markers',
                    name='IDHM Geral',
                    line=dict(color=CORES['grafico_idhm'], width=3),
                    marker=dict(size=8, color=CORES['grafico_idhm']),
                    yaxis='y2' if metrica_tendencia == "Ambos" else 'y'
                ))
            
            layout_config = {
                'title': f'Tendência {ano_inicio}-{ano_fim} - {selected_faixa}',
                'xaxis': dict(title='Ano', gridcolor=CORES['grid_lines']),
                'yaxis': dict(
                    title='% Mães' if metrica_tendencia == "Percentual de Mães" else 'IDHM Geral',
                    gridcolor=CORES['grid_lines']
                ),
                'template': 'plotly_white',
                'height': 500
            }
            
            if metrica_tendencia == "Ambos":
                layout_config['yaxis2'] = dict(
                    title='IDHM Geral',
                    overlaying='y',
                    side='right',
                    gridcolor=CORES['grid_lines']
                )
            
            fig_tendencia.update_layout(**layout_config)
            
            st.plotly_chart(fig_tendencia, use_container_width=True)
            
            # Análise estatística da tendência
            st.markdown("#### 📊 Análise Estatística da Tendência")
            
            # Calcular variação percentual
            if len(tendencia_agrupada) > 1:
                primeira_linha = tendencia_agrupada.iloc[0]
                ultima_linha = tendencia_agrupada.iloc[-1]
                
                var_percentual = ((ultima_linha['Percentual'] - primeira_linha['Percentual']) / primeira_linha['Percentual']) * 100
                var_idhm = ultima_linha['IDHM'] - primeira_linha['IDHM']
                
                col_var1, col_var2 = st.columns(2)
                
                with col_var1:
                    st.metric(
                        "Variação % Mães",
                        f"{var_percentual:+.1f}%",
                        delta=f"{ultima_linha['Percentual'] - primeira_linha['Percentual']:+.1f}%",
                        help="Variação percentual no período"
                    )
                
                with col_var2:
                    st.metric(
                        "Variação IDHM",
                        f"{var_idhm:+.3f}",
                        delta=f"{var_idhm:+.3f}",
                        help="Variação absoluta no período"
                    )
                
                # Interpretação
                st.markdown("#### 📝 Interpretação da Tendência")
                
                if var_percentual < -10:
                    st.success("""
                    **✅ FORTE REDUÇÃO na maternidade!**
                    - Tendência muito positiva
                    - Políticas públicas eficazes
                    - Continuar estratégias atuais
                    """)
                elif var_percentual < -5:
                    st.info("""
                    **📉 REDUÇÃO MODERADA na maternidade**
                    - Tendência positiva
                    - Manter esforços atuais
                    - Monitorar continuamente
                    """)
                elif var_percentual > 10:
                    st.error("""
                    **⚠️ AUMENTO SIGNIFICATIVO na maternidade**
                    - Necessidade de intervenção urgente
                    - Revisar políticas atuais
                    - Implementar programas específicos
                    """)
                else:
                    st.warning("""
                    **🔍 ESTABILIDADE nos padrões**
                    - Pouca variação no período
                    - Necessidade de novas estratégias
                    - Analisar fatores específicos
                    """)

# =============================================================================
# RODAPÉ (mantido em ambas as abas)
# =============================================================================
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666; font-size: 0.9rem; border-top: 1px solid #E8DCCF; margin-top: 40px;'>
    <p>📊 <strong>Dashboard IDHM vs Maternidade</strong> | Análise de dados de 2000-2021</p>
    <p>🛠️ Desenvolvido com Streamlit, Plotly e Pandas | Gerado em {}</p>
    <p>📚 Fontes: DataSUS (SINASC) + Atlas do Desenvolvimento Humano (PNUD)</p>
    <p>🎯 Objetivo: Informar políticas públicas baseadas em evidências</p>
</div>
""".format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)