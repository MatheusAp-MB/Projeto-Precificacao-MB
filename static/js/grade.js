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