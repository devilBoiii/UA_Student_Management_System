from flask import render_template,request,jsonify,session,flash,current_app,redirect
from flask_login import current_user, login_required

from app.class_teacher.service import get_std_in_class, getRatings
from app.subject_teacher import blueprint
from app.admin.service import is_subjectTeacher,is_classTeacher
from app.subject_teacher.service import get_std_subject_teacher,get_std_marks,  store_student_assessment_details,check_exist, term_rating,update_marks,get_std_rating,getRatingValue,load_std_marks,get_std_classes
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

@blueprint.route('/view-std-table/<class_id>/<section_id>')
def view_std_table(class_id, section_id):
    id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s LIMIT 1'''
    result = connection.execute(details_str, id).fetchall()
    subject_str = '''
        SELECT subject_name FROM public.tbl_subjects AS ts INNER JOIN public.user_detail AS ud ON ts.subject_code = ud.subject WHERE ud.user_id = %s AND ud.grade = %s AND ud.section_no = %s 
    	'''
    subject_result = connection.execute(subject_str, id, class_id, section_id).fetchone()
    subject = subject_result[0]
    return render_template('/pages/view-student-table/view-std.html', class_id=class_id, section_id=section_id,result=result, subject = subject)

#Routes For Directing The Users To Their ClassesList
@blueprint.route('/view-std-class-sub')
def view_subj_class_table():
    id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s LIMIT 1'''
    result = connection.execute(details_str, id).fetchall()
    return render_template('/pages/view-student-table/view_class.html', result=result)

#Routes To Display The Classes
@blueprint.route('/display_class_list', methods=['POST', 'GET'])
def displaying_classes():
    return get_std_classes()

@blueprint.route('/view-std-info/<id>')
def view_std_info(id):
    flash("Successfully Submitted!")
    
    std_class = connection.execute(
        'SELECT *, P.id FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        # 'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_present_dzongkhag '
        # 'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_present_gewog '
        # 'inner join public.tbl_village_list as village on village.village_id = P.student_present_village '
        'WHERE P.id =%s',
        id).first()
    user_id=current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s LIMIT 1'''
    result = connection.execute(details_str, user_id).fetchall()
    return render_template('/pages/view-student-table/std_detail.html', std=std_class, result=result)

#@blueprint.route('/edit-subjectmarks/<studentId>/<subject>')
@blueprint.route('/get-student-class-list', methods=['POST'])
def get_student_classList():
    if is_subjectTeacher() or is_classTeacher():
        get_student_in_class = get_std_subject_teacher()
    else:
        get_student_in_class = []
    return get_student_in_class

 # for edit
@blueprint.route('/edit-subjectmarks/<student_id>/<subject>')
def edit_subjectmarks(student_id, subject):
    return get_std_marks(student_id)

#to update the edit button
@blueprint.route('/update-std-marks/<id>', methods=['POST'])
def update_std_marks(id):
    return update_marks(id)

# Route to store student detail
@blueprint.route('/store-std-marks', methods=['POST'])
def store_student_marks():
     # try:
    stdId = request.form.get('std_id')
    print("****STORE ID****",stdId)
    check = check_exist(stdId)
    if check==True:
        return "Error"
    else:
       return store_student_assessment_details(stdId)
       #return storePersonality(getId,subject_teacher_id)

@blueprint.route('/view-std-gradings')
def view_std_gradings():
    return render_template('/pages/view-student-table/view_std_marks.html')

@blueprint.route('/get-std-grade/<id>', methods=['POST'])
def get_student_grade(id):
    if is_subjectTeacher() and is_classTeacher():
        student_grade = get_std_marks(id)
    else:
        student_grade = []
    return student_grade


@blueprint.route('/dropdown_values_rating',methods=['GET','POST'])
def getRatingValues():
    if is_subjectTeacher() or is_classTeacher():
        return getRatingValue()
    else:
        return redirect('login-user') 
    
@blueprint.route('/eget-dropdown-rating', methods=['GET'])
@login_required
def get_dropdown_rating():
    if is_subjectTeacher():
        return getRatings()

@blueprint.route('/edit-std-grade/<id>', methods=['POST'])
def get_student(id):
    if is_subjectTeacher():
        student_grade = get_std_marks(id)
    else:
        student_grade = []
    return student_grade

#@blueprint.route('/view-subjectrating') 
@blueprint.route('/get-subject-marks/<studentId>/<subject>', methods=['GET'])
def load_student_grade(studentId, subject):
    if is_subjectTeacher():
        print("----------------This is the marks given by the subteacher:----;",studentId, subject)

        student_grade = load_std_marks(studentId, subject)

        return student_grade
    else:
        response = {
            "draw": 0,
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": [],
        }
        return jsonify(response)

@blueprint.route('/view-subjectrating/<studentId>/<subject>', methods=['GET'])
def get_student_rating(studentId,subject):
    if is_subjectTeacher():
        student_rate = get_std_rating(studentId,subject)
        print(student_rate,"**Student")
    else:
        student_rate = []
    return jsonify(student_rate)

@blueprint.route('/termrating/<uuid:studentId>', methods=['POST'])
def termrating(studentId):
    term1Scale1 = request.form.get("termratingScale1")
    print("Block1", term1Scale1)
    term1Scale2 = request.form.get("termratingScale2")
    print("Block2", term1Scale2)
    term2Scale1 = request.form.get("termratingScale3")
    print("Block3", term2Scale1)
    term2Scale2 = request.form.get('termratingScale4')
    print("Block4", term2Scale2)
    

    # Assuming you want to get the student ID from the form data
    student_id = request.form.get("std_id")

    # Rest of your code

    return term_rating(studentId, term1Scale1, term1Scale2, term2Scale1, term2Scale2)

    
@blueprint.route('/teaching', methods=['GET'])
@login_required
def teachingList():
    if is_subjectTeacher():
        return getRatings()


import os
from random import randint

random_id = randint(000, 999)

@blueprint.route('/settings_sub', methods=['POST','GET'])
def settings_sub():
    user_id = current_user.id
    details_str = '''SELECT U.*, UD.* FROM public."User" AS U LEFT JOIN public.user_detail as UD on U.id = UD.user_id where U.id = %s LIMIT 1'''
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
        try:
            formatted_dob.append(row_dict)
            formatted_dob = row_dict["DOB"]
        except AttributeError:
            pass
        
    context = {'user_id':user_id, 'result':result, 'formatted_dob':formatted_dob}
    return render_template('/pages/settings_sub.html', **context)