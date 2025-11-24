# Scripts de População do Banco de Dados

Esta pasta contém scripts para popular o banco de dados com dados de teste realistas.

## 📋 Scripts Disponíveis

### 1. `populate_complete.py` ⭐ **RECOMENDADO**
Script completo e organizado que gera dados de **5 anos** (2020-2025).

**Características:**
- ✅ 4 usuários (1 admin + 3 operadores)
- ✅ 12 categorias variadas
- ✅ 10 unidades de medida
- ✅ **80+ produtos** de diferentes categorias
- ✅ **1500+ movimentações** distribuídas de 2020 a 2025
- ✅ Dados realistas com documentos, notas e timestamps
- ✅ Estatísticas completas ao final

**Como usar:**
```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Executar script
python manage.py shell < scripts/populate_complete.py
```

**Tempo de execução:** ~2-3 minutos

---

## 🎯 O que cada script faz?

### `populate_complete.py`
- Cria estrutura completa de dados
- Gera movimentações distribuídas uniformemente ao longo de 5 anos
- Ideal para testar:
  - ✅ Gráficos históricos (dashboard)
  - ✅ Relatórios por período
  - ✅ Análise de tendências
  - ✅ Filtros avançados
  - ✅ Performance com grande volume de dados

---

## 📊 Dados Gerados

### Usuários
| Username | Senha | Perfil | Nome |
|----------|-------|--------|------|
| admin | admin123 | Superusuário | Administrador Sistema |
| joao.silva | senha123 | Operador | João Silva |
| maria.santos | senha123 | Operador | Maria Santos |
| carlos.oliveira | senha123 | Operador | Carlos Oliveira |

### Categorias (12)
- Alimentos
- Bebidas
- Higiene
- Limpeza
- Eletrônicos
- Papelaria
- Ferramentas
- Vestuário
- Automotivo
- Jardinagem
- Pet Shop
- Medicamentos

### Produtos (80+)
Produtos distribuídos entre todas as categorias, com:
- SKUs únicos (ALM001, BEB001, etc.)
- Preços realistas
- Validades variadas
- Estoques mínimos configurados
- Estoque atual calculado pelas movimentações

### Movimentações (1500+)
- **Período:** 01/01/2020 até hoje
- **Tipos:**
  - 40% Entradas (compras, reposições)
  - 45% Saídas (vendas, consumo)
  - 10% Ajustes (correções, quebras)
  - 5% Inventários (contagens)
- **Documentos:** NF, NFe, VD, SAI, AJ, INV, etc.
- **Notas explicativas** em 75% das movimentações
- **Timestamps realistas** (horário comercial 8h-18h)

---

## ⚙️ Configurações Importantes

### Período de Dados
Para alterar o período, edite em `populate_complete.py`:
```python
# Linha ~250
data_inicial = datetime(2020, 1, 1)  # Alterar ano inicial
```

### Quantidade de Movimentações
Para ajustar a densidade de dados:
```python
# Linha ~340
num_movimentacoes = random.randint(15, 30)  # Alterar range
```

### Probabilidade de Tipos
Para ajustar proporção de entradas/saídas:
```python
# Linha ~273
tipos_movimentacao = [
    (InventoryMovement.ENTRADA, 40),   # % entradas
    (InventoryMovement.SAIDA, 45),     # % saídas
    (InventoryMovement.AJUSTE, 10),    # % ajustes
    (InventoryMovement.INVENTARIO, 5), # % inventários
]
```

---

## 🧪 Testando o Sistema

Após executar o script, teste:

### 1. Dashboard
```
http://localhost:8000/dashboard/
```
- Verifique gráfico de movimentações (deve mostrar dados de 2020-2025)
- Teste filtros por período (últimos 7 dias, 30 dias, 12 meses, tudo)
- Verifique alertas de estoque crítico/baixo

### 2. Produtos
```
http://localhost:8000/produtos/
```
- Deve listar 80+ produtos
- Teste filtros por categoria
- Verifique status de estoque (crítico/baixo/OK)

### 3. Movimentações
```
http://localhost:8000/movimentacoes/
```
- Deve listar 1500+ movimentações
- Teste filtros por tipo e período
- Verifique documentos e notas

### 4. Relatórios
```
http://localhost:8000/relatorios/
```
- Gere relatório de estoque
- Gere relatório de movimentações (filtrar 2020-2025)
- Exporte para PDF

---

## 🔄 Limpando o Banco

Para resetar e popular novamente:

```bash
# Deletar banco SQLite
rm db.sqlite3

# Recriar estrutura
python manage.py migrate

# Popular novamente
python manage.py shell < scripts/populate_complete.py
```

---

## 📝 Notas

- **Primeiro uso:** Execute apenas `populate_complete.py`
- **Performance:** Com 1500+ movimentações, queries podem levar alguns segundos
- **Indexação:** As migrations já incluem índices nos campos críticos
- **Dados realistas:** Todos os dados são fictícios mas seguem padrões realistas

---

## 🐛 Troubleshooting

### Erro: "No module named 'produtos'"
```bash
# Certifique-se de estar no diretório correto
cd /home/gedes/Documents/Projeto-Ares-Gestao-de-estoque
```

### Erro: "DJANGO_SETTINGS_MODULE not set"
```bash
# O script define automaticamente, mas pode forçar:
export DJANGO_SETTINGS_MODULE=sitepadrao.settings.development
```

### Muitas movimentações (lento)
```python
# Reduza em populate_complete.py linha ~340:
num_movimentacoes = random.randint(8, 15)  # Antes: 15-30
```

---

## 📧 Suporte

Problemas? Verifique:
1. Ambiente virtual ativado
2. Dependências instaladas (`pip install -r requirements.txt`)
3. Migrations aplicadas (`python manage.py migrate`)
4. Banco de dados limpo (sem dados antigos conflitantes)
