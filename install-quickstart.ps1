# Script de instalação rápida para Windows (PowerShell)
# Execute: .\install-quickstart.ps1

Write-Host "🚀 Instalação Rápida - Projeto Ares" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ Python não encontrado. Instale Python 3.12+ primeiro." -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green

# Verificar Node.js
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCmd) {
    $nodeVersion = node --version
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Node.js não encontrado. Instale Node.js 20+ para compilar o frontend." -ForegroundColor Yellow
}

# Criar ambiente virtual
Write-Host ""
Write-Host "📦 Criando ambiente virtual..." -ForegroundColor Cyan
python -m venv .venv

# Ativar ambiente virtual
Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1

# Atualizar pip
Write-Host "⬆️  Atualizando pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Instalar dependências
Write-Host ""
Write-Host "📥 Instalando dependências Python (modo local - SQLite)..." -ForegroundColor Cyan
pip install -r requirements/local.txt

# Instalar dependências do frontend (se Node.js disponível)
if ($nodeCmd) {
    Write-Host ""
    Write-Host "📥 Instalando dependências do frontend..." -ForegroundColor Cyan
    npm install
    
    Write-Host ""
    Write-Host "🔨 Compilando frontend..." -ForegroundColor Cyan
    npm run build
} else {
    Write-Host "⚠️  Pulando instalação do frontend (Node.js não disponível)" -ForegroundColor Yellow
}

# Migrations
Write-Host ""
Write-Host "🗄️  Aplicando migrations..." -ForegroundColor Cyan
python manage.py migrate

# Collectstatic
Write-Host ""
Write-Host "📂 Coletando arquivos estáticos..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

# Finalização
Write-Host ""
Write-Host "✅ Instalação concluída com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Crie um superusuário: python manage.py createsuperuser"
Write-Host "   2. Execute o servidor: python manage.py runserver"
Write-Host "   3. Acesse: http://127.0.0.1:8000/"
Write-Host ""
Write-Host "💡 Lembre-se de ativar o ambiente virtual antes:" -ForegroundColor Yellow
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host ""
