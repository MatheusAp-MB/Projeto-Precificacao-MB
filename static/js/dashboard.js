$(document).ready(function () {

    // Toggle dos dropdowns da sidebar
    $(".dashboard-nav-dropdown-toggle").click(function () {
        $(this)
            .closest(".dashboard-nav-dropdown")
            .toggleClass("show")
            .find(".dashboard-nav-dropdown")
            .removeClass("show");
        $(this).parent().siblings().removeClass("show");
    });

    // Toggle ocultar/exibir sidebar
    $("#btn-toggle-sidebar").click(function () {
        if (window.matchMedia("(max-width: 992px)").matches) {
            $(".dashboard-nav").toggleClass("mobile-show");
        } else {
            $(".dashboard").toggleClass("dashboard-compact");
        }
    });

});