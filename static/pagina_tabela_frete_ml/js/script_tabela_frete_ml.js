// * [RESUMO] → Script da tela de tabela de frete do ML.
//              Gerencia a calculadora de frete e o destaque da célula correspondente.


// ================================================
// DESTAQUE
// ================================================

function limpar_destaque() {
    document.querySelectorAll('.destaque, .destaque-linha, .destaque-coluna').forEach(function(el) {
        el.classList.remove('destaque', 'destaque-linha', 'destaque-coluna');
    });
}

// ================================================
// ALTURA DA GRADE
// ================================================

// * [EXPLICAÇÃO] → Ajusta a altura da matriz para preencher o espaço restante
//                  da tela sem número fixo — funciona em qualquer resolução.
function ajustar_altura_grade() {
    var container = document.querySelector('.grade-container');
    if (!container) return;
    var distanciaDoTopo = container.getBoundingClientRect().top;
    var margemInferior  = 24;
    container.style.maxHeight = (window.innerHeight - distanciaDoTopo - margemInferior) + 'px';
}



ajustar_altura_grade();
window.addEventListener('resize', ajustar_altura_grade);

// ================================================
// DESTAQUE DA CÉLULA
// ================================================

// * [EXPLICAÇÃO] → Chamada pelo template parcial após o HTMX receber o resultado.
//                  Recebe peso_min e preco_min retornados pelo servidor e localiza
//                  a célula correspondente na tabela usando os data attributes.
function destacar_celula(peso_min, preco_min) {
    limpar_destaque();

    var celula = document.querySelector(
        `td[data-peso-min="${peso_min}"][data-preco-min="${preco_min}"]`
    );
    if (!celula) return;

    celula.classList.add('destaque');
    celula.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // * [EXPLICAÇÃO] → Destaca as células da linha até a coluna da célula encontrada (inclusive).
    var linha     = celula.parentElement;
    var colIndex  = Array.from(linha.children).indexOf(celula);
    Array.from(linha.children).slice(0, colIndex).forEach(function(td) {
        td.classList.add('destaque-linha');
    });

    // * [EXPLICAÇÃO] → Destaca as células da coluna até a linha da célula encontrada (exclusive —
    //                  a célula final já tem .destaque).
    var tabela    = celula.closest('table');
    var linhaIndex = Array.from(tabela.querySelectorAll('tbody tr')).indexOf(linha);
    tabela.querySelectorAll('tbody tr').forEach(function(tr, i) {
        if (i < linhaIndex) {
            var td = tr.children[colIndex];
            if (td) td.classList.add('destaque-coluna');
        }
    });

    // * [EXPLICAÇÃO] → Destaca também o cabeçalho da coluna correspondente.
    var ths = tabela.querySelectorAll('thead th');
    if (ths[colIndex]) ths[colIndex].classList.add('destaque');

    // * [EXPLICAÇÃO] → Destaca os cabeçalhos de peso (De/Até) da linha correspondente.
    var thsPeso = linha.querySelectorAll('td.col-peso');
    thsPeso.forEach(function(th) { th.classList.add('destaque'); });
}