$(document).ready(function () {

  var table = $("#tabela-produtos").DataTable({
    scrollX: true,
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json"
    },
    columnDefs: [
      { targets: '_all', defaultContent: '—' }
    ]
  });

  // Aplica visibilidade inicial conforme botões not_active
  var botoes = document.getElementsByClassName("not_active");
  for (const botao of botoes) {
    fnShowHide(botao.id, false);
  }

});

// Mostra/oculta coluna
function fnShowHide(iCol, toggle = null) {
  var oTable = $("#tabela-produtos").dataTable();
  if (toggle === null) {
    var bVis = oTable.fnSettings().aoColumns[iCol].bVisible;
    oTable.fnSetColumnVis(iCol, !bVis);
  } else {
    oTable.fnSetColumnVis(iCol, toggle);
  }
}

// Alterna estado do botão e visibilidade da coluna
function mudar(botao) {
  if (botao.classList.contains("active")) {
    botao.classList.remove("active");
    botao.classList.add("not_active");
    fnShowHide(botao.id);
  } else {
    botao.classList.remove("not_active");
    botao.classList.add("active");
    fnShowHide(botao.id);
  }
}

// Mostra/oculta painel de opções
var painelAberto = false;

function opcoes_exibicao() {
  var painel = document.getElementById("Mostrar_Colunas");
  if (painelAberto) {
    painel.style.display = "none";
    painelAberto = false;
  } else {
    painel.style.display = "block";
    painelAberto = true;
  }
}