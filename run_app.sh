# run_app.sh
#!/bin/bash
# Script para iniciar o dashboard Streamlit

echo "🚀 Iniciando Dashboard IDHM vs Maternidade..."
echo "📂 Diretório: $(pwd)"
echo "🔧 Verificando dependências..."

# Verificar se o arquivo de dados existe
if [ ! -f "dados_normalizados/comparacao_idhm_idade_mae.csv" ]; then
    echo "❌ ERRO: Arquivo de dados não encontrado!"
    echo "📁 Crie a estrutura:"
    echo "   trabalho_modelagem/"
    echo "   ├── app_idhm.py"
    echo "   ├── dados_normalizados/"
    echo "   │   └── comparacao_idhm_idade_mae.csv"
    echo "   └── requirements.txt"
    exit 1
fi

# Ativar ambiente virtual (se existir)
if [ -d "venv" ]; then
    echo "🔧 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Instalar dependências se necessário
echo "📦 Verificando dependências..."
pip install -r requirements.txt

# Iniciar o Streamlit
echo "🌐 Iniciando dashboard Streamlit..."
echo "👉 Acesse: http://localhost:8501"
echo "👉 Pressione Ctrl+C para parar"

streamlit run app_idhm.py