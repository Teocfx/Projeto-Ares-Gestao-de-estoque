#!/usr/bin/env bash
# Script de instalação rápida para Linux/Mac
# Execute: bash install-quickstart.sh

set -e  # Sair se houver erro

echo "🚀 Instalação Rápida - Projeto Ares"
echo "===================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.12+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js não encontrado. Instale Node.js 20+ para compilar o frontend."
else
    echo "✅ Node.js encontrado: $(node --version)"
fi

# Criar ambiente virtual
echo ""
echo "📦 Criando ambiente virtual..."
python3 -m venv .venv

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

# Atualizar pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo ""
echo "📥 Instalando dependências Python (modo local - SQLite)..."
pip install -r requirements/local.txt

# Instalar dependências do frontend (se Node.js disponível)
if command -v npm &> /dev/null; then
    echo ""
    echo "📥 Instalando dependências do frontend..."
    npm install
    
    echo ""
    echo "🔨 Compilando frontend..."
    npm run build
else
    echo "⚠️  Pulando instalação do frontend (Node.js não disponível)"
fi

# Migrations
echo ""
echo "🗄️  Aplicando migrations..."
python manage.py migrate

# Collectstatic
echo ""
echo "📂 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Finalização
echo ""
echo "✅ Instalação concluída com sucesso!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Crie um superusuário: python manage.py createsuperuser"
echo "   2. Execute o servidor: python manage.py runserver"
echo "   3. Acesse: http://127.0.0.1:8000/"
echo ""
echo "💡 Lembre-se de ativar o ambiente virtual antes:"
echo "   source .venv/bin/activate"
echo ""
