const admin_user_form= document.getElementById('user_form'); 
const admin_add_newUser = FormValidation.formValidation(admin_user_form, {
fields: {
    role:{
        validators:{
            notEmpty:{
                message: 'Role is required',
            }
        }
    },
    
    cid: {
        validators: {
            notEmpty: {
                message: 'Please enter CID',
            }
        }
    },
    username: {
        validators: {
            notEmpty: {
                message: 'Please enter user name',
            }
        }
    },
    password: {
        validators: {
            notEmpty: {
                message: 'Please enter password',
            }
        }
    },
    email: {
        validators: {
            notEmpty: {
                message: 'Please enter Email',
            }
        }
    },
 }, plugins: {
        trigger: new FormValidation.plugins.Trigger(),
        bootstrap: new FormValidation.plugins.Bootstrap(),
        // tachyons: new FormValidation.plugins.Tachyons(),
        submitButton: new FormValidation.plugins.SubmitButton(),

    },
}).on('core.form.valid', function (e) {
    save_user();
    $('#save').attr('disabled', true);
}).on('core.form.invalid', function (e) {
    console.log(e);
    swal("Validation failed !!!", "Some required fields are empty", "error")
});
$('#user_form').submit(function (event) {
    if ($('#cid-error').is(':visible') || $('#cidError').text() !== '') {
        // If error messages related to CID are visible, prevent form submission
        event.preventDefault(); // Prevent form submission
        alert('Please fix the errors before submitting the form.');
    }
});

function save_user() {
    var form = document.getElementById("user_form");
    var data = new FormData(form);
    $.ajax({
        type: 'POST',
        url: '/save-user',
        data: data,
        contentType: false,
        cache: false,
        processData: false,
        beforeSend: function () {
            $("#save").text("Loading....")
            $("#save").attr("disabled", true)
            $("#save").addClass("disabled")

        },
        success: function (res) {
            swal("Information successfully saved", "Click Ok to continue", "success")
                .then(function () {
                    $('#user_form').trigger('reset');
                    window.location = "/admin-user-list";
                });
        },
    });
}
//grade stream

$("#role").on("change", function(){
    let role =  $("#role").val();
    if(role === "class_teacher"){
        $("#classTeacher_div").show();
    }else{
        $("#classTeacher_div").hide();
    }
});
// $("#grade").on("change",function(){
//     let grade= $("#grade").val();
//         //if (grade=='x')
//     if (grade=="XII" || grade=="XI"){
//       $('#chooseStream').show()
//     }
//     else{
//         $('#chooseStream').hide()
//     }
// })

$("#grade").on("change", function() {
var gradeId = $(this).val();

// Send an AJAX request to retrieve the dropdown values for the "section" select element
$.ajax({
    type: 'GET',
    url: '/dropDownSection/' + gradeId,
    success: function(response) {
        var dropdownValues = response;

        // Get the select element for "section" and "class"
        var sectionSelect = $('select[name="section"]');
        var classSelect = $('select[name="class"]');

        // Clear the existing options
        sectionSelect.empty();
        classSelect.empty();

        // Check if there are sections available for the selected grade
        if (dropdownValues.length === 0) {
            // If no sections are available, disable the select element and display "No Section" as an option
            sectionSelect.prop("disabled", true);
            classSelect.prop("disabled", true);

            // Create and append the "No Section" option
            var noSectionOption = $('<option>');
            noSectionOption.val("no_section");
            noSectionOption.text("No Section");
            sectionSelect.append(noSectionOption);

            // Create and append the "No Class" option
            var noClassOption = $('<option>');
            noClassOption.val("no_class");
            noClassOption.text("No Class");
            classSelect.append(noClassOption);
        } else {
            // If sections are available, enable the select elements and populate them with the options
            sectionSelect.prop("disabled", false);
            classSelect.prop("disabled", false);

            // Add the default "Select Section" and "Select Class" options at the top
            var selectSectionOption = $('<option>');
            selectSectionOption.val("");
            selectSectionOption.text("---Select Section---");
            sectionSelect.append(selectSectionOption);

            var selectClassOption = $('<option>');
            selectClassOption.val("");
            selectClassOption.text("---Select Class---");
            classSelect.append(selectClassOption);

            // Create and append the new section options
            for (var i = 0; i < dropdownValues.length; i++) {
                var option = $('<option>');
                option.val(dropdownValues[i].id);
                option.text(dropdownValues[i].name);
                sectionSelect.append(option);
            }
        }
    },
    error: function() {
        // Handle error case
    }
});
});

$(document).ready(() => {
$.ajax({
    type: 'GET',
    url: '/dropDownClass',
    success: function(response) {
        // Assuming response is the JSON array containing dropdown values
        var dropdownValues = response;

        // Get the select element in your HTML
        var selectElement = document.getElementById('grade');

        // Loop through the dropdown values and create option elements
        for (var i = 0; i < dropdownValues.length; i++) {
            var option = document.createElement('option');
            option.value = dropdownValues[i].id;
            option.textContent = dropdownValues[i].name;
            selectElement.appendChild(option);
        }
    },
    error: function() {
        // Handle error case
    }
});
});