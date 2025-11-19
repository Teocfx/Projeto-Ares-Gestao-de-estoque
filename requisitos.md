## 📦 ARES Sistema de Gerenciamento e Controle de Estoque

O uso de um sistema de gerenciamento e controle de estoque traz melhorias significativas em diversos setores. A flexibilidade e a adaptabilidade tornam-se essenciais para empresas que desejam otimizar suas operações.  
O monitoramento constante proporciona maior eficiência, colaborando para o bom funcionamento do negócio e evitando perdas financeiras decorrentes da falta de organização ou falhas na comunicação.

### 🔧 Funcionalidades Principais
- Cadastro de produtos  
- Controle de entradas e saídas  
- Controle de estoque em tempo real  
- Níveis mínimos e alertas (estoque mínimo + notificação)  
- Relatórios básicos:
  - Produtos mais vendidos  
  - Histórico de movimentações por período  

---

## ✅ Requisitos Funcionais (RF)

**RF1** – O sistema deve permitir cadastro de funcionários, com definição de login, senha e nível de acesso.  
**RF2** – O sistema deve permitir o cadastro de produtos, incluindo nome, código, descrição e categoria.  
**RF3** – O sistema deve permitir o registro de entradas e saídas de produtos, atualizando o estoque e registrando quantidade e responsável.  
**RF4** – O sistema deve permitir a definição de estoque mínimo e gerar alertas ao atingir ou ficar abaixo do nível definido.  
**RF5** – O sistema deve gerar relatórios de movimentação, incluindo itens mais vendidos e histórico por período.  
**RF6** – O sistema deve permitir acesso e controle de estoque conforme o nível de permissão do funcionário.  
**RF7** – O sistema deve registrar as alterações feitas por usuários de acordo com seu nível de acesso.  
**RF8** – O sistema deve associar cada ação ao respectivo usuário e seu nível de acesso, garantindo rastreabilidade.  
**RF9** – O sistema deve permitir que o usuário cadastre e atualize produtos diariamente, mantendo a organização da movimentação.  
**RF10** – O sistema deve permitir alterar a quantidade de produtos em estoque e cadastrar novos produtos, registrando todas as mudanças corretamente.  

---

## ⚙️ Requisitos Não Funcionais (RNF)

**RNF1** – O sistema deve ser confiável e garantir a correção de alterações caso o usuário cometa erros, mantendo a integridade dos dados.  
**RNF2** – O banco de dados deve seguir um formato padrão, evitando inconsistências e preservando a integridade.  
**RNF3** – O sistema deve realizar backup dos dados alterados e manter o banco atualizado, evitando perda de informações.  
**RNF4** – O sistema deve manter registros de todas as alterações dos usuários, garantindo rastreabilidade.  
**RNF5** – O sistema deve ser acessível via navegador, em desktops e tablets.  
**RNF6** – O backend deve validar requisições e garantir autenticação/autorização conforme nível de usuário.  
**RNF7** – A interface deve ser intuitiva e de fácil navegação.  
**RNF8** – O sistema deve fornecer mensagens claras de erro e confirmação em todas as operações.  
**RNF9** – O sistema deve controlar o acesso às funcionalidades por nível de usuário (administrador, operador, visualizador).  
**RNF10** – O sistema deve registrar todas as ações para rastreabilidade.  

---