$(document).ready(function() {

    load_bubble()

    $("#show_bubble").click(function(){
        load_bubble()
    })
    
    $("#show_heatmap").click(function(){
        load_heatmap()
    })

    $("#show_marker").click(function(){
        load_marker()
    })

    function load_bubble() {
        $.ajax({
            url: "load_bubble/", 
            method: "POST",
            cache: false,
            success: function(data) {
                
                $("#main_map").html(data.map)
            }
        })
    }
    

    function load_heatmap() {
        $.ajax({
            url: "load_heatmap/", 
            method: "POST",
            cache: false,
            success: function(data) {
                
                $("#main_map").html(data.map)
            }
        })
    }

    function load_marker() {
        $.ajax({
            url: "load_marker/", 
            method: "POST",
            cache: false,
            success: function(data) {
                
                $("#main_map").html(data.map)
            }
        })
    }
});