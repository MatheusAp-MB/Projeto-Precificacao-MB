function ajustarAltura() {
  const wrap = document.querySelector('.prec-tabela-wrap');
  if (!wrap) return;
  const rect = wrap.getBoundingClientRect();
  const alturaDisponivel = window.innerHeight - rect.top - 80;
  wrap.style.maxHeight = Math.max(200, alturaDisponivel) + 'px';
}
// ================================================
// Estado da sessão
// ================================================

const alteracoes = {};

// ================================================
// Toggle do painel de edição
// ================================================

function togglePainel(produtoId, btn) {
  const expandRow = document.getElementById('expand-row-' + produtoId);
  const aberto = expandRow.style.display !== 'none';

  if (aberto) {
    expandRow.style.display = 'none';
    btn.classList.remove('ativo');
    btn.innerHTML = '<i class="fas fa-pencil-alt"></i> Editar';
    } else {
        expandRow.style.display = '';
        btn.classList.add('ativo');
        btn.innerHTML = '<i class="fas fa-chevron-up"></i> Fechar';
        setTimeout(function() { ajustarAlturaPainel(produtoId); }, 50);
      }

  ajustarAltura();
}

// ================================================
// Recalcular produto via HTMX
// ================================================

function recalcularProduto(produtoId) {
  const painel = document.getElementById('painel-' + produtoId);
  if (!painel) return;
  htmx.trigger(painel, 'calcular');
}

// Configura HTMX no painel ao ser carregado
document.body.addEventListener('htmx:afterSwap', function (evt) {
  setTimeout(ajustarAltura, 50);
  const el = evt.detail.target;

  // Encontra o painel dentro do elemento trocado
  const painel = el.querySelector('[id^="painel-"]') || el.closest('[id^="painel-"]');
  if (!painel) return;

  const produtoId = painel.id.replace('painel-', '');

  // Configura HTMX no painel para recalcular
  painel.setAttribute('hx-post', calcularUrl);
  painel.setAttribute('hx-trigger', 'calcular');
  painel.setAttribute('hx-target', '#resultado-' + produtoId);
  painel.setAttribute('hx-include', '#painel-' + produtoId);
  htmx.process(painel);

  // Reaplicar valores alterados que já estavam registrados
  Object.keys(alteracoes).forEach(function (key) {
    if (key.startsWith('prod_' + produtoId + '_')) {
      const campo = key.split('_').slice(2).join('_');
      const input = painel.querySelector('[name="' + campo + '"]');
      if (input) {
        input.value = alteracoes[key].novo;
        input.classList.add('alterado');
      }
    }
  });
});

// ================================================
// Registro de alterações — parâmetros master
// ================================================

function registrarParamMaster(input) {
  const param    = input.dataset.param;
  const original = input.defaultValue;
  const novo     = input.value;
  const key      = 'master_' + param;

  if (novo !== original) {
    alteracoes[key] = {
      campo:  input.dataset.param,
      escopo: 'Todos os produtos',
      antigo: original,
      novo:   novo,
    };
  } else {
    delete alteracoes[key];
  }

  renderAlteracoes();
  atualizarBotoes();
}

// ================================================
// Registro de alterações — campos por produto
// ================================================

function registrarAlteracaoProduto(input) {
  const produtoId   = input.dataset.produtoId;
  const produtoNome = input.dataset.produtoNome;
  const campo       = input.dataset.campo;
  const original    = input.dataset.original;
  const novo        = input.value;
  const key         = 'prod_' + produtoId + '_' + input.name;

  if (novo !== original) {
    alteracoes[key] = {
      campo:  campo,
      escopo: produtoNome,
      antigo: original,
      novo:   novo,
    };
    input.classList.add('alterado');
  } else {
    delete alteracoes[key];
    input.classList.remove('alterado');
  }

  // Marca a linha na tabela
  const row = document.getElementById('row-' + produtoId);
  if (row) {
    const temAlteracao = Object.keys(alteracoes).some(k => k.startsWith('prod_' + produtoId + '_'));
    row.classList.toggle('tem-alteracao', temAlteracao);
  }

  renderAlteracoes();
  atualizarBotoes();
}

// ================================================
// Renderiza o painel de alterações
// ================================================

function renderAlteracoes() {
  const itens  = Object.values(alteracoes);
  const badge  = document.getElementById('badge-alteracoes');
  const lista  = document.getElementById('lista-alteracoes');

  badge.textContent = itens.length;
  badge.classList.toggle('tem-alteracao', itens.length > 0);

  if (itens.length === 0) {
    lista.innerHTML = `
      <div class="alteracoes-vazio">
        <i class="fas fa-check-circle"></i><br>
        Nenhuma alteração<br>na sessão atual
      </div>`;
    return;
  }

  lista.innerHTML = itens.map(function (a) {
    return `
      <div class="alteracao-item">
        <div class="alteracao-escopo">${a.escopo}</div>
        <div class="alteracao-campo">${a.campo}</div>
        <div class="alteracao-diff">
          <span class="diff-antigo">${a.antigo}</span>
          <span>→</span>
          <span class="diff-novo">${a.novo}</span>
        </div>
      </div>`;
  }).join('');
}

// ================================================
// Atualiza estado dos botões da toolbar
// ================================================

function atualizarBotoes() {
  const temAlteracao = Object.keys(alteracoes).length > 0;
  document.getElementById('btn-recalcular').disabled = !temAlteracao;
  document.getElementById('btn-salvar').disabled     = !temAlteracao;
}

// ================================================
// Recalcular / Salvar
// ================================================

function recalcularAlteracoes() {
  alert('Em breve: recalculará apenas os produtos com alterações.');
}

function recalcularTudo() {
  alert('Em breve: recalculará todos os produtos.');
}

function salvar() {
  const params   = {};
  const produtos = {};

  Object.keys(alteracoes).forEach(function (key) {
    const item = alteracoes[key];
    if (key.startsWith('master_')) {
      params[key.replace('master_', '')] = item.novo;
    } else {
      const partes    = key.split('_');
      const produtoId = partes[1];
      const campo     = partes.slice(2).join('_');
      if (!produtos[produtoId]) produtos[produtoId] = { id: produtoId };
      produtos[produtoId][campo] = item.novo;
    }
  });

  fetch(salvarUrl, {
    method:  'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken':  getCookie('csrftoken'),
    },
    body: JSON.stringify({
      parametros: params,
      produtos:   Object.values(produtos),
    }),
  })
  .then(r => r.json())
  .then(function (data) {
    if (data.ok) {
      Object.keys(alteracoes).forEach(k => delete alteracoes[k]);
      renderAlteracoes();
      atualizarBotoes();
      document.querySelectorAll('.tem-alteracao').forEach(r => r.classList.remove('tem-alteracao'));
      document.querySelectorAll('.campo-input.alterado').forEach(i => i.classList.remove('alterado'));
    }
  });
}

// ================================================
// Aviso ao sair sem salvar
// ================================================

window.addEventListener('beforeunload', function (e) {
  if (Object.keys(alteracoes).length > 0) {
    e.preventDefault();
    e.returnValue = '';
  }
});

// ================================================
// Filtro da tabela
// ================================================

function filtrarTabela(q) {
  const termo = q.toLowerCase();
  document.querySelectorAll('.prod-row').forEach(function (row) {
    const nome = row.dataset.nome || '';
    const sku  = row.dataset.sku  || '';
    const visivel = nome.includes(termo) || sku.includes(termo);
    row.style.display = visivel ? '' : 'none';

    // Oculta o expand-row junto se necessário
    const expandRow = document.getElementById('expand-row-' + row.id.replace('row-', ''));
    if (expandRow) expandRow.style.display = visivel ? expandRow.style.display : 'none';
  });
}

// ================================================
// Utilitários
// ================================================

function getCookie(name) {
  const value = '; ' + document.cookie;
  const parts = value.split('; ' + name + '=');
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

// ================================================
// Altura dinâmica da tabela
// ================================================

function ajustarAlturaPainel(produtoId) {
  const painel = document.getElementById('expand-' + produtoId);
  if (!painel) return;
  const top = painel.getBoundingClientRect().top;
  const altura = window.innerHeight - top - 16;
  painel.style.maxHeight = altura + 'px';
  painel.style.overflowY = 'auto';
}

window.addEventListener('resize', ajustarAltura);


function toggleParametros() {
  const conteudo = document.querySelector('.params-grid');
  const frete    = document.querySelector('.frete-link');
  const icon     = document.getElementById('icon-parametros');
  const visivel  = conteudo.style.display !== 'none';
  conteudo.style.display = visivel ? 'none' : '';
  frete.style.display    = visivel ? 'none' : '';
  icon.className         = visivel ? 'fas fa-chevron-down' : 'fas fa-chevron-up';
  setTimeout(ajustarAltura, 200);
}