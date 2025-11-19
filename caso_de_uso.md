 # 📘 Casos de Uso — Sistema de Gerenciamento de Estoque Ares

---

## UC01 — Gerenciar Funcionários
**Ator Principal:** Administrador  
**Pré-condições:** O administrador deve estar autenticado no sistema  

### Fluxo Principal
1. O administrador acessa o módulo de gerenciamento de funcionários.  
2. O sistema exibe a lista de funcionários cadastrados.  
3. O administrador seleciona a opção **"Cadastrar novo funcionário"**.  
4. O sistema solicita: nome, login, senha e nível de acesso (Administrador, Operador ou Visualizador).  
5. O administrador preenche as informações e confirma.  
6. O sistema valida os dados e registra o novo funcionário.  
7. O sistema exibe mensagem de confirmação e registra a ação no log.  

### Fluxos Alternativos
**FA01 — Editar funcionário:**  
- No passo 3, o administrador seleciona um funcionário existente e escolhe **"Editar"**.  
- O sistema permite alterar informações (exceto login).  
- Segue para passos 5–7.  

**FA02 — Excluir funcionário:**  
- No passo 3, o administrador seleciona um funcionário e escolhe **"Excluir"**.  
- O sistema solicita confirmação.  
- O sistema inativa o funcionário e registra a ação.  

### Fluxo de Exceção
- **FE01 – Login já existente:** o sistema informa que o login já existe e solicita outro.  
- **FE02 – Dados inválidos:** o sistema exibe mensagem de erro e solicita correção.  

### Pós-condições
- Funcionário cadastrado/alterado com permissões definidas.  

---

## UC02 — Gerenciar Produtos
**Atores Principais:** Administrador, Operador de Estoque  
**Pré-condições:** Usuário deve estar autenticado com permissões adequadas  

### Fluxo Principal
1. O usuário acessa o módulo de produtos.  
2. O sistema exibe a lista de produtos cadastrados.  
3. O usuário seleciona **"Cadastrar novo produto"**.  
4. O sistema solicita: nome, código, descrição, categoria, quantidade inicial e estoque mínimo.  
5. O usuário preenche e confirma.  
6. O sistema valida os dados e registra o produto.  
7. O sistema confirma a operação e registra no log com identificação do usuário.  

### Fluxos Alternativos
**FA01 — Editar produto:**  
- No passo 3, o usuário seleciona um produto e escolhe **"Editar"**.  
- O sistema permite alterar informações.  
- Segue para passos 5–7.

**FA02 — Visualizar detalhes:**  
- No passo 3, o usuário seleciona **"Visualizar"**.  
- O sistema exibe informações completas, incluindo histórico de movimentações.

### Fluxo de Exceção
- **FE01 – Código duplicado**  
- **FE02 – Campos obrigatórios não preenchidos**  
- **FE03 – Permissão insuficiente**  

### Pós-condições
- Produto cadastrado/atualizado no sistema.

---

## UC03 — Registrar Movimentação de Estoque
**Ator Principal:** Operador de Estoque  
**Pré-condições:**  
- Usuário autenticado como Operador ou Administrador  
- Produtos cadastrados  

### Fluxo Principal
1. O operador acessa o módulo de movimentações.  
2. O sistema exibe as opções **Entrada** ou **Saída**.  
3. O operador seleciona o tipo.  
4. O sistema solicita: produto, quantidade e observações (opcional).  
5. O operador preenche e confirma.  
6. O sistema valida os dados.  
7. O sistema atualiza o estoque.  
8. O sistema registra a movimentação (data/hora, tipo, quantidade, responsável).  
9. O sistema verifica se o estoque atingiu o nível mínimo.  
10. O sistema exibe confirmação.  

### Fluxos Alternativos
**FA01 — Múltiplos produtos:**  
- No passo 4, o operador adiciona vários produtos.  
- O sistema processa cada item individualmente.

### Fluxo de Exceção
- **FE01 — Estoque insuficiente para saída**  
- **FE02 — Produto não encontrado**  
- **FE03 — Quantidade inválida**  

### Pós-condições
- Estoque atualizado  
- Movimentação registrada  
- Alerta gerado (se necessário)

---

## UC04 — Consultar e Gerenciar Alertas de Estoque
**Atores:** Administrador, Operador, Gerente  
**Pré-condições:** Usuário autenticado  

### Fluxo Principal
1. O usuário acessa o painel de alertas.  
2. O sistema lista produtos com estoque abaixo ou igual ao mínimo.  
3. Produtos críticos são destacados.  
4. O usuário seleciona um produto.  
5. O sistema exibe: quantidade atual, mínimo, última movimentação e histórico recente.  

### Fluxos Alternativos
**FA01 — Definir estoque mínimo:**  
- O usuário (Administrador ou Operador) altera o valor mínimo do produto.  
- O sistema registra a alteração.

**FA02 — Filtrar alertas:**  
- O usuário filtra por categoria, criticidade ou data.

### Pós-condições
- Usuário informado sobre os produtos críticos.

---

## UC05 — Gerar Relatórios
**Atores:** Gerente, Administrador  
**Pré-condições:** Usuário autenticado com permissão de visualização  

### Fluxo Principal
1. O usuário acessa o módulo de relatórios.  
2. O sistema exibe opções:  
   - Produtos mais vendidos  
   - Histórico de movimentações  
   - Estoque baixo  
   - Atividades por usuário  
3. O usuário seleciona um relatório.  
4. O sistema solicita parâmetros (período, categoria, etc.).  
5. O usuário configura filtros e confirma.  
6. O sistema processa dados.  
7. O relatório é exibido.  
8. O usuário pode exportar (PDF, Excel) ou imprimir.  

### Fluxos Alternativos
**FA01 — Relatório personalizado:**  
- O usuário define filtros e campos personalizados.  
- O sistema gera o relatório.

### Fluxo de Exceção
- **FE01 — Período inválido**  
- **FE02 — Sem dados para os filtros**  

### Pós-condições
