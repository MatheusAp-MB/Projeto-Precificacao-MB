// * [RESUMO] → Script da tela de precificação do Mercado Livre.
//              DataTables com RowGroup recolhível, SearchPanes e filtros ativos.

// * [EXPLICAÇÃO] → Controla quais grupos estão expandidos. Por padrão todos recolhidos.
var gruposExpandidos = new Set();

$(document).ready(function () {
    inicializar_tabela('#tabela-precificar-ml', {
        autoWidth: true,
        dom: 'Plfrtip',
        searchPanes: {
            layout: 'columns-4',
            threshold: 1,
        },
        columnDefs: [
            { type: 'pt-string', targets: [0, 1] },
            { searchPanes: { show: true }, targets: '_all' }
        ],
        rowGroup: {
            dataSrc: 0,
            startRender: function (rows, group) {
                var firstRow = rows.nodes()[0];
                var expandido = gruposExpandidos.has(group);

                rows.nodes().each(function () {
                    $(this).addClass('linha-grupo-' + group.replace(/[^a-zA-Z0-9]/g, '_'));
                    if (!expandido) {
                        $(this).addClass('grupo-recolhido');
                    } else {
                        $(this).removeClass('grupo-recolhido');
                    }
                });

                return $('<tr class="grupo-produto"/>')
                    .attr('data-grupo', group)
                    .append(
                        $('<td colspan="20"/>')
                            .html(
                                '<span class="grupo-toggle">' + (expandido ? '▼' : '▶') + '</span>' +
                                ' <span class="grupo-sku">' + group + '</span>' +
                                ' | <span class="grupo-ean">' + $(firstRow).data('ean') + '</span>' +
                                ' | <span class="grupo-fab">' + $(firstRow).data('fab') + '</span>' +
                                ' | <span class="grupo-marca">' + $(firstRow).data('marca') + '</span>' +
                                ' | <span class="grupo-curva">' + $(firstRow).data('curva') + '</span>' +
                                ' | <span class="grupo-estoque">' + $(firstRow).data('estoque') + ' un.</span>' +
                                ' | <span class="grupo-categoria">' + $(firstRow).data('categoria') + '</span>'
                            )
                    );
            }
        }
    });

    // * [EXPLICAÇÃO] → Toggle ao clicar no cabeçalho do grupo.
    $('#tabela-precificar-ml tbody').on('click', 'tr.grupo-produto', function () {
        var grupo = $(this).data('grupo');
        var classeGrupo = '.linha-grupo-' + grupo.replace(/[^a-zA-Z0-9]/g, '_');

        if (gruposExpandidos.has(grupo)) {
            gruposExpandidos.delete(grupo);
            $(this).find('.grupo-toggle').text('▶');
            $(classeGrupo).addClass('grupo-recolhido');
        } else {
            gruposExpandidos.add(grupo);
            $(this).find('.grupo-toggle').text('▼');
            $(classeGrupo).removeClass('grupo-recolhido');
        }
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

// ================================================
// TOGGLE DO SEARCHPANES
// ================================================

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

// ================================================
// FILTROS ATIVOS
// ================================================

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