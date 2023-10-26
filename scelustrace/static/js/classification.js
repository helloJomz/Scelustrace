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