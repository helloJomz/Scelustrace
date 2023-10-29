
$(".menu-sidebar").click(function(){

    $(".sidebar").show().css({
        "position": "fixed",
        "display": "flex",
        "justify-content": "end",
    })

})

$(document).ready(function () {
    var isMenuVisible = false; // Variable to track menu visibility

    $(".desktop-menu-toggle").click(function () {
        if (isMenuVisible) {
            $(".desktop-menu").hide();
        } else {
            $(".desktop-menu").show();
        }
        isMenuVisible = !isMenuVisible; // Toggle the variable
    });

    // Hide the menu when clicking outside of it
    $(document).click(function (e) {
        if (!$(e.target).closest(".desktop-menu-toggle").length && !$(e.target).closest(".desktop-menu").length) {
            $(".desktop-menu").hide();
            isMenuVisible = false; // Ensure the variable is set to false
        }
    });

    // Prevent clicks inside the menu from closing it
    $(".desktop-menu").click(function (e) {
        e.stopPropagation();
    });

});

$(".close-sidebar, .outside-sidebar").click(function(){
    $(".sidebar").hide()
})

$("#signout-btn").click(function(){

    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    
    $.ajax({
        url: "/logout/", 
        method: "POST",
        processData: false,  // Prevent jQuery from automatically processing the data
        contentType: false,  // Prevent jQuery from automatically setting the content type
        cache: false,
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);  // Include the CSRF token
        },
        success: function(data) {
            
           alert(data.location)

        //    setTimeout(function() {
        //     $('#loading_login').hide();  // Hide loading element after 2000 milliseconds (2 seconds)
        //     window.location.href = "/" + data.location;
        // }, 2000);
        },
        error: function(xhr, textStatus, errorThrown) {
            console.error('Form submission failed. Error: ' + errorThrown);
        }
    })
})