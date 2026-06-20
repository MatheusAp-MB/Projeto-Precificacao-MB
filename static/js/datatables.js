var table = $("#tabela-produtos").DataTable({
    scrollX: true,
    language: {
      emptyTable: "Nenhum registro encontrado",
      info: "Mostrando _START_ até _END_ de _TOTAL_ registros",
      infoEmpty: "Mostrando 0 até 0 de 0 registros",
      infoFiltered: "(filtrado de _MAX_ registros no total)",
      lengthMenu: "Exibir _MENU_ resultados por página",
      loadingRecords: "Carregando...",
      processing: "Processando...",
      search: "Buscar:",
      zeroRecords: "Nenhum registro encontrado",
      paginate: {
        first: "Primeiro",
        last: "Último",
        next: "Próximo",
        previous: "Anterior"
      }
    },
    initComplete: function () {
      var botoes = document.getElementsByClassName("not_active");
      for (const botao of botoes) {
        fnShowHide(botao.id, false);
      }
    }
});

function fnShowHide(iCol, toggle = null) {
  var colIndex = parseInt(iCol) - 1;
  var oTable = $("#tabela-produtos").dataTable();
  if (toggle === null) {
    var bVis = oTable.fnSettings().aoColumns[colIndex].bVisible;
    oTable.fnSetColumnVis(colIndex, !bVis);
  } else {
    oTable.fnSetColumnVis(colIndex, toggle);
  }
}

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