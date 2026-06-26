// * [RESUMO] → Script da tela de produtos.
//              Inicializa o DataTables e gerencia a abertura do modal de detalhes.

// ================================================
// DATATABLES
// ================================================

$(document).ready(function () {
    inicializar_tabela('#tabela-produtos', {
        autoWidth: true,
        // scrollX: true
    });
});
// ================================================
// MODAL
// ================================================

// * [EXPLICAÇÃO] → Abre o modal do Bootstrap após o HTMX injetar o conteúdo.
//                  O setTimeout garante que o HTMX terminou o swap antes de abrir.
function abrirModal() {
    setTimeout(function () {
        var modal = new bootstrap.Modal(document.getElementById('modal-produto'));
        modal.show();
    }, 100);
}