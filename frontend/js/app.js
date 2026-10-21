/**
 * Stoky — Gestão de Estoque no estilo Mercury (Frontend JavaScript).
 * 
 * O que este arquivo faz?
 * Gerencia a comunicação assíncrona (Fetch API) com o backend FastAPI,
 * atualiza o painel de estatísticas, renderiza dinamicamente a tabela de produtos,
 * controla a abertura e fechamento de modais e exibe notificações toast ao usuário.
 * 
 * Por que foi feito assim?
 * Utilizar JavaScript Vanilla (sem frameworks pesados) mantém o frontend leve,
 * rápido, de fácil manutenção e sem necessidade de etapas adicionais de build (npm/webpack).
 */

// ─── Configurações e Estado Global ───
// Detecta automaticamente o endereço da API se estiver rodando no mesmo servidor ou localmente
const API_BASE = (window.location.protocol === "file:" || !window.location.port || window.location.port !== "8000")
  ? "http://localhost:8000/api/produtos"
  : "/api/produtos";

const HEALTH_URL = (window.location.protocol === "file:" || !window.location.port || window.location.port !== "8000")
  ? "http://localhost:8000/health"
  : "/health";

let produtosCache = [];      // Armazena os produtos carregados da API
let filtroAtual = "todos";   // "todos" ou "criticos"
let termoBusca = "";         // Texto digitado na caixa de busca

// ─── Inicialização da Aplicação ───
document.addEventListener("DOMContentLoaded", () => {
  /*
   * O que faz: Registra ouvintes de eventos e inicia o carregamento dos dados.
   * Por que assim: Garante que os elementos do DOM já existam antes de serem manipulados.
   */
  configurarOuvintes();
  verificarConexaoAPI();
  carregarDados();
});

/**
 * O que esta função faz?
 * Vincula os botões da interface aos seus respectivos manipuladores de eventos.
 */
function configurarOuvintes() {
  // Botão para abrir o modal de cadastro de novo produto
  const btnNovo = document.getElementById("btn-abrir-novo-produto");
  if (btnNovo) {
    btnNovo.addEventListener("click", () => {
      // Reseta o contador de caracteres do nome ao abrir
      const contador = document.getElementById("contador-nome");
      if (contador) contador.textContent = "0";
      abrirModal("modal-novo-produto");
    });
  }

  // Campo de busca em tempo real
  const inputBusca = document.getElementById("input-busca");
  if (inputBusca) {
    inputBusca.addEventListener("input", (e) => {
      termoBusca = e.target.value.toLowerCase().trim();
      renderizarTabela();
    });
  }

  /*
   * O que este bloco faz?
   * Aplica limites de digitação em tempo real aos campos de entrada de dados.
   * - Nome: máximo de 100 caracteres e atualização de contador numérico.
   * - Preço: máximo de 10 caracteres (ex: 9999999.99).
   * - Quantidades: máximo de 7 dígitos (até 1.000.000).
   * 
   * Por que foi feito assim?
   * O atributo type="number" no HTML padrão não bloqueia digitações excessivas
   * em alguns navegadores. Este controle garante uma experiência uniforme e impede
   * envio de dados fora dos padrões do banco.
   */
  const campoNome = document.getElementById("campo-nome");
  const contadorNome = document.getElementById("contador-nome");
  if (campoNome && contadorNome) {
    campoNome.addEventListener("input", () => {
      if (campoNome.value.length > 100) {
        campoNome.value = campoNome.value.slice(0, 100);
      }
      contadorNome.textContent = campoNome.value.length;
    });
  }

  const campoPreco = document.getElementById("campo-preco");
  if (campoPreco) {
    campoPreco.addEventListener("input", () => {
      if (campoPreco.value.length > 10) {
        campoPreco.value = campoPreco.value.slice(0, 10);
      }
    });
  }

  const campoQuantidade = document.getElementById("campo-quantidade");
  if (campoQuantidade) {
    campoQuantidade.addEventListener("input", () => {
      if (campoQuantidade.value.length > 7) {
        campoQuantidade.value = campoQuantidade.value.slice(0, 7);
      }
    });
  }

  const entradaQuantidade = document.getElementById("entrada-quantidade");
  if (entradaQuantidade) {
    entradaQuantidade.addEventListener("input", () => {
      if (entradaQuantidade.value.length > 7) {
        entradaQuantidade.value = entradaQuantidade.value.slice(0, 7);
      }
    });
  }

  const vendaQuantidade = document.getElementById("venda-quantidade");
  if (vendaQuantidade) {
    vendaQuantidade.addEventListener("input", () => {
      if (vendaQuantidade.value.length > 7) {
        vendaQuantidade.value = vendaQuantidade.value.slice(0, 7);
      }
    });
  }

  // Fecha modais ao clicar no fundo escuro (backdrop)
  document.querySelectorAll(".modal-backdrop").forEach(backdrop => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) {
        fecharModal(backdrop.id);
      }
    });
  });
}

/**
 * O que esta função faz?
 * Checa a saúde da API (healthcheck) e atualiza o indicador visual no cabeçalho.
 * 
 * Por que foi feito assim?
 * Dá clareza imediata ao usuário sobre o status do servidor, evitando confusão
 * se o backend não estiver rodando no momento do teste.
 */
async function verificarConexaoAPI() {
  const badge = document.getElementById("api-status-badge");
  if (!badge) return;

  try {
    const res = await fetch(HEALTH_URL);
    if (res.ok) {
      badge.className = "badge-status badge-online";
      badge.innerHTML = '<span class="status-dot"></span> API Online (FastAPI)';
    } else {
      throw new Error();
    }
  } catch (err) {
    badge.className = "badge-status badge-offline";
    badge.innerHTML = '<span class="status-dot"></span> API Desconectada';
  }
}

/**
 * O que esta função faz?
 * Faz requisições simultâneas para buscar a lista de produtos e o valor patrimonial total.
 * 
 * Por que foi feito assim?
 * O uso de `Promise.all` executa as duas consultas em paralelo, reduzindo o tempo de espera.
 */
async function carregarDados() {
  try {
    const [resProdutos, resValor] = await Promise.all([
      fetch(`${API_BASE}/`),
      fetch(`${API_BASE}/valor-estoque`)
    ]);

    if (!resProdutos.ok || !resValor.ok) {
      throw new Error("Erro ao consultar a API.");
    }

    produtosCache = await resProdutos.json();
    const dadosValor = await resValor.json();

    atualizarDashboard(produtosCache, dadosValor.valor_total);
    renderizarTabela();
  } catch (error) {
    console.error("Falha ao carregar dados:", error);
    mostrarToast("Não foi possível carregar os dados da API.", true);
  }
}

/**
 * O que esta função faz?
 * Atualiza os 3 cartões de métricas (Valor Total, Catálogo e Estoque Crítico).
 * 
 * Por que foi feito assim?
 * Centraliza o cálculo e a formatação numérica dos indicadores principais.
 */
function atualizarDashboard(produtos, valorTotal) {
  // Formata o valor monetário no padrão brasileiro (R$ 0.000,00)
  const formatadorMoeda = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL"
  });

  const elementoValor = document.getElementById("stat-valor-total");
  const elementoTotal = document.getElementById("stat-total-produtos");
  const elementoBaixo = document.getElementById("stat-estoque-baixo");

  if (elementoValor) elementoValor.textContent = formatadorMoeda.format(valorTotal);
  if (elementoTotal) elementoTotal.textContent = produtos.length;

  // Conta quantos produtos têm estoque abaixo de 5 unidades
  const qtdEstoqueBaixo = produtos.filter(p => p.quantidade < 5).length;
  if (elementoBaixo) elementoBaixo.textContent = qtdEstoqueBaixo;
}

/**
 * O que esta função faz?
 * Alterna a aba ativa entre "todos" e "criticos", re-renderizando a tabela.
 */
function definirFiltro(tipo) {
  filtroAtual = tipo;
  
  const tabTodos = document.getElementById("tab-todos");
  const tabCriticos = document.getElementById("tab-criticos");

  if (tabTodos && tabCriticos) {
    if (tipo === "todos") {
      tabTodos.classList.add("active");
      tabCriticos.classList.remove("active");
    } else {
      tabCriticos.classList.add("active");
      tabTodos.classList.remove("active");
    }
  }

  renderizarTabela();
}

/**
 * O que esta função faz?
 * Constrói o HTML da tabela aplicando os filtros de busca e de aba selecionados.
 * 
 * Por que foi feito assim?
 * A renderização reativa a partir de `produtosCache` permite buscas instantâneas
 * sem gerar requisições adicionais ao banco de dados a cada tecla digitada.
 */
function renderizarTabela() {
  const corpoTabela = document.getElementById("tabela-produtos-corpo");
  if (!corpoTabela) return;

  // Aplica o filtro de estoque baixo se selecionado
  let listaFiltrada = produtosCache;
  if (filtroAtual === "criticos") {
    listaFiltrada = listaFiltrada.filter(p => p.quantidade < 5);
  }

  // Aplica o filtro de texto
  if (termoBusca) {
    listaFiltrada = listaFiltrada.filter(p => p.nome.toLowerCase().includes(termoBusca));
  }

  // Se não houver produtos, exibe mensagem amigável de estado vazio
  if (listaFiltrada.length === 0) {
    corpoTabela.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; padding: 48px; color: var(--color-slate);">
          Nenhum produto encontrado para os critérios selecionados.
        </td>
      </tr>
    `;
    return;
  }

  const formatadorMoeda = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL"
  });

  // Gera o HTML de cada linha da tabela
  corpoTabela.innerHTML = listaFiltrada.map(produto => {
    const isEstoqueBaixo = produto.quantidade < 5;
    const classeBadge = isEstoqueBaixo ? "stock-badge stock-low" : "stock-badge stock-normal";
    const textoBadge = isEstoqueBaixo ? `${produto.quantidade} un.  ⚠️  ` : `${produto.quantidade} un.`;
    const valorTotalItem = produto.preco * produto.quantidade;

    return `
      <tr>
        <td style="color: var(--color-slate); font-weight: 500;">#${produto.id}</td>
        <td class="product-name-cell">${escapeHtml(produto.nome)}</td>
        <td>${formatadorMoeda.format(produto.preco)}</td>
        <td><span class="${classeBadge}">${textoBadge}</span></td>
        <td style="font-weight: 500;">${formatadorMoeda.format(valorTotalItem)}</td>
        <td>
          <div class="action-buttons">
            <button 
              type="button" 
              class="btn-table-action" 
              title="Adicionar unidades ao estoque"
              onclick="abrirModalEntrada(${produto.id})"
            >
              Entrada
            </button>
            <button 
              type="button" 
              class="btn-table-action" 
              title="Registrar venda/saída deste produto"
              onclick="abrirModalVenda(${produto.id})"
            >
              Venda
            </button>
            <button 
              type="button" 
              class="btn-table-action btn-table-danger" 
              title="Excluir produto do catálogo"
              onclick="confirmarExclusao(${produto.id}, '${escapeHtml(produto.nome)}')"
            >
              Excluir
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

// ─── Manipulação de Modais ───

function abrirModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("active");
  }
}

function fecharModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("active");
  }
}

/**
 * Abre o modal de entrada preenchendo os dados do produto correspondente.
 */
function abrirModalEntrada(produtoId) {
  const produto = produtosCache.find(p => p.id === produtoId);
  if (!produto) return;

  document.getElementById("entrada-produto-id").value = produto.id;
  document.getElementById("entrada-produto-nome").textContent = produto.nome;
  document.getElementById("entrada-produto-atual").textContent = produto.quantidade;
  document.getElementById("entrada-quantidade").value = "";

  abrirModal("modal-entrada-estoque");
}

/**
 * Abre o modal de venda preenchendo os dados do produto correspondente.
 * Define o limite máximo de venda baseado no estoque disponível em tempo real.
 */
function abrirModalVenda(produtoId) {
  const produto = produtosCache.find(p => p.id === produtoId);
  if (!produto) return;

  document.getElementById("venda-produto-id").value = produto.id;
  document.getElementById("venda-produto-nome").textContent = produto.nome;
  document.getElementById("venda-produto-atual").textContent = produto.quantidade;
  
  const inputVenda = document.getElementById("venda-quantidade");
  inputVenda.value = "";
  inputVenda.max = produto.quantidade; // Limita o valor máximo no formulário

  const helperVenda = document.getElementById("helper-venda");
  if (helperVenda) {
    helperVenda.textContent = `Máx. ${produto.quantidade} un. disponíveis no estoque`;
  }

  abrirModal("modal-venda-estoque");
}

// ─── Ações de Envio de Dados (POST / PATCH / DELETE) ───

/**
 * O que esta função faz?
 * Envia uma requisição POST para cadastrar um novo produto.
 * 
 * Por que foi feito assim?
 * Valida rigorosamente os limites de caracteres (nome <= 100, preço <= 10 dígitos/caracteres,
 * quantidade <= 7 dígitos/1.000.000) antes de disparar a requisição ao servidor.
 */
async function submeterNovoProduto(event) {
  event.preventDefault();

  const inputNome = document.getElementById("campo-nome");
  const inputPreco = document.getElementById("campo-preco");
  const inputQtd = document.getElementById("campo-quantidade");

  const nome = inputNome.value.trim();
  const preco = parseFloat(inputPreco.value);
  const quantidade = parseInt(inputQtd.value, 10);

  // Validação de limites no frontend
  if (!nome) {
    mostrarToast("Por favor, informe o nome do produto.", true);
    return;
  }
  if (nome.length > 100) {
    mostrarToast("O nome do produto deve ter no máximo 100 caracteres.", true);
    return;
  }
  if (isNaN(preco) || preco <= 0) {
    mostrarToast("O preço unitário deve ser maior que zero.", true);
    return;
  }
  if (inputPreco.value.length > 10 || preco > 9999999.99) {
    mostrarToast("O preço deve ter no máximo 10 caracteres (até R$ 9.999.999,99).", true);
    return;
  }
  if (isNaN(quantidade) || quantidade < 0) {
    mostrarToast("A quantidade em estoque não pode ser negativa.", true);
    return;
  }
  if (inputQtd.value.length > 7 || quantidade > 1000000) {
    mostrarToast("A quantidade não pode exceder 1.000.000 unidades (máx. 7 dígitos).", true);
    return;
  }

  try {
    const resposta = await fetch(`${API_BASE}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, preco, quantidade })
    });

    if (!resposta.ok) {
      const erro = await resposta.json();
      throw new Error(erro.detail || "Erro ao cadastrar produto.");
    }

    mostrarToast(`Produto "${nome}" cadastrado com sucesso!`);
    fecharModal("modal-novo-produto");
    document.getElementById("form-novo-produto").reset();
    const contador = document.getElementById("contador-nome");
    if (contador) contador.textContent = "0";
    await carregarDados();
  } catch (error) {
    mostrarToast(error.message, true);
  }
}

/**
 * O que esta função faz?
 * Envia uma requisição PATCH para somar estoque a um produto existente.
 * Valida limite máximo de 7 dígitos (até 1.000.000 unidades por movimentação).
 */
async function submeterEntradaEstoque(event) {
  event.preventDefault();

  const produtoId = document.getElementById("entrada-produto-id").value;
  const inputQtd = document.getElementById("entrada-quantidade");
  const quantidade = parseInt(inputQtd.value, 10);

  if (!quantidade || quantidade <= 0) {
    mostrarToast("Informe uma quantidade válida maior que zero.", true);
    return;
  }
  if (inputQtd.value.length > 7 || quantidade > 1000000) {
    mostrarToast("A quantidade de entrada não pode exceder 1.000.000 unidades.", true);
    return;
  }

  try {
    const resposta = await fetch(`${API_BASE}/${produtoId}/entrada`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quantidade })
    });

    if (!resposta.ok) {
      const erro = await resposta.json();
      throw new Error(erro.detail || "Erro ao registrar entrada.");
    }

    mostrarToast(`Entrada de ${quantidade} unidade(s) registrada com sucesso!`);
    fecharModal("modal-entrada-estoque");
    await carregarDados();
  } catch (error) {
    mostrarToast(error.message, true);
  }
}

/**
 * O que esta função faz?
 * Envia uma requisição PATCH para dar baixa (venda) de estoque.
 * Valida limites de caracteres e se a quantidade não supera o estoque disponível.
 */
async function submeterVendaEstoque(event) {
  event.preventDefault();

  const produtoId = parseInt(document.getElementById("venda-produto-id").value, 10);
  const inputQtd = document.getElementById("venda-quantidade");
  const quantidade = parseInt(inputQtd.value, 10);

  if (!quantidade || quantidade <= 0) {
    mostrarToast("Informe uma quantidade válida maior que zero.", true);
    return;
  }
  if (inputQtd.value.length > 7 || quantidade > 1000000) {
    mostrarToast("A quantidade vendida não pode exceder 1.000.000 unidades.", true);
    return;
  }

  // Validação preventiva no frontend: impede tentar vender mais do que tem no estoque
  const produto = produtosCache.find(p => p.id === produtoId);
  if (produto && quantidade > produto.quantidade) {
    mostrarToast(`Estoque insuficiente! Disponível: apenas ${produto.quantidade} un.`, true);
    return;
  }

  try {
    const resposta = await fetch(`${API_BASE}/${produtoId}/venda`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quantidade })
    });

    if (!resposta.ok) {
      const erro = await resposta.json();
      throw new Error(erro.detail || "Erro ao registrar venda.");
    }

    mostrarToast(`Venda de ${quantidade} unidade(s) registrada com sucesso!`);
    fecharModal("modal-venda-estoque");
    await carregarDados();
  } catch (error) {
    mostrarToast(error.message, true);
  }
}

/**
 * O que esta função faz?
 * Abre o card modal em HTML para confirmação antes de excluir o produto.
 * 
 * Por que foi feito assim?
 * Substitui o confirm() nativo do navegador por um card estilizado no padrão Mercury,
 * proporcionando uma experiência visual consistente, segura e adaptada para mobile.
 */
function confirmarExclusao(produtoId, nome) {
  const produto = produtosCache.find(p => p.id === produtoId);
  const nomeProduto = produto ? produto.nome : nome;

  const inputId = document.getElementById("exclusao-produto-id");
  const elementoNome = document.getElementById("exclusao-produto-nome");

  if (inputId) inputId.value = produtoId;
  if (elementoNome) elementoNome.textContent = nomeProduto;

  abrirModal("modal-confirmar-exclusao");
}

/**
 * O que esta função faz?
 * Executa a exclusão definitiva do produto via requisição DELETE após a confirmação no card HTML.
 * 
 * Por que foi feito assim?
 * Separa a etapa de confirmação visual do usuário da execução assíncrona com a API.
 */
async function executarExclusao() {
  const inputId = document.getElementById("exclusao-produto-id");
  const produtoId = inputId ? inputId.value : null;
  const elementoNome = document.getElementById("exclusao-produto-nome");
  const nome = elementoNome ? elementoNome.textContent : "Item";

  if (!produtoId) return;

  try {
    const resposta = await fetch(`${API_BASE}/${produtoId}`, {
      method: "DELETE"
    });

    if (!resposta.ok && resposta.status !== 204) {
      const erro = await resposta.json();
      throw new Error(erro.detail || "Erro ao excluir produto.");
    }

    fecharModal("modal-confirmar-exclusao");
    mostrarToast(`Produto "${nome}" excluído com sucesso.`);
    await carregarDados();
  } catch (error) {
    fecharModal("modal-confirmar-exclusao");
    mostrarToast(error.message, true);
  }
}

// ─── Utilitários (Toast e Escape HTML) ───

/**
 * O que esta função faz?
 * Exibe uma notificação flutuante suave (Toast) no canto inferior da tela.
 * 
 * Por que foi feito assim?
 * Feedback visual não bloqueante que melhora a experiência de uso (UX).
 */
function mostrarToast(mensagem, isErro = false) {
  const toast = document.getElementById("toast");
  if (!toast) return;

  toast.textContent = mensagem;
  toast.style.backgroundColor = isErro ? "var(--color-danger)" : "var(--color-night)";
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3500);
}

/**
 * Previne ataques de XSS simples limpando tags HTML antes de renderizar strings de texto.
 */
function escapeHtml(texto) {
  if (!texto) return "";
  return String(texto)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
