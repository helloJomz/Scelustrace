$(document).ready(function () {

    var editableDiv = $("#editable-div");
    var placeholder = "Type or paste text here to start predicting...";
    var wordCountDisplay = $("#word-count");
    
    // Set the placeholder text initially
    editableDiv.html(placeholder).css("color", "gray");

    // Add an event listener to remove the placeholder when the div is clicked
    editableDiv.on("focus", function () {
        if (editableDiv.html() === placeholder) {
            editableDiv.html("").css("color", "black");
        }
    });

    // Add an event listener to restore the placeholder if the div is empty
    editableDiv.on("blur", function () {
        if ($.trim(editableDiv.text()) === "") {
            editableDiv.html(placeholder).css("color", "gray");
        }
    });

    // Add an event listener to update word count
    editableDiv.on("input", function () {
        var content = editableDiv.text();
        var words = content.split(/\s+/).filter(Boolean);
        var wordCount = words.length;
        wordCountDisplay.text(wordCount + " Words");
    });
});


$(document).ready(function(){

    $("#clearall-btn").click(function(){

        var placeholder = "Type or paste text here to start predicting...";

        $("#editable-div").html(placeholder).css("color", "gray");
        $("#word-count").text('0 Words')

    });

    $("#clear-result-btn").click(function(){

        $("#result_container").hide()
        $("#result-menu").hide()
        $("#predicted_label").text('')
        $("#crime_desc").text('')

    })

    $("#predict-btn").click(function(){
        
        var editableDiv = $("#editable-div");
        var content = editableDiv.text();
        var words = content.split(/\s+/).filter(Boolean);
        var wordCount = words.length;

        const text_area = $("#editable-div").text()
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        $("#errorAlert").hide()
        $("#wrapper_textarea").removeClass('border-red-400')
        $("#result-menu").hide()
        $("#result_container").hide()
    
        if(text_area != "Type or paste text here to start predicting..." || text_area == '') {
            
            if (wordCount > 10) {

                $("#cf-loading").css('display', 'flex');

                $.ajax({
                    url: "/app/classification/", 
                    method: "POST",
                    data: {'input_content': text_area, },
                    cache: false,
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);  // Include the CSRF token
                    },
                    success: function(data) {
                
                        if (Object.keys(data).length > 0) {
                            
                            setTimeout(function() {

                                $("#cf-loading").hide();  
                                $("#result-menu").show().css('display', 'flex')
                                $("#result_container").show()
                                $("#empty_result").hide()
                                $("#result_error_alert").show()
                                $("#predicted_label").show().text(data.predicted_label).css("background-color", data.bg_color)
                                $("#crime_desc").text(data.desc)
        
                            }, 1000);

                        }else{
                            setTimeout(function() {
                                $("#cf-loading").hide();  
                                $("#result_container").show()
                                $("#result_error_alert").hide()
                                $("#empty_result").show()
                            }, 1000)
                        }
                        
                    },
                    error: function(xhr, textStatus, errorThrown) {
                        console.error('Form submission failed. Error: ' + errorThrown);
                    }
                })

            }else{
                $("#errorAlert").show().text("The input should consist of more than 10 words, please try again!")
                $("#wrapper_textarea").addClass('border-red-400')
            }
            

        }else{
            
            $("#errorAlert").show()
            $("#wrapper_textarea").addClass('border-red-400')
        
        }
        
    });


})
