// * [RESUMO] → Script da tela de precificação do Mercado Livre.
//              Inicializa o DataTables e gerencia filtros.

$(document).ready(function () {
    inicializar_tabela('#tabela-precificar-ml', {
        autoWidth: true,
        dom: 'Plfrtip',
        searchPanes: {
            layout: 'columns-4',
            threshold: 1,
        },
        columnDefs: [
            { type: 'pt-string', targets: [0, 1, 2, 3, 4, 5, 6, 7] },
            { searchPanes: { show: true }, targets: '_all' }
        ],
    });

    $('#tabela-precificar-ml').on('draw.dt', function () {
        atualizar_filtros_ativos();
    });

    setTimeout(function () {
        $('.dtsp-panesContainer').show();
        $(window).trigger('resize');
        setTimeout(function () {
            $('.dtsp-panesContainer').hide();
        }, 100);
    }, 200);
});

var filtrosAbertos = false;

function toggle_filtros() {
    var painel = document.querySelector('.dtsp-panesContainer');
    var caret = document.getElementById('btn-filtros-caret');

    if (filtrosAbertos) {
        $(painel).hide();
        caret.textContent = '▼';
        filtrosAbertos = false;
    } else {
        $(painel).show();
        caret.textContent = '▲';
        filtrosAbertos = true;
        $(window).trigger('resize');

        setTimeout(function () {
            $('.dtsp-collapseButton').each(function () {
                var pane = $(this).closest('.dtsp-searchPane');
                var temFiltroAtivo = pane.find('tr.selected').length > 0;
                var estaAberto = !pane.find('.dataTables_scrollBody').is(':hidden');
                if (estaAberto && !temFiltroAtivo) {
                    $(this).trigger('click');
                }
            });
        }, 100);
    }
}

function atualizar_filtros_ativos() {
    var filtros = [];

    $('.dtsp-searchPane').each(function () {
        var coluna = $(this).find('.dtsp-search').attr('placeholder');
        var valores = [];

        $(this).find('tr.selected .dtsp-name').each(function () {
            valores.push($(this).attr('title') || $(this).text());
        });

        if (valores.length > 0) {
            filtros.push('<strong>' + coluna + '</strong> = ' + valores.join(', '));
        }
    });

    var texto = document.getElementById('filtros-ativos-texto');
    if (filtros.length > 0) {
        texto.innerHTML = 'Filtros ativos → ' + filtros.join(' &nbsp;|&nbsp; ');
    } else {
        texto.textContent = 'Nenhum filtro ativo';
    }
}