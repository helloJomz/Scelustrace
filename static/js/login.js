function login_user() {

    const username = $("input[name='username']").val();
    const password = $("input[name='password']").val();
    const inputFields = $('#login_user').find('input[type="text"], input[type="password"]');
    const formData = new FormData(document.getElementById('login_user'));
    const emptyFields = [];

    // Close all effects on every
    $('#errorAlert').empty().hide();
    $('#usernameErrorIcon').hide();
    $('#passwordErrorIcon').hide();
    $('input[type="text"], input[type="password"]').removeClass('border border-red-600');


    function capitalizeFirstLetter(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    inputFields.each(function () {

        const fieldValue = $(this).val();
        const fieldName = $(this).attr("name");

        if (fieldValue === undefined || fieldValue.trim() === '') {
            emptyFields.push(fieldName);
        } else if (!/^[a-zA-Z0-9]+$/.test(fieldValue)) {
            emptyFields.push(fieldName + '_alpha');
        }

    });

    if (emptyFields.length > 0) {

        emptyFields.forEach(function (fieldName) {

            cleanedFieldName = fieldName.replace('_alpha', '');

            if (fieldName.includes('_alpha')) {

                errorContent = `
                    <div class="flex space-x-1">
                        <span class="material-symbols-outlined text-[0.9rem] text-red-600">error</span>
                        <p class="font-inter text-red-600 text-[0.6rem] font-bold py-0">${
                    capitalizeFirstLetter(cleanedFieldName)
                } should be in an alphanumeric format.</p>
                    </div>
                `

            } else {

                errorContent = `
                <div class="flex space-x-1">
                    <span class="material-symbols-outlined text-[0.9rem] text-red-600">error</span>
                    <p class="font-inter text-red-600 text-[0.6rem] font-bold py-0">${
                    capitalizeFirstLetter(fieldName)
                } should not be empty.</p>
                </div>
                `
            }

            $('#errorAlert').css('display', 'flex').append(errorContent);
            $('#' + fieldName + 'ErrorIcon').css('display', 'flex');
            $('#' + cleanedFieldName + 'ErrorIcon').css('display', 'flex');
            $('input[name="' + fieldName + '"]').addClass('border').addClass('border-red-600');
            $('input[name="' + cleanedFieldName + '"]').addClass('border').addClass('border-red-600');
        })

    }else{

        $('#loading_login').css('display', 'flex');
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        $.ajax({
            url: "/login/", 
            method: "POST",
            data: formData,
            processData: false,  // Prevent jQuery from automatically processing the data
            contentType: false,  // Prevent jQuery from automatically setting the content type
            cache: false,
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);  // Include the CSRF token
            },
            success: function(data) {
                
                if(data.login_status == true){
                    setTimeout(function() {
                        $('#loading_login').hide();  // Hide loading element after 2000 milliseconds (2 seconds)
                        window.location.href = "/" + data.location;
                    }, 2000);
                }else{
                    setTimeout(function() {

                        errorContent = `
                                    <div class="flex space-x-1">
                                        <span class="material-symbols-outlined text-[0.9rem] text-red-600">error</span>
                                        <p class="font-inter text-red-600 text-[0.6rem] font-bold py-0">${data.msg}</p>
                                    </div>
                                     `
                
                        $('#loading_login').hide();  // Hide loading element after 2000 milliseconds (2 seconds)
                        $("input[type='password']").val();
                        $('#errorAlert').css('display', 'flex').append(errorContent);
                    }, 2000);
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                console.error('Form submission failed. Error: ' + errorThrown);
            }
        })


    }

}
