$(function () {
    $(".sidebar-toggler").click(function () {
        $(this).toggleClass("active")
        $("#sidebar").toggleClass("hide")
    })
    $(".graph-btns a").click(function () {
        $(this).siblings().removeClass("active")
        $(this).addClass("active")
    })
})