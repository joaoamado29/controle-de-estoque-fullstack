"""
Testes de integração das rotas de Produtos (FastAPI endpoints).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cadastrar_produto_sucesso(client: AsyncClient):
    """Deve cadastrar um novo produto com status 201 e retornar seus dados."""
    payload = {"nome": "Teclado Mecânico", "quantidade": 15, "preco": 250.0}
    response = await client.post("/api/produtos/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["nome"] == "Teclado Mecânico"
    assert data["quantidade"] == 15
    assert data["preco"] == 250.0


@pytest.mark.asyncio
async def test_cadastrar_produto_duplicado_retorna_400(client: AsyncClient):
    """Deve retornar 400 ao tentar cadastrar produto com nome já existente."""
    payload = {"nome": "Mouse Gamer", "quantidade": 10, "preco": 120.0}
    res1 = await client.post("/api/produtos/", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/produtos/", json=payload)
    assert res2.status_code == 400
    assert "já cadastrado" in res2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_listar_produtos(client: AsyncClient):
    """Deve retornar a lista de todos os produtos cadastrados."""
    await client.post("/api/produtos/", json={"nome": "Item A", "quantidade": 10, "preco": 5.0})
    await client.post("/api/produtos/", json={"nome": "Item B", "quantidade": 20, "preco": 10.0})

    response = await client.get("/api/produtos/")
    assert response.status_code == 200
    produtos = response.json()
    assert len(produtos) >= 2


@pytest.mark.asyncio
async def test_listar_produtos_estoque_baixo_com_limite_configuravel(client: AsyncClient):
    """
    Deve listar produtos com quantidade abaixo do limite.
    Testa limite padrão (5) e limite customizável via query param (?limite=8).
    """
    await client.post("/api/produtos/", json={"nome": "Crítico", "quantidade": 2, "preco": 10.0})
    await client.post("/api/produtos/", json={"nome": "Médio", "quantidade": 6, "preco": 15.0})
    await client.post("/api/produtos/", json={"nome": "Abundante", "quantidade": 20, "preco": 5.0})

    # Limite padrão = 5 (deve retornar apenas 'Crítico')
    res_padrao = await client.get("/api/produtos/estoque-baixo")
    assert res_padrao.status_code == 200
    nomes_padrao = [p["nome"] for p in res_padrao.json()]
    assert "Crítico" in nomes_padrao
    assert "Médio" not in nomes_padrao
    assert "Abundante" not in nomes_padrao

    # Limite configurável = 8 (deve retornar 'Crítico' e 'Médio')
    res_custom = await client.get("/api/produtos/estoque-baixo?limite=8")
    assert res_custom.status_code == 200
    nomes_custom = [p["nome"] for p in res_custom.json()]
    assert "Crítico" in nomes_custom
    assert "Médio" in nomes_custom
    assert "Abundante" not in nomes_custom


@pytest.mark.asyncio
async def test_calcular_valor_total_estoque(client: AsyncClient):
    """
    Deve calcular o valor total do estoque: soma de (quantidade * preco) de cada produto.
    Exemplo: (10 * 20.0) + (5 * 50.0) = 200 + 250 = 450.0
    """
    await client.post("/api/produtos/", json={"nome": "Produto X", "quantidade": 10, "preco": 20.0})
    await client.post("/api/produtos/", json={"nome": "Produto Y", "quantidade": 5, "preco": 50.0})

    response = await client.get("/api/produtos/valor-estoque")
    assert response.status_code == 200
    data = response.json()
    assert "valor_total" in data
    assert data["valor_total"] == 450.0


@pytest.mark.asyncio
async def test_entrada_estoque(client: AsyncClient):
    """Deve aumentar a quantidade do produto no estoque."""
    create_res = await client.post("/api/produtos/", json={"nome": "Monitor", "quantidade": 8, "preco": 800.0})
    prod_id = create_res.json()["id"]

    response = await client.patch(f"/api/produtos/{prod_id}/entrada", json={"quantidade": 4})
    assert response.status_code == 200
    data = response.json()
    assert data["quantidade"] == 12


@pytest.mark.asyncio
async def test_registrar_venda_sucesso(client: AsyncClient):
    """Deve diminuir a quantidade do produto no estoque."""
    create_res = await client.post("/api/produtos/", json={"nome": "Cabo HDMI", "quantidade": 10, "preco": 25.0})
    prod_id = create_res.json()["id"]

    response = await client.patch(f"/api/produtos/{prod_id}/venda", json={"quantidade": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["quantidade"] == 7


@pytest.mark.asyncio
async def test_registrar_venda_estoque_insuficiente_retorna_400(client: AsyncClient):
    """Não pode permitir venda com quantidade maior que o estoque (estoque não pode ser negativo)."""
    create_res = await client.post("/api/produtos/", json={"nome": "Webcam", "quantidade": 3, "preco": 150.0})
    prod_id = create_res.json()["id"]

    # Tentativa de vender 5 quando só há 3
    response = await client.patch(f"/api/produtos/{prod_id}/venda", json={"quantidade": 5})
    assert response.status_code == 400
    assert "insuficiente" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_venda_produto_inexistente_retorna_404(client: AsyncClient):
    """Deve retornar 404 ao tentar registrar venda de produto inexistente."""
    response = await client.patch("/api/produtos/9999/venda", json={"quantidade": 1})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deletar_produto(client: AsyncClient):
    """Deve remover o produto e retornar 204."""
    create_res = await client.post("/api/produtos/", json={"nome": "Obsoleto", "quantidade": 1, "preco": 10.0})
    prod_id = create_res.json()["id"]

    del_res = await client.delete(f"/api/produtos/{prod_id}")
    assert del_res.status_code == 204

    # Confirma que produto não existe mais
    venda_res = await client.patch(f"/api/produtos/{prod_id}/venda", json={"quantidade": 1})
    assert venda_res.status_code == 404


@pytest.mark.asyncio
async def test_healthcheck_endpoint(client: AsyncClient):
    """
    O que faz: Testa se o endpoint /health responde corretamente com status ok.
    Por que assim: Garante que os serviços de monitoramento consigam checar a saúde da API.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_servir_frontend_estatico(client: AsyncClient):
    """
    O que faz: Testa se a página inicial (/) carrega o arquivo index.html do frontend Mercury do Stoky.
    Por que assim: Assegura que o frontend integrado seja entregue corretamente pelo servidor FastAPI.
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert "Stoky" in response.text
    assert "Gestão de Estoque" in response.text


@pytest.mark.asyncio
async def test_produto_com_aspas_e_caracteres_especiais(client: AsyncClient):
    """
    O que faz: Testa o ciclo de vida de produtos contendo aspas simples ('), duplas (\") e apóstrofos.
    Por que assim: Garante que caracteres especiais nos nomes sejam persistidos e excluídos com segurança
    sem quebrar a API, banco de dados ou renderização.
    """
    nome_com_aspas = "Óleo D'Oliveira Extra 500ml \"Premium\""
    payload = {"nome": nome_com_aspas, "quantidade": 8, "preco": 35.90}

    # 1. Cadastro com aspas simples e duplas
    res_post = await client.post("/api/produtos/", json=payload)
    assert res_post.status_code == 201
    prod = res_post.json()
    assert prod["nome"] == nome_com_aspas
    prod_id = prod["id"]

    # 2. Busca e listagem
    res_list = await client.get("/api/produtos/")
    assert res_list.status_code == 200
    nomes = [p["nome"] for p in res_list.json()]
    assert nome_com_aspas in nomes

    # 3. Exclusão bem sucedida
    res_del = await client.delete(f"/api/produtos/{prod_id}")
    assert res_del.status_code == 204


@pytest.mark.asyncio
async def test_resistencia_contra_sql_injection(client: AsyncClient):
    """
    O que faz: Testa payloads maliciosos de SQL Injection como nomes de produto.
    Por que assim: Comprova que as consultas parametrizadas do SQLAlchemy tratam o payload
    estritamente como texto puro (data literal), impedindo injeção de comandos SQL ou quebra de tabela.
    """
    payload_sqli = "Robert'); DROP TABLE produtos;--"
    res = await client.post(
        "/api/produtos/",
        json={"nome": payload_sqli, "quantidade": 5, "preco": 10.0}
    )
    assert res.status_code == 201
    prod_id = res.json()["id"]

    # A tabela continua íntegra e o produto com nome malicioso pode ser consultado normalmente
    res_check = await client.get("/api/produtos/")
    assert res_check.status_code == 200
    assert any(p["id"] == prod_id for p in res_check.json())

    # Deleta o produto de teste
    del_res = await client.delete(f"/api/produtos/{prod_id}")
    assert del_res.status_code == 204

