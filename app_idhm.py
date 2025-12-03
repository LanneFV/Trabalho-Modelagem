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
# CORES DEFINIDAS PELO USUÁRIO
# =============================================================================
CORES = {
    "fundo": "#FAF7F3",           # Off-white quente
    "texto_principal": "#1F3A5F", # Azul profundo
    "texto_graficos": "#2C3E50",  # Azul quase preto - ESCURO para contraste
    "texto_ui": "#1F3A5F",        # Azul profundo para UI
    "detalhes_ui": "#E8DCCF",     # Off-white secundário
    "grafico_idhm": "#5DA9E9",    # Azul claro
    "grafico_maes": "#F4B6C2",    # Rosa claro suave
    "alertas": "#FFD166",         # Amarelo suave
    "destaques": "#FF9F1C",       # Amarelo mais forte
    "linha_idhm": "#5DA9E9",      # Linha IDHM
    "linha_maes": "#F4B6C2",      # Linha Mães
    "grid_lines": "#E8DCCF",      # Grid lines
    "tooltip": "#1F3A5F",         # Tooltip
    "branco": "#FFFFFF",
    "cinza_claro": "#F0F0F0",
    "cinza_medio": "#D0D0D0",
    "cinza_escuro": "#444444"     # Escuro para contraste
}

REGIAO_CORES = {
    'NORTE': '#FF6B6B',
    'NORDESTE': '#FFA726',
    'CENTRO-OESTE': '#4CAF50',
    'SUDESTE': '#42A5F5',
    'SUL': '#AB47BC',
    'Outro': '#78909C'
}

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
def limpar_cor(cor):
    """Remove transparência das cores (converte de 9 para 7 caracteres)"""
    if len(cor) == 9:
        return cor[:7]
    return cor

def configurar_layout_plotly(fig, titulo, altura=500, rotacao_x=0):
    """Configura layout padrão para todos os gráficos Plotly"""
    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(color=CORES['texto_graficos'], size=16, family="Arial, sans-serif")
        ),
        plot_bgcolor=CORES['branco'],
        paper_bgcolor=CORES['branco'],
        font=dict(color=CORES['texto_graficos'], size=12, family="Arial, sans-serif"),
        height=altura,
        margin=dict(l=50, r=20, t=60, b=80),
        legend=dict(
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor=CORES['detalhes_ui'],
            borderwidth=1,
            font=dict(size=10, color=CORES['texto_graficos'])
        )
    )
    
    # Configurar eixos
    fig.update_xaxes(
        gridcolor=CORES['grid_lines'],
        linecolor=CORES['detalhes_ui'],
        showgrid=True,
        title_font=dict(color=CORES['texto_graficos'], size=12, family="Arial, sans-serif"),
        tickfont=dict(size=11, color=CORES['texto_graficos'], family="Arial, sans-serif")
    )
    
    fig.update_yaxes(
        gridcolor=CORES['grid_lines'],
        linecolor=CORES['detalhes_ui'],
        showgrid=True,
        title_font=dict(color=CORES['texto_graficos'], size=12, family="Arial, sans-serif"),
        tickfont=dict(size=11, color=CORES['texto_graficos'], family="Arial, sans-serif")
    )
    
    # Rotacionar labels do eixo X se necessário
    if rotacao_x > 0:
        fig.update_xaxes(tickangle=rotacao_x)
    
    return fig

@st.cache_data
def load_data():
    """Carrega e prepara os dados"""
    try:
        df = pd.read_csv('dados/comparacao_idhm_idade_mae.csv')
        
        if 'IDHM' not in df.columns:
            if all(col in df.columns for col in ['IDHM_Educacao', 'IDHM_Renda', 'IDHM_Longevidade']):
                df['IDHM'] = df[['IDHM_Educacao', 'IDHM_Renda', 'IDHM_Longevidade']].mean(axis=1)
        
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
        
        faixa_order = [
            'Menor de 10 anos', '10-14 anos', '15-19 anos', '20-24 anos',
            '25-29 anos', '30-34 anos', '35-39 anos', '40-44 anos',
            'Outras idades', 'Idade ignorada'
        ]
        
        if 'Faixa_Etaria' in df.columns:
            df['Faixa_Etaria'] = pd.Categorical(df['Faixa_Etaria'], categories=faixa_order, ordered=True)
        
        st.success(f"✅ Dados carregados: {len(df)} registros")
        return df, regioes
        
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        return pd.DataFrame(), {}

def get_region_color(regiao):
    """Retorna cor para cada região"""
    return REGIAO_CORES.get(regiao, CORES['cinza_escuro'])

def calcular_estatisticas_regionais(df, ano, faixa_etaria):
    """Calcula estatísticas regionais"""
    dados_filtrados = df[(df['Ano'] == ano) & (df['Faixa_Etaria'] == faixa_etaria)]
    
    if dados_filtrados.empty:
        return {}
    
    estatisticas = {
        'Media Brasil': dados_filtrados['Percentual'].mean()
    }
    
    for regiao, cor in REGIAO_CORES.items():
        if regiao != 'Outro':
            estados_regiao = [e for e in df['Estado'].unique() if e in regioes.get(regiao, [])]
            if estados_regiao:
                media = dados_filtrados[dados_filtrados['Estado'].isin(estados_regiao)]['Percentual'].mean()
                estatisticas[regiao] = media
    
    return estatisticas

# =============================================================================
# NOVAS FUNÇÕES PARA GRÁFICOS ADICIONAIS
# =============================================================================
def plot_ranking_idhm_geral(df, ano, top_n, faixa_etaria):
    """Gera gráfico de ranking dos estados (HORIZONTAL)"""
    dados_faixa = df[(df['Ano'] == ano) & (df['Faixa_Etaria'] == faixa_etaria)]
    
    if dados_faixa.empty:
        st.warning(f"Não há dados para {faixa_etaria} no ano {ano}")
        return None
    
    top_estados = dados_faixa.nlargest(top_n, 'Percentual')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_estados['Estado'],
        x=top_estados['Percentual'],
        orientation='h',
        marker_color=px.colors.sequential.RdPu[:len(top_estados)],
        text=top_estados['Percentual'].round(1),
        textposition='outside',
        texttemplate='%{text}%',
        hovertemplate='<b>%{y}</b><br>% Mães: %{x:.1f}%<br>IDHM: %{customdata:.3f}<extra></extra>',
        customdata=top_estados['IDHM'],
        textfont=dict(color=CORES['texto_graficos'], size=11)
    ))
    
    # Configurar layout com fundo branco
    fig.update_layout(
        title=dict(
            text=f'TOP {top_n} ESTADOS - Maior % de Mães {faixa_etaria} ({ano})',
            font=dict(color=CORES['texto_graficos'], size=16)
        ),
        xaxis=dict(
            title=f'% Mães {faixa_etaria}',
            gridcolor=CORES['grid_lines'],
            linecolor=CORES['detalhes_ui'],
            showgrid=True,
            title_font=dict(color=CORES['texto_graficos'], size=12)
        ),
        yaxis=dict(
            title='Estado',
            gridcolor=CORES['grid_lines'],
            linecolor=CORES['detalhes_ui'],
            tickfont=dict(size=12, color=CORES['texto_graficos'])
        ),
        plot_bgcolor=CORES['branco'],
        paper_bgcolor=CORES['branco'],
        font=dict(color=CORES['texto_graficos'], size=12),
        height=max(500, top_n * 40),
        margin=dict(l=100, r=20, t=60, b=20),
        showlegend=False
    )
    
    return fig, top_estados, dados_faixa

def plot_ranking_vertical(df, ano, top_n, faixa_etaria):
    """Gera gráfico de ranking vertical (melhor para muitos estados)"""
    dados_faixa = df[(df['Ano'] == ano) & (df['Faixa_Etaria'] == faixa_etaria)]
    
    if dados_faixa.empty:
        return None
    
    top_estados = dados_faixa.nlargest(top_n, 'Percentual')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_estados['Estado'],
        y=top_estados['Percentual'],
        marker_color=px.colors.sequential.RdPu[:len(top_estados)],
        text=top_estados['Percentual'].round(1),
        textposition='auto',
        texttemplate='%{text}%',
        hovertemplate='<b>%{x}</b><br>% Mães: %{y:.1f}%<br>IDHM: %{customdata:.3f}<extra></extra>',
        customdata=top_estados['IDHM'],
        textfont=dict(color=CORES['texto_graficos'], size=11)
    ))
    
    fig.update_layout(
        title=dict(
            text=f'TOP {top_n} ESTADOS - Maior % de Mães {faixa_etaria} ({ano})',
            font=dict(color=CORES['texto_graficos'], size=16)
        ),
        xaxis=dict(
            title='Estado',
            gridcolor=CORES['grid_lines'],
            linecolor=CORES['detalhes_ui'],
            showgrid=False,
            tickangle=45,
            tickfont=dict(size=11, color=CORES['texto_graficos'])
        ),
        yaxis=dict(
            title=f'% Mães {faixa_etaria}',
            gridcolor=CORES['grid_lines'],
            linecolor=CORES['detalhes_ui'],
            showgrid=True,
            title_font=dict(color=CORES['texto_graficos'], size=12)
        ),
        plot_bgcolor=CORES['branco'],
        paper_bgcolor=CORES['branco'],
        font=dict(color=CORES['texto_graficos'], size=12),
        height=500,
        margin=dict(l=50, r=20, t=60, b=100),
        showlegend=False
    )
    
    return fig

def gerar_relatorio_ranking(top_estados, dados_faixa, top_n, faixa_etaria, ano):
    """Gera relatório detalhado do ranking"""
    relatorio = f"## 📊 ANÁLISE DETALHADA DO RANKING - {faixa_etaria} ({ano})\n"
    relatorio += "-" * 50 + "\n\n"
    
    # Estatísticas do grupo
    media_top = top_estados['Percentual'].mean()
    media_idhm_top = top_estados['IDHM'].mean()
    media_geral = dados_faixa['Percentual'].mean()
    media_idhm_geral = dados_faixa['IDHM'].mean()
    
    relatorio += f"### 📈 TOP {top_n} ESTADOS - ANÁLISE:\n"
    relatorio += f"• **Média do Top {top_n}:** {media_top:.1f}% (IDHM: {media_idhm_top:.3f})\n"
    relatorio += f"• **Média de Todos Estados:** {media_geral:.1f}% (IDHM: {media_idhm_geral:.3f})\n"
    relatorio += f"• **Diferença:** +{media_top - media_geral:.1f}% | IDHM: {media_idhm_top - media_idhm_geral:+.3f}\n\n"
    
    # Distribuição regional
    relatorio += f"### 🌎 DISTRIBUIÇÃO REGIONAL NO TOP {top_n}:\n"
    
    regioes_grupo = {
        'NORTE': ['Acre', 'Amapá', 'Amazonas', 'Pará', 'Rondônia', 'Roraima', 'Tocantins'],
        'NORDESTE': ['Alagoas', 'Bahia', 'Ceará', 'Maranhão', 'Paraíba', 'Pernambuco', 
                    'Piauí', 'Rio Grande do Norte', 'Sergipe'],
        'CENTRO-OESTE': ['Distrito Federal', 'Goiás', 'Mato Grosso', 'Mato Grosso do Sul'],
        'SUDESTE': ['Espírito Santo', 'Minas Gerais', 'Rio de Janeiro', 'São Paulo'],
        'SUL': ['Paraná', 'Rio Grande do Sul', 'Santa Catarina']
    }
    
    for regiao, estados in regioes_grupo.items():
        estados_no_top = [estado for estado in top_estados['Estado'] if estado in estados]
        if estados_no_top:
            relatorio += f"• **{regiao}:** {len(estados_no_top)} estado(s) - {', '.join(estados_no_top)}\n"
    
    # Correlações
    correlacao_top = top_estados['Percentual'].corr(top_estados['IDHM'])
    correlacao_geral = dados_faixa['Percentual'].corr(dados_faixa['IDHM'])
    
    relatorio += f"\n### 🔗 CORRELAÇÃO NO TOP {top_n}:\n"
    relatorio += f"• **Correlação Top {top_n}:** {correlacao_top:.3f}\n"
    relatorio += f"• **Correlação Geral:** {correlacao_geral:.3f}\n"
    
    if abs(correlacao_top) > abs(correlacao_geral):
        relatorio += "• **Relação mais forte** entre IDHM e maternidade nos estados com maiores percentuais\n"
    else:
        relatorio += "• **Relação mais fraca** entre IDHM e maternidade nos estados com maiores percentuais\n"
    
    # Análise de tendências
    relatorio += f"\n### 📅 EVOLUÇÃO DOS ESTADOS DO TOP:\n"
    
    if ano > 2010:
        anos_comparacao = [2000, 2010]
    else:
        anos_comparacao = [2000]
    
    for ano_comp in anos_comparacao:
        if ano_comp < ano:
            dados_ano_anterior = df[(df['Ano'] == ano_comp) & (df['Faixa_Etaria'] == faixa_etaria)]
            if not dados_ano_anterior.empty:
                estados_evolucao = []
                for _, row in top_estados.iterrows():
                    estado = row['Estado']
                    if estado in dados_ano_anterior['Estado'].values:
                        percentual_anterior = dados_ano_anterior[dados_ano_anterior['Estado'] == estado]['Percentual'].values[0]
                        mudanca = row['Percentual'] - percentual_anterior
                        if abs(mudanca) > 1:
                            direcao = "📈 AUMENTOU" if mudanca > 0 else "📉 REDUZIU"
                            estados_evolucao.append(f"{estado} ({direcao} {abs(mudanca):.1f}%)")
                
                if estados_evolucao:
                    relatorio += f"• **{ano_comp} → {ano}:** {', '.join(estados_evolucao[:3])}\n"
    
    # Implicações políticas
    relatorio += f"\n### 🏛️ IMPLICAÇÕES PARA POLÍTICAS PÚBLICAS:\n"
    
    if faixa_etaria in ['10-14 anos', '15-19 anos']:
        relatorio += "• **ESTADOS CRÍTICOS:** Necessitam de intervenções urgentes\n"
        relatorio += "• **Foco em:** Educação sexual, prevenção, proteção à adolescência\n"
        relatorio += "• **Programas:** Bolsa Família condicionado à frequência escolar\n"
        
        if faixa_etaria == '10-14 anos':
            estados_criticos = top_estados[top_estados['Percentual'] > 1.0]
            if not estados_criticos.empty:
                relatorio += f"• 🔴 **ALERTA MÁXIMO:** {len(estados_criticos)} estado(s) com gravidez infantil >1%\n"
    
    elif faixa_etaria in ['25-29 anos', '30-34 anos']:
        relatorio += "• **PADRÃO SAUDÁVEL:** Maternidade em idade adulta\n"
        relatorio += "• **Foco em:** Planejamento familiar, apoio à maternidade\n"
        relatorio += "• **Programas:** Licença-maternidade, creches, apoio à dupla jornada\n"
    
    # Recomendações específicas
    relatorio += f"\n### 🎯 RECOMENDAÇÕES ESPECÍFICAS:\n"
    
    estados_prioridade = top_estados[top_estados['IDHM'] < 0.700]
    if not estados_prioridade.empty:
        relatorio += "• 🔴 **PRIORIDADE ABSOLUTA (Baixo IDHM + Alto %):**\n"
        for _, estado in estados_prioridade.iterrows():
            relatorio += f"  - **{estado['Estado']}:** {estado['Percentual']:.1f}% (IDHM: {estado['IDHM']:.3f})\n"
    
    estados_atipicos = top_estados[top_estados['IDHM'] > 0.800]
    if not estados_atipicos.empty and faixa_etaria in ['10-14 anos', '15-19 anos']:
        relatorio += "• **CASOS ATÍPICOS (Alto IDHM + Alto %):**\n"
        for _, estado in estados_atipicos.iterrows():
            relatorio += f"  - **{estado['Estado']}:** Investigar causas específicas\n"
    
    return relatorio

def plot_evolucao_completa(df, faixa_etaria, tipo_analise='Todos Estados', estado_selecionado='Acre'):
    """Gera gráfico de evolução temporal"""
    dados_faixa = df[df['Faixa_Etaria'] == faixa_etaria]
    
    if dados_faixa.empty:
        st.warning(f"Não há dados para {faixa_etaria}")
        return None, ""
    
    if tipo_analise == 'Todos Estados':
        fig = go.Figure()
        
        estados_unicos = sorted(dados_faixa['Estado'].unique())
        
        # Limitar a 20 estados para não sobrecarregar
        estados_unicos = estados_unicos[:20]
        
        # Cores válidas para Plotly (sem transparência, 7 caracteres)
        cores_regioes = {
            'NORTE': ['#FF0000', "#DF4156", "#CA3939", "#550303", "#A31780", "#E77E6C", "#F182B6"],
            'NORDESTE': ['#FF8C00', "#FFBB00", "#DDCA5D", "#DAB820", '#B8860B', "#4B2D07", "#AD6200", '#D2691E', "#BB8F4C"],
            'CENTRO-OESTE': ['#32CD32', '#228B22', '#006400', '#9ACD32'],
            'SUDESTE': ['#1E90FF', "#739ABE", "#6FDBDF", '#000080'],
            'SUL': ['#8A2BE2', '#4B0082', '#9400D3']
        }
        
        regioes_grupo = {
            'NORTE': ['Acre', 'Amapá', 'Amazonas', 'Pará', 'Rondônia', 'Roraima', 'Tocantins'],
            'NORDESTE': ['Alagoas', 'Bahia', 'Ceará', 'Maranhão', 'Paraíba', 'Pernambuco', 
                        'Piauí', 'Rio Grande do Norte', 'Sergipe'],
            'CENTRO-OESTE': ['Distrito Federal', 'Goiás', 'Mato Grosso', 'Mato Grosso do Sul'],
            'SUDESTE': ['Espírito Santo', 'Minas Gerais', 'Rio de Janeiro', 'São Paulo'],
            'SUL': ['Paraná', 'Rio Grande do Sul', 'Santa Catarina']
        }
        
        cores_estados = {}
        for regiao, estados in regioes_grupo.items():
            if regiao in cores_regioes:
                for i, estado in enumerate(estados):
                    if i < len(cores_regioes[regiao]):
                        # Garantir que a cor tem 7 caracteres (sem alpha)
                        cor = cores_regioes[regiao][i]
                        cor = limpar_cor(cor)  # Limpar a cor
                        cores_estados[estado] = cor
        
        for estado in estados_unicos:
            dados_estado = dados_faixa[dados_faixa['Estado'] == estado]
            cor = cores_estados.get(estado, '#666666')
            
            # Garantir que a cor seja válida
            if len(cor) != 7:
                cor = '#666666'  # Fallback para cor segura
            
            fig.add_trace(go.Scatter(
                x=dados_estado['Ano'],
                y=dados_estado['Percentual'],
                mode='lines+markers',
                name=estado,
                line=dict(color=cor, width=1.5),
                marker=dict(size=4, color=cor),
                hovertemplate='<b>%{fullData.name}</b><br>Ano: %{x}<br>% Mães: %{y:.1f}%<extra></extra>',
                opacity=0.7,
                visible='legendonly' if estado not in estados_unicos[:5] else True
            ))
        
        # Linha da média Brasil
        evolucao_media = dados_faixa.groupby('Ano')['Percentual'].mean().reset_index()
        fig.add_trace(go.Scatter(
            x=evolucao_media['Ano'],
            y=evolucao_media['Percentual'],
            mode='lines',
            name='MÉDIA BRASIL',
            line=dict(color='black', width=3, dash='dash'),
            hovertemplate='<b>MÉDIA BRASIL</b><br>Ano: %{x}<br>% Mães: %{y:.1f}%<extra></extra>'
        ))
        
        # Configurar layout com fundo branco
        fig.update_layout(
            title=dict(
                text=f'TODOS OS {len(estados_unicos)} ESTADOS: % Mães {faixa_etaria}',
                font=dict(color=CORES['texto_graficos'], size=16)
            ),
            xaxis=dict(
                title='Ano',
                gridcolor=CORES['grid_lines'],
                linecolor=CORES['detalhes_ui'],
                showgrid=True,
                title_font=dict(color=CORES['texto_graficos'])
            ),
            yaxis=dict(
                title=f'% Mães {faixa_etaria}',
                gridcolor=CORES['grid_lines'],
                linecolor=CORES['detalhes_ui'],
                showgrid=True,
                title_font=dict(color=CORES['texto_graficos'])
            ),
            plot_bgcolor=CORES['branco'],
            paper_bgcolor=CORES['branco'],
            font=dict(color=CORES['texto_graficos']),
            height=700,
            margin=dict(l=50, r=20, t=60, b=50),
            hovermode='closest',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02,
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor=CORES['detalhes_ui'],
                borderwidth=1,
                font=dict(size=10, color=CORES['texto_graficos']),
                itemsizing='constant'
            )
        )
        
        # Gerar relatório
        relatorio = f"### 📈 EVOLUÇÃO COMPLETA: IDHM GERAL vs MATERNIDADE\n"
        relatorio += "-" * 40 + "\n\n"
        
        dados_2021 = dados_faixa[dados_faixa['Ano'] == 2021]
        percentual_medio_2021 = dados_2021['Percentual'].mean()
        
        relatorio += f"#### 📊 ESTATÍSTICAS {faixa_etaria} (2021):\n"
        relatorio += f"• **Média Brasil:** {percentual_medio_2021:.1f}%\n"
        
        for regiao, estados in regioes_grupo.items():
            estados_presentes = [e for e in estados if e in estados_unicos]
            if estados_presentes:
                media_regiao = dados_2021[dados_2021['Estado'].isin(estados_presentes)]['Percentual'].mean()
                relatorio += f"• **{regiao}:** {media_regiao:.1f}%\n"
        
        relatorio += f"\n**Plotando {len(estados_unicos)} estados para {faixa_etaria}**\n"
        relatorio += "*DICA: Passe o mouse sobre as linhas para ver o nome do estado!*\n"
        relatorio += "*Apenas 5 estados estão visíveis por padrão. Clique na legenda para mostrar mais.*\n\n"
        
        relatorio += "#### 🎯 EXPLICAÇÃO:\n"
        relatorio += "• **NORTE:** Estados com maiores % (cores vermelhas)\n"
        relatorio += "• **NORDESTE:** Estados com % elevados (cores laranjas)\n"
        relatorio += "• **CENTRO-OESTE:** % intermediários (cores verdes)\n"
        relatorio += "• **SUDESTE:** % mais baixos (cores azuis)\n"
        relatorio += "• **SUL:** % mais baixos (cores roxas)\n"
        
    elif tipo_analise == 'Comparação IDHM Geral':
        dados_estado = dados_faixa[dados_faixa['Estado'] == estado_selecionado]
        
        if dados_estado.empty:
            st.warning(f"Não há dados para {estado_selecionado} - {faixa_etaria}")
            return None, ""
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=dados_estado['Ano'],
                y=dados_estado['Percentual'],
                name=f'% Mães {faixa_etaria}',
                line=dict(color=CORES['linha_maes'], width=3),
                mode='lines+markers'
            ),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(
                x=dados_estado['Ano'],
                y=dados_estado['IDHM'],
                name='IDHM Geral',
                line=dict(color=CORES['linha_idhm'], width=3, dash='dash'),
                mode='lines+markers'
            ),
            secondary_y=True,
        )
        
        # Configurar layout com fundo branco
        fig.update_layout(
            title=dict(
                text=f'{estado_selecionado}: % Mães vs IDHM Geral ({faixa_etaria})',
                font=dict(color=CORES['texto_graficos'], size=16)
            ),
            plot_bgcolor=CORES['branco'],
            paper_bgcolor=CORES['branco'],
            font=dict(color=CORES['texto_graficos']),
            height=500,
            margin=dict(l=50, r=20, t=60, b=50),
            legend=dict(
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor=CORES['detalhes_ui'],
                borderwidth=1,
                font=dict(color=CORES['texto_graficos'])
            )
        )
        
        fig.update_xaxes(
            title_text="Ano",
            gridcolor=CORES['grid_lines'],
            linecolor=CORES['detalhes_ui'],
            showgrid=True,
            title_font=dict(color=CORES['texto_graficos'])
        )
        fig.update_yaxes(
            title_text=f"% Mães {faixa_etaria}",
            secondary_y=False,
            gridcolor=CORES['grid_lines'],
            linecolor=CORES['detalhes_ui'],
            title_font=dict(color=CORES['texto_graficos'])
        )
        fig.update_yaxes(
            title_text="IDHM Geral",
            secondary_y=True,
            gridcolor=CORES['grid_lines'],
            linecolor=CORES['detalhes_ui'],
            title_font=dict(color=CORES['texto_graficos'])
        )
        
        # Relatório
        relatorio = f"### 📊 ANÁLISE INDIVIDUAL: {estado_selecionado}\n"
        relatorio += "-" * 40 + "\n\n"
        
        if len(dados_estado) > 1:
            primeira = dados_estado.iloc[0]
            ultima = dados_estado.iloc[-1]
            
            variacao_percentual = ultima['Percentual'] - primeira['Percentual']
            variacao_idhm = ultima['IDHM'] - primeira['IDHM']
            
            relatorio += f"#### 📈 EVOLUÇÃO {primeira['Ano']} → {ultima['Ano']}:\n"
            relatorio += f"• **% Mães:** {primeira['Percentual']:.1f}% → {ultima['Percentual']:.1f}% "
            relatorio += f"({variacao_percentual:+.1f}%)\n"
            relatorio += f"• **IDHM Geral:** {primeira['IDHM']:.3f} → {ultima['IDHM']:.3f} "
            relatorio += f"({variacao_idhm:+.3f})\n\n"
            
            if variacao_percentual < 0 and variacao_idhm > 0:
                relatorio += "✅ **Tendência ideal:** % mães ↓ e IDHM ↑\n"
            else:
                relatorio += "⚠️ **Padrão atípico:** Analisar causas específicas\n"
        
    elif tipo_analise == 'Estados por Região':
        fig = go.Figure()
        
        regioes_grupo = {
            'NORTE': ['Acre', 'Amapá', 'Amazonas', 'Pará', 'Rondônia', 'Roraima', 'Tocantins'],
            'NORDESTE': ['Alagoas', 'Bahia', 'Ceará', 'Maranhão', 'Paraíba', 'Pernambuco', 
                        'Piauí', 'Rio Grande do Norte', 'Sergipe'],
            'CENTRO-OESTE': ['Distrito Federal', 'Goiás', 'Mato Grosso', 'Mato Grosso do Sul'],
            'SUDESTE': ['Espírito Santo', 'Minas Gerais', 'Rio de Janeiro', 'São Paulo'],
            'SUL': ['Paraná', 'Rio Grande do Sul', 'Santa Catarina']
        }
        
        cores_regioes_plot = {
            'NORTE': '#FF0000',
            'NORDESTE': '#FF8C00',
            'CENTRO-OESTE': '#32CD32',
            'SUDESTE': '#1E90FF',
            'SUL': '#8A2BE2'
        }
        
        for regiao, estados in regioes_grupo.items():
            dados_regiao = dados_faixa[dados_faixa['Estado'].isin(estados)]
            if not dados_regiao.empty:
                evolucao_media = dados_regiao.groupby('Ano')['Percentual'].mean().reset_index()
                
                fig.add_trace(go.Scatter(
                    x=evolucao_media['Ano'],
                    y=evolucao_media['Percentual'],
                    mode='lines+markers',
                    name=regiao,
                    line=dict(color=cores_regioes_plot[regiao], width=3),
                    marker=dict(size=6, color=cores_regioes_plot[regiao]),
                    hovertemplate=f'<b>{regiao}</b><br>Ano: %{{x}}<br>% Mães: %{{y:.1f}}%<extra></extra>'
                ))
        
        # Configurar layout com fundo branco
        fig.update_layout(
            title=dict(
                text=f'EVOLUÇÃO POR REGIÃO: % Mães {faixa_etaria}',
                font=dict(color=CORES['texto_graficos'], size=16)
            ),
            xaxis=dict(
                title='Ano',
                gridcolor=CORES['grid_lines'],
                linecolor=CORES['detalhes_ui'],
                showgrid=True,
                title_font=dict(color=CORES['texto_graficos'])
            ),
            yaxis=dict(
                title=f'% Mães {faixa_etaria}',
                gridcolor=CORES['grid_lines'],
                linecolor=CORES['detalhes_ui'],
                showgrid=True,
                title_font=dict(color=CORES['texto_graficos'])
            ),
            plot_bgcolor=CORES['branco'],
            paper_bgcolor=CORES['branco'],
            font=dict(color=CORES['texto_graficos']),
            height=500,
            margin=dict(l=50, r=20, t=60, b=50),
            legend=dict(
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor=CORES['detalhes_ui'],
                borderwidth=1,
                font=dict(color=CORES['texto_graficos'])
            )
        )
        
        # Relatório
        relatorio = f"### 🌎 COMPARAÇÃO REGIONAL\n"
        relatorio += "-" * 40 + "\n\n"
        
        dados_2021 = dados_faixa[dados_faixa['Ano'] == 2021]
        relatorio += f"#### 📊 COMPARAÇÃO REGIONAL (2021):\n"
        
        for regiao, estados in regioes_grupo.items():
            media_regiao = dados_2021[dados_2021['Estado'].isin(estados)]['Percentual'].mean()
            relatorio += f"• **{regiao}:** {media_regiao:.1f}%\n"
        
        relatorio += f"\n#### 🎯 ANÁLISE REGIONAL:\n"
        relatorio += "• **VISÃO REGIONAL:** Média de cada região\n"
        relatorio += "• **Norte:** Sempre maiores % de maternidade precoce\n"
        relatorio += "• **Sul/Sudeste:** Sempre menores %\n"
    
    return fig, relatorio

# =============================================================================
# CSS ESTILO CLARO MODERNO COM CORREÇÕES
# =============================================================================
st.markdown(f"""
<style>
    /* Tema claro moderno */
    .stApp {{
        background: {CORES['fundo']} !important;
        color: {CORES['texto_principal']} !important;
    }}
    
    /* Texto principal em todos os elementos - AZUL ESCURO para contraste */
    body, p, div, span, label, .stMarkdown, .stText {{
        color: {CORES['texto_principal']} !important;
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    
    /* Cards de métricas */
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, {CORES['grafico_idhm']}15, {CORES['grafico_maes']}15);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05);
        border: 2px solid {CORES['detalhes_ui']};
        margin: 8px;
    }}
    
    div[data-testid="stMetric"] label {{
        color: {CORES['texto_principal']} !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }}
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {CORES['texto_principal']} !important;
        font-size: 28px !important;
        font-weight: bold !important;
    }}
    
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
        color: {CORES['destaques']} !important;
        font-weight: 600 !important;
    }}
    
    /* Títulos */
    h1, h2, h3, h4 {{
        color: {CORES['texto_principal']} !important;
        font-weight: 700 !important;
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    
    h1 {{
        background: linear-gradient(90deg, {CORES['grafico_idhm']}, {CORES['grafico_maes']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
        margin-bottom: 5px !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {CORES['branco']} !important;
        border-right: 2px solid {CORES['detalhes_ui']};
    }}
    
    /* Labels */
    .stSelectbox label, .stSlider label, .stRadio label {{
        color: {CORES['texto_principal']} !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }}
    
    /* Inputs */
    .stSelectbox > div > div, .stTextInput > div > div {{
        background: {CORES['branco']} !important;
        border: 2px solid {CORES['detalhes_ui']} !important;
        color: {CORES['texto_principal']} !important;
    }}
    
    /* Alertas */
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {{
        color: {CORES['texto_principal']} !important;
        background: linear-gradient(135deg, {CORES['alertas']}20, {CORES['destaques']}10);
        border-left: 4px solid {CORES['alertas']};
    }}
    
    /* Tabelas */
    [data-testid="stDataFrame"] {{
        background: {CORES['branco']} !important;
        color: {CORES['texto_principal']} !important;
    }}
    
    /* Botões */
    .stButton > button {{
        background: linear-gradient(135deg, {CORES['grafico_idhm']}, {CORES['grafico_idhm']}CC) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, {CORES['destaques']}, {CORES['destaques']}CC) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}
    
    /* ====== ESPAÇAMENTO REDUZIDO ====== */
    
    /* Gráficos Plotly */
    .stPlotlyChart {{
        margin: 5px 0 !important;
        padding: 0 !important;
    }}
    
    /* Melhorar legibilidade dos gráficos */
    .js-plotly-plot .plotly .modebar {{
        padding: 5px !important;
    }}
    
    .js-plotly-plot .plotly .main-svg {{
        border-radius: 8px !important;
        border: 1px solid {CORES['detalhes_ui']} !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }}
    
    /* Tooltips mais legíveis */
    .hovertext {{
        font-size: 12px !important;
        font-weight: 500 !important;
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid {CORES['detalhes_ui']} !important;
        color: {CORES['texto_graficos']} !important;
    }}
    
    /* Contêineres */
    .element-container {{
        margin-bottom: 8px !important;
    }}
    
    /* Expandable sections */
    .streamlit-expanderHeader {{
        color: {CORES['texto_principal']} !important;
        font-weight: 600 !important;
        padding: 10px 0 !important;
        background: linear-gradient(90deg, {CORES['fundo']}, {CORES['detalhes_ui']});
        border-radius: 8px;
        border: 1px solid {CORES['detalhes_ui']};
    }}
    
    .streamlit-expanderHeader:hover {{
        background: linear-gradient(90deg, {CORES['detalhes_ui']}, {CORES['alertas']}30);
    }}
    
    .streamlit-expanderContent {{
        color: {CORES['texto_principal']} !important;
        padding: 10px 0 !important;
    }}
    
    /* Cards */
    .analysis-card {{
        background: {CORES['branco']};
        padding: 15px;
        margin: 8px 0;
        border-left: 4px solid {CORES['grafico_idhm']};
        border-radius: 10px;
        color: {CORES['texto_principal']};
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* Separadores */
    hr {{
        margin: 10px 0 !important;
        height: 1px;
        background: {CORES['detalhes_ui']};
        border: none;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        margin-bottom: 10px !important;
        gap: 2px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {CORES['texto_principal']} !important;
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {CORES['grafico_idhm']} !important;
        border-bottom: 2px solid {CORES['grafico_idhm']} !important;
    }}
    
    /* Ícones */
    .big-icon {{
        color: {CORES['grafico_idhm']} !important;
        margin-bottom: 8px !important;
        font-size: 2.5rem;
    }}
    
    /* Highlight states */
    .highlight-state {{
        background: linear-gradient(135deg, {CORES['grafico_idhm']}15, {CORES['grafico_maes']}15) !important;
        color: {CORES['texto_principal']} !important;
        border: 2px solid {CORES['detalhes_ui']};
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* Tags de região */
    .tag-norte {{ background: linear-gradient(135deg, {REGIAO_CORES['NORTE']}40, {REGIAO_CORES['NORTE']}20); color: {REGIAO_CORES['NORTE']}; }}
    .tag-nordeste {{ background: linear-gradient(135deg, {REGIAO_CORES['NORDESTE']}40, {REGIAO_CORES['NORDESTE']}20); color: {REGIAO_CORES['NORDESTE']}; }}
    .tag-centro-oeste {{ background: linear-gradient(135deg, {REGIAO_CORES['CENTRO-OESTE']}40, {REGIAO_CORES['CENTRO-OESTE']}20); color: {REGIAO_CORES['CENTRO-OESTE']}; }}
    .tag-sudeste {{ background: linear-gradient(135deg, {REGIAO_CORES['SUDESTE']}40, {REGIAO_CORES['SUDESTE']}20); color: {REGIAO_CORES['SUDESTE']}; }}
    .tag-sul {{ background: linear-gradient(135deg, {REGIAO_CORES['SUL']}40, {REGIAO_CORES['SUL']}20); color: {REGIAO_CORES['SUL']}; }}
    
    .region-tag {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 11px;
        margin: 2px;
        border: 1px solid currentColor;
    }}
    
    /* Ajustes para visualização expandida */
    .expanded-chart {{
        height: 700px !important;
    }}
    
    /* Ajustes para textos em gráficos */
    .gtitle {{
        color: {CORES['texto_graficos']} !important;
        font-weight: 600 !important;
    }}
    
    /* Eixos dos gráficos */
    .xtick, .ytick {{
        fill: {CORES['texto_graficos']} !important;
    }}
    
    .axis-title {{
        fill: {CORES['texto_graficos']} !important;
        font-weight: 600 !important;
    }}
    
    /* Ajustes de seleção */
    .stSelectbox:focus-within > div > div {{
        border-color: {CORES['destaques']} !important;
        box-shadow: 0 0 0 2px {CORES['destaques']}20 !important;
    }}
    
    /* Slider personalizado */
    .stSlider > div > div > div > div {{
        background: {CORES['grafico_idhm']} !important;
    }}
    
    .stSlider > div > div > div > div:hover {{
        background: {CORES['destaques']} !important;
    }}
    
    /* Radio buttons */
    .stRadio > div {{
        background: {CORES['branco']} !important;
        border: 1px solid {CORES['detalhes_ui']} !important;
        border-radius: 8px;
        padding: 5px;
    }}
    
    .stRadio > div > label {{
        color: {CORES['texto_principal']} !important;
    }}
    
    /* Hover effects */
    .highlight-state:hover, .analysis-card:hover {{
        transform: translateY(-2px);
        transition: transform 0.2s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CARREGAR DADOS
# =============================================================================
df, regioes = load_data()

if df.empty:
    st.stop()

# Listas para filtros
anos_disponiveis = sorted(df['Ano'].unique())
estados_disponiveis = sorted(df['Estado'].unique())
faixas_disponiveis = sorted(df['Faixa_Etaria'].cat.categories)
regioes_disponiveis = sorted(df['Regiao'].unique())

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown('<div class="big-icon">🎛️</div>', unsafe_allow_html=True)
    st.markdown("### 🔍 Filtros de Análise")
    
    selected_year = st.selectbox("Selecione o Ano", anos_disponiveis, index=len(anos_disponiveis)-1)
    selected_faixa = st.selectbox("Selecione a Faixa Etária", faixas_disponiveis, index=2)
    selected_regiao = st.selectbox("Selecione a Região", ['TODAS'] + regioes_disponiveis)
    
    if selected_regiao == 'TODAS':
        estados_filtrados = estados_disponiveis
    else:
        estados_filtrados = [e for e in estados_disponiveis if e in regioes.get(selected_regiao, [])]
    
    selected_estado = st.selectbox("Selecione o Estado (opcional)", ['TODOS'] + estados_filtrados)
    
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
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Atualizar", width='stretch'):
            st.rerun()
    
    with col2:
        if st.button("📥 Exportar", width='stretch'):
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
# ABAS PRINCIPAIS
# =============================================================================
tab1, tab2, tab3 = st.tabs(["📊 Dashboard Principal", "📋 Relatórios Avançados", "📈 Gráficos Comparativos"])

# =============================================================================
# TAB 1: DASHBOARD PRINCIPAL
# =============================================================================
with tab1:
    st.markdown(f"""
    <div style='text-align: center; padding: 15px;'>
        <h1>👶 Dashboard IDHM vs Maternidade 💼</h1>
        <p style='font-size: 1.1rem; color: #5DA9E9;'>
            Análise da Relação entre Desenvolvimento Humano e Padrões de Maternidade
        </p>
        <p style='font-size: 0.9rem; color: #666;'>
            Período: {df['Ano'].min()}-{df['Ano'].max()} | {df['Estado'].nunique()} Estados | {df['Faixa_Etaria'].nunique()} Faixas Etárias
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # KPIs PRINCIPAIS
    st.markdown(f"### 📊 Indicadores Principais - {selected_faixa}")
    
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
        max_percentual = dados_kpi['Percentual'].max()
        min_percentual = dados_kpi['Percentual'].min()
        media_percentual = dados_kpi['Percentual'].mean()
        media_idhm = dados_kpi['IDHM'].mean()
        correlacao = dados_kpi['Percentual'].corr(dados_kpi['IDHM'])
        
        estado_max = dados_kpi.loc[dados_kpi['Percentual'].idxmax(), 'Estado']
        estado_min = dados_kpi.loc[dados_kpi['Percentual'].idxmin(), 'Estado']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Média % Mães", f"{media_percentual:.1f}%")
        
        with col2:
            st.metric("IDHM Médio", f"{media_idhm:.3f}")
        
        with col3:
            st.metric("Correlação", f"{correlacao:.3f}", delta="Negativa" if correlacao < 0 else "Positiva")
        
        with col4:
            st.metric("Amplitude", f"{max_percentual - min_percentual:.1f}%")
        
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
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # GRÁFICO DE CORRELAÇÃO
    st.markdown(f"### 📈 Correlação IDHM vs % Mães - {selected_faixa}")
    
    if not dados_kpi.empty:
        fig_corr = px.scatter(
            dados_kpi,
            x='IDHM',
            y='Percentual',
            color='Regiao',
            hover_data=['Estado', 'IDHM_Educacao', 'IDHM_Renda', 'IDHM_Longevidade'],
            size='Percentual',
            size_max=25,
            color_discrete_map=REGIAO_CORES,
            labels={
                'IDHM': 'IDHM Geral (0-1)',
                'Percentual': f'% Mães {selected_faixa}',
                'Regiao': 'Região'
            }
        )
        
        # Aplicar layout com fundo branco e cores escuras
        fig_corr = configurar_layout_plotly(
            fig_corr,
            f'Correlação IDHM vs % Mães - {selected_faixa}',
            altura=500
        )
        
        # Ajustar cores dos textos
        fig_corr.update_xaxes(title_font=dict(color=CORES['texto_graficos']))
        fig_corr.update_yaxes(title_font=dict(color=CORES['texto_graficos']))
        
        # Gráfico principal COM KEY ÚNICO
        st.plotly_chart(fig_corr, width='stretch', key="correlacao_principal")
        
        # Opção de expandir COM KEY ÚNICO
        with st.expander("🔍 Ampliar Gráfico", expanded=False):
            st.plotly_chart(fig_corr, width='stretch', height=600, key="correlacao_expandido")
        
        # Análise da correlação
        with st.expander("📊 Análise da Correlação", expanded=False):
            if correlacao < -0.7:
                st.success("**FORTE CORRELAÇÃO NEGATIVA** - IDHM alto ↔ Baixa maternidade")
            elif correlacao < -0.5:
                st.info("**CORRELAÇÃO NEGATIVA MODERADA** - Tendência clara de redução")
            elif correlacao < -0.3:
                st.warning("**CORRELAÇÃO NEGATIVA FRACA** - Leve tendência negativa")
            else:
                st.info("**CORRELAÇÃO FRACA/INEXISTENTE** - Pouca relação linear")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # RANKING DOS ESTADOS
    st.markdown(f"### 🏆 Ranking dos Estados - {selected_faixa}")
    
    if not dados_kpi.empty:
        # Adicionar escolha de tipo de gráfico
        col_tipo1, col_tipo2 = st.columns([3, 1])
        with col_tipo2:
            tipo_grafico = st.radio(
                "Tipo de Gráfico",
                ["Barras Horizontais", "Barras Verticais"],
                horizontal=True,
                label_visibility="collapsed",
                key="tipo_grafico_ranking"
            )
        
        dados_ranking = dados_kpi.sort_values('Percentual', ascending=False).head(15)
        
        if tipo_grafico == "Barras Horizontais":
            fig_rank = px.bar(
                dados_ranking,
                y='Estado',
                x='Percentual',
                color='Regiao',
                color_discrete_map=REGIAO_CORES,
                orientation='h',
                hover_data=['IDHM'],
                labels={'Percentual': f'% Mães {selected_faixa}', 'Estado': 'Estado'},
                text='Percentual'
            )
            
            fig_rank.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside',
                textfont=dict(color=CORES['texto_graficos'], size=11)
            )
            
            fig_rank.update_layout(
                yaxis=dict(tickfont=dict(size=12, color=CORES['texto_graficos'])),
                height=500,
                margin=dict(l=100, r=20, t=60, b=20)
            )
        else:
            fig_rank = px.bar(
                dados_ranking,
                x='Estado',
                y='Percentual',
                color='Regiao',
                color_discrete_map=REGIAO_CORES,
                hover_data=['IDHM'],
                labels={'Percentual': f'% Mães {selected_faixa}', 'Estado': 'Estado'},
                text='Percentual'
            )
            
            fig_rank.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside',
                textfont=dict(color=CORES['texto_graficos'], size=11)
            )
            
            fig_rank.update_layout(
                xaxis=dict(tickangle=45, tickfont=dict(size=11, color=CORES['texto_graficos'])),
                height=500,
                margin=dict(l=50, r=20, t=60, b=100)
            )
        
        # Aplicar layout com fundo branco
        fig_rank = configurar_layout_plotly(
            fig_rank,
            f'Top 15 Estados - Maior % de Mães {selected_faixa}',
            altura=500,
            rotacao_x=45 if tipo_grafico == "Barras Verticais" else 0
        )
        
        # Gráfico principal COM KEY ÚNICO
        st.plotly_chart(fig_rank, width='stretch', key="ranking_principal")
        
        # Opção de expandir COM KEY ÚNICO
        with st.expander("🔍 Ampliar Gráfico", expanded=False):
            st.plotly_chart(fig_rank, width='stretch', height=600, key="ranking_expandido")

# =============================================================================
# TAB 2: RELATÓRIOS AVANÇADOS
# =============================================================================
with tab2:
    st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <h1 style='font-size: 2rem;'>📋 Relatórios Avançados</h1>
        <p style='font-size: 1rem; color: #5DA9E9;'>
            Análises detalhadas e relatórios personalizados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # RELATÓRIO POR ESTADO
    st.markdown("### 📊 Relatório por Estado")
    
    col_rel1, col_rel2 = st.columns([1, 2])
    
    with col_rel1:
        estado_relatorio = st.selectbox("Selecione o Estado", ['TODOS'] + estados_disponiveis, key="estado_relatorio")
        ano_relatorio = st.selectbox("Ano para Análise", anos_disponiveis, index=len(anos_disponiveis)-1, key="ano_relatorio")
        gerar_relatorio = st.button("📄 Gerar Relatório", width='stretch', key="btn_gerar_relatorio")
    
    with col_rel2:
        st.markdown("#### 📝 Conteúdo do Relatório")
        st.markdown("""
        O relatório completo incluirá:
        
        1. **Análise Demográfica**
        2. **Indicadores de IDHM**
        3. **Correlações e Tendências**
        4. **Recomendações**
        """)
    
    if gerar_relatorio:
        if estado_relatorio == 'TODOS':
            dados_relatorio = df[df['Ano'] == ano_relatorio]
            titulo = f"Relatório Nacional - {ano_relatorio}"
        else:
            dados_relatorio = df[(df['Estado'] == estado_relatorio) & (df['Ano'] == ano_relatorio)]
            titulo = f"Relatório {estado_relatorio} - {ano_relatorio}"
        
        if not dados_relatorio.empty:
            st.markdown(f"### {titulo}")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                # REMOVIDO: key="metric_registros"
                st.metric("Total de Registros", len(dados_relatorio))
            
            with col_r2:
                media_perc = dados_relatorio['Percentual'].mean()
                # REMOVIDO: key="metric_media_maes"
                st.metric("Média % Mães", f"{media_perc:.1f}%")
            
            with col_r3:
                media_idhm = dados_relatorio['IDHM'].mean()
                # REMOVIDO: key="metric_media_idhm"
                st.metric("IDHM Médio", f"{media_idhm:.3f}")
            
            # Distribuição por faixa etária
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
                title=f'Distribuição por Faixa Etária - {ano_relatorio}'
            )
            
            # Aplicar layout com fundo branco
            fig_dist = configurar_layout_plotly(
                fig_dist,
                f'Distribuição por Faixa Etária - {ano_relatorio}',
                altura=400,
                rotacao_x=45
            )
            
            st.plotly_chart(fig_dist, width='stretch', key="dist_faixa_etaria")
            
            # Análise de correlação
            st.markdown("#### 🔗 Análise de Correlação")
            
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
                    title='Correlação por Faixa Etária'
                )
                
                # Aplicar layout com fundo branco
                fig_corr_faixas = configurar_layout_plotly(
                    fig_corr_faixas,
                    'Correlação por Faixa Etária',
                    altura=400,
                    rotacao_x=45
                )
                
                st.plotly_chart(fig_corr_faixas, width='stretch', key="correlacao_faixas")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ANÁLISE COMPARATIVA
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
        key="ano_comparacao_tab2"
    )
    
    if estados_comparar and len(estados_comparar) >= 2:
        dados_comparacao = df[
            (df['Estado'].isin(estados_comparar)) & 
            (df['Ano'] == ano_comparacao) &
            (df['Faixa_Etaria'] == selected_faixa)
        ]
        
        if not dados_comparacao.empty:
            fig_comp = px.bar(
                dados_comparacao,
                x='Estado',
                y='Percentual',
                color='Regiao',
                color_discrete_map=REGIAO_CORES,
                hover_data=['IDHM'],
                title=f'Comparação entre Estados - {selected_faixa}',
                text='Percentual'
            )
            
            fig_comp.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside',
                textfont=dict(color=CORES['texto_graficos'], size=11)
            )
            
            # Aplicar layout com fundo branco
            fig_comp = configurar_layout_plotly(
                fig_comp,
                f'Comparação entre Estados - {selected_faixa}',
                altura=400,
                rotacao_x=45
            )
            
            st.plotly_chart(fig_comp, width='stretch', key="comparacao_estados")
            
            # Tabela comparativa
            st.markdown("#### 📋 Tabela Comparativa")
            
            dados_tabela = dados_comparacao[['Estado', 'Regiao', 'Percentual', 'IDHM']].sort_values('Percentual', ascending=False)
            st.dataframe(dados_tabela, width='stretch', key="tabela_comparativa")

# =============================================================================
# TAB 3: GRÁFICOS COMPARATIVOS
# =============================================================================
with tab3:
    st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <h1 style='font-size: 2rem;'>📈 Gráficos Comparativos</h1>
        <p style='font-size: 1rem; color: #5DA9E9;'>
            Análises avançadas com relatórios dinâmicos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # SEÇÃO 1: RANKING DE ESTADOS
    st.markdown("### 🏆 Ranking de Estados")
    
    col_rank1, col_rank2, col_rank3 = st.columns(3)
    
    with col_rank1:
        ano_ranking = st.selectbox("Ano para Ranking", anos_disponiveis, index=len(anos_disponiveis)-1, key="ano_ranking")
    
    with col_rank2:
        top_n = st.slider("Número de Estados no Ranking", 5, 20, 10, key="top_n")
    
    with col_rank3:
        faixa_ranking = st.selectbox("Faixa Etária para Ranking", faixas_disponiveis, index=2, key="faixa_ranking")
    
    if st.button("📊 Gerar Ranking", key="gerar_ranking", width='stretch'):
        with st.spinner("Gerando ranking..."):
            resultado = plot_ranking_idhm_geral(df, ano_ranking, top_n, faixa_ranking)
            
            if resultado:
                fig_ranking, top_estados, dados_faixa = resultado
                
                # Gráfico principal COM KEY ÚNICO
                st.plotly_chart(fig_ranking, width='stretch', key="ranking_comparativo_principal")
                
                # Opção de expandir COM KEY ÚNICO
                with st.expander("🔍 Ampliar Gráfico", expanded=False):
                    st.plotly_chart(fig_ranking, width='stretch', height=600, key="ranking_comparativo_expandido")
                
                # Gerar gráfico vertical alternativo COM KEY ÚNICO
                st.markdown("### 📊 Vista Alternativa (Vertical)")
                fig_vertical = plot_ranking_vertical(df, ano_ranking, top_n, faixa_ranking)
                if fig_vertical:
                    st.plotly_chart(fig_vertical, width='stretch', key="ranking_vertical")
                
                # Gerar relatório
                relatorio = gerar_relatorio_ranking(top_estados, dados_faixa, top_n, faixa_ranking, ano_ranking)
                
                with st.expander("📋 Ver Relatório Completo do Ranking", expanded=True):
                    st.markdown(relatorio)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # SEÇÃO 2: EVOLUÇÃO TEMPORAL
    st.markdown("### 📅 Evolução Temporal")
    
    col_evo1, col_evo2, col_evo3 = st.columns(3)
    
    with col_evo1:
        tipo_analise = st.selectbox(
            "Tipo de Análise",
            ['Todos Estados', 'Comparação IDHM Geral', 'Estados por Região'],
            key="tipo_analise"
        )
    
    with col_evo2:
        faixa_evolucao = st.selectbox("Faixa Etária", faixas_disponiveis, index=2, key="faixa_evolucao")
    
    with col_evo3:
        if tipo_analise == 'Comparação IDHM Geral':
            estado_evolucao = st.selectbox("Estado", estados_disponiveis, key="estado_evolucao")
        else:
            estado_evolucao = 'Acre'
    
    if st.button("📈 Gerar Evolução", key="gerar_evolucao", width='stretch'):
        with st.spinner("Gerando análise de evolução..."):
            fig_evolucao, relatorio_evolucao = plot_evolucao_completa(
                df, faixa_evolucao, tipo_analise, estado_evolucao
            )
            
            if fig_evolucao:
                # Gráfico principal COM KEY ÚNICO
                st.plotly_chart(fig_evolucao, width='stretch', key="evolucao_principal")
                
                # Opção de expandir COM KEY ÚNICO
                with st.expander("🔍 Ampliar Gráfico", expanded=False):
                    st.plotly_chart(fig_evolucao, width='stretch', height=700, key="evolucao_expandido")
                
                # Exibir relatório
                with st.expander("📋 Relatório da Análise", expanded=True):
                    st.markdown(relatorio_evolucao)
                    
                    # Adicionar estatísticas regionais dinâmicas
                    if tipo_analise == 'Todos Estados':
                        estatisticas = calcular_estatisticas_regionais(df, 2021, faixa_evolucao)
                        if estatisticas:
                            st.markdown("#### 📊 ESTATÍSTICAS ATUALIZADAS:")
                            for regiao, valor in estatisticas.items():
                                st.markdown(f"• **{regiao}:** {valor:.1f}%")

# =============================================================================
# RODAPÉ
# =============================================================================
st.markdown("""
<div style='text-align: center; padding: 15px; color: #666; font-size: 0.8rem; border-top: 1px solid #E8DCCF; margin-top: 20px;'>
    <p>📊 <strong>Dashboard IDHM vs Maternidade</strong> | Análise de dados de 2000-2021</p>
    <p>🛠️ Desenvolvido com Streamlit, Plotly e Pandas | Gerado em {}</p>
    <p>📚 Fontes: DataSUS (SINASC) + Atlas do Desenvolvimento Humano (PNUD)</p>
    <p>🎯 Objetivo: Informar políticas públicas baseadas em evidências</p>
</div>
""".format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)