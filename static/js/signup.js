function signup_user() {

    const inputFields       = $('#signup_user input[type="text"], #signup_user input[type="password"]');
    const errorFields       = [];
    const successFields     = [];
    const passwordField     = $('input[name="password"]').val().trim();
    const cpasswordField    = $('input[name="cpassword"]').val().trim();
    const firstname         = $('input[name="firstname"]').val().trim();
    const lastname          = $('input[name="lastname"]').val().trim();
    const username          = $('input[name="username"]').val().trim();
    const formData          = new FormData(document.getElementById('signup_user'));

    // Close all effects on every click
    $('[id*="ErrorAlert"]').empty().hide();
    $('[id*="ErrorIcon"], [id*="SuccessIcon"]').hide();
    $('input[type="text"], input[type="password"]').removeClass('border border-red-600');
    $('input[type="text"], input[type="password"]').removeClass('border border-green-600');

    function capitalizeFirstLetter(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function hasNumberAndSymbol(str) {
        return /[!@#$%^&*(),.?":{}|<>\d]/.test(str);
    }

    function remove_abr(str) {
        if (str === 'cpassword') {
            return 'Confirm Password'
        } else {
            return str
        }
    }

    inputFields.each(function () {

        const fieldValue = $(this).val();
        const fieldName = $(this).attr("name");

        if (fieldValue === undefined || fieldValue.trim() === '') {
            errorFields.push({'fieldName': fieldName, 'error': 'empty'});
        } else if (fieldName == 'firstname' && hasNumberAndSymbol(firstname)) {
            errorFields.push({'fieldName': fieldName, 'error': 'hasNumberAndSymbol'});
        } else if (fieldName == 'lastname' && hasNumberAndSymbol(lastname)) {
            errorFields.push({'fieldName': fieldName, 'error': 'hasNumberAndSymbol'});
        } else if (!/^[a-zA-Z0-9]+$/.test(fieldValue)) {
            errorFields.push({'fieldName': fieldName, 'error': 'alpha'});
        } else if ((fieldName == 'password' || fieldName == 'cpassword') && passwordField !== cpasswordField) {
            errorFields.push({'fieldName': fieldName, 'error': 'passwordNotMatch'});
        } else if (fieldName == 'username' && username.trim().length < 6) {
            errorFields.push({'fieldName': fieldName, 'error': 'usernameLength'});
        } else if ((fieldName == 'password' || fieldName == 'cpassword') && passwordField.trim().length < 8 && cpasswordField.trim().length < 8) {
            errorFields.push({'fieldName': fieldName, 'error': 'passwordLength'});
        } else {
            successFields.push({'fieldName': fieldName, 'status': 'success'});
        }

    });

    function showAlertBox(fieldName, msg, status, color) {

        const errorContent = `
            <div class="flex space-x-1">
                <span class="material-symbols-outlined text-[0.9rem] text-${color}-600">error</span>
                <p class="font-inter text-${color}-600 text-[0.6rem] font-bold py-0">${
            capitalizeFirstLetter(remove_abr(fieldName) + ' ' + msg)
        }</p>
            </div>
        `;

        if (fieldName == 'firstname' || fieldName == 'lastname') {
            $('#name' + status + 'Alert').css('display', 'flex').append(errorContent);
        } else {
            $('#' + fieldName + status + 'Alert').css('display', 'flex').append(errorContent);
        }
    }

    function showAlertIcon(fieldName, status) {

        if (status == 'Error') {
            $('#' + fieldName + 'ErrorIcon').css('display', 'flex');
            $('input[name="' + fieldName + '"]').addClass('border').addClass('border-red-600')
        } else {
            $('#' + fieldName + 'SuccessIcon').css('display', 'flex');
            $('input[name="' + fieldName + '"]').addClass('border').addClass('border-green-600')
        }

    }

    errorFields.forEach(function (errorLabel) {

        if (errorLabel['error'] == 'empty') {
            const msg = 'should not be empty.'

            showAlertBox(errorLabel['fieldName'], msg, 'Error', 'red')
            showAlertIcon(errorLabel['fieldName'], 'Error')

        } else if (errorLabel['error'] == 'passwordNotMatch') {
            const msg = 'does not match.';

            if (errorLabel['fieldName'] === 'password' || errorLabel['fieldName'] === 'cpassword') {
                const msg = 'does not match.';
                showAlertBox(errorLabel['fieldName'], msg, 'Error', 'red');
                showAlertIcon(errorLabel['fieldName'], 'Error');
            }

        } else if (errorLabel['error'] == 'usernameLength') {
            const msg = 'length should be greater than 6 characters.'

            showAlertBox(errorLabel['fieldName'], msg, 'Error', 'red');
            showAlertIcon(errorLabel['fieldName'], 'Error')
        } else if (errorLabel['error'] == 'passwordLength') {
            const msg = 'length should be greater than 8 characters.'

            showAlertBox(errorLabel['fieldName'], msg, 'Error', 'red');
            showAlertIcon(errorLabel['fieldName'], 'Error');
        } else if (errorLabel['error'] == 'hasNumberAndSymbol') {
            const msg = 'should not contain number and symbols.'

            showAlertBox(errorLabel['fieldName'], msg, 'Error', 'red');
            showAlertIcon(errorLabel['fieldName'], 'Error')

        } else if (errorLabel['error'] == 'alpha') {
            const msg = 'special symbols are forbidden.'

            showAlertBox(errorLabel['fieldName'], msg, 'Error', 'red')
            showAlertIcon(errorLabel['fieldName'], 'Error')
        }

    });

    successFields.forEach(function (successLabel) {
        showAlertIcon(successLabel['fieldName'], 'Success')
    });


    if (errorFields.length === 0) {

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        Swal.fire({
            title: 'Do you want to create this account?', 
            showDenyButton: true, 
            confirmButtonText: 'Save', 
            denyButtonText: `Don't save`})
            .then((result) => {

                if (result.isConfirmed) {

                    $('#loading_login').css('display', 'flex');

                    $.ajax({
                        url: "/signup/", 
                        method: "POST",
                        data: formData,
                        processData: false,  // Prevent jQuery from automatically processing the data
                        contentType: false,  // Prevent jQuery from automatically setting the content type
                        cache: false,
                        beforeSend: function(xhr, settings) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);  // Include the CSRF token
                        },
                        success: function(data) {

                            if (data && data.error && data.error !== "") {
                                // Rest of your code for handling errors
                                setTimeout(function() {
                                    $("input[name='username']").removeClass('border border-green-600');
                                    $('[id*="SuccessIcon"]').hide();
                                    $('#loading_login').hide();  // Hide loading element after 2000 milliseconds (2 seconds)
                                    showAlertBox(data.fieldName, data.error, 'Error', 'red');
                                    showAlertIcon(data.fieldName, 'Error');
                                }, 2000);

                            } else {
                   
                                inputFields.val("");
                                setTimeout(function() {
                                    $('#loading_login').hide();  // Hide loading element after 2000 milliseconds (2 seconds)
                                    window.location.href = "/" + data.location;
                                }, 2000);
                            }

                        
                        },
                        error: function(xhr, textStatus, errorThrown) {
                            console.error('Form submission failed. Error: ' + errorThrown);
                        }
                    });
                    
                } else if (result.isDenied) {

                    Swal.fire('Changes are not saved', '', 'info')
                }

        })
    }


}
