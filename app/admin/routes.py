from flask import jsonify, render_template,request,redirect,session,flash,current_app
from flask_login import login_required
from app.HR.service import class_teacher, subjectTeacher
from app.admin import blueprint
from app.admin.service import delete_slot, deleteadminuser, deleteFeedback,get_std_id, get_std_slot, save_std_slot, save_user_table,  application_update, all_users, is_admin,is_classTeacher, is_subjectTeacher, get_user_by_id, all_std, save_user_table_list, update_std_slot, user_quries, edit_the_user, update_editfunction,getClasses,getSection, save_subTeacher, update_edit_subfunction,is_human_resource
from app.admin.service import deleteUser as __DU__
from flask_login import current_user
from datetime import datetime
import pytz
from flask import make_response
import pdfkit
from sqlalchemy import create_engine
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()

@blueprint.before_request
def check_session_timeout():
    if 'last_activity' in session:
        last_activity_time = session['last_activity']
        last_activity_time = last_activity_time.replace(tzinfo=pytz.UTC)
        current_time = datetime.now(pytz.utc)

        # Calculate the duration of inactivity
        inactivity_duration = current_time - last_activity_time
        print(inactivity_duration,"***********INACTIVITYinHr **********",current_time,"**CURRENTHr",last_activity_time,"LAST ACTIVITYHr*")
        if inactivity_duration >  current_app.config['PERMANENT_SESSION_LIFETIME']:
            # Perform actions for session timeout (e.g., log out the user)
            # logout_user() or session.clear()
            print("***********session time out **********")
            flash('Your session has timed out. Please log in again.')

        # Update the last activity time to the current time
        session['last_activity'] = current_time


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
@blueprint.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authenticated and current_user.id is not None:
        if is_admin():
            id = current_user.id
            try:
                educators = connection.execute(
            "SELECT count(UD.id) from public.user_detail AS UD where UD.role = 'subject_teacher' OR UD.role = 'class_teacher'").fetchone()[0]
                sup_staff = connection.execute(
            "SELECT count(UD.id) from public.user_detail AS UD where UD.role != 'subject_teacher' AND UD.role != 'class_teacher'").fetchone()[0]
                total_application = connection.execute(
            "SELECT count(sp.id) from public.tbl_students_personal_info AS sp").fetchone()[0]
                accepted_application = connection.execute(
            "SELECT count(sp.id) from public.tbl_students_personal_info AS sp where sp.status = 'approved'").fetchone()[0]
                male_std = connection.execute("SELECT count(sp.id) from public.tbl_students_personal_info AS sp where sp.status = 'approved' and sp.gender = 'Male';").fetchone()[0]
                female_std = connection.execute("SELECT count(sp.id) from public.tbl_students_personal_info AS sp where sp.status = 'approved' and sp.gender = 'Female';").fetchone()[0]
                female_per = round((female_std/accepted_application) * 100,2)
                male_per = round((male_std/accepted_application) * 100,2)
                details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
                result = connection.execute(details_str, id).fetchall()
            except ZeroDivisionError:
                pass
            std_results_str = '''
                SELECT * FROM public.tbl_academic_summary AS tas LEFT JOIN public.tbl_student_evaluation AS tse ON tas.std_id = tse.student_id
                LEFT JOIN public.tbl_students_personal_info AS tsp ON tsp.id = tas.std_id
            '''
            std_result = connection.execute(std_results_str).fetchall()
            print("This is the data:", std_result)
            context = {'educators':educators, 'sup_staff':sup_staff, 'total_application':total_application, 'accepted_application':accepted_application, 'male_std':male_std, 'female_std':female_std, 'male_per':male_per, 'female_per':female_per, 'result':result}
            return render_template('admin.html', **context)
        elif (is_classTeacher()):
            id = current_user.id
            results = connection.execute(
            'SELECT *, c.class_name, ss.section, s.subject_name FROM public.user_detail AS UD join public.class as c on c.class_id = UD.grade join public.std_section as ss on ss.section_id = UD.section_no join public.tbl_subjects as s on s.subject_code = UD.subject where UD.stream = %s AND UD.user_id = %s', 'class_teacher',id ).fetchall()
            str_qry=[]
            try:
                str_q = results[0]
                str_qry.append(str_q)
            except IndexError:
                pass
            class_teacher = str_qry[0][-3]
            subject_name = str_qry[0][-1]
            section_og = str_qry[0][-2]
            total_std = connection.execute(
            'SELECT count(ad.student_code) FROM public.user_detail AS UD join public.tbl_academic_detail as ad on ad.admission_for_class = UD.grade and ad.section = UD.section_no where UD.stream = %s AND UD.user_id = %s','class_teacher', id ).fetchone()[0]
            total_male = connection.execute("SELECT count(*) FROM public.user_detail AS UD join public.tbl_academic_detail as ad on ad.admission_for_class = UD.grade and ad.section = UD.section_no join public.tbl_students_personal_info as tsp on tsp.id = ad.std_personal_info_id where UD.stream = %s AND UD.user_id = %s and tsp.gender = 'Male'",'class_teacher', id).fetchone()[0]
            total_female = connection.execute("SELECT count(*) FROM public.user_detail AS UD join public.tbl_academic_detail as ad on ad.admission_for_class = UD.grade and ad.section = UD.section_no join public.tbl_students_personal_info as tsp on tsp.id = ad.std_personal_info_id where UD.stream = %s AND UD.user_id = %s and tsp.gender = 'Female'",'class_teacher', id).fetchone()[0]

            details_str = '''SELECT * FROM public."User" where id = %s'''
            result = connection.execute(details_str, id).fetchall()
            user = '''SELECT role FROM public.user_detail where user_id = %s'''
            current_user_role = connection.execute(user, id).fetchall()
            extracted_values = []
            try:
                extracted = current_user_role[0][0]
                extracted_values.append(extracted)
            except IndexError:
                pass
            print('Herebro!!', extracted_values, id)
            context = {'subject_name':subject_name,'section_og':section_og,'class_teacher':class_teacher, 'total_std':total_std, 'total_male':total_male, 'total_female':total_female,'result':result, 'extracted_values':extracted_values}
            return render_template('class_teacherDash.html', **context)
        elif is_subjectTeacher():
            id = current_user.id
            total_class = connection.execute(
            'SELECT count(grade) FROM public.user_detail AS UD where UD.user_id = %s', id ).fetchone()[0]
            print("---------This is the total class-----------",id, total_class)
            details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s LIMIT 1'''
            result = connection.execute(details_str, id).fetchall()
            context = {'total_class':total_class, 'result':result}
            return render_template('subject_teacherDash.html', **context)
        else:
            id = current_user.id
            educators = connection.execute(
            "SELECT count(UD.id) from public.user_detail AS UD where UD.role = 'subject_teacher' OR UD.role = 'class_teacher'").fetchone()[0]
            sup_staff = connection.execute(
            "SELECT count(UD.id) from public.user_detail AS UD where UD.role != 'subject_teacher' AND UD.role != 'class_teacher'").fetchone()[0]
            total_application = connection.execute(
            "SELECT count(sp.id) from public.tbl_students_personal_info AS sp").fetchone()[0]
            accepted_application = connection.execute(
            "SELECT count(sp.id) from public.tbl_students_personal_info AS sp where sp.status = 'approved'").fetchone()[0]
            male_std = connection.execute("SELECT count(sp.id) from public.tbl_students_personal_info AS sp where sp.status = 'approved' and sp.gender = 'Male';").fetchone()[0]
            female_std = connection.execute("SELECT count(sp.id) from public.tbl_students_personal_info AS sp where sp.status = 'approved' and sp.gender = 'Female';").fetchone()[0]
            female_per = round((female_std/accepted_application) * 100,2)
            male_per = round((male_std/accepted_application) * 100,2)
            details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
            result = connection.execute(details_str, id).fetchall()
            context = {'educators':educators, 'sup_staff':sup_staff, 'total_application':total_application, 'accepted_application':accepted_application, 'male_std':male_std, 'female_std':female_std, 'male_per':male_per, 'female_per':female_per, 'result':result}
        
            return render_template('hr_dashboard.html',  **context)
    else:
        # Handle the case when the user is not authenticated
        # You can redirect to the login page or display an error message
        return redirect('login-user')
    
@blueprint.route('/admin-add-user')
@login_required
def admin_add_user():
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    context = {'result':result}
    return render_template('/pages/user-management/add-new-user.html', **context)

@blueprint.route('/admin-user-list')
@login_required
def admin_user_list():
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    context = {'result':result}
    return render_template('/pages/user-management/user-list.html', **context)


@blueprint.route('/admin-typography')
@login_required
def admin_typography():
    return render_template('/pages/ui-features/typography.html')


@blueprint.route('/admin-student-application-list')
@login_required
def admin_std_app_list():
    user_id=current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    return render_template('/pages/student-applications/student_application_list.html', result=result)

@blueprint.route('/admin-basic-tables')
@login_required
def admin_basic_tables():
    return render_template('/pages/tables/basic-table.html')

@blueprint.route('/feedback')
@login_required
def usrfeedback():
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    return render_template('/pages/user-feedback/feedback.html', result = result)

@blueprint.route('/admin-icons')
@login_required
def admin_icons():
    return render_template('/pages/icons/mdi.html')
 

@blueprint.route('/admin-login')
@login_required
def admin_login():
    return render_template('/pages/samples/login.html')


@blueprint.route('/admin-register')
@login_required
def admin_register():
    return render_template('/pages/samples/register.html')


@blueprint.route('/admin-error-404')
def admin_error_404():
    return render_template('/pages/samples/error-404.html')


@blueprint.route('/admin-error-500')
def admin_error_500():
    return render_template('/pages/samples/error-500.html')


@blueprint.route('/admin-documentation')
def admin_documentation():
    return render_template('/pages/documentation/documentation.html')


@blueprint.route('/users', methods=['POST'])
def usersList():
    if(is_admin()):
        users = all_users()
    else:
        users = []
    return users
    

# For storing admin details
@blueprint.route("/save-user", methods=['POST'])
def save_user():
        password = request.form['password']
        user_id = save_user_table(password)
        print(user_id,"***USERID")
        return save_user_table_list(user_id,password)

@blueprint.route('/dropDownClass', methods=['GET','POST'])
def getClassId():
    return getClasses()

# fetch user details
@blueprint.route('/user/<id>', methods=['GET'])
def users(id):
    user = get_user_by_id(id)
    return user

@blueprint.route('/dropDownSection/<gradeId>',methods=['GET','POST'])
def dropDownSection(gradeId):
    return getSection(gradeId)


@blueprint.route('/users-std', methods=['GET','POST'])
def stdList():
    if(is_admin()):
        users_st = all_std()
    else:
        users_st = []

    return users_st

@blueprint.route('/users-std-hr', methods=['GET','POST'])
def stdListHR():
    if(is_human_resource()):
        users_st = all_std()
    else:
        users_st = []

    return users_st

# fetch student details
@blueprint.route('/std-detials/<id>', methods=['GET'])
@login_required
def std_details(id):
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
    return render_template('/pages/student-applications/studentinfo.html', std=std_details, std_info=std_info, result=result)

@blueprint.route('/update-status', methods=['POST'])
def update_app_status():
    if(is_admin()):
        return application_update()
    else:
        return "Failed"

# user doubt
@blueprint.route('/users-queries', methods=['POST'])
def queryList():
    if(is_admin()):
        users_query = user_quries()
    else:
        users_query = []

    return users_query

@blueprint.route('/getclassteacher')
@login_required
def getclassteacher():
     # Example using SQLAlchemy's text() for executing raw SQL
    grade_query = '''SELECT * FROM public.class'''
    grades = engine.execute(grade_query).fetchall()
    print(grades, "==================")

    # If you need user_id for getSection, you can use current_user.id again
    subject_query = '''SELECT * FROM public.tbl_subjects'''
    subjects = engine.execute(subject_query).fetchall()
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    return render_template('/pages/teacher/getclassteacher.html', grades=grades, subjects=subjects, result=result)

@blueprint.route('/add_classTeacher')
@login_required
def add_classTeacher():
    user_query = '''SELECT * FROM public.user_detail
    ORDER BY id ASC '''
    users = engine.execute(user_query).fetchall()
    roles = [user['role'] for user in users]   
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()     
    return render_template('/pages/teacher/add-class-teacher.html', roles=roles, result=result)

#saving class teacher and subject teacher
@blueprint.route("/save_sub_teacher", methods = ['GET','POST'])
@login_required
def save_teacher():
    return save_subTeacher()

@blueprint.route('/add_subject_teacher', methods=['GET','POST'])
@login_required
def add_subject_teacher():
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    return render_template('/pages/teacher/add-subject-teacher.html', result=result)

# edit modal
@blueprint.route('/edit-user/<id>', methods=['GET'])
@login_required
def edit_user(id):
    return edit_the_user(id)

# updating modal
@blueprint.route('/updating_users', methods=['POST'])
@login_required
def updating_the_user():
    if(is_admin()):
        return update_editfunction()
    else:
        return "errorFound"

@blueprint.route('/deleteUser/<id>', methods=['POST'])
def delete_user(id):
    success = __DU__.delete_user_by_id(id)
    if success=="done":
        return jsonify({"message": "User deleted successfully"})
    else:
        return jsonify({"error": "Failed to delete user"})
    
    
@blueprint.route('/delete_list/<id>', methods=['POST'])
def delete_user_list(id):
    success = deleteadminuser.delete_admin_user(id)

    if success == "done":
        return jsonify({"message": "User deleted successfully"})
    else:
        return jsonify({"error": "Failed to delete user: {success}"})

        
@blueprint.route('/class-teacher-list', methods=['POST'])
@login_required
def cl_teacherList():
    return class_teacher()   

@blueprint.route('/getsubjectteacher')
@login_required
def getsubjectteacher():
    # Example using SQLAlchemy's text() for executing raw SQL
    grade_query = '''SELECT * FROM public.class'''
    grades = engine.execute(grade_query).fetchall()
    print(grades, "==================")

    # If you need user_id for getSection, you can use current_user.id again
    subject_query = '''SELECT * FROM public.tbl_subjects'''
    subjects = engine.execute(subject_query).fetchall()

    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    return render_template('/pages/teacher/getsubteacher.html', grades=grades, subjects=subjects, result=result) 

@blueprint.route('/admin/getsubteacher',methods=['POST'])
@login_required
def getsubteacher():
    return subjectTeacher()

# update subject teacher
@blueprint.route('/updating_sub_teacherlist', methods=['POST'])
@login_required
def updating_subject_user():
        return update_edit_subfunction()
# @blueprint.route('/print', methods=['GET'])
# @login_required
# def print_page():
#     return render_template('/pages/student-applications/print.html')

@blueprint.route('/print/<id>', methods=['GET'])
@login_required
def print_page(id):
   return get_std_id(id)

@blueprint.route('student-slot')
@login_required
def student_slot():
   user_id = current_user.id
   details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
   result = connection.execute(details_str, user_id).fetchall()
   return render_template("/pages/studentslot.html", result=result)

@blueprint.route('/std_slot', methods=['POST'])
def slot():
    # You can return a JSON response if needed
    return save_std_slot()

@blueprint.route('slot-list')
@login_required
def student_slot_list():
   user_id = current_user.id
   details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
   result = connection.execute(details_str, user_id).fetchall()
   return render_template("/pages/studentslotlist.html", result=result)

@blueprint.route('/admin/getslots', methods=['POST'])
@login_required
def get_slots():
    return get_std_slot()

@blueprint.route('admin/updateslot', methods=['POST'])
@login_required
def update_slot():
    return update_std_slot()

# # delete 
# @blueprint.route('/admin/deleteslot/<id>', methods=['POST'])
# def delete_slot(id):return __DU__.delete_slot(id)

# @blueprint.route('/admin/deleteslot/<slotId>', methods=['POST'])
# def deleteslot(slotId):

#     # Return a JSON response to the client
#     return delete_slot(slotId)

@blueprint.route('/admin/deleteslot/<slotId>', methods=['POST'])
def deleteslot(slotId):
    # Your existing code to delete the slot using the provided id (slotId)
    # ...

    # Return a JSON response to the client
    return delete_slot.delete_slot(slotId)

@blueprint.route('/deleteFeedback/<id>', methods=['POST'])
def delete_feedback(id):
    return deleteFeedback(id)


import os
from random import randint

random_id = randint(000, 999)

@blueprint.route('/settings_admin', methods=['POST','GET'])
def settings():
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
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
    formatted_dob = []
    for row in result:
        row_dict = dict(row)
        if "DOB" in row_dict:
            try:
                row_dict["DOB"] = row_dict["DOB"].strftime('%Y-%m-%d')
            except AttributeError:
                # Handle the case where DOB is not in the expected format
                pass
        formatted_dob.append(row_dict)
        formatted_dob = row_dict["DOB"]
    context = {'user_id':user_id, 'result':result, 'formatted_dob':formatted_dob}
    return render_template('/pages/settings_admin.html', **context)