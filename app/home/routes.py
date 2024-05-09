from flask import Flask, app, render_template, request, jsonify, session, redirect, url_for,flash,current_app
from numpy import std
from app.home.service import get_std_class, get_std_results, gettermrating, marks_results, view_std_result
from app.home import blueprint
from sqlalchemy import create_engine
from app import db, login_manager
from flask_login import (current_user, login_user, logout_user)
from config import Config
from app.admin.models import User
from app.admin.forms import LoginForm
from app.home.service import get_std_class, store_student_details, check_exist, store_academic_details, get_dzo_list, get_gewog, get_village,track_std, store_contact_details, printing_result,pay_std_fee,getStartDate,getEndDate,checkIndexorCid,getstudentDetail,getClassId,getClassIdx,getClassIdGeneral,getClassIdxi,getpaymentHistory,get_gewog_std, get_village_std
from flask_login import current_user, login_required
from app.admin.util import get_user_by_id, verify_pass, check_user_login_info, update_login_info, hash_pass
from app.home.service import gettermrating
from uuid import uuid4
from datetime import datetime,date
import google.auth
from flask_mail import Message
from app import mail
import time
import hashlib
import urllib.parse
from cryptography.fernet import Fernet,InvalidToken
from urllib.parse import quote
import base64
import psycopg2
import binascii
import os
import  pytz


@blueprint.before_request
def check_session_timeout():
    if 'last_activity' in session:
        last_activity_time = session['last_activity']
        last_activity_time = last_activity_time.replace(tzinfo=pytz.UTC)
        current_time = datetime.datetime.now(pytz.UTC)
        print(current_app.config['PERMANENT_SESSION_LIFETIME'],"********Curent time")
        # Calculate the duration of inactivity
        inactivity_duration = current_time - last_activity_time
        print(inactivity_duration,"***********INACTIVITY **********",current_time,"**CURRENT",last_activity_time,"LAST ACTIVITY*")
        if inactivity_duration >  current_app.config['PERMANENT_SESSION_LIFETIME']:
            # Perform actions for session timeout (e.g., log out the user)
            # logout_user() or session.clear()
            print("***********session time out **********")
            flash('Your session has timed out. Please log in again.')

        # Update the last activity time to the current time
        session['last_activity'] = current_time

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
#enrollment_start_date = return getStartDate()
# datetime.strptime('2023-01-01', '%Y-%m-%d').date()
# enrollment_end_date = datetime.strptime('2023-08-31', '%Y-%m-%d').date()


@blueprint.route('/')
def route_default():
    conn = psycopg2.connect("postgresql://postgres:root@localhost:5432/student_db"
)
    cursor = conn.cursor()

    query = 'SELECT * FROM public."Announcement" ORDER BY id DESC limit 1'
    cursor.execute(query)
    announce = cursor.fetchone()

    cursor.close()
    conn.close()

    if announce:
        title, subject, content, link= announce[1:5]  # Assuming title, subject, and content are the second, third, and fourth columns
    else:
        title = "No Announcement"
        subject = ""
        content = ""
        link = ""

    context = {"title": title, "subject": subject, "content": content, "link":link}
    return render_template('index.html', **context)

# Route for enroll_student.html and dzongkhang list
@blueprint.route('/enroll-student-detail')
def enroll_page():
    current_date = date.today()
    enrollment_start_date = getStartDate()
    enrollment_end_date=getEndDate()
    enrolStart=datetime.datetime.strptime(enrollment_start_date,'%Y-%m-%d').date()
    enrollEnd=datetime.datetime.strptime(enrollment_end_date,'%Y-%m-%d').date()
    
    if enrolStart <= current_date <= enrollEnd:        
        return get_dzo_list()
    else:
        return render_template('enroll.html')


# Route to store student detail
@blueprint.route('/store-student-info', methods=['GET','POST'])
def store_studentInfo_page():
    # try:
    identification_number = request.form.get('cid')
    check = check_exist(identification_number)
    if check==False: 
        id_personal = store_student_details()
        store_academic_details(id_personal)
        return "success"
    else:
        return "Error"
        

# Route to fetch gewog list
@blueprint.route("/get-gewog-list", methods=["GET", "POST"])
def get_gewog_list():
    return get_gewog()

@blueprint.route("/get-gewog-list-std", methods=["GET", "POST"])
def get_gewog_list_std():
    return get_gewog_std()

# Route to fetch gewog list
@blueprint.route("/dropdown_values", methods=["GET", "POST"])
def getClass():
    return getClassId()

@blueprint.route("/dropdown_valuesx", methods=["GET", "POST"])
def get_class_id():
    return getClassIdx()

@blueprint.route("/dropdown_values_general", methods=["GET", "POST"])
def get_class_id_general():
    return getClassIdGeneral()

@blueprint.route("/dropdown_valuesxi", methods=["GET", "POST"])
def get_class_idxi():
    return getClassIdxi()

# Route to fetch village list
@blueprint.route("/get-village-list", methods=["GET", "POST"])
def get_village_list():
    return get_village()

@blueprint.route("/get-village-list-std", methods=["GET", "POST"])
def get_village_list_std():
    return get_village_std()

@blueprint.route("/forgotPassword/<username>",methods=["GET","POST"])
def forgotpass(username):
    check_user='select username,email from public."User" where username=%s '
    checkUser=connection.execute(check_user,username).fetchone()
    if checkUser is None:
     return {"error": "You don't have a user account."}
    else:
     emailId = checkUser['email']
     userName=checkUser['username']
     print(userName,emailId,"****email")
     return {"emailId": emailId, "userName": userName}
    
@blueprint.route("/resetPassword/<emailId>/<userNames>", methods=["POST"])
def resetPassword(emailId, userNames):
    print(emailId, "**email", userNames, "**user")
    if send_reset_mail(emailId, userNames):
        print("****in sendMail")
        return "success"
    else:
        print("** not send mail")
        return "Error"
    
@blueprint.route('/resetuserPassword', methods=["GET"])
def passwordresetPage():
    userUrl = request.args.get('userUrl')
    key = request.args.get('pwd')
    print(userUrl,"*****User",key,"********pwd")

    decryptedUsers = Fernet(key).decrypt(userUrl.encode('utf-8')).decode('utf-8')
        # Perform additional processing using the decrypted userUrl
    strQuery = 'select username,email from public."User" where username=%s'
    check_User = connection.execute(strQuery, decryptedUsers).fetchone()
    print(is_valid_key_format(key),"*****is Valid Key",decryptedUsers,"******USERURL")

    if (not is_valid_key_format(key)) :
        return {"error":"Invalid key format. Unable to decrypt userUrl."}
    elif decrypt_userUrl(userUrl, key) is None:
        return {"error":"Invalid userUrl. Unable to decrypt userUrl."}
    elif (not is_valid_key_format(key)) and decrypt_userUrl(userUrl, key) is None:
        return {"error":"Both are incorrect."}
    elif decrypt_userUrl(userUrl, key) is not None and ( is_valid_key_format(key)) :
        if check_User is None:
            return {"error":"You don't have a user account."}
        else:
            emailId = check_User['email']
            userName = check_User['username']
            print(userName, emailId, "****email")
            return render_template('resetPass.html')

def is_valid_key_format(key):
    try:
        Fernet(key)
        return True
    except (ValueError, TypeError):
        return False
   
def decrypt_userUrl(userUrl, key):    
    try:
        f = Fernet(key)
        return f.decrypt(userUrl.encode('utf-8')).decode('utf-8') 
    except (InvalidToken, ValueError):
        return None

@blueprint.route('/resetnewPassword',methods=["POST"])
def resetforgotpass():
    epassword = request.form.get('epassword')
    userUrl = request.form.get('userUrl')
    key=request.form.get('pwd')
    f=Fernet(key)
    userName=f.decrypt(userUrl.encode('utf-8')).decode('utf-8')
    print(key,"******KEY",userName,"***username")
    strQuery='update public."User" set password=%s where username=%s'
    updatePassword=connection.execute(strQuery,(hash_pass(epassword),userName))
    return updatePassword

@blueprint.route('/checkUsernameResetPassword/<userNames>')

def checkUseracc(userNames):
    strQuery='select username,email from public."User" where username=%s '
    check_User=connection.execute(strQuery,userNames).fetchall()
    print(check_User,"***USERS***")
    if check_User is None:
        return {"error": "You don't have a user account."}
    else: 
        emailId = check_User['email']
        userName=check_User['username']
        print(userName,emailId,"****email")
        return {"emailId": emailId, "userName": userName}


def send_reset_mail(emailId, userNames):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    userUrl = cipher_suite.encrypt(userNames.encode('utf-8'))
    print(emailId, "**email", userNames, "**user",userUrl,'*****USER')
    reset_url = 'http://127.0.0.1:5000/resetuserPassword?userUrl=' + quote(userUrl) + '&pwd=' + quote(key)
    msg = Message(subject='Application Status', sender='karma123karma456@gmail.com', recipients=[emailId])
    msg.body = "Dear " + str(userNames) + ', ' + "\n" + "To reset your password, click on the following link: " + reset_url
    print(msg, "***MESSAGE", msg.body, '**BODY')
    try:
        mail.send(msg)
        print("****in sendMail")
        return True  # Return True if the email is sent successfully
    except Exception as e:
        print("** not send mail:", str(e))
        return False
       
@blueprint.route('/edit-users', methods=['GET'])
def editUsers():
    userUrl = request.args.get('userUrl')
    key = request.args.get('pwd')
    decryptedUsers = Fernet(key).decrypt(userUrl.encode('utf-8')).decode('utf-8')
    print(userUrl,"****UserName",key,"******key")
    if not is_valid_key_formats(key):
        return "Invalid key format. Unable to decrypt userUrl.", 400
    elif decrypt_userUrls(userUrl, key) is None:
        return "Invalid userUrl. Unable to decrypt userUrl.", 400
    elif (not is_valid_key_formats(key)) and decrypt_userUrls(userUrl, key) is None:
        return "Both are incorrect.", 400
    elif decrypt_userUrls(userUrl, key) is not None and is_valid_key_formats(key):
        strQuery = 'select username,email,password from public."User" where username=%s'
        check_User = connection.execute(strQuery, decryptedUsers)
        user_data = check_User.fetchone()
        userDetail=User.query.filter_by(username=decryptedUsers).first()
        if user_data:
            emailId = user_data['email']
            userName = user_data['username']
            epassword = user_data['password']
            print(user_data.password,"******PASSWORD Bytea")
            hashed_passwords=binascii.hexlify(epassword).decode('utf-8')
            print(hashed_passwords,"HASH PASSSSPASSSS")
            return render_template( 'editUsers.html', emailId=emailId, userName=userName, epassword=epassword,hashed_passwords=hashed_passwords)
        else:
            return "User not found.", 404


def is_valid_key_formats(key):
    try:
        Fernet(key)
        return True
    except (ValueError, TypeError):
        return False
   
def decrypt_userUrls(userUrl, key):    
    try:
        f = Fernet(key)
        return f.decrypt(userUrl.encode('utf-8')).decode('utf-8') 
    except (InvalidToken, ValueError):
        return None

@blueprint.route('/update-password-data', methods=['POST'])
def update_password_data():
    emailIds = request.form.get('emailIds')
    userName = request.form.get('userNamed')
    password = request.form.get('passwords')
    passwords = request.form.get('passworded')
    userNames = request.form.get('userNamess')
    emails = request.form.get('emails')
    hashed_passwords = request.form.get('hashed_passwords')
    print(hashed_passwords,"****HASHEDPASS***")
    passwordhash=''
    is_valid_password=''
    if password == passwords:
        password = password
        print("**PASSWORD of same",password)
    else:
        print("****PASSWORD AHSH",passwordhash)
        binData = 'select password from public."User" where username=%s'
        binDatas = connection.execute(binData, 'hr22').fetchone()
        print("****HR2", binDatas, '***')
        print(userName, "%%%%%%%UserName", emailIds, '%%%%%%%email', password, '****Password', passwords, '***Passwords',
          userNames, '****uNames', "**hashed")

    # Verify the input password against the stored hashed password
    if emailIds == emails and userName == userNames and verify_pass(password,hashed_passwords.encode('utf-8')):
        return jsonify({"error": "You have all the same data as updated."})
    else:
        updateQuery = 'UPDATE public."User" SET username = %s, email = %s, password = %s WHERE username = %s'
        connection.execute(updateQuery, userNames, emailIds, password, userName)
        return jsonify({"message": "The data has been updated successfully."})

@blueprint.route('/login', methods=['POST'])
def do_login():
    # read form data
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    
    if user:
        s_password = bytearray(user.password)
        
        if user and verify_pass(password, s_password):
            # Set the initial session time or update the last activity time
            session['last_activity'] = datetime.datetime.now(pytz.UTC)
            print(session['last_activity'],"***********session")
            login_user(user)

            return jsonify({"output": {"fa_required": False, "message": "Login successful"}})   

        return jsonify({"output": {"fa_required": "invalid", "message": "Your password is invalid"}})
    else:
        return jsonify({"output": {"fa_required": "invalid", "message": "Your username is invalid."}})


# Login & Registration
@blueprint.route('/login-user', methods=['GET'])
def login():
    login_form = LoginForm(request.form)
    # if not current_user.is_authenticated:
    return render_template('signin.html',
                               form=login_form)

# Logout user
@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_blueprint.login'))


# Errors handling
@login_manager.unauthorized_handler
def unauthorized_handler():
    login_form = LoginForm(request.form)
    #if not current_user.is_authenticated:
    return render_template('signin.html',
                               form=login_form)
    # return render_template('accounts/login.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    login_form = LoginForm(request.form)
    # if not current_user.is_authenticated:
    return render_template('signin.html',
                               form=login_form)
    # return render_template('accounts/login.html'), 403

# students fee structure


@blueprint.route('/fees-detail')
def studentFee():
    return render_template("std_fee.html")

@blueprint.route('/checkForIndexNo')
def studentIndex():
    id=request.args.get('studentCid')
    return checkIndexorCid(id)

@blueprint.route('/getPaymentHistory')
def paymentHis():
    id=request.args.get('studentCid')
    return getpaymentHistory(id)

@blueprint.route('/getstudentDetails')
def getstudentDetails():
    getDetails=getstudentDetail()
    return "success"


@blueprint.route('/add-admin')
def add_admin():
    create_user = 'INSERT INTO public."User" (id, username, email, password, type, is_active, cid_number, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    connection.execute(create_user, (uuid4(), 'administrator', 'test@gmail.com', hash_pass('admin@123'), '', True, '1234345', '17277768'))

    return "Success"

# track student
@blueprint.route('/track-student')
def trackapplication():
    return render_template('track_std.html', std=std)

# track students
@blueprint.route('/search', methods=['POST','GET'])
def search():
    print("**********TRACK")
    return track_std()


# student result
@blueprint.route('/student-result/<id>')
def result(id):
    query = "SELECT ev.class_test_one, ev.class_test_two, ev.mid_term, ev.annual_exam, ev.cont_assessment FROM public.tbl_academic_detail ac LEFT JOIN public.tbl_student_evaluation ev ON ac.std_personal_info_id=ev.student_id WHERE ac.index_number=%s"
    result = engine.execute(query, (id,)).fetchall()
    print(result, "**RESULT")
    if result:
        keys = ('class_test_one', 'class_test_two', 'mid_term', 'annual_exam', 'cont_assessment')
        if len(result) > 0:
            data = [{keys[i]: int(row[i]) for i in range(len(keys))} for row in result]
            print(data, "**DATA")
            return render_template("std_result.html", data=data)
        else:
            return jsonify({'error': 'No data found for the given index number.'})
    else:
        return jsonify({'error': 'No data found for the given index number.'})


@blueprint.route('/Contact-us')
def contact():
    return render_template("contact_us.html")

# contact form
@blueprint.route('/store-contact-form', methods=['POST'])
def contact_us():
    return store_contact_details()

# To check if CID / data already exist in database
@blueprint.route('/check-cid-exist', methods=['GET', 'POST'])
def checkCID():
    identification_number = request.form.get('cid')
    check = check_exist(identification_number)
    if check:
        return "ErrorFound"
    else:
        return "Done"

# printing student result

@blueprint.route('/get-student-result', methods=['POST'])
def student_result():
         return printing_result()

# account submitting
@blueprint.route('/account_submitting', methods=['POST'])
def fee_submmition():
    studentCid = request.form.get('studentCid')
    return pay_std_fee(studentCid)

@blueprint.route('/view-std-details/<id>', methods=['GET'])
def view_student_detail(id):
    try:
        return get_std_class(id)
    except Exception as e:
        return "The organization has not prepared result for him or her yet!"

# @blueprint.route('/home/getslots', methods=['POST'])
# @login_required
# def get_slots():

#     slot_query = '''SELECT id, class7, class8, class9, class10, class11_arts, class11_com, class11_sci, class12_art, class12_com, class12_sci FROM public.tbl_std_slots'''
#     slot = engine.execute(slot_query).fetchall()

#     return jsonify(slot)

@blueprint.route('/view-term-rating/<id>', methods=['GET'])
def view_term_rating(id):
    print(f'Received id: {id}')
    return gettermrating(id)

    # return render_template ("termrating.html")
import datetime

@blueprint.route('/check_std_cid/<cid>', methods=['GET'])
def check_std_cid(cid):
    print("CID_IS_HERE: ", cid)
    cid_check_query = '''SELECT *, gg.* FROM public.tbl_students_personal_info AS sp 
    LEFT JOIN public.tbl_gewog_list AS gg ON gg.gewog_id = sp.student_gewog WHERE sp.student_cid = %s'''
    cid_check = engine.execute(cid_check_query, cid).fetchone()
    print("CID_check: ", cid_check)
    
    if cid_check:
        # CID exists, return user details
        row_dict = dict(cid_check)
        formatted_date = row_dict.get("dob")
        formatted_dob = []
        if formatted_date:
            dob_datetime = datetime.datetime.strptime(formatted_date, '%Y-%m-%d')
            formatted_dob = dob_datetime.strftime('%Y-%m-%d')
        print(row_dict.get('gewog_name'), "THISGEWOG")
        return jsonify({
            'exists': True,
            'first_name': row_dict.get('first_name'),
            'last_name': row_dict.get('last_name'),
            'email': row_dict.get('student_email'),
            'gender': row_dict.get('gender'),
            'phone_number': row_dict.get('student_phone_number'),
            'permanent_dzongkhag': row_dict.get('student_dzongkhag'),
            'permanent_gewog': row_dict.get('student_gewog'),
            'permanent_village': row_dict.get('student_village'),
            'dob': formatted_dob
        })
    else:
        # CID does not exist
        return jsonify({'exists': False})