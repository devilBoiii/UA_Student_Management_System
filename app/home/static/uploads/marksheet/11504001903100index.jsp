<%@ page import="java.text.SimpleDateFormat" %>
<%@ page import="java.util.Date" %>
<%--<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>--%>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib prefix="form" uri="http://www.springframework.org/tags/form" %>
<html>
<head>
    <title>Ekaasel</title>
    <meta name="decorator" content="/layout/user.jsp">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
</head>

<body>
<div class="card"  id="targetId">
    <div class="card-header">
        <span style="font-size: 20px;color: #000000"><b style="color: #000000">Ekaasel </b> >>Application for public grievance </span>
    </div>
        <form class=" card-body form-horizontal"  id="applicationForm"  method="post" enctype="multipart/form-data">
                <div class="panel panel-default">
                    <div class="panel-heading"><label style="color: #000000">Enter your details below:</label></div>
                    <div class="panel-body">
                        <div class="form-group row">
                            <label class="col-lg-3 required"><b style="color: #000000">CID Number : </b></label>
                            <div class="col-lg-9">
                                <input type="text" class="form-control field numeric border-secondary" onkeypress="return isNumberKey(event)" id="cid" name="cidNo" onchange="getCidDetails()"  maxlength="11"/>
                                <span id="cidNoErrorMsg" class="text-danger"></span>
                            </div>
                        </div>

                        <div class="form-group row">
                            <label class="col-lg-3 required"><b style="color: #000000">Full Name : </b></label>
                            <div class="col-lg-3">
                                <input type="text" class="form-control field numeric border-secondary" id="fname" name="firstName" readonly="true"  placeholder="First Name" >
                            </div>
                            <div class="col-lg-3">
                                <input type="text" class="form-control field numeric border-secondary" id="mname" name="middleName" readonly="true" placeholder="Middle Name" >
                            </div>
                            <div class="col-lg-3">
                                <input type="text" class="form-control field numeric border-secondary" id="lname" name="lastName" readonly="true"  placeholder="Last Name" >
                            </div>
                        </div>
                        <div class="form-group row">
                            <label class="col-lg-3 required"><b style="color: #000000">Address : </b></label>
                            <div class="col-lg-3">
                                <input type="text" class="form-control field numeric border-secondary" id="dzo_id" name="dzongkhagName" readonly="true"  placeholder="Dzongkhag" >
                            </div>
                            <div class="col-lg-3">
                                <input type="text" class="form-control field numeric border-secondary" id="gewog_id" name="gewogName" readonly="true" placeholder="Gewog">
                            </div>
                            <div class="col-lg-3">
                                <input type="text" class="form-control field numeric border-secondary" id="village_id" name="villageName" readonly="true"  placeholder="Village" >
                            </div>
                        </div>
                        <div class="form-group row">
                            <label class="col-lg-3 required"><b style="color: #000000">Mobile Number : </b>
                            </label>
                            <div class="col-lg-9">
                                <input type="text" class="form-control field numeric border-secondary" onkeypress="return isNumberKey(event)" id="phone_id" name="contact_No" maxlength="8" >
                                <span id="phoneErrorMsg" class="text-danger"></span>
                            </div>
                        </div>
                        <div class="form-group row">
                            <label class="col-lg-3 "><b style="color: #000000">Email Id : </b></label>
                            <div class="col-lg-9">
                                <input type="email" class="form-control field text border-secondary" required="false" id="email" name="email_Id" >
                                <span class="text-danger" id="emailErrorMsg"></span>
                            </div>
                        </div>
                        <div class="form-group row">
                            <label class="col-lg-3"><b style="color: #000000">Grievance Description : <span style="color:red;font-weight: bold">*</span></b> </label>
                            <div class="col-lg-9">
                                <textarea class="form-control field border-secondary" id="public_area" name="appl_Type_Remark"></textarea>
                                <span class="text-danger" id="desc_ErrorMsg"></span>
                            </div>
                        </div>


                        <div class="form-group row" id="ifYes" >
                            <label class="col-lg-3"><b style="color: #000000">Supporting Documents(if any):</b></label>
                            <div class="col-lg-6">
                                <%--<input type="hidden" class="alert badge-primary"  name='attachedFileType' value="publicAttachment">--%>
                                <input type="file"  class="btn btn-primary" name="fileName" id="file" accept="image/jpeg,image/png,.doc,.docx,.pdf,.xlsx,.xls">
                            </div>
                        </div>

            <div class="form-group row">
                            <div class="col-lg-3"></div>
                <div class="col-md-4">
                               <button class="btn btn-success" id="btn_submit" onclick="saveData()" type="button"><b class="fa fa-save lg"></b>&nbsp;<b style="font-weight: bold"> Submit</b> </button> &nbsp;&nbsp;
                               <button class="btn btn-danger" id="btn_cancel" onclick="cancelData()" type="button"><b class="fa fa-close lg"></b>&nbsp;<b style="font-weight: bold">Cancel</b> </button>
                           </div>
                        </div>
                    </div>
                </div>
        </form>
</div>
<script>
    function getCidDetails(){
        var cid = $('#cid').val();
        var fname=$('#fname').val();
        if (cid == "") {
            $('#cid').addClass('error');
            $('#cidNoErrorMsg').html('CID is required').show();
            return false;
        }

        else if (cid.length != 11 && cid != '') {
            $('#cid').addClass('error');
            $('#cidNoErrorMsg').html('Bhutanese CID should have 11 digit long').show();
            return false;
        }
        if (cid.length==11&&fname==''){
            $('#cid').addClass('error');
            $('#cidNoErrorMsg').html('Invalid CID, Please try again with correct CID!').show();
        }

        if(cid !='' || cid != null){

            $.ajax({
                url:'${pageContext.request.contextPath}/index/getAllCitizenDetails?cid='+cid,
                type: 'GET',
                success: function (res) {
                    if(res.firstName == null||res.firstName==''){
                        $('#cid').addClass('error');
                        $('#cidNoErrorMsg').html('Invalid CID, PLease try again with correct CID!').show();
                    }
                    else{
                        $('#dob').val(res.applicantDob);
                        $('#fname').val(res.firstName);
                        $('#mname').val(res.middleName);
                        $('#lname').val(res.lastName);
                        $('#dzo_id').val(res.dzongkhagName);
                        $('#gewog_id').val(res.gewogName);
                        $('#village_id').val(res.villageName);
                        $('#phone_id').val(res.contact_No);
                    }

                }
            });
        }
    }
    function cancelData(){
        document.getElementById("applicationForm").reset();
    }

    /*
     function yesnoCheck(type) {
     var file = $('#file').val();
     var file1 = $('#file1').val();
     if (type == "Y") {
     $('#ifYes').show();
     $('#ifNo').hide();
     $('#yesCheck').prop('checked');
     }
     else if (type == "N") {
     $('#ifYes').hide();
     $('#ifNo').show();
     }

     }*/

    function saveData(){
        var cid = $('#cid').val();
        var file = $('#file').val();
        var isSubmit=true;
        if(validate()){
            /*if (true) {
             errorMsg('Your request is processing. Please wait...').show();
             return;
             }*/

            var applicationForm =$("#applicationForm");
            var doc_type = "Applicant";
            var url='${pageContext.request.contextPath}/index/save?cid='+cid+'&document_type='+doc_type;
            var options = {
                target: '#targetId',
                url: url,
                type: 'POST',
                enctype: "multipart/form-data",
                data: applicationForm.serialize()
                /*success:function(res){ if (res==1) {
                 errorMsg('Your request is processing. Please wait...',5000).show();
                 return;
                 }}*/

            };
            applicationForm.ajaxSubmit(options);
        }
    }

    function validate() {
        var returnVal = true;
        var cid = $('#cid').val();
        var public_area = $('#public_area').val();
        var phone_id = $('#phone_id').val();
        var email = $('#email').val();
        var fname=$('#fname').val();
        var file=$('#file').val();
        var file1=$('#file1').val();

        if (cid == "") {
            $('#cid').addClass('error');
            $('#cidNoErrorMsg').html('CID is required').show();
            returnVal = false;
        } else if(isNaN(cid)) {
            $('#cid').addClass('error');
            $('#cidNoErrorMsg').html('Cid should contain numbers only').show();
            returnVal = false;
        }
        else if (cid.length != 11 && cid != '') {
            $('#cid').addClass('error');
            $('#cidNoErrorMsg').html('Bhutanese CID should have 11 digit long').show();
            returnVal = false;
        }
        if (phone_id == "") {
            $('#phone_id').addClass('error');
            $('#phoneErrorMsg').html('Mobile Number is required').show();
            returnVal = false;
        }
        else if (isNaN(phone_id)){
            $('#phone_id').addClass('error');
            $('#phoneErrorMsg').html('Mobile Number should contain numbers only').show();
            returnVal = false;
        } else if (phone_id.length < 8 && phone_id != null) {
            $('#phone_id').addClass('error');
            $('#phoneErrorMsg').html('Mobile Number should have 8 digit').show();
            returnVal = false;
        }

        if (public_area == "") {
            $('#public_area').addClass('error');
            $('#desc_ErrorMsg').html('Please provide reason').show();
            returnVal = false;
        }

        if(email!=null&&email!='') {
            var atposition = email.indexOf("@");
            var dotposition = email.lastIndexOf(".");
            if (atposition < 1 || dotposition < atposition + 2 || dotposition + 2 >= email.length) {
                $('#emailErrorMsg').html('Please provide a valid email').show();
                returnVal= false;
            }
        }

        if(cid.length == 11 && fname==''){
            $('#cid').addClass('error');
            $('#cidNoErrorMsg').html('Invalid CID, PLease try again with correct CID!');
            returnVal=false;
        }
        return returnVal;
    }

    $('#cid').on("keyup blur", function() {
        $('#cid').on('keyup blur', function () {
            var cid = $(this).val();
            if (cid.length == 11 && cid != '' && !(isNaN(cid))) {
                $('#cid').removeClass('error');
                $('#cidNoErrorMsg').text('');
            }
        });
        $('#public_area').on('keyup blur', function () {
            var public_area = $(this).val();
            if (public_area != '') {
                $('#public_area').removeClass('error');
                $('#desc_ErrorMsg').text('');
            }
        });
        $('#phone_id').on('keyup blur', function () {
            var phone_id = $(this).val();
            if (phone_id.length == 8 && phone_id != '' && !( isNaN(phone_id))) {
                $('#phone_id').removeClass('error');
                $('#phoneErrorMsg').text('');
            }
        });
        $('#email').on('keyup blur', function () {
            var email = $(this).val();
            if (email!=null||email!=''){
                $('#email').removeClass('error');
                $('#emailErrorMsg').text('');
            }
        });
    });

    function isNumberKey(evt) {
        var retval=true;
        var cid = $('#cid').val();
        var charCode = (evt.which) ? evt.which : event.keyCode
        if (charCode > 31 && (charCode < 48 || charCode > 57)){
            return false;
            return true;
        }
    }

</script>

</body>

<%--<script src="resources/js/vendors/jquery.min.js"></script>
<script type="text/javascript" src="<c:url value="/resources/js/vendors/JqueryAjaxFormSubmit.js"/>"></script>
<script type="text/javascript" src="<c:url value="/resources/js/vendors/jquery.form.js"/>"></script>--%>


</html>
