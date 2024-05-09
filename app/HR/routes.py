from cgitb import text
import re
from uuid import uuid4
from flask import app, render_template,request,redirect,session,flash,current_app,jsonify
from flask_login import current_user, login_required
from app.HR import blueprint
from app.admin.service import get_std_slot, is_human_resource, save_subuser_detail_table,save_user_table, save_user_detail_table, all_users, is_admin,is_classTeacher, is_subjectTeacher, get_user_by_id,getClasses,getSection,getSubjects
# send_application_mailUser
from app.HR.service import edit_the_user, get_student_fee,class_teacher,subjectTeacher,getModaldetails,assignSection,dropdownHostels, update_editfunction,update_edit_subfunction, save_subTeacher_hr,save_subjectTeacher,past_payment,edit_the_sub_teacher, edit_the_sub_user
from app.HR.service import deleteUser as __DU__
from app.HR.service import deleteSubjectUser as __DUU__
from app.HR.service import deletePastPayments as ___DUU___
from app.admin.util import hash_pass, verify_pass

import pytz
from datetime import datetime
from sqlalchemy import create_engine
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()


@blueprint.before_request
def check_session_timeout():
    if 'last_activity' in session:
        last_activity_time = session['last_activity']
        last_activity_time = last_activity_time.replace(tzinfo=pytz.UTC)
        current_time = datetime.now(pytz.UTC)
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

@blueprint.route('/transaction_list')
@login_required
def view_payment_seatconfirm():
    if is_human_resource():
     id = current_user.id
     details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
     result = connection.execute(details_str, id).fetchall()
     paymentmodes = request.args.get('paymentmodes')
    #  print("paymentmodes====", paymentmodes)
     return render_template('/pages/payment.html', paymentmodes=paymentmodes, result=result)
    else:
        return redirect('/login-user')

@blueprint.route('/student-application-list')
@login_required
def std_app_list():
    user_id=current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    return render_template('/pages/student_application_list.html', result=result)


@blueprint.route('/std-detials-hr/<id>', methods=['GET'])
@login_required
def std_details_hr(id):
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    std_details = connection.execute(
        'SELECT *, P.id FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        'left join public.class as cc on A.admission_for_class=cc.class_id '
        'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_present_dzongkhag '
        'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_present_gewog '
        'inner join public.tbl_village_list as village on village.village_id = P.student_present_village '
        'WHERE P.id =%s',
        id).first()

    std_info = connection.execute(
        'SELECT *, P.id FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_dzongkhag '
        'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_gewog '
        'inner join public.tbl_village_list as village on village.village_id = P.student_village '
        'WHERE P.id =%s',
        id).first()
    return render_template('/pages/studentinfo.html', std=std_details, std_info=std_info, result=result)



@blueprint.route('/past_payment')
@login_required
def view_past_payment():
    if is_human_resource():
     id = current_user.id
     details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
     result = connection.execute(details_str, id).fetchall()
     paymentmodes = request.args.get('paymentmodes')
    #  print("paymentmodes====", paymentmodes)
     return render_template('/pages/past_payment.html', paymentmodes=paymentmodes, result=result)
    else:
        return redirect('/login-user')
    
@blueprint.route('/transaction_list')
@login_required
def view_payment_installment():
    user_query = '''SELECT * FROM public.user_detail
    ORDER BY id ASC '''
    users = engine.execute(user_query).fetchall()
    roles = [user['role'] for user in users]            
    if is_human_resource():
     paymentmodes = request.args.get('paymentmodes')
     return render_template('/pages/payment.html', paymentmodes=paymentmodes, roles=roles)
    else:
        return "http://127.0.0.1:5000/login-user"
    
@blueprint.route('/transaction_list')
@login_required
def view_payment_full():
    user_query = '''SELECT * FROM public.user_detail
    ORDER BY id ASC '''
    users = engine.execute(user_query).fetchall()
    roles = [user['role'] for user in users]            
    if is_human_resource():
     paymentmodes = request.args.get('paymentmodes')
    if is_human_resource():
        paymentmodes='Full'
        return render_template('/pages/payment.html', paymentmodes=paymentmodes, roles=roles)
    else:
        return redirect('/login-user')

@blueprint.route('/summit_fees', methods=['GET'])
@login_required
def submit_fee():
    if(is_human_resource()):
        paymentmodes=request.args.get('paymentmodes')
        print(paymentmodes,"****PAYMENTMODE")
        student_fee = get_student_fee(paymentmodes)
    else:
        student_fee = []
    return student_fee

@blueprint.route('/getModalDetails', methods=['GET'])
@login_required
def getModals():
    if is_human_resource():   
        stdCid=request.args.get('stdCid')
        print(stdCid,"**********************cid")
        getdetail=getModaldetails(stdCid)
        print(getdetail,"**getDetails**")
        return jsonify(getdetail)

@blueprint.route('/dropdownHostel',methods=['GET'])
@login_required
def dropdownHostel():
    if is_human_resource():
        return dropdownHostels()

@blueprint.route('/assignSection',methods=['POST'])
@login_required
def giveSection():
    if is_human_resource():
        studentCID = request.form.get('stdCid')
        selectedSection = request.form.get('selectedSectionId')
        selectedHostel=request.form.get('selectedHostel')
        accomodation=request.form.get('accomodation')
        print(studentCID,"**Index**",selectedSection,"***section**", selectedHostel)
        return assignSection(studentCID,selectedSection,selectedHostel,accomodation)

@blueprint.route('/addClassTeacher')
@login_required
def addClassTeacher():
    id = current_user.id
    user_query = '''SELECT * FROM public.user_detail
    ORDER BY id ASC '''
    users = engine.execute(user_query).fetchall()
    roles = [user['role'] for user in users] 
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, id).fetchall()       
    return render_template('/pages/class-teacher/add_class_teacher.html', roles=roles, result=result)

@blueprint.route('/check_class_steam_sec', methods=['GET', 'POST'])
@login_required
def check_class_steam_sec():
    user_id = current_user.id
    for key, value in request.form.items():
            print("HereReaching------------------------------------------------", key,"Value", value)
            if key == 'uu_id':
                subject = request.form.get('subject[0]')
                grade = request.form.get('grade[0]')
                section = request.form.get('section[0]')
                #insert query .....

                print(key,'This is the Grade11: ', grade, 'This is the section: ', section, 'This is the subject: ', subject)
                checking_str = '''
                SELECT COUNT(*) FROM public.user_detail WHERE grade = %s AND section_no = %s AND stream = %s
                '''
                checking_results = connection.execute(checking_str, grade, section, 'class_teacher').fetchall()
                check_result = checking_results[0][0]
                print("This is the result:-------- ", check_result)
                if check_result > 0:
                    return jsonify({'exists': True})
                else:
                    return jsonify({'exists': False})
            else:
                subject = request.form.get('subject')
                grade = request.form.get('grade')
                section = request.form.get('section')
                print(key,'This is the Grade00: ', grade, 'This is the section: ', section, 'This is the subject: ', subject)
                checking_str = '''
                SELECT COUNT(*) FROM public.user_detail WHERE grade = %s AND section_no = %s AND stream = %s
                '''
                checking_results = connection.execute(checking_str, grade, section, 'class_teacher').fetchall()
                check_result = checking_results[0][0]
                print("This is the result:-------- ", check_result)
                if check_result > 0:
                    return jsonify({'exists': True})
                else:
                    return jsonify({'exists': False})

@blueprint.route('/check_class_sub_sec', methods=['GET', 'POST'])
@login_required
def check_class_sub_sec():
    user_id = current_user.id
    for key, value in request.form.items():
            print("HereReaching------------------------------------------------")
            if key.startswith('grade['):
                index = key[key.index('[')+1:key.index(']')]
                grade = request.form.get('grade['+str(index)+']')
                section = request.form.get('section['+str(index)+']')
                subject = request.form.get('subject['+str(index)+']')
                #insert query .....

                print(key,'This is the Grade: ', grade, 'This is the section: ', section, 'This is the subject: ', subject)
                checking_str = '''
                SELECT COUNT(*) FROM public.user_detail WHERE grade = %s AND section_no = %s AND subject = %s
                '''
                checking_results = connection.execute(checking_str, grade, section, subject).fetchall()
                check_result = checking_results[0][0]
                print("This is the result:-------- ", check_result)
                if check_result > 0:
                    return jsonify({'exists': True})
                else:
                    return jsonify({'exists': False})

@blueprint.route('/getClassTeacher_hr')
@login_required
def getClassTeacher_hr():
    user_query = '''SELECT * FROM public.user_detail
    ORDER BY id ASC '''
    users = engine.execute(user_query).fetchall()
    roles = [user['role'] for user in users]          
    
     # Example using SQLAlchemy's text() for executing raw SQL
    grade_query = '''SELECT * FROM public.class'''
    grades = engine.execute(grade_query).fetchall()
    print(grades,  "==================", roles)

    # If you need user_id for getSection, you can use current_user.id again
    subject_query = '''SELECT * FROM public.tbl_subjects'''
    subjects = engine.execute(subject_query).fetchall()
    id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, id).fetchall()
    return render_template('/pages/class-teacher/getclteacher_list.html', grades=grades, subjects=subjects, result=result)

@blueprint.route('/class-teacher-list_hr', methods=['POST'])
@login_required
def cl_teacherList():
    return class_teacher() 

@blueprint.route('/addSubjectTeacher', methods=['GET','POST'])
@login_required
def addSubTeacher():
    id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, id).fetchall()
    context = {'result':result}
    return render_template('/pages/subject-teacher/add-subject-teacher.html', **context)

from sqlalchemy import text

@blueprint.route('/getSubjectTeacher', methods=['GET','POST'])
@login_required
def getSubjectTeacher():
    grade = request.form.get('grade')
    grade_query = '''SELECT class_id, class_name FROM public.class'''
    grades = engine.execute(grade_query).fetchall()

    # If you need user_id for getSection, you can use current_user.id again
    subject_query = '''SELECT subject_code, subject_name FROM public.tbl_subjects '''
    subjects = engine.execute(subject_query).fetchall()

    section_query = text('''Select C.class_name, SS.section from public.class as C
    left join public.std_section as SS on SS.class_id = :class_id
    ''')
    sect = engine.execute(section_query, {'class_id' : grade}).fetchall()

    id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, id).fetchall()
    return render_template('/pages/subject-teacher/subject-teacher-list.html', grades=grades, subjects=subjects, sect=sect, result=result )

@blueprint.route('hr/subjectTeacherList',methods=['POST'])
@login_required
def sub_teacherList():
    return subjectTeacher()

@blueprint.route('hr/past_payments',methods=['POST'])
@login_required
def past_payments():
    return past_payment()

@blueprint.route("/saveTeacher", methods=['POST'])
@login_required
def savesub_user():
    # Retrieve form data
    password = request.form['password']
    role = request.form['role']
    section = request.form['section']
    grade = request.form['grade']
    subject = request.form['subject']

    # Check for duplicate assignment
    existing_assignment = get_subexisting_assignment(grade, role, section, subject)

    if existing_assignment:
        return "The class Teacher already exists."

    # If not a duplicate, proceed with saving the user details
    user_id = save_user_table(password)
    save_subuser_detail_table(user_id, password, role, section, grade, subject)

    return "Class Teacher saved successfully."

@blueprint.route("/save_sub_teacher_hr", methods = ['GET','POST'])
@login_required
def save_teacher_hr():
    return save_subTeacher_hr()

@blueprint.route("/save_subject_teacher_hr", methods = ['GET','POST'])
@login_required
def save_subject_teacher():
    
    return save_subjectTeacher()

def get_subexisting_assignment(grade, role, section, subject):
    # Check if there is an existing assignment for the same class, section, and subject
    query = 'SELECT user_id FROM public.user_detail WHERE grade = %s AND role = %s AND section = %s AND subject = %s'
    result = connection.execute(query, (grade, role, section, subject)).fetchone()
    
    if result:
        return result[0]  # Return the existing user_id if assignment exists
    else:
        return None

        
@blueprint.route("/saveclassTeacher", methods=['POST'])
@login_required
def save_user():
    # Retrieve form data
    password = request.form['password']
    role = request.form['role']
    section = request.form['section']
    grade = request.form['grade']
    subject = request.form['subject']

    # Check for duplicate assignment
    existing_assignment = get_existing_assignment(grade, role, section)

    if existing_assignment:
        return "The class Teacher already exists."

    # If not a duplicate, proceed with saving the user details
    user_id = save_user_table(password)
    save_user_detail_table(user_id, password, role, section, grade, subject)

    return "Class Teacher saved successfully."

def get_existing_assignment(grade, role, section):
    # Check if there is an existing assignment for the same class, section, and subject
    query = 'SELECT user_id FROM public.user_detail WHERE grade = %s AND role = %s AND section_no = %s'
    result = connection.execute(query, (grade, role, section)).fetchone()
    
    if result:
        return result[0]  # Return the existing user_id if assignment exists
    else:
        return None

@blueprint.route('/dropDownClass', methods=['GET','POST'])
@login_required
def getClassId():
    return getClasses()


@blueprint.route('/get_section/<gradeId>', methods=['GET','POST'])
@login_required
def getSectionId(gradeId):
    try:
        gradeId = int(gradeId)
    except ValueError:
        return jsonify({'error': 'Invalid gradeId'}), 400

    query = text("SELECT section_id, section FROM public.std_section WHERE class_id=:gradeId")
    result = connection.execute(query, gradeId=gradeId)

    # Convert the result into a list of dictionaries
    section = [{'id': row.section_id, 'name': row.section} for row in result]

    # Return the dropdown values as JSON
    return jsonify(section)

@blueprint.route('/get_subjects/<sectionId>', methods=['GET','POST'])
@login_required
def getSubjectId(sectionId):
    return getSubjects(sectionId)


# fetch user details
@blueprint.route('/user/<id>', methods=['GET'])
@login_required
def users(id):
    user = get_user_by_id(id)
    return user

@blueprint.route('/dropDownSection/<gradeId>',methods=['GET','POST'])
def dropDownSection(gradeId):
    return getSection(gradeId)


@blueprint.route('/hr/edit-user/<id>', methods=['GET'])
@login_required
def edit_user(id):
    return edit_the_user(id)

@blueprint.route('/hr/edit-sub-user/<id>', methods=['GET'])
@login_required
def edit_sub_user(id):
    return edit_the_sub_user(id)    

@blueprint.route('/hr/edit-sub-teacher/<id>', methods=['GET'])
@login_required
def edit_sub_teacher(id):
    return edit_the_sub_teacher(id)

#For checking the duplicate CID
@blueprint.route('/check_cid/<cid>', methods=['GET'])
@login_required
def check_cid(cid):
    print("CID_IS: ", cid)
    cid_check_query = '''SELECT * FROM public."User" WHERE "CID" = %s'''
    cid_check = engine.execute(cid_check_query, cid).fetchone()
    print("CID_check: ", cid_check)
    
    if cid_check:
        # CID exists, return user details
        row_dict = dict(cid_check)
        formatted_dob = row_dict.get("DOB")
        if formatted_dob:
            formatted_dob = formatted_dob.strftime('%Y-%m-%d')
        return jsonify({
            'exists': True,
            'username': row_dict.get('username'),
            'full_name': row_dict.get('full_name'),
            'email': row_dict.get('email'),
            'dob': formatted_dob
        })
    else:
        # CID does not exist
        return jsonify({'exists': False})

    # Return JSON response indicating whether CID exists or not

# updating class teacher modal
@blueprint.route('/updating_clsteacher_hr', methods=['POST'])
@login_required
def updating_the_user():
        return update_editfunction()

# update class teacher
# @blueprint.route('/updating_teacherlist', methods=['POST'])
# @login_required
# def updating_sub_user():
#         return update_editfunction()

# update subject teacher
@blueprint.route('/updating_sub_teacherlist_hr', methods=['POST'])
@login_required
def updating_subject_user():
        return update_edit_subfunction()

# delete 
@blueprint.route('/deleteTeacher/<id>', methods=['POST'])
def delete_user(id):return __DU__.delete_user_by_id(id)

@blueprint.route('/subDeleteTeacher/<id>', methods=['POST'])
def delete_sub_user(id):return __DUU__.delete_sub_user_by_id(id)

@blueprint.route('/pastPayments/<id>', methods=['POST'])
def delete_past_payments(id):
    print("Here Was Reached", id)
    return ___DUU___.past_payments_del_by_id(id)

@blueprint.route('/studentslot_list')
@login_required
def std_slot():

    slot_query = '''SELECT id, class7, class8, class9, class10, class11_arts, class11_com, class11_sci, class12_arts, class12_com, class12_sci FROM public.tbl_std_slots'''
    slot = engine.execute(slot_query).fetchall()
    id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, id).fetchall()
    return render_template('/pages/slotlist.html', slot=slot, result = result) 


# @blueprint.route('/hr/getslots', methods=['POST'])
# @login_required
# def get_slots():
#     return get_std_slot()



#Commands for creating announcement
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import db

#for Announcement
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:root@localhost:5432/announcement" 
    db.app = app
    db.init_app(app) 
    return app
app = create_app()

class Announce(db.Model):
    __tablename__ = "Announcement"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(150))
    content = db.Column(db.String(250), nullable=False)
    created = db.Column(db.DateTime(timezone = True), default=db.func.now())

from uuid import uuid4
from datetime import datetime
from flask import request, render_template

@blueprint.route('/create_announcement', methods=['GET', 'POST'])
@login_required
def create_announcement():  
    user_query = '''SELECT * FROM public.user_detail
    ORDER BY id ASC '''
    users = engine.execute(user_query).fetchall()
    roles = [user['role'] for user in users]       
    title = request.form.get('title')
    subject = request.form.get('subject')
    content = request.form.get('content')
    link = request.form.get('link')
    id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, id).fetchall()
    context = {'result':result}
    
    # Check if required fields are not None
    if title is None or subject is None or content is None:
        # Handle the case where required fields are not provided
        return render_template('createAnnouncement1.html', message='Title, subject, and content are required.', **context)

    ip = request.remote_addr

    # Assuming you have a database connection named 'connection'
    # Assuming the column name is "client_ip" in your Announcement table
    connection.execute('INSERT INTO public."Announcement" ("title", "subject", "content","link") VALUES (%s, %s, %s,%s)',
                   (title, subject, content,link))
    
    return render_template('/createAnnouncement1.html', **context)
    
import os
from random import randint

random_id = randint(000, 999)

@blueprint.route('/settings_hr', methods=['POST','GET'])
def settings_hr():
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    formatted_dob = []
    for row in result:
        row_dict = dict(row)
        if "DOB" in row_dict:
            try:
                row_dict["DOB"] = row_dict["DOB"].strftime('%Y-%m-%d')
            except AttributeError:
                pass
        formatted_dob.append(row_dict)
        formatted_dob = row_dict["DOB"]
    context = {'user_id':user_id, 'result':result, 'formatted_dob':formatted_dob}

    if request.method == 'POST':
        cid = request.form.get('cid')
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        username = request.form.get('username')
        email = request.form.get('email')
        half_photo = request.files.get('half_photo')
        print('Half_Pic:===', half_photo)
        img_url = os.path.join('./app/home/static/uploads/halfphoto/',
                            cid +str(random_id) + half_photo.filename)
        half_photo.save(img_url)
        halfphoto_url = '/static/uploads/halfphoto/'+ cid + \
                str(random_id) + half_photo.filename
        user_detail_insert = '''UPDATE public."User" SET username = %s, 
        email=%s,full_name=%s,"CID"=%s,"DOB"=%s, half_photo=%s WHERE id = %s'''
        connection.execute(user_detail_insert, (username,email,full_name,cid,dob,halfphoto_url,user_id))
        return render_template('/pages/settings.html', **context)
    
    return render_template('/pages/settings.html', **context)

@blueprint.route('/update_pwd', methods=['POST','GET'])
def update_pwd():
    user_id = current_user.id
    if request.method == 'POST':
        provided_password = request.form.get('old_pwd')
        new_password = request.form.get('new_pwd')
        repeat_password = request.form.get('repeat_pwd')

        old_pass_str = '''select password from public."User" where id = %s'''
        db_pass = connection.execute(old_pass_str, user_id).fetchone()
        if db_pass:
            db_password = db_pass[0]
            db_password=bytearray(db_password)
             # Now you can compare old_password with the password provided by the user
            if verify_pass(provided_password, db_password) == True:
                update_pwd = '''UPDATE public."User" SET password = %s WHERE id = %s'''
                connection.execute(update_pwd,hash_pass(repeat_password),user_id)
            else:
               return jsonify({'error': 'Incorrect old password'}), 400
        else:
            print("User with ID {} not found.".format(user_id))

    return "Success"
