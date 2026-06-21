// ================================================
// Limpa o destaque de todas as células da grade
// ================================================
function limpar_destaque() {
  document.querySelectorAll('.grade-tabela td.destaque').forEach(function(cel) {
    cel.classList.remove('destaque');
  });
}

// ================================================
// Destaca a célula correspondente ao resultado
// Chamada pelo HTMX após receber a resposta
// ================================================
function destacar_celula(peso_min, preco_min) {
  limpar_destaque();
  var celula = document.querySelector(
    `td[data-peso="${peso_min}"][data-preco="${preco_min}"]`
  );
  if (celula) {
    celula.classList.add('destaque');
    celula.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

// ================================================
// Ajusta a altura da grade para preencher o
// espaço restante da tela — funciona em qualquer
// resolução, sem número fixo
// ================================================
function ajustar_altura_grade() {
  var container = document.querySelector('.grade-container');
  if (!container) return;

  var distanciaDoTopo = container.getBoundingClientRect().top;
  var margemInferior = 24; // espaço de respiro no rodapé
  container.style.maxHeight = (window.innerHeight - distanciaDoTopo - margemInferior) + 'px';
}

// Roda ao carregar a página
ajustar_altura_grade();

// Roda quando a janela é redimensionada
window.addEventListener('resize', ajustar_altura_grade);

// Roda após o HTMX carregar o resultado (o resultado
// empurra a tabela para baixo, então precisa recalcular)
document.body.addEventListener('htmx:afterSwap', ajustar_altura_grade);