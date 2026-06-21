// ================================================
// Variável global — ID da tabela ativa na página
// ================================================
var TABELA_ATIVA = null;

// ================================================
// Inicializa a tabela DataTables
// Chamada por cada página com suas configurações
// ================================================
function inicializar_tabela(tableId, opcoes) {
  TABELA_ATIVA = tableId;

  var config = Object.assign({
    scrollX: true,
    autoWidth: false,
    language: {
      emptyTable:   "Nenhum registro encontrado",
      info:         "Mostrando _START_ até _END_ de _TOTAL_ registros",
      infoEmpty:    "Mostrando 0 até 0 de 0 registros",
      infoFiltered: "(filtrado de _MAX_ registros no total)",
      lengthMenu:   "Exibir _MENU_ resultados por página",
      loadingRecords: "Carregando...",
      processing:   "Processando...",
      search:       "Buscar:",
      zeroRecords:  "Nenhum registro encontrado",
      paginate: {
        first:    "Primeiro",
        last:     "Último",
        next:     "Próximo",
        previous: "Anterior"
      }
    }
  }, opcoes);

  // initComplete genérico — aplica visibilidade inicial
  config.initComplete = function () {
    var botoes = document.getElementsByClassName("not_active");
    for (const botao of botoes) {
      fnShowHide(botao.id, false);
    }
    if (opcoes && opcoes.initComplete) {
      opcoes.initComplete.call(this);
    }
  };

  $(tableId).DataTable(config);
}

// ================================================
// Mostra/oculta coluna pelo índice do botão
// ================================================
function fnShowHide(iCol, toggle = null) {
  var colIndex = parseInt(iCol) - 1;
  var oTable = $(TABELA_ATIVA).dataTable();
  if (toggle === null) {
    var bVis = oTable.fnSettings().aoColumns[colIndex].bVisible;
    oTable.fnSetColumnVis(colIndex, !bVis);
  } else {
    oTable.fnSetColumnVis(colIndex, toggle);
  }
}

// ================================================
// Alterna estado do botão e visibilidade da coluna
// ================================================
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

// ================================================
// Mostra/oculta painel de opções de exibição
// ================================================
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