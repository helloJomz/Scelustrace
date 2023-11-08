$(document).ready(function() {

    $("#show_bubble").removeClass("bg-white");
    $("#show_bubble").addClass("text-white");
    $("#show_bubble").addClass("bg-sky-500");
    

    load_bubble()

    $("#show_bubble").click(function(){
        $("#main_map").empty()
        $(".map-button").removeClass("bg-sky-500").addClass("bg-white");
        $(".map-button").removeClass("text-white");

        $("#show_bubble").removeClass("bg-white");
        $("#show_bubble").addClass("text-white");
        $("#show_bubble").addClass("bg-sky-500");


        load_bubble()
    })
    
    $("#show_heatmap").click(function(){
        $("#main_map").empty()
        $(".map-button").removeClass("bg-sky-500").addClass("bg-white");
        $(".map-button").removeClass("text-white");

        $("#show_heatmap").removeClass("bg-white");
        $("#show_heatmap").addClass("text-white");
        $("#show_heatmap").addClass("bg-sky-500");



        load_heatmap()
    })

    $("#show_marker").click(function(){
        $("#main_map").empty()
        $(".map-button").removeClass("bg-sky-500").addClass("bg-white");
        $(".map-button").removeClass("text-white");

        $("#show_marker").removeClass("bg-white");
        $("#show_marker").addClass("text-white");
        $("#show_marker").addClass("bg-sky-500");

        
        load_marker()
    })

    function load_bubble() {

        $("#loading_login").css("display", "flex")

        $.ajax({
            url: "load_bubble/", 
            method: "GET",
            success: function(data) {

                $("#loading_login").hide()
                $("#main_map").html(data.map_circle)

            }
        })
    }
    

    function load_heatmap() {

        $("#loading_login").css("display", "flex")

        $.ajax({
            url: "load_heatmap/", 
            method: "POST",
            cache: false,
            success: function(data) {

                $("#loading_login").hide()
                $("#main_map").html(data.map)
            }
        })
    }

    function load_marker() {

        $("#loading_login").css("display", "flex")

        $.ajax({
            url: "load_marker/", 
            method: "GET",
            success: function(data) {

                $("#loading_login").hide()
                $("#main_map").html(data.map)
                
            }
        })
        
        
    }
});


$(document).ready(function() {

    // Click event on the legend menu to show the legend container
    $("#legend-menu").click(function() {
        $(this).hide();
        $("#legend-container").show();
        $("#close-legend").show();
    });

    $("#close-legend").click(function() {
        $(this).hide();
        $("#legend-container").hide();
        $("#legend-menu").show();
    })

    // Show content-0 by default
    $('.content-0').removeClass('hidden');
    $('.content-1').addClass('hidden');

    $('.legend-button').click(function() {
        var buttonIndex = $('.legend-button').index(this);

        // Remove bg-slate-200 from all buttons
        $('.legend-button').removeClass('bg-slate-200');

        if (buttonIndex === 0) {
            // Clicked the HeatMap button
            $('.content-0').removeClass('hidden');
            $('.content-1').addClass('hidden');
            // Add bg-slate-200 to HeatMap button
            $(this).addClass('bg-slate-200');
        } else if (buttonIndex === 1) {
            // Clicked the Bubble button
            $('.content-0').addClass('hidden');
            $('.content-1').removeClass('hidden');
            // Add bg-slate-200 to Bubble button
            $(this).addClass('bg-slate-200');
        }
    });
});