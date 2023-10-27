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
        $("#predicted_label").text('')
        $("#crime_desc").text('')

    })

    $("#predict-btn").click(function(){
        
        const text_area = $("#editable-div").text()
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        if(text_area != "Type or paste text here to start predicting..." || text_area == '') {

            $.ajax({
                url: "/app/classification", 
                method: "POST",
                data: {'input_content': text_area, },
                cache: false,
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);  // Include the CSRF token
                },
                success: function(data) {
                    $("#result_container").show()
                    $("#predicted_label").text(data.predicted_label).css("background-color", ""+data.bg_color)
                    $("#crime_desc").text(data.desc)
                },
                error: function(xhr, textStatus, errorThrown) {
                    console.error('Form submission failed. Error: ' + errorThrown);
                }
            })

        }else{
            




        }
        
    });


})
