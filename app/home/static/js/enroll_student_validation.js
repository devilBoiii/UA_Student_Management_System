// -----------------------Form Validation--------------------------------//
const enrollForm = document.getElementById('registration_form');

const enrollfv = FormValidation.formValidation(enrollForm, {
    fields: {
        half_photo: {
            validators: {
                notEmpty: {
                    message: 'The Passport size photo is required',
                },
                file: {
                    extension: 'jpeg,jpg,png', // Accept only these image file extensions
                    type: 'image/jpeg,image/png', // Accept only JPEG and PNG images
                    maxSize: 5 * 1024 * 1024, // 5MB
                    message: 'Please upload a valid image file (JPEG or PNG) with a maximum size of 5MB',
                    callback: {
                        message: 'Please upload a passport-size photo (e.g., 200x250 pixels).',
                        callback: function (value, validator, $field) {
                            // Define the required dimensions for a passport-size photo
                            const requiredWidth = 200;
                            const requiredHeight = 250;

                    // Check if the uploaded image matches the required dimensions
                    const image = new Image();
                    image.src = URL.createObjectURL($field[0].files[0]);

                    return new Promise((resolve) => {
                        image.onload = function () {
                            if (image.width === requiredWidth && image.height === requiredHeight) {
                                resolve({ valid: true });
                            } else {
                                resolve({ valid: false });
                                    }
                                };
                            });
                        },
                    },
                },
            },
        },

        
        marksheet: {
            validators: {
                notEmpty: {
                    // extension: 'jpeg,jpg,png',
                    // type: 'image/jpeg,image/png',
                    // maxSize: 5 * 1024 * 1024, // 5MB
                    message: 'Please upload a marksheet',
                }
            }
        },

        cid: {
            validators: {
                notEmpty: {
                    message: 'This field is required',
                },
                stringLength: {
                    max: 17,
                    min: 11,
                    message: 'The student index must be 13 or 17 digits'
                },
            }
        },        

        dob: {
            validators: {
                notEmpty: {
                    message: 'The DOB field is required',
                },
            },
        },
        gender: {
            validators: {
                notEmpty: {
                    message: 'The Gender field is required',
                },
            },
        },

        email: {
            validators: {
                emailAddress: {
                    message: 'The value is not a valid email address',
                },
                notEmpty: {
                    message: 'The email field is required',
                },
            },
        },
        phone_number: {
            validators: {
                notEmpty: {
                    message: 'This field is required',
                },
                stringLength: {
                    max: 8,
                    min: 8,
                    message: 'The Phone number must be 8 digits'
                },
                numeric: {
                    message: 'The value is not a number',
                    // The default separators
                    thousandsSeparator: '',
                    decimalSeparator: '.',
                },
            },
        },
        student_code: {
            validators: {
                stringLength: {
                    max: 17,
                    min: 11,
                    message: 'The Student Code must be 17 digits and CID must be 11 digits'
                },
                numeric: {
                    message: 'The value is not a number',
                    // The default separators
                    thousandsSeparator: '',
                    decimalSeparator: '.',
                },
            },
        },
        first_name: {
            validators: {
                notEmpty: {
                    message: 'The Name field is required',
                },
            },
        },


        permanent_dzongkhag: {
            validators: {
                notEmpty: {
                    message: 'Please select Dzongkhag',
                }
            },
        },
        permanent_gewog: {
            validators: {
                notEmpty: {
                    message: 'Please select Gewog',
                }
            }
        },

        permanent_village: {
            validators: {
                notEmpty: {
                    message: 'Please select Village',
                }
            }
        },

        //academic details

        admission_for: {
            validators: {
                notEmpty: {
                    message: 'Admission for class is required',
                }
            }
        },

        index_number: {
            validators: {
                notEmpty: {
                    message: 'This field is required',
                },
                regexp: {
                    regexp: /^.{11,12}$/,
                    message: 'The student code must be between 11 to 17 characters or use CID',
                },
            }
        },

        percent: {
            validators: {
                notEmpty: {
                    message: 'This field is required',
                },
                stringLength: {
                    min: 2,
                    message: 'The student index must be 2 digits'
                },
                numeric: {
                    message: 'The value is not a number',
                    // The default separators
                    thousandsSeparator: '',
                    decimalSeparator: '.',
                },
            },
        },

        supw: {
            validators: {
                notEmpty: {
                    message: 'This field is required',
                }
            }
        },

        parent_cid: {
            validators: {
                // notEmpty: {
                    // message: 'The CID field is required',
                // },
                regexp: {
                    regexp: /^.{11}$/,
                    message: 'The CID must be 11 characters',
                },
            }
        },
        parent_name: {
            validators: {
                notEmpty: {
                    message: 'This field is required',
                }
            }
        },


        parent_number: {
            validators: {
                notEmpty: {
                    message: 'This field is required',
                },
                stringLength: {
                    min: 8,
                    message: 'The Phone number must be 8 digits'
                },
                numeric: {
                    message: 'The value is not a number',
                    // The default separators
                    thousandsSeparator: '',
                    decimalSeparator: '.',
                },
            },
        },

        present_dzongkhag: {
            validators: {
                notEmpty: {
                    message: 'Please select Dzongkhag',
                },
            },
        },
        present_gewog: {
            validators: {
                notEmpty: {
                    message: 'Please select Gewog',
                },
            },
        },

        present_village: {
            validators: {
                notEmpty: {
                    message: 'Please select Village',
                },
            },
        },

        previous_school: {
            validators: {
                notEmpty: {
                    enabled: true,
                    message: 'Please enter previous school',
                },
            },
        },
        accommodation: {
            validators: {
                notEmpty: {
                    message: 'Please select Accomodation'
                },
            },
        },
        
    },

    plugins: {
        trigger: new FormValidation.plugins.Trigger(),
        bootstrap: new FormValidation.plugins.Bootstrap(),
        // tachyons: new FormValidation.plugins.Tachyons(),
        submitButton: new FormValidation.plugins.SubmitButton(),

    },
}).on('core.form.valid', function (e) {
    studentDetail();
    $('#submitBtn').prop('disabled', true);
}).on('core.form.invalid', function (e) {
    console.log(e);
    swal("Validation failed !!!", "Some required fields are empty", "error")
});

function studentDetail() {
    var form = document.getElementById("registration_form");
    var data = new FormData(form);
    $.ajax({
        type: 'POST',
        url: '/store-student-info',
        data: data,
        processData: false,
        contentType: false,
        cache: false,
        beforeSend: function () {
            $("#submitBtn").text("Loading....")
            $("#submitBtn").attr("disabled", true)
            $("#submitBtn").addClass("disabled")

        },

        success: function (res) {
            if (res === 'Error') {
                swal("Data already exists", "Check CID or Index No. and try again", "error")
                    .then(function () {
                        window.location = "";
                    });
            } else {
                swal("Information successfully submitted", "Click Ok to continue", "success")
                    .then(function () {
                        window.location = "";
                    });
            }
        },
        error: function () {
            swal("Information submission failed", "Click Ok to continue", "error")
                .then(function () {
                    window.location = "";
                });
        }
    });
}


//------------------------Script for fetching gewog list-------------------------//
$("#present_dzongkhag").on("change", function () {
    var gewog_id = $("#present_dzongkhag").val();
    $.ajax({
        url: "/get-gewog-list",
        method: "POST",
        data: { type: 'Gewog', gewog_id: gewog_id },
        dataType: "json",
        success: function (data) {

            var list = data.gewogList;
            var html = "<option value=''>---Select Gewog---</option>";
            for (var count = 0; count < list.length; count++) {
                html += "<option value='" + list[count].gewog_id + "'>" + list[count].gewog_name + "</option>"
            }
            $("#present_gewog").html(html);
        },
        error: function (e) {
            alert('error', e);
        }
    });
});
//-------------------------script ends-----------------------------------//

//--------------------------Script for fetching village list-------------------//
$("#present_gewog").on("change", function () {
    var village_id = $("#present_gewog").val();
    $.ajax({
        url: "/get-village-list",
        method: "POST",
        data: { type: 'village', village_id: village_id },
        dataType: "json",
        success: function (data) {
            var list = data.villageList
            var html = "<option value=''>---Select Village---</option>";
            for (var count = 0; count < list.length; count++) {
                html += "<option value='" + list[count].village_id + "'>" + list[count].village_name + "</option>"
            }

            $("#present_village").html(html);
        },
        error: function () {
            alert('error');
        }
    });
});
//-------------------------------Script ends--------------------------------//


//------------------------Script for fetching gewog list for permanent address-------------------------//
$("#permanent_dzongkhag").on("change", function () {
    var gewog_id = $("#permanent_dzongkhag").val();
    $.ajax({
        url: "/get-gewog-list",
        method: "POST",
        data: { type: 'Gewog', gewog_id: gewog_id },
        dataType: "json",
        success: function (data) {

            var list = data.gewogList;
            var html = "<option value=''>---Select Gewog---</option>";
            for (var count = 0; count < list.length; count++) {
                html += "<option value='" + list[count].gewog_id + "'>" + list[count].gewog_name + "</option>"
            }
            $("#permanent_gewog").html(html);
        },
        error: function () {
            alert('error');
        }
    });
});
//-------------------------script ends-----------------------------------//

//--------------------------Script for fetching village list-------------------//
$("#permanent_gewog").on("change", function () {
    var village_id = $("#permanent_gewog").val();
    $.ajax({
        url: "/get-village-list",
        method: "POST",
        data: { type: 'village', village_id: village_id },
        dataType: "json",
        success: function (data) {
            var list = data.villageList
            var html = "<option value=''>---Select Village---</option>";
            for (var count = 0; count < list.length; count++) {
                html += "<option value='" + list[count].village_id + "'>" + list[count].village_name + "</option>"
            }

            $("#permanent_village").html(html);
        },
        error: function () {
            alert('error');
        }
    });
});
//-------------------------------Script ends--------------------------------//

// -------------------------------Script for changing form------------------//
$("#X").click(function (e) {
    e.preventDefault();
    $(".form_std").removeClass("d-none");
    $(".form_title").addClass("d-none");
    $(".grade_xi").addClass("d-none");
    $(".grade_x_title").removeClass("d-none");
    $(".grade_xii").addClass("d-none");
    $(".general_grade").addClass("d-none");
    $(".pre_school").removeClass("d-none");
    
    $(".pre_school_X").addClass("d-none");
    $(".pre_school_XII").addClass("d-none");
    // $(".emis_code").addClass("d-none");
    console.log("Reaching HERE!")
    enrollfv.enableValidator('previous_school');
    
        var selectedOption = $('input[name="class_select"]:checked').val();
        var selectElement = $('#admission_for');
        selectElement.html('<option value="">---Select One---</option>');
      
          if (selectedOption === 'X') {
          $.ajax({
            type: 'GET',
            url: '/dropdown_valuesx',
            success: function(response) {
              // Assuming response is the JSON array containing dropdown values
              var dropdownValues = response;
              console.log("classXhere", dropdownValues)
      
              // Loop through the dropdown values and create option elements
              for (var i = 0; i < dropdownValues.length; i++) {
                var option = $('<option></option>');
                option.val(dropdownValues[i].id);
                option.text(dropdownValues[i].name);
                selectElement.append(option);
                console.log("classXhere", dropdownValues)
              }
            },
            error: function() {
              // Handle error case
            }
          });
        }
        enrollForm.reset();
    // enrollfv.resetForm();
});

$("#XI").click(function (e) {
    e.preventDefault();
    $(".form_std").removeClass("d-none");
    $(".form_title").addClass("d-none");
    $(".grade_xi").removeClass("d-none");
    $(".grade_x_title").addClass("d-none");
    $(".grade_xii").addClass("d-none");
    $(".general_grade").addClass("d-none");
    $(".pre_school").removeClass("d-none");
    $(".pre_school_X").addClass("d-none");
    $(".pre_school_XII").addClass("d-none");
    // $(".emis_code").addClass("d-none");
    enrollfv.enableValidator('previous_school');
        var selectedOption = $('input[name="class_select"]:checked').val();
          var selectElement = $('#admission_for');
          selectElement.html('<option value="">---Select One---</option>');
          if (selectedOption === 'XI') {
          $.ajax({
            type: 'GET',
            url: '/dropdown_valuesxi',
            success: function(response) {
              // Assuming response is the JSON array containing dropdown values
              var dropdownValues = response;
      
              // Loop through the dropdown values and create option elements
              for (var i = 0; i < dropdownValues.length; i++) {
                var option = $('<option></option>');
                option.val(dropdownValues[i].id);
                option.text(dropdownValues[i].name);
                selectElement.append(option);
              }
            },
            error: function() {
                console.log('Error For General');

              // Handle error case
            }
          });
        }
        enrollForm.reset();
    // enrollfv.resetForm();
    // $(".stream_choose").removeClass("d-none");
});

$("#XII").click(function (e) {
    e.preventDefault();
    // $(".emis_code").removeClass("d-none");
    $(".form_std").removeClass("d-none");
    $(".form_title").addClass("d-none");
    $(".grade_xi").removeClass("d-none");
    $(".grade_x_title").addClass("d-none");
    $(".grade_xii").addClass("d-none");
    $(".general_grade").addClass("d-none");
    $(".pre_school").removeClass("d-none");
    $(".pre_school_X").addClass("d-none");
    $(".pre_school_XII").removeClass("d-none");
    enrollfv.disableValidator('previous_school');
    enrollfv.updateFieldStatus('previous_school', 'NotValidated');
        var selectedOption = $('input[name="class_select"]:checked').val();
          var selectElement = $('#admission_for');
          selectElement.html('<option value="">---Select One---</option>');
          if (selectedOption === 'XII') {
          $.ajax({
            type: 'GET',
            url: '/dropdown_values',
            success: function(response) {
              // Assuming response is the JSON array containing dropdown values
              var dropdownValues = response;
      
              // Loop through the dropdown values and create option elements
              for (var i = 0; i < dropdownValues.length; i++) {
                var option = $('<option></option>');
                option.val(dropdownValues[i].id);
                option.text(dropdownValues[i].name);
                selectElement.append(option);
              }
            },
            error: function() {
                console.log('Error For General');

              // Handle error case
            }
          });
        }
        enrollForm.reset();
    // enrollfv.resetForm();
});
    
$("#General").click(function (e) {
    e.preventDefault();
    $(".form_std").removeClass("d-none");
    $(".form_title").addClass("d-none");
    $(".grade_xi").addClass("d-none");
    $(".grade_x_title").addClass("d-none");
    $(".grade_xii").addClass("d-none");
    $(".general_grade").removeClass("d-none");
    $(".pre_school").removeClass("d-none");
    $(".pre_school_X").addClass("d-none");
    $(".pre_school_XII").addClass("d-none");
    // $(".emis_code").addClass("d-none");
    enrollfv.enableValidator('previous_school');
    
        var selectedOption = $('input[name="class_select"]:checked').val();
          var selectElement = $('#admission_for');
          selectElement.html('<option value="">---Select One---</option>');
        if (selectedOption === 'general') {
          $.ajax({
            type: 'GET',
            url: '/dropdown_values_general',
            success: function(response) {
              // Assuming response is the JSON array containing dropdown values
              var dropdownValues = response;
      
              // Loop through the dropdown values and create option elements
              for (var i = 0; i < dropdownValues.length; i++) {
                var option = $('<option></option>');
                option.val(dropdownValues[i].id);
                option.text(dropdownValues[i].name);
                selectElement.append(option);
              }
            },
            error: function() {
              console.log('Error For General');
                // Handle error case
            }
          });
        }
        enrollForm.reset();
    // enrollfv.resetForm();
});


//---------------------------------Script ends------------------------------//


