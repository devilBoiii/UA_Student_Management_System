// -----------------------Form Validation--------------------------------//
const contactForm = document.getElementById('contact_form');

const contactfv = FormValidation.formValidation(contactForm, {
    fields: {
        Username: {
            validators: {
                notEmpty: {
                    message: 'The name field is required',
                },
            },
        },

        Useremail: {
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
        comment: {
            validators: {
                notEmpty: {
                    message: 'The comment field is required',
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
    contactDetail();

}).on('core.form.invalid', function (e) {
    swal("Validation failed !!!", "Some required fields are empty", "error")
});
