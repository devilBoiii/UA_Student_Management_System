const userForm = document.getElementById('user-form');
var isRoleChanged = false; // Flag to track if the role field has been changed

const addNewUsers = FormValidation.formValidation(userForm, {
  fields: {
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
    grade: {
      validators: {
        notEmpty: {
          message: 'Please select a grade',
        }
      }
    },
    subject: {
      validators: {
        notEmpty: {
          message: 'Please select a subject',
        }
      }
    },
    role: {
      validators: {
        notEmpty: {
          message: 'Please select a role',
        }
      }
    },
    email: {
      validators: {
        notEmpty: {
          message: 'Please enter email address',
        }
      }
    },
    section: {
        validators: {
          callback: {
            message: 'Please select a section',
            callback: function(input) {
              var selectedRole = $('#user-form [name="role"]').val();
              var sectionId = $('#section').val();
              var selectedGrade = $('#user-form [name="grade"]').val();
              var dropdownValues = [];
      
              // Fetch dropdown values synchronously
              $.ajax({
                type: 'GET',
                url: '/dropDownSection/' + selectedGrade,
                success: function(response) {
                  dropdownValues = response;
                },
                error: function() {
                  // Handle error case
                },
                async: false, // Make the AJAX request synchronous
              });
      
              var section = dropdownValues.find(section => section.id === sectionId);
              var sectionName = section ? section.section_name : null;
              var sectionGroupVisible = $('#section_group').is(':visible');
      
              // Check if the selected role is 'class_teacher'
              if (selectedRole === 'class_teacher') {
                // Hide the error message for section if section is not visible
                if (!sectionGroupVisible && sectionName === null) {
                  return true;
                }
                // Show the error message if section is selected but section name is null
              }
      
              // Perform validation if the section is visible and either the section name is not null or section is selected
              return sectionGroupVisible && (sectionName !== null || sectionId !== '');
            }
          }
        }
      },      
                
  },
  plugins: {
    trigger: new FormValidation.plugins.Trigger(),
    bootstrap: new FormValidation.plugins.Bootstrap(),
    submitButton: new FormValidation.plugins.SubmitButton(),
  },
}).on('core.form.valid', function (e) {
  save_user();
  $('#save').attr('disabled', true);
}).on('core.form.invalid', function (e) {
  console.log(e);
  swal("Validation failed!", "Some required fields are empty", "error");
});


function save_user() {
    var form = document.getElementById("user-form");
    var data = new FormData(form);
    var selectedRole = $('#user-form [name="role"]').val();
    // var selectedGrade = $('#user-form [name="grade"]').val();
    // if (selectedRole === 'class_teacher' && selectedGrade === '2') {
    //   data.set('section', '3'); // Set the value of section as 3
    // }
    $.ajax({
      type: 'POST',
      url: '/saveclassTeacher',
      data: data,
      contentType: false,
      cache: false,
      processData: false,
      beforeSend: function () {
          $("#save").text("Loading....");
  
          // Set a timeout to clear the loading message after 3 seconds (3000 milliseconds)
          // setTimeout(function () {
          //     $("#save").text("Save");
          //     $("#save").removeAttr("disabled");
          //     $("#save").removeClass("disabled");
          // }, 1500); // 3000 milliseconds = 1 seconds
      },
      success: function (res) {
          swal("Information successfully saved", "Click Ok to continue", "success")
              .then(function () {
                  $('#user-form').trigger('reset');
                  window.location = "/getClassTeacher";
              });
      },
  });
  }

$(document).ready(function() {
    // Set the default value of the role field to "class_teacher"
    $('#user-form [name="role"]').val('class_teacher');
  }); 
  
function getSections(gradeId) {
    var sections = [];
  
    // Send an AJAX request to retrieve the dropdown values for the "section" select element
    $.ajax({
      type: 'GET',
      url: '/dropDownSection/' + gradeId,
      success: function(response) {
        sections = response;
      },
      error: function() {
        // Handle error case
      },
      async: false, // Make the AJAX request synchronous
    });
  
    return sections;
  }

  $("#grade").on("change", function() {
    var gradeId = $(this).val();
    $('#subject_group').hide();
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
  
        if (dropdownValues.length === 0) {
          // If no sections are available, disable the select element and display "No Section" as an option
          sectionSelect.prop("disabled", true);
          classSelect.prop("disabled", true);
  
          // Create and append the "No Section" option
          var noSectionOption = $('<option>');
          noSectionOption.val("no_section");
          noSectionOption.text("No Section");
          sectionSelect.append(noSectionOption);
  
          // Set the hidden section_id for the "No Section" option
          noSectionOption.data('section-id', 'hidden_section_id');
  
          // Create and append the "No Class" option
          var noClassOption = $('<option>');
          noClassOption.val("no_class");
          noClassOption.text("No Class");
          classSelect.append(noClassOption);
  
          // Hide the section group
          $("#section_group").hide();
  
          // Fetch subjects based on the hidden section_id
          var hiddenSectionId = noSectionOption.val();
          fetchSubjects(hiddenSectionId);
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
  
            // Check if the section name is null
            if (dropdownValues[i].name === null) {
              // Hide the section group if the section name is null
              $("#section_group").hide();
  
              // Fetch subjects based on the hidden section_id
              var hiddenSectionId = dropdownValues[i].id;
              fetchSubjects(hiddenSectionId);
            } else {
              // Show the section group
              $("#section_group").show();
            }
          }
        }
      },
      error: function() {
        // Handle error case
      }
    });
  });
  
  // Function to handle the change event for the section select element
  $("#section").on("change", function() {
    var sectionId = $(this).val();
  
    // Fetch subjects based on the selected section_id
    fetchSubjects(sectionId);
  });

// Function to handle the change event for the section select element

function fetchSubjects(sectionId) {
    // Send an AJAX request to retrieve the subjects for the selected section
    $.ajax({
      url: '/get_subjects/' + sectionId,
      type: 'GET',
      success: function(response) {
        if (response.length===0){
            $('#subject_group').hide();
        }
        else{  
        // Update the "Select Subject" dropdown with the retrieved subjects
        var subjectDropdown = $('#subject');
        subjectDropdown.empty();
        subjectDropdown.append($('<option>', { value: '', text: '---Select Subject---' }));
        for (var i = 0; i < response.length; i++) {
          var subject = response[i];
          var option = $('<option>');
          option.val(subject.id);
          option.text(subject.name);
          subjectDropdown.append(option);
        }
        $('#subject_group').show();
    }
      },
      error: function(xhr, status, error) {
        // Handle the error if the AJAX request fails
        console.error(error);
      }
    });
  }


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