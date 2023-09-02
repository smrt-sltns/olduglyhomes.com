$(function(){
    $(".sidebar-toggler").click(function(){
        $(this).toggleClass("active")
        $("#sidebar").toggleClass("hide")
    })
})