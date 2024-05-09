from multiprocessing.connection import _ConnectionBase
from flask import Blueprint, Flask, app, redirect, request, jsonify
from flask import render_template,jsonify,session,flash,current_app
from flask_login import current_user, login_required
from app.class_teacher import blueprint
from app.class_teacher.service import  insert_student_remarks, search_std, std_class, subjectTeacher, term_rating, update_tbl_academic, get_std_in_class, get_std_class, get_std_marks, update_tbl_std_evaluation,students, std_time_table,get_time_table,get_subject_teacher_info,get_stds_rating,load_std_marks,view_result,marks_result,checkExist,midtermExamMarks, getRatings, get_std_result,get_std_cls_subject_teacher
from app.admin.service import is_classTeacher, is_subjectTeacher
from datetime import datetime
from sqlalchemy import create_engine
import pytz
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
        
# for time table upload
@blueprint.route('/timetable')
@login_required
def get_student_timetable():
    try:
        return render_template('/pages/user-management/timetable.html')
    except Exception as e:
        return "Template Not Created Yet!"
    


@blueprint.route('/stdtimetable')
@login_required
def upload_studenttimetable():
    return render_template('/pages/user-management/view_time_table.html')

@blueprint.route('/add-std-class')
@login_required
def add_student():
    return render_template('/pages/add-student/add_student_class.html')


@blueprint.route('/search-for-std', methods=['POST', 'GET'])
def search_stdList():
    if(is_classTeacher()):
     return search_std()


@blueprint.route('/get-std-list')
@login_required
def get_student_list():
    user_id = current_user.id
    user = '''SELECT role FROM public.user_detail where user_id = %s'''
    current_user_role = connection.execute(user, user_id).fetchall()
    extracted_values = [current_user_role[0][0]]
    details_str = '''SELECT * FROM public."User" WHERE id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    class_str = '''SELECT grade, section_no FROM public.user_detail WHERE user_id = %s AND stream = %s''' 
    class_sec = connection.execute(class_str, user_id, "class_teacher").fetchone()
    class_id = class_sec.grade
    section_id = class_sec.section_no
    subject_text = '''
        SELECT subject_name, cc.class_name, ss.section FROM public.tbl_subjects AS ts 
        INNER JOIN public.user_detail AS ud ON ts.subject_code = ud.subject 
        INNER JOIN public.class AS cc ON cc.class_id = ud.grade
        INNER JOIN public.std_section AS ss ON ss.section_id = ud.section_no
        WHERE ud.user_id = %s AND ud.grade = %s AND ud.section_no = %s 
    	'''
    subject_result = connection.execute(subject_text, user_id, class_id, section_id).fetchone()
    subject = subject_result.subject_name
    grade = subject_result.class_name
    section = subject_result.section
    class_teacher_str = '''SELECT cc.class_name FROM public.class as cc INNER JOIN public.user_detail AS ud 
    ON ud.grade = cc.class_id WHERE ud.user_id = %s AND ud.stream = %s'''
    class_teacher = connection.execute(class_teacher_str, user_id, 'class_teacher').fetchone()[0]
    section_str = '''SELECT ss.section FROM public.std_section as ss INNER JOIN public.user_detail AS ud 
    ON ud.section_no = ss.section_id WHERE ud.user_id = %s AND ud.stream = %s'''
    section_og = connection.execute(section_str, user_id, 'class_teacher').fetchone()[0]
    return render_template('/pages/add-student/student_class_list.html', result=result,extracted_values=extracted_values, subject = subject, grade=grade, section=section, class_teacher = class_teacher, section_og = section_og)

@blueprint.route('/get-subject-teacher-list')
@login_required
def get_subject_teacher_list():
    user_id = current_user.id
    user = '''SELECT role FROM public.user_detail where user_id = %s'''
    current_user_role = connection.execute(user, user_id).fetchall()
    extracted_values = current_user_role[0][0]
    details_str = '''SELECT * FROM public."User" where id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    if '&' in extracted_values:
    # If it does, encapsulate it into a list
        extracted_values = [extracted_values]
    class_str = '''SELECT grade, section_no FROM public.user_detail WHERE user_id = %s AND stream = %s''' 
    class_sec = connection.execute(class_str, user_id, "class_teacher").fetchone()
    class_id = class_sec.grade
    section_id = class_sec.section_no
    subject_text = '''
        SELECT subject_name, cc.class_name, ss.section FROM public.tbl_subjects AS ts 
        INNER JOIN public.user_detail AS ud ON ts.subject_code = ud.subject 
        INNER JOIN public.class AS cc ON cc.class_id = ud.grade
        INNER JOIN public.std_section AS ss ON ss.section_id = ud.section_no
        WHERE ud.user_id = %s AND ud.grade = %s AND ud.section_no = %s 
    	'''
    subject_result = connection.execute(subject_text, user_id, class_id, section_id).fetchone()
    subject = subject_result.subject_name
    grade = subject_result.class_name
    section = subject_result.section    
    return render_template('/pages/add_subject_teacher/subject_teachers.html', result=result, extracted_values=extracted_values, grade=grade, section=section, subject=subject
    )

# @blueprint.route('/get-subject-teacher-list')
# @login_required
# def get_subject_teacher_list():
#     if current_user.is_authenticated:
#         # Assuming you have a User model with 'class_name' and 'section' attributes
#         class_name = current_user.class_name
#         section = current_user.section

#         return render_template('/pages/add_subject_teacher/subject_teachers.html', class_name=class_name, section=section)
#     else:
#         # Handle the case where the user is not authenticated
#         flash('User is not authenticated', 'error')
#         return redirect('/')  # Redirect to the login page or another appropriate action


@blueprint.route('/view-std-result')
@login_required
def view_std_result():
        return render_template('/pages/add-student/view_std_result.html')

# fetch student details
@blueprint.route('/view-std-detail/<id>', methods=['GET'])
@login_required
def view_student_detail(id):
    print(id,'====cponsioleId')
    return get_std_class(id)


@blueprint.route('/view-std-marks/<id>')
@login_required
def view_student_marks(id):
    return get_subject_teacher_info(id)

@blueprint.route('/view-std-class-marks')
@login_required
def view_student_class_marks():

    return render_template('/pages/add-student/class_teacher_assessment.html')

@blueprint.route('/update-std-details', methods=['POST'])
@login_required
def update_std_class():
    if(is_classTeacher()):
        return update_tbl_academic()
    else:
        return "error"

@blueprint.route("/midterm-exam-marks/<stdId>",methods=[''])
@login_required
def midterm_exam_marks(stdId):
    if is_classTeacher():
        return midtermExamMarks()

@blueprint.route('/update-std-evaluation/<stdId>', methods=['POST'])
@login_required   
def update_std_evaluation(stdId):
     # This is a Flask route decorator that maps the URL '/update-std-evaluation/<stdId>' to this function.
    # <stdId> is a dynamic part of the URL, which will be passed as an argument to the function.
    if is_classTeacher():
        # Check if the current user is a class teacher using the is_classTeacher() function.
        # This is a custom authorization function that you likely have defined elsewhere.
        check=checkExist(stdId)
        # Call the checkExist() function, which likely checks if the student with the given stdId exists in the database.
        if check==True:
        # If checkExist() returns True, it means the student already exists, so return an "Error" message.
         return "Error"
        else:
        # If checkExist() returns False, it means the student does not exist, so proceed with updating the student's evaluation.
         return update_tbl_std_evaluation(stdId)

@blueprint.route('/get-dropdown-rating', methods=['GET'])
@login_required
def get_dropdown_rating():
    if is_classTeacher() or is_subjectTeacher():
        return getRatings()
    

@blueprint.route('/student-class-list', methods=['GET','POST'])
@login_required
def student_classList():
    student_in_class = get_std_in_class()
    return student_in_class

# to fetch student result in view button
@blueprint.route('/view_resultlist/<id>', methods=['GET'])
@login_required
def view_student_result(id):
    print(id,'====cponsioleId')
    return get_std_result(id)

@blueprint.route('/get-subject-marks/<stdId>', methods=['POST'])
@login_required
def subject_marks(stdId):
    # This is a Flask route definition using the @blueprint.route decorator.
    # It defines a route accessible at '/get-subject-marks/<stdId>' that accepts POST requests.
    # The '<stdId>' part is a dynamic parameter in the URL, representing the student's ID.
    print("*****IDDDD",stdId)    # Print the student ID for debugging purposes.
    if is_classTeacher():
        # Check if the current user is a class teacher. The is_classTeacher() function
        # likely contains logic to determine the user's role or permissions.
        subject_marks = get_std_marks(stdId)
        # If the user is a class teacher, call the get_std_marks function to retrieve
        # student marks data based on the provided 'stdId'.
    else:
        subject_marks=[]
        # If the user is not a class teacher (or does not have the required permissions),
        # set 'subject_marks' to an empty list.
    return subject_marks 
        # Return the 'subject_marks' data, which can be an empty list if the user is not a class teacher.

@blueprint.route('/view-std-rating/<studentId>/<subject>', methods=['GET'])
def get_student_rating(studentId,subject):
    print(subject,"*SUbjectId")
    if is_classTeacher():
        student_rate = get_stds_rating(studentId,subject)
    else:
        student_rate = []
    return jsonify(student_rate)

@blueprint.route('/view-std-ratingResult/<stdId>',methods=['POST'])
@login_required
def view_std_rating(stdId):
    if is_classTeacher():
        student_rate = view_result(stdId)
    else:
        student_rate = []
    return student_rate

@blueprint.route('/viewResult',methods=['POST'])
def viewResult():
    result=5
    return result

   # for remarks
@blueprint.route('/stdremarks', methods=['POST'])
def stdremarks():
    try:
        print(insert_student_remarks(), "======================")
        if (insert_student_remarks() == 'insert' or insert_student_remarks() == 'updated'):
            return jsonify({'message': 'Data inserted successfully', 'type': str(insert_student_remarks())}), 200
        else:
            return jsonify({'message': 'Data insertion failed'}), 500
    except Exception as e:
        return jsonify({'message': 'Error: ' + str(e)}), 500

@blueprint.route('/load-marksResult/<stdId>', methods=['POST'])
def result_marks(stdId):
    if is_classTeacher():
        student_grade = marks_result(stdId)
    else:
        student_grade=[]
    return jsonify(student_grade)

@blueprint.route('/load-marks/<studentId>/<subject>', methods=['GET'])
@login_required
def load_student_grade(studentId, subject):
    if is_classTeacher():
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

@blueprint.route('class_teacher/subjectTeacherList', methods=['GET', 'POST'])
@login_required
def sub_teacherList():
    return subjectTeacher()

# delete student list
@blueprint.route('/deleteStudentList/<id>', methods=['POST'])
def delete_student(id):
    return students(id)

# ädding time table
@blueprint.route('/save-timetable', methods=['POST'])
def student_timetable():
    return std_time_table()

# fetch time table
@blueprint.route('/view-time-table<id>', methods=['POST'])
def std_timetable():
        return get_time_table()


@blueprint.route('/print-page/<id>')
def print_page(id):
    return std_class(id)

@blueprint.route('/termrating/<uuid:studentId>', methods=['POST'])
def termrating(studentId):
    term1Scale1 = request.form.get("termratingScale1")
    term1Scale2 = request.form.get("termratingScale2")
    term2Scale1 = request.form.get("termratingScale3")
    term2Scale2 = request.form.get('termratingScale4')
    # Assuming you want to get the student ID from the form data
    # student_id = request.form.get("std_id")
    # return "HERE"
    # Rest of your code
    return term_rating(studentId, term1Scale1, term1Scale2, term2Scale1, term2Scale2)

import os
from random import randint

random_id = randint(000, 999)

@blueprint.route('/settings_class', methods=['POST','GET'])
def settings_class():
    user_id = current_user.id
    user = '''SELECT role FROM public.user_detail where user_id = %s'''
    current_user_role = connection.execute(user, user_id).fetchall()
    extracted_values = [current_user_role[0][0]]
    details_str = '''SELECT * FROM public."User" WHERE id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    if request.method == 'POST':
        cid = request.form.get('cid')
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        username = request.form.get('username')
        email = request.form.get('email')
        half_photo = request.files.get('half_photo')
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
    context = {'user_id':user_id, 'result':result, 'formatted_dob':formatted_dob, 'extracted_values':extracted_values}
    return render_template('/pages/settings_class.html', **context)

#Routes For Directing The Users To Their ClassesList
@blueprint.route('/view-std-class')
def view_class_table():
    id = current_user.id
    details_str = '''SELECT * FROM public."User" where id = %s'''
    class_teacher_str = '''SELECT cc.class_name FROM public.class as cc INNER JOIN public.user_detail AS ud 
    ON ud.grade = cc.class_id WHERE ud.user_id = %s AND ud.stream = %s'''
    class_teacher = connection.execute(class_teacher_str, id, 'class_teacher').fetchone()[0]
    section_str = '''SELECT ss.section FROM public.std_section as ss INNER JOIN public.user_detail AS ud 
    ON ud.section_no = ss.section_id WHERE ud.user_id = %s AND ud.stream = %s'''
    section = connection.execute(section_str, id, 'class_teacher').fetchone()[0]
    result = connection.execute(details_str, id).fetchall()
    user = '''SELECT role FROM public.user_detail where user_id = %s'''
    current_user_role = connection.execute(user, id).fetchall()
    extracted_values = [current_user_role[0][0]]
    print("YOYO:", extracted_values)
    return render_template('/pages/view_class_tbl.html', result=result, extracted_values=extracted_values, class_teacher=class_teacher, section=section)

@blueprint.route('/display_class_list', methods=['POST', 'GET'])
def displaying_classes():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']

    user_id = current_user.id
    class_query = '''SELECT DISTINCT U.id, U.type, UD.role, UD.stream, CC.class_id, CC.class_name, S.section_id, S.section, TS.subject_code, TS.subject_name 
    FROM public."User" AS U 
    LEFT JOIN public.user_detail AS UD ON U.id = UD.user_id 
    LEFT JOIN public.class AS CC ON CC.class_id = UD.grade 
    LEFT JOIN public.std_section AS S ON S.section_id = UD.section_no 
    LEFT JOIN public.tbl_subjects AS TS ON TS.subject_code = UD.subject 
    WHERE U.id = %s AND UD.stream = %s
    '''
    get_class = connection.execute(class_query, user_id, 'subject_teacher').fetchall()
    data = []
    count = 0
    print("USERID: ", user_id)
    for index, user in enumerate(get_class):
        data.append({
            'sl': index + 1,
            'type':user.stream,
            'class_name':user.class_name,
            'section':user.section,
            'subject_name':user.subject_name,
            'id': user.class_name,
            'class_id': user.class_id,
            'section_id': user.section_id
        })
        print(f'These are the data details-----: {data}')

        respose_get_std = {
                "draw": int(draw),
                "iTotalRecords": count,
                "iTotalDisplayRecords": count,
                "aaData": data
            }
    return respose_get_std

@blueprint.route('/view-std-table-cls/<class_id>/<section_id>')
def view_std_table_cls(class_id, section_id):
    id = current_user.id
    user = '''SELECT role FROM public.user_detail where user_id = %s'''
    current_user_role = connection.execute(user, id).fetchall()
    extracted_values = [current_user_role[0][0]]
    details_str = '''SELECT * FROM public."User" where id = %s'''
    result = connection.execute(details_str, id).fetchall()
    subject_str = '''
        SELECT subject_name, cc.class_name, ss.section FROM public.tbl_subjects AS ts 
        INNER JOIN public.user_detail AS ud ON ts.subject_code = ud.subject 
        INNER JOIN public.class AS cc ON cc.class_id = ud.grade
        INNER JOIN public.std_section AS ss ON ss.section_id = ud.section_no
        WHERE ud.user_id = %s AND ud.grade = %s AND ud.section_no = %s 
    	'''
    subject_result = connection.execute(subject_str, id, class_id, section_id).fetchone()
    print("THIS_IS_ID: ", subject_result, subject_result.class_name)
    subject = subject_result.subject_name
    grade = subject_result.class_name
    section = subject_result.section
    class_teacher_str = '''SELECT cc.class_name FROM public.class as cc INNER JOIN public.user_detail AS ud 
    ON ud.grade = cc.class_id WHERE ud.user_id = %s AND ud.stream = %s'''
    class_teacher = connection.execute(class_teacher_str, id, 'class_teacher').fetchone()[0]
    section_str = '''SELECT ss.section FROM public.std_section as ss INNER JOIN public.user_detail AS ud 
    ON ud.section_no = ss.section_id WHERE ud.user_id = %s AND ud.stream = %s'''
    section_og = connection.execute(section_str, id, 'class_teacher').fetchone()[0]
    return render_template('/pages/view-std.html', class_id=class_id, section_id=section_id,result=result, extracted_values=extracted_values, subject=subject, grade=grade, section=section, section_og=section_og, class_teacher=class_teacher)

@blueprint.route('/view-std-cls-info/<id>')
def view_std_cls_info(id):
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
    details_str = '''SELECT * FROM public."User" WHERE id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    user = '''SELECT role FROM public.user_detail where user_id = %s'''
    current_user_role = connection.execute(user, user_id).fetchall()
    extracted_values = [current_user_role[0][0]]
    class_teacher_str = '''SELECT cc.class_name FROM public.class as cc INNER JOIN public.user_detail AS ud 
    ON ud.grade = cc.class_id WHERE ud.user_id = %s AND ud.stream = %s'''
    class_teacher = connection.execute(class_teacher_str, user_id, 'class_teacher').fetchone()[0]
    section_str = '''SELECT ss.section FROM public.std_section as ss INNER JOIN public.user_detail AS ud 
    ON ud.section_no = ss.section_id WHERE ud.user_id = %s AND ud.stream = %s'''
    section_og = connection.execute(section_str, user_id, 'class_teacher').fetchone()[0]
    return render_template('/pages/std_detail.html', std=std_class, result=result, extracted_values=extracted_values, section_og=section_og, class_teacher=class_teacher)