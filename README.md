# 📦 Stoky — Sistema de Gestão de Estoque

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20Async-d71f00?logo=sqlalchemy&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-17%20Passed-success?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 1 - Qual caso de borda você considerou que mais pode dar problema, e como tratou?

1.	Sobrecargas de pacotes que poderiam causar instabilidade no sistema, causada por envios de caracteres ilimitados. Tratei isto limitando a quantidade de caracteres que podem ser definitos no frontend e que podem ser recebidos no backend. Ficando 100 caracteres para o nome, o preço sendo 10 dígitos e a quantidade sendo limitado a 7 dígitos.

---
## 2 - Se duas vendas acontecerem ao mesmo tempo no mesmo produto, o que pode dar errado?

2.	Perda de dados por sobrescrita
Acontece quando duas requisições leem o valor antes que qualquer uma delas salve o resultado. Exemplo: existem 10 teclados no estoque. Chegam duas vendas ao mesmo tempo: uma de 4 unidades e outra de 5.
  Formato certo: A primeira vende 4 (sobra 6) e a segunda vende 5 sobre o novo total (sobra 1).
  Formato errado: As duas leem o total de 10 ao mesmo tempo. A primeira calcula 10 - 4 = 6 e salva. Um milissegundo depois, a segunda calcula 10 - 5 = 5 e salva por cima. O estoque final fica em 5, e a primeira venda é ignorada.

---

## 3 - O que você faria diferente se o sistema precisasse atender 100 lojas?

3.	Neste caso, posso supor duas soluções em casos diferentes. 

  Se fosse 1 estoque para distribuir em 100 lojas diferentes (um Centro de Distribuição): 
  Permissões divididas por cargos (gerente/coordenador pode dar entrada e vender) e adicionaria um filtro para visualizar o estoque de cada loja para melhor controle.

  Se 100 lojas diferentes fosse usar o mesmo sistema com estoque diferente: Cada loja teria um banco de dados separado, login e senha para cada loja e funcionalidade adicionais especificas para atender o tipo de comércio especifico.


---

## 🌟 Visão Geral

O projeto foi concebido seguindo os mais altos padrões de engenharia de software e arquitetura limpa (**Clean Architecture**, **SOLID** e **Test-Driven Development - TDD**). O sistema disponibiliza uma API RESTful de alta performance integrada a uma interface web elegante, com contraste marcante entre o universo escuro (*Night World*) e o painel operacional claro (*Light World*).

---

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.11+**
- **FastAPI 0.115+**: Framework web moderno, assíncrono e de alto desempenho.
- **SQLAlchemy 2.0 (Asyncio)**: ORM robusto com suporte a conexões assíncronas (`asyncpg` / `aiosqlite`).
- **Pydantic V2**: Validação estrita de tipos, regras de integridade e esquemas de dados.
- **Alembic**: Gerenciamento e versionamento de migrações de banco de dados.
- **Uvicorn**: Servidor ASGI de alta performance.

### Banco de Dados & Infraestrutura
- **PostgreSQL 16**: Banco de dados relacional principal via contêiner Docker.
- **Docker & Docker Compose**: Orquestração simplificada do ambiente de banco de dados.
- **SQLite (In-Memory / aiosqlite)**: Utilizado para testes unitários e de integração ultrarrápidos e isolados.

### Frontend (Mercury Model)
- **HTML5 Semântico**: Estrutura acessível com modais de interação e painel executivo.
- **CSS3 Moderno**: Implementação fiel dos design tokens do Mercury (`#5266eb`, `#171721`, `#fbfcfd`), botões em cápsula (*pill* de 40px) e tipografia Inter em pesos refinados.
- **JavaScript Vanilla**: Comunicação assíncrona (Fetch API), renderização reativa sem necessidade de build/npm e sanitização defensiva contra XSS.

### Qualidade & Testes
- **Pytest & pytest-asyncio**: Suíte automatizada com 17 testes de integração e validação de esquemas.
- **HTTPX (AsyncClient)**: Cliente HTTP assíncrono para testes ponta a ponta dos endpoints.

---

## 🎯 Funcionalidades Principais

- [x] **Catálogo Completo de Produtos (CRUD)**:
  - Cadastro de produtos com nome único, preço unitário e quantidade inicial.
  - Listagem geral e exclusão com diálogo de confirmação.
- [x] **Movimentação de Estoque**:
  - **Entrada (+)**: Adiciona unidades ao inventário existente.
  - **Venda / Saída (-)**: Baixa de estoque com bloqueio defensivo contra saldos negativos.
- [x] **Inteligência e Métricas (Dashboard Executivo)**:
  - **Valor Patrimonial Total (R$)**: Somatório em tempo real de `quantidade × preço` de todos os itens.
  - **Alerta de Estoque Crítico**: Identificação automática de itens com menos de 5 unidades.
  - **Contador do Catálogo**: Totalização imediata de produtos registrados.
- [x] **Interface Reativa**:
  - Busca instantânea por nome do produto.
  - Abas de filtro rápido (*Todos* vs. *Estoque Baixo < 5*).
  - Indicador de status de saúde da API (*Online* / *Offline*) no topo da página.
  - Notificações flutuantes (*Toast*) para respostas rápidas de sucesso ou erro.
- [x] **Limites de Entrada e Segurança Defensiva**:
  - **Nome**: Máximo de 100 caracteres com contador numérico em tempo real.
  - **Preço**: Máximo de 10 caracteres (até R$ 9.999.999,99).
  - **Quantidade**: Máximo de 7 dígitos (até 1.000.000 unidades por operação).
  - Limite dinâmico no modal de venda restrito ao estoque atual disponível.

---

## 📂 Estrutura do Projeto

```text
desafio/
├── alembic/                 # Configurações e scripts de migrações do banco
│   ├── versions/            # Histórico de versões DDL
│   └── env.py               # Configuração do ambiente Alembic
├── backend/                 # Código-fonte da aplicação FastAPI
│   ├── models/              # Modelos ORM SQLAlchemy (Entidade Produto)
│   ├── repositories/        # Camada de acesso a dados (ProdutoRepository)
│   ├── routers/             # Rotas HTTP e controllers FastAPI
│   ├── schemas/             # Esquemas de validação Pydantic V2
│   ├── services/            # Camada de lógica de negócio (ProdutoService)
│   ├── config.py            # Variáveis de ambiente e configurações
│   ├── database.py          # Sessões e conexões com o banco de dados
│   └── main.py              # Inicialização do app, CORS e montagem estática
├── frontend/                # Interface web (Design System Mercury)
│   ├── css/
│   │   └── style.css        # Folha de estilos e variáveis de design tokens
│   ├── js/
│   │   └── app.js           # Lógica reativa de consumo da API e modais
│   └── index.html           # Página principal da aplicação
├── docs/plans/              # Rastreamento de progresso das tarefas do projeto
│   └── task.md              # Quadro de status da entrega
├── mercury-model/           # Especificação e análise visual do Design System Mercury
│   └── DESIGN.md            # Tokens de cores, tipografia, bordas e espaçamentos
├── tests/                   # Suíte de testes automatizados (Pytest)
│   ├── conftest.py          # Fixtures de banco em memória e AsyncClient
│   ├── test_routers.py      # Testes de integração das rotas e endpoints
│   └── test_schemas.py      # Testes unitários dos esquemas Pydantic
├── .env                     # Variáveis de ambiente (URLs de conexão)
├── alembic.ini              # Arquivo de configuração do Alembic
├── docker-compose.yml       # Orquestração do contêiner PostgreSQL
├── pytest.ini               # Configurações do executor de testes Pytest
├── requirements.txt         # Dependências Python do projeto
└── README.md                # Documentação do projeto
```

---

## ⚙️ Pré-requisitos

Para rodar o projeto localmente, certifique-se de possuir instalado:
- **Python 3.11** ou superior
- **Docker** e **Docker Compose**
- **Git** (opcional para clonagem)

---

## 🛠️ Como Executar o Projeto

### 1. Clonar o Repositório e Criar Ambiente Virtual

```bash
# Clone o repositório ou acesse a pasta raiz
cd desafio

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual:
# No Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# No Linux/Mac:
source venv/bin/activate
```

### 2. Configurar as Variáveis de Ambiente

Copie o arquivo de exemplo `.env.example` para `.env`:

```bash
# No Windows (PowerShell):
Copy-Item .env.example .env

# No Linux/Mac:
cp .env.example .env
```

### 3. Instalar as Dependências

```bash
pip install -r requirements.txt
```

### 4. Subir o Banco de Dados PostgreSQL (Docker)

```bash
docker compose up -d
```

> O PostgreSQL estará acessível na porta `5432` com as credenciais configuradas no `.env`.

### 5. Executar as Migrações do Banco (Alembic)

```bash
alembic upgrade head
```

### 6. Iniciar o Servidor da Aplicação

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🌐 Acesso à Aplicação

Após iniciar o servidor, abra seu navegador nos seguintes endereços:

| Serviço | URL | Descrição |
| :--- | :--- | :--- |
| **Aplicação Web (Frontend)** | [http://localhost:8000](http://localhost:8000) | Interface gráfica no padrão visual Mercury |
| **Documentação Interativa (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Teste e documentação Swagger UI da API |
| **Documentação Alternativa (ReDoc)** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Documentação de referência detalhada |
| **Healthcheck** | [http://localhost:8000/health](http://localhost:8000/health) | Verificação de disponibilidade da API |

---

## 🧪 Executando os Testes Automatizados

A aplicação conta com cobertura completa orientada a testes (**TDD**). Para rodar toda a suíte:

```bash
pytest -v
```

Saída esperada:
```text
============================= test session starts =============================
collected 17 items

tests/test_routers.py::test_cadastrar_produto_sucesso PASSED             [  5%]
tests/test_routers.py::test_cadastrar_produto_duplicado_retorna_400 PASSED [ 11%]
tests/test_routers.py::test_listar_produtos PASSED                       [ 17%]
tests/test_routers.py::test_listar_produtos_estoque_baixo_com_limite_configuravel PASSED [ 23%]
tests/test_routers.py::test_calcular_valor_total_estoque PASSED          [ 29%]
tests/test_routers.py::test_entrada_estoque PASSED                       [ 35%]
tests/test_routers.py::test_registrar_venda_sucesso PASSED               [ 41%]
tests/test_routers.py::test_registrar_venda_estoque_insuficiente_retorna_400 PASSED [ 47%]
tests/test_routers.py::test_venda_produto_inexistente_retorna_404 PASSED [ 52%]
tests/test_routers.py::test_deletar_produto PASSED                       [ 58%]
tests/test_routers.py::test_healthcheck_endpoint PASSED                  [ 64%]
tests/test_routers.py::test_servir_frontend_estatico PASSED              [ 70%]
tests/test_schemas.py::test_produto_create_valido PASSED                 [ 76%]
tests/test_schemas.py::test_produto_create_nome_vazio_invalido PASSED    [ 82%]
tests/test_schemas.py::test_produto_create_preco_menor_ou_igual_a_zero_invalido PASSED [ 88%]
tests/test_schemas.py::test_produto_create_quantidade_negativa_invalida PASSED [ 94%]
tests/test_schemas.py::test_quantidade_input_menor_ou_igual_zero_invalido PASSED [100%]

============================= 17 passed in 0.54s ==============================
```

---

## 📡 Endpoints da API REST

Todas as rotas de produtos utilizam o prefixo `/api/produtos`:

| Método | Rota | Descrição | Status de Sucesso |
| :---: | :--- | :--- | :---: |
| `POST` | `/api/produtos/` | Cadastra um novo produto no estoque | `201 Created` |
| `GET` | `/api/produtos/` | Lista todos os produtos cadastrados | `200 OK` |
| `GET` | `/api/produtos/estoque-baixo` | Lista produtos com quantidade menor que o limite (padrão `< 5`) | `200 OK` |
| `GET` | `/api/produtos/valor-estoque` | Retorna o somatório patrimonial do estoque | `200 OK` |
| `PATCH` | `/api/produtos/{id}/entrada` | Adiciona unidades ao estoque do produto | `200 OK` |
| `PATCH` | `/api/produtos/{id}/venda` | Registra saída/venda de unidades (previne saldo negativo) | `200 OK` |
| `DELETE` | `/api/produtos/{id}` | Remove um produto do catálogo | `204 No Content` |
| `GET` | `/health` | Checagem de disponibilidade da API | `200 OK` |

---

## 🏛️ Diretrizes de Código e Arquitetura

O projeto adota a diretriz de **Linguagem Simples e Didática**:
- Todos os módulos, classes e funções possuem comentários e docstrings explicando de forma direta:
  1. *O que este bloco faz?*
  2. *Por que foi feito assim?*
- A camada de dados é estritamente isolada:
  - **Modelos SQLAlchemy**: Representam apenas o esquema relacional e constraints.
  - **Repositórios**: Executam queries e operações no banco.
  - **Serviços**: Aplicam regras de negócio e validações sem acoplamento a frameworks HTTP.
  - **Roteadores**: Recebem requisições, validam parâmetros e devolvem respostas HTTP.

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais detalhes.
