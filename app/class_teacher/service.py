from operator import add
from uuid import uuid4
from flask import Response, request, render_template,jsonify
from app.admin.routes import std_details
from config import Config
from sqlalchemy import create_engine,text,alias
from flask_login import current_user
from datetime import datetime
from random import randint
from app.admin.models import User
import os
import sqlite3 


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
random_id = randint(000, 999)

# for remarks
def insert_student_remarks():
    try:
        percentage = request.form.get('percentage')
        position = request.form.get('position')
        attendance = request.form.get('attendance')
        total_no_stds = request.form.get('total_no_stds')
        percentage2 = request.form.get('percentage2')
        position2 = request.form.get('position2')
        attendance2 = request.form.get('attendance2')
        total_no_stds2 = request.form.get('total_no_stds2')
        std_status = request.form.get('std_status')
        punctuality = request.form.get('punctuality')
        discipline = request.form.get('discipline')
        leadership = request.form.get('leadership')
        supw_grade = request.form.get('supw_grade')
        remarks = request.form.get('remarks')
        student_id = request.form.get('stdId')
        total_percentage = request.form.get('total_percentage')
        total_position = request.form.get('total_position')
        total_attendance = request.form.get('total_attendance')
        grandtotoal_no_stds = request.form.get('grandtotoal_no_stds')

        # Check if std_id exists
        check_query = "SELECT COUNT(*) FROM public.tbl_academic_summary WHERE std_id = %s"
        count = engine.execute(check_query, (student_id,)).scalar()

        if count > 0:
            # If std_id exists, perform an update
            update_query = """
            UPDATE public.tbl_academic_summary SET
                percentage = %s,
                position = %s,
                attendance = %s,
                total_no_stds = %s,
                percentage2 = %s,
                position2 = %s,
                attendance2 = %s,
                total_no_stds2 = %s,
                std_status = %s,
                punctuality = %s,
                discipline = %s,
                leadership = %s,
                supw_grade = %s,
                remarks = %s,
                total_percentage = %s,
                total_position = %s,
                total_attendance = %s,
                grandtotoal_no_stds = %s
            WHERE std_id = %s
            """
            engine.execute(update_query, (
                percentage, position, attendance, total_no_stds, percentage2, position2,
                attendance2, total_no_stds2, std_status, punctuality, discipline, leadership,
                supw_grade, remarks, total_percentage, total_position, total_attendance, grandtotoal_no_stds, student_id
            ))
            print("These is the Std_ID: ", student_id)
            return 'updated'
        else:
            # If std_id does not exist, perform an insert
            insert_query = """
            INSERT INTO public.tbl_academic_summary (
                percentage, position, attendance, total_no_stds, percentage2, position2,
                attendance2, total_no_stds2, std_status, punctuality, discipline, leadership,
                supw_grade, remarks, std_id, total_percentage, total_position, total_attendance, grandtotoal_no_stds
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            engine.execute(insert_query, (
                percentage, position, attendance, total_no_stds, percentage2, position2,
                attendance2, total_no_stds2, std_status, punctuality, discipline, leadership,
                supw_grade, remarks, student_id, total_percentage, total_position, total_attendance, grandtotoal_no_stds
            ))

        print("These is the Std_ID: ", student_id)
        # Commit the transaction to persist the data
        return 'insert'  # Success
    except Exception as e:
        # Handle exceptions and return False on error
        print('Error:', e)
        return False

def search_std():
    student_cid = request.form.get('cid')
    index_number = request.form.get('index_num')
    user_id = current_user.id
    print(user_id,"***USERID")
    class_student_query = """
        SELECT ac.admission_for_class
        FROM public.tbl_students_personal_info AS sp
        INNER JOIN public.tbl_academic_detail AS ac
        ON ac.std_personal_info_id = sp.id
        WHERE sp.student_cid = %s AND ac.index_number = %s
    """
    class_for_student = engine.execute(class_student_query, student_cid, index_number).scalar()
    get_class_query = "SELECT grade FROM public.user_detail WHERE user_id = %s"
    class_value = int(engine.execute(get_class_query, user_id).scalar())

    section_student_query = '''
        SELECT ac.section
        FROM public.tbl_students_personal_info AS sp
        INNER JOIN public.tbl_academic_detail AS ac
        ON ac.std_personal_info_id = sp.id
        WHERE sp.student_cid = %s AND ac.index_number = %s
        '''
    section_for_student = engine.execute(section_student_query, student_cid, index_number).scalar()
    str_queryWithoutClass = """
        SELECT *
        FROM public.tbl_students_personal_info AS sp
        INNER JOIN public.tbl_academic_detail AS ac
        ON ac.std_personal_info_id = sp.id
        WHERE sp.student_cid = %s AND ac.index_number = %s
    """
    addstd_listwithoutClass = connection.execute(str_queryWithoutClass, student_cid, index_number).fetchall()
    checkstatusApproved= 'SELECT status \
        FROM public.tbl_students_personal_info AS sp \
        INNER JOIN public.tbl_academic_detail AS ac \
        ON ac.std_personal_info_id = sp.id \
        WHERE sp.student_cid = %s AND ac.index_number = %s '
    checkStatus=engine.execute(checkstatusApproved,student_cid, index_number).scalar()
    if addstd_listwithoutClass ==[]:
     return {"error": "No data, Either CID or Index is incorrect."}
    if checkStatus!='approved' and class_value == class_for_student:
     return {"error": "This application is not Approved, Please until its approved!"}
    else:
        print(type(class_value), type(class_for_student),'**$')
        if class_value != class_for_student:
         print("You have a different class. Try another Index No.**")
         return {"error": "You have a different class. Try another Index No."}
        # elif section_for_student is not None and class_value == class_for_student:
        #  print("You have already given a section. Try another index.*****")
        #  return {"error": "You have already given a section. Try another index."}
        else: 
         print("INSIDE COndition")
         str_query = """
         SELECT *
         FROM public.tbl_students_personal_info AS sp
         INNER JOIN public.tbl_academic_detail AS ac
         ON ac.std_personal_info_id = sp.id
         WHERE sp.student_cid = %s AND ac.index_number = %s AND ac.admission_for_class = %s
         """
         addstd_list = connection.execute(str_query, student_cid, index_number, class_value).fetchall()
    data = []
    for index, user in enumerate(addstd_list):
        data.append({'sl': index + 1,
                     'id': user.id,
                     'index_number': user.index_number,
                     'student_cid': user.student_cid,
                     'first_name': user.first_name,
                     'last_name': user.last_name,
                     'student_email': user.student_email,
                     'status': user.status,
                     'id': user.id})

    response = {
        "iTotalRecords": len(addstd_list),
        "iTotalDisplayRecords": len(addstd_list),
        "aaData": data,
    }

    return response


def update_tbl_academic():
    index_number = request.form.get('index_num')
    user_id = current_user.id
    
    check_section_query = 'SELECT section FROM public.tbl_academic_detail WHERE index_number = %s'
    section_exists = engine.execute(check_section_query, index_number).scalar()
    
    if section_exists:
        return {"error": "There is already a section assigned for this student. Please check with another Index No."}
    else:
        user_section_query = 'SELECT section_no FROM public.user_detail WHERE user_id = %s'
        user_section = engine.execute(user_section_query, user_id).scalar()
        
        connection.execute('UPDATE public.tbl_academic_detail SET user_id = %s, section = %s WHERE index_number = %s',
                           user_id, user_section, index_number)
    
    return str(user_id)

def checkExist(stdId):
    getUser=current_user.id
    getUsersub='''select ud.subject,ud.grade,ud.section_no,ud.role 
	from public."User" uu 
    join public.user_detail ud  
    on uu.id=ud.user_id where uu.id=%s'''
    getuserSub=connection.execute(getUsersub,getUser).fetchall()
    getData = getuserSub[0]
    print(f'----------------getData-------: ', getData)
    #Retrieve the values of class and section
    class_value = getData['grade']
    section_value = getData['section_no']
    subject_value = getData['subject']
    role=getData['role']
    print(class_value,"class*",section_value,"section*",subject_value,"subject*",role,"*role")
    check_exist_data = '''select count(*) from public.tbl_student_evaluation ev 
	join public."User" uu on ev.subject_teacher_id=uu.id 
	join public.user_detail ud on (uu.id=ud.user_id and ev.subject_teacher_id=ud.user_id)
	join public.tbl_students_personal_info std 
	on ev.student_id=std.id 
	join public.tbl_academic_detail ac 
	on (std.id=ac.std_personal_info_id and ev.student_id=ac.std_personal_info_id)
	join public.class cl on (ac.admission_for_class=cl.class_id 
	and ud.grade=cl.class_id)
	join public.std_section sec on (ud.section_no=sec.section_id and ac.section=sec.section_id)
	join public.section_subject ss on (ud.subject=ss.section_subject_id and ac.section=ss.section_id and ud.section_no=ss.section_id)
	join public.tbl_subjects sub on ss.subject_id=sub.subject_code  
	where cl.class_id =%s and sec.section_id=%s and ss.section_subject_id=%s
	and ev.subject_teacher_id=%s
	and student_id=%s'''
    results = connection.execute(
        check_exist_data,class_value,section_value,subject_value,getUser,stdId).fetchone()[0]
    output = int(results)
    if output > 0:
        return True
    else:
        return False
    
def midtermExamMarks(stdId):
    class_test_one = request.form.get("class_test_1")
    cA1= request.form.get("CA1")
    mid_term = request.form.get("mid_term")
    
def getRatings():
    selectQuery='select "ratingScaleId", "ratingName" from public.tbl_rating_scale'
    runQuery=connection.execute(selectQuery).fetchall()
    data = [{'value': row[0], 'text': row[1]} for row in runQuery]
    print(data,'**UAUUUAUHA')
    return jsonify(data)

def update_tbl_std_evaluation(stdId):
    id = uuid4()
    class_test_one = request.form.get("class_test_1")
    class_test_two = request.form.get("class_test_2")
    mid_term = request.form.get("mid_term")
    annual_exam = request.form.get("annual_exam")
    ca1 = request.form.get('CA1')
    ca2 = request.form.get('CA2')
    rate1= request.form.get('ratingScale1')
    rate2= request.form.get('ratingScale2')
    status_remarks = request.form.get('std_status')
    punctuality = request.form.get('punctuality')
    discipline = request.form.get("discipline")
    social_service = request.form.get("socialservice")
    leadership_quality = request.form.get("leadership")
    socialWork=request.form.get("supw_grade")
    userId=current_user.id
    stdId = stdId
    created_at = datetime.now()
    check_query = """
    SELECT COUNT(*) 
    FROM public.tbl_student_evaluation where subject_teacher_id = %s and student_id = %s
    """
    count = engine.execute(check_query, userId, stdId).scalar()
    print(userId, stdId, 'Count: ',count)
    if count>0:
        update_query = """
            UPDATE public.tbl_student_evaluation SET
                id = %s,
                subject_teacher_id = %s,
                student_id = %s,
                class_test_one = %s,
                class_test_two = %s,
                mid_term = %s,
                annual_exam = %s,
                ca1 = %s,
                ca2 = %s,
                ratingscale1 = %s,
                ratingscale2 = %s,
                status_remarks = %s,
                punctuality = %s,
                discipline = %s,
                social_service = %s,
                leadership_quality = %s,
                created_at = %s,
                supw_grade = %s
            WHERE subject_teacher_id = %s and student_id = %s
            """
        engine.execute(update_query, (id, userId, stdId, class_test_one, class_test_two, mid_term, annual_exam, ca1,ca2, rate1, rate2,status_remarks, punctuality, discipline, 
        social_service,leadership_quality,created_at,socialWork, userId, stdId ))
    else:
        connection.execute("INSERT INTO public.tbl_student_evaluation (id, subject_teacher_id, student_id, class_test_one,  class_test_two, mid_term, annual_exam, ca1,"
        "ca2, \"ratingscale1\", \"ratingscale2\", status_remarks, punctuality, discipline, social_service, leadership_quality, created_at,supw_grade) "
        "VALUES ("
        "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s)",
        (id, userId, stdId, class_test_one, class_test_two, mid_term, annual_exam, ca1,ca2, rate1, rate2,status_remarks, punctuality, discipline, 
        social_service,leadership_quality,created_at,socialWork  ))
    return "ok"


# fetching student list in class
def get_std_in_class():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    user_id = current_user.id
    getClassSection='''select grade,section_no from public."User" uu
    join public.user_detail ud 
    on uu.id=ud.user_id where uu.id=%s AND ud.stream=%s'''
    getclassSects=connection.execute(getClassSection,user_id, 'class_teacher').first()
    class_value = getclassSects[0]  # Grade
    section_value = getclassSects[1]  # Section No.

    search_query = ''
    if search_value:
        search_query = "AND (ac.index_number LIKE '%" + search_value + "%' " \
                       "OR P.student_cid LIKE '%" + search_value + "%' " \
                       "OR P.first_name LIKE '%" + search_value + "%' " \
                       "OR P.student_email LIKE '%" + search_value + "%') "
    str_query = ''' SELECT *, count(*) OVER() AS count_all, P.id FROM
	public.tbl_students_personal_info P JOIN  
	public.tbl_academic_detail ac on P.id=ac.std_personal_info_id
	WHERE ac.admission_for_class = %s AND section=%s ''' + search_query + '''
    LIMIT ''' + row_per_page + ''' OFFSET ''' + row + '''
    '''
    add_std = connection.execute(str_query, class_value,section_value).fetchall()

    data = []
    count = 0
    for index, user in enumerate(add_std):
        data.append({'sl': index + 1,
                     'student_code': user.student_code,
                     'student_cid': user.student_cid,
                     'first_name': user.first_name + ' ' + user.last_name,
                     'student_email': user.student_email,
                     'id': user.id})
        count = user.count_all

    respose_add_std = {
        "draw": int(draw),
        "recordsTotal": count, 
        "recordsFiltered": count,
        "data": data
    }
    return respose_add_std


# fetch student details from database
def get_std_class(id):
    user_id = current_user.id
    user = '''SELECT role FROM public.user_detail where user_id = %s'''
    current_user_role = connection.execute(user, user_id).fetchall()
    extracted_values = [current_user_role[0][0]]
    details_str = '''SELECT * FROM public."User" WHERE id = %s'''
    result = connection.execute(details_str, user_id).fetchall()
    std_class = connection.execute(
        'SELECT *, P.id FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_present_dzongkhag '
        'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_present_gewog '
        'inner join public.tbl_village_list as village on village.village_id = P.student_present_village '
        'WHERE P.id =%s',
        id).first()
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
    return render_template('/pages/add-student/student_detail.html', std=std_class, extracted_values=extracted_values,result=result, section=section, grade=grade, subject=subject, class_teacher=class_teacher, section_og = section_og)


def get_std_result(id):
    std_result = connection.execute(
        'SELECT * FROM public.tbl_academic_summary AS std_result '
        'WHERE std_id = %s',
        id).first()
    # Check if std_result is not None (i.e., a student record was found)
    if std_result:
        # Convert the std_result data to a dictionary (or customize as needed)
        result_dict = {
            'id': std_result.std_id,
            'percentage': std_result.percentage,
            'position': std_result.position,
            'attendance': std_result.attendance,
            'total_no_stds': std_result.total_no_stds,
            'percentage2': std_result.percentage2,
            'position2': std_result.position2,
            'total_no_stds2': std_result.total_no_stds2,
            'attendance2': std_result.attendance2,
            'std_status': std_result.std_status,
            'punctuality': std_result.punctuality,
            'discipline': std_result.discipline,
            'leadership': std_result.leadership,
            'supw_grade': std_result.supw_grade,
            'remarks': std_result.remarks,
            'total_percentage': std_result.total_percentage,
            'total_position': std_result.total_position,
            'total_attendance': std_result.total_attendance,
            'grandtotoal_no_stds': std_result.grandtotoal_no_stds,

        }
        print(result_dict)
        # Return the data as JSON response
        return jsonify(result_dict)
    else:
        # Return a response indicating that no data was found
        return jsonify({'error': 'No data found for the specified ID'})

# fetching student marks given by subject teacher
def get_std_marks(stdId):
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    getUser = current_user.id
    getUsersub='''select ud.subject,ud.grade,ud.section_no,ud.role 
	from public."User" uu 
    join public.user_detail ud  
    on uu.id=ud.user_id where uu.id=%s'''
    getuserSub=connection.execute(getUsersub,getUser).fetchall()
    print(getUser,"****GETUSER******")
    getData = getuserSub[0]
    #Retrieve the values of class and section
    class_value = getData['grade']
    section_value = getData['section_no']
   # subject_value = getData['subject']
    getRole='select ud.subject from public."User" uu \
	join public.user_detail ud on uu.id=ud.user_id where uu.id=%s'
    current_role=connection.execute(getRole,getUser).scalar()
    print(current_role,"**GETCURRENT ROLE")
    search_query = ''
    params = [stdId,class_value,section_value,current_role]

    if search_value:
        search_query += "AND (sub.subject_name ILIKE %s OR "
        search_query += "CAST(class_test_one AS TEXT) ILIKE %s OR "
        search_query += "CAST(mid_term AS TEXT) ILIKE %s OR "
        search_query += "CAST(class_test_two AS TEXT) ILIKE %s OR "
        search_query += "CAST(annual_exam AS TEXT) ILIKE %s OR "
        search_query += "CAST(ca1 AS TEXT) ::TEXT ILIKE %s) "

        search_value = f"%{search_value}%"
        params.extend([search_value] * 6)

    str_query = '''select ev.*, sub.*,ss.*, scl."ratingName" AS ratingname_one, scl1."ratingName" AS ratingname_two, COUNT(*) OVER() AS count_all from public.tbl_student_evaluation ev 
	join public."User" uu on ev.subject_teacher_id=uu.id 
	join public.user_detail ud on (uu.id=ud.user_id and ev.subject_teacher_id=ud.user_id)
	join public.tbl_students_personal_info std  
	on ev.student_id=std.id 
	join public.tbl_academic_detail ac 
	on (std.id=ac.std_personal_info_id and ev.student_id=ac.std_personal_info_id)
	join public.class cl on (ac.admission_for_class=cl.class_id 
	and ud.grade=cl.class_id)
	join public.std_section sec on (ac.admission_for_class=sec.class_id and ud.grade=sec.class_id and cl.class_id=sec.class_id)
	join public.section_subject ss on (ac.section=ss.section_id and ud.section_no=ss.section_id and sec.section_id=ss.section_id)
	join public.tbl_subjects sub on ss.subject_id=sub.subject_code
	join public.tbl_rating_scale scl on ev."ratingscale1"=scl."ratingScaleId"
	join public.tbl_rating_scale scl1 on ev."ratingscale2"=scl1."ratingScaleId"
    WHERE ev.student_id = %s and cl.class_id=%s and sec.section_id=%s and ss.section_subject_id=%s ''' + search_query + '''
    LIMIT %s::integer OFFSET %s::integer'''

    get_std_marks = connection.execute(str_query, *params, row_per_page, row).fetchall()
    print(get_std_marks, "***STDMARKS")
    data = []
    ratings = []
    count = 0
    rows_as_dicts = [dict(row) for row in get_std_marks]
    for index, user in enumerate(rows_as_dicts):
        data.append({
            'sl_no': index + 1,
            'subject': user['subject_name'],
            'class_test_one': user['class_test_one'],
            'ca1': user['ca1'],
            'ratingscale1': user['ratingname_one'],
            'mid_term': user['mid_term'],
            'class_test_two': user['class_test_two'],
            'ca2': user['ca2'],
            'ratingscale2': user['ratingname_two'],
            'annual_exam': user['annual_exam'],
            'student_id': user['student_id'],
            'subjectId': user['section_subject_id'],
            'id': user['id']
        })
        count = user['count_all']

    response = {
        "draw": draw,
        "recordsTotal": count,
        "recordsFiltered": count,
        "data": data,
    }

    print(response, "GETRESPONSE******")

    return jsonify(response)

from sqlalchemy import select, func, cast, Float, case, desc
from sqlalchemy.sql.expression import text

def marks_result(stdId):
    draw = request.args.get('draw')
    row = request.args.get('start')
    userId=current_user.id
    row_per_page = request.args.get('length')
    getUsersub='''select ud.subject,ud.grade,ud.section_no,ud.role 
	from public."User" uu 
    join public.user_detail ud  
    on uu.id=ud.user_id where uu.id=%s'''
    getuserSub=connection.execute(getUsersub,userId).fetchall()
    getData = getuserSub[0]
    #Retrieve the values of class and section
    class_value = getData['grade']
    section_value = getData['section_no']
    # subject_value = getData['subject']
    params = [stdId,class_value,section_value]
    str_query = '''select ev.*, sub.*,ss.*, COUNT(*) OVER() AS count_all from public.tbl_student_evaluation ev 
	join public."User" uu on ev.subject_teacher_id=uu.id 
	join public.user_detail ud on (uu.id=ud.user_id and ev.subject_teacher_id=ud.user_id)
	join public.tbl_students_personal_info std 
	on ev.student_id=std.id 
	join public.tbl_academic_detail ac 
	on (std.id=ac.std_personal_info_id and ev.student_id=ac.std_personal_info_id)
	join public.class cl on (ac.admission_for_class=cl.class_id 
	and ud.grade=cl.class_id)
	join public.std_section sec on (ac.section=sec.section_id and ud.section_no=sec.section_id and cl.class_id=sec.class_id)
	join public.section_subject ss on (ud.subject=ss.subject_id and ss.section_id=sec.section_id)
	join public.tbl_subjects sub on ss.subject_id=sub.subject_code
    WHERE ev.student_id = %s and cl.class_id=%s and sec.section_id=%s 
    LIMIT %s::integer OFFSET %s::integer '''

    get_std_marks = connection.execute(str_query, *params, row_per_page, row).fetchall()
    data = []
    count = 0
    for index, users in enumerate(get_std_marks):
        data.append({
            'sl_no': index + 1,
            'subject': users.subject_name,
            'class_test_one': users.class_test_one,
            'ca1': users.ca1,
            'ratingscale1': users.ratingscale1,
            'mid_term': users.mid_term,
            'class_test_two': users.class_test_two,
            'ca2': users.ca2,
            'ratingscale2': users.ratingscale2,
            'annual_exam': users.annual_exam,
            'student_id': users.student_id,
            'id': users.id
        })

        mid_term_and_ca1_marks = [users.mid_term + users.ca1 for users in get_std_marks if users.subject_name != 'English']
        sorted_mid_term_marks = sorted(mid_term_and_ca1_marks, reverse=True)[:4]     
        english_marks = [users.mid_term + users.ca1 for users in get_std_marks if users.subject_name == 'English']
        english_total = sum(english_marks)  # Sum of English marks
        mid_term_total = sum(sorted_mid_term_marks)  # Sum of mid-term marks
        # Calculate total marks out of 500
        midterm_total_marks = english_total + mid_term_total
        # Calculate percentage
        mid_term_percentage = round((midterm_total_marks / 250) * 100,2)

        annual_and_ca2_marks = [users.annual_exam + users.ca2 for users in get_std_marks if users.subject_name != 'English']
        sorted_annual_exam_marks = sorted(annual_and_ca2_marks, reverse=True)[:4]     
        english_marks = [users.annual_exam + users.ca2 for users in get_std_marks if users.subject_name == 'English']
        english_total = sum(english_marks)  # Sum of English marks
        annual_term_total = sum(sorted_annual_exam_marks)  # Sum of mid-term marks
        # Calculate total marks out of 500
        annual_total_marks = english_total + annual_term_total
        # Calculate percentage
        annual_term_percentage = round((annual_total_marks / 250) * 100, 2)

        grand_total_marks = annual_total_marks + midterm_total_marks
        grand_total_percentage = round((grand_total_marks / 500) * 100,2)
        print("These is the percentage: ",mid_term_percentage,annual_term_percentage,grand_total_percentage )
        #Need to fetch the total number of the student inside the class
        total_std_str='''select count(*)
                        from public.tbl_academic_detail as ad
                        join public.class as c on c.class_id = ad.admission_for_class
                        join public.std_section as ss on ss.section_id = ad.section where c.class_id = %s and ss.section_id = %s'''
        total_stds = connection.execute(total_std_str, class_value,section_value).scalar()

        mid_term_position_str = '''SELECT mid_term_position FROM public.tbl_std_position
                    where std_id = %s and class_id = %s and section_id = %s
                    ;'''
        annual_position_str = '''SELECT annual_position FROM public.tbl_std_position
                    where std_id = %s and class_id = %s and section_id = %s
                    ;'''
        final_position_str = '''SELECT final_position FROM public.tbl_std_position
                    where std_id = %s and class_id = %s and section_id = %s
                    ;'''
        mid_term_position_exe = connection.execute(mid_term_position_str, *params).fetchall()
        annual_position_exe = connection.execute(annual_position_str, *params).fetchall()
        final_position_exe = connection.execute(final_position_str, *params).fetchall()

        # Remove '%' symbol from percentage values
        # mid_term_position = mid_term_position_exe[0][0]
        mid_term_position = "20"
        annual_position = "20"
        final_position = "20"


        count = users.count_all
    if count == 0:
        response = {
            "draw": draw,
            "recordsTotal": 0,
            "recordsFiltered": 0
        }
    else:    
     response = {
            "mid_term_position":mid_term_position,
            "annual_position":annual_position,
            "final_position":final_position,
            "mid_term_percentage":mid_term_percentage,
            "annual_term_percentage":annual_term_percentage,
            "grand_total_percentage":grand_total_percentage,
            "total_stds":total_stds,
            "draw": draw,
            "recordsTotal": count,
            "recordsFiltered": count,
            "data": data,
         }
    return response

def load_std_marks(studentId,subject):
    draw = request.args.get('draw')
    row = request.args.get('start')
    row_per_page = request.args.get('length')
    userId=current_user.id
    getUsersub='''select ud.grade,ud.section_no
	from public."User" uu 
    join public.user_detail ud  
    on uu.id=ud.user_id where uu.id=%s'''
    getuserSub=connection.execute(getUsersub,userId).fetchall()
    getData = getuserSub[0]
    #Retrieve the values of class and section
    class_value = getData['grade']
    section_value = getData['section_no']
    #subject_value = getData['subject']
    #params = [studentId,subject,class_value,section_value]
    # Define aliases for the rating scales
    str_query = text('''select ev.*, sub.*,ud.*, scl."ratingName" AS ratingname_one, scl1."ratingName" AS ratingname_two,  COUNT(*) OVER() AS count_all from public.tbl_student_evaluation ev 
	join public."User" uu on ev.subject_teacher_id=uu.id 
	join public.user_detail ud on (uu.id=ud.user_id and ev.subject_teacher_id=ud.user_id)
	join public.tbl_students_personal_info std 
	on ev.student_id=std.id 
	join public.tbl_academic_detail ac 
	on (std.id=ac.std_personal_info_id and ev.student_id=ac.std_personal_info_id)
	join public.class cl on (ac.admission_for_class=cl.class_id and ud.grade=cl.class_id)
	join public.std_section sec on (ac.admission_for_class=sec.class_id and ud.grade=sec.class_id and cl.class_id=sec.class_id)
	join public.section_subject ss on (ac.section=ss.section_id and ud.section_no=ss.section_id and sec.section_id=ss.section_id)
	join public.tbl_subjects sub on ss.subject_id=sub.subject_code
	join public.tbl_rating_scale scl on ev."ratingscale1"=scl."ratingScaleId"
	join public.tbl_rating_scale scl1 on ev."ratingscale2"=scl1."ratingScaleId"
	where ud.subject=ss.section_subject_id
    and ev.student_id = :student_id and ud.subject=:subject and ac.admission_for_class=:class_value and ud.section_no=:section_value
    LIMIT :row_per_page OFFSET :row ''')
    params = {
    "student_id": studentId,
    "subject": subject,
    "class_value": class_value,
    "section_value": section_value,
    "row_per_page": row_per_page,
    "row": row
    }
    get_std_marks = connection.execute(str_query, **params).fetchall()
    print(get_std_marks, "***STDMARKS")
    data = []
    ratings = []
    count = 0
    # Convert each row into a dictionary with column names as keys
    rows_as_dicts = [dict(row) for row in get_std_marks]
    for index, users in enumerate(rows_as_dicts):
        print(users,'==0000===')
        data.append({
            'sl_no': index + 1,
            'subject': users['subject_name'],
            'class_test_one': users['class_test_one'],
            'ca1': users['ca1'],
            'ratingscale1': users['ratingname_one'],
            'mid_term': users['mid_term'],
            'class_test_two': users['class_test_two'],
            'ca2': users['ca2'],
            'ratingscale2': users['ratingname_two'],
            'annual_exam': users['annual_exam'],
            'student_id': users['student_id'],
            'id': users['id']
        })
        count = users['count_all']

    response = {
        "draw": draw,
        "recordsTotal": count,
        "recordsFiltered": count,
        "data": data,
    }

    print(response, "GETRESPONSE******")
    return response

def view_result(stdId):
    draw = request.args.get('draw')
    row = request.args.get('start')
    row_per_page = request.args.get('length')
    userId=current_user.id
    getUsersub='''select ud.grade,ud.section_no
	from public."User" uu 
    join public.user_detail ud  
    on uu.id=ud.user_id where uu.id=%s'''
    getuserSub=connection.execute(getUsersub,userId).fetchall()
    getData = getuserSub[0]
    #Retrieve the values of class and section
    class_value = getData['grade']
    section_value = getData['section_no']
    #subject_value = getData['subject']
    params = [stdId,class_value,section_value]
    # I dont the use of the following SQL
    getRating =  ''' WITH Ratings AS (
            SELECT
                ev.*,
                ROUND(AVG(ev.punctuality) OVER ()) AS avg_punctuality,
                ROUND(AVG(ev.discipline) OVER ()) AS avg_discipline,
                ROUND(AVG(ev.social_service) OVER ()) AS avg_social_service,
                ROUND(AVG(ev.leadership_quality) OVER ()) AS avg_leadership_quality
            FROM public.tbl_student_evaluation ev
            
        JOIN public."User" uu ON ev.subject_teacher_id = uu.id 
        JOIN public.user_detail ud ON (uu.id = ud.user_id AND ev.subject_teacher_id = ud.user_id)
        JOIN public.tbl_students_personal_info std ON ev.student_id = std.id 
        JOIN public.tbl_academic_detail ac ON (std.id = ac.std_personal_info_id AND ev.student_id = ac.std_personal_info_id)
        JOIN public.class cl ON (ac.admission_for_class = cl.class_id AND ud.grade = cl.class_id)
        JOIN public.std_section sec ON (ac.admission_for_class = sec.class_id AND ud.grade = sec.class_id AND cl.class_id = sec.class_id)
        JOIN public.section_subject ss ON (ud.subject = ss.section_subject_id AND ud.section_no = ss.section_id AND ac.section = ss.section_id AND sec.section_id = ss.section_id)
        WHERE ev.student_id = %s
            AND cl.class_id = %s
            AND sec.section_id = %s
            
        )
        SELECT
            r_punctuality.rating AS punctuality_rating,
            r_discipline.rating AS discipline_rating,
            r_social_service.rating AS social_service_rating,
            r_leadership_quality.rating AS leadership_quality_rating,
            Ratings.*
        FROM Ratings
        JOIN public.rating r_punctuality ON Ratings.avg_punctuality = r_punctuality."ratingId"
        JOIN public.rating r_discipline ON Ratings.avg_discipline = r_discipline."ratingId"
        JOIN public.rating r_social_service ON Ratings.avg_social_service = r_social_service."ratingId"
        JOIN public.rating r_leadership_quality ON Ratings.avg_leadership_quality = r_leadership_quality."ratingId"
    LIMIT %s::integer OFFSET %s::integer
    '''
    ratingValue = connection.execute(getRating, *params, row_per_page, row).fetchall()
    print(ratingValue, "***Rating")

    data = []
    if ratingValue:
        ratings = list(ratingValue[0])  # Generate a list of incremental numbers
    else:
        ratings = []  # Create an empty list for ratings   
    slValue = []
    print(len(ratings),"*len")
    for i in range(1, len(ratings) + 1):
        slValue.append(i)
    array_value = [tuple(slValue)]
    print(ratingValue, "**RATINGVALUE*")
    print(array_value,"array**")
    for slvalue, rating_row in zip(array_value, ratingValue):
        for slno, personal_quality, rating in zip(slvalue, ['Punctuality', 'Discipline', 'Social Service', 'Leadership Quality'], rating_row):
            row_data = {
                'sl': [slno],  # Placeholder for sl values
                'personal': [personal_quality],  # Placeholder for personal qualities
                'rating': [rating]  # Placeholder for rating
            }
            data.append(row_data)  # Append to data list

    # Assign the sl value to the corresponding field in row_data
    # Iterate over personal qualities and rating values and append them separately

    print(data, '**data****')
    if len(ratingValue) == 0:
        response = {
            "draw": draw,
            "recordsTotal": 0,
            "recordsFiltered": 0,
        }
    else:    
     response = {
        "draw": draw,
        "recordsTotal": len(ratingValue),
        "recordsFiltered": len(ratingValue),
        "data": data,
     }
    return jsonify(response)

def get_stds_rating(studentId, subject):
    draw = request.args.get('draw')
    row = request.args.get('start')
    row_per_page = request.args.get('length')
    userId=current_user.id
    getUsersub='''select ud.grade,ud.section_no
	from public."User" uu 
    join public.user_detail ud  
    on uu.id=ud.user_id where uu.id=%s'''
    getuserSub=connection.execute(getUsersub,userId).fetchall()
    getData = getuserSub[0]
    #Retrieve the values of class and section
    class_value = getData['grade']
    section_value = getData['section_no']
    #subject_value = getData['subject']
    params = [studentId,subject,class_value,section_value]

    getRating = '''SELECT 
       r_punctuality.rating AS punctuality_rating,
       r_discipline.rating AS discipline_rating,
       r_social_service.rating AS social_service_rating,
       r_leadership_quality.rating AS leadership_quality_rating   
    FROM public.tbl_student_evaluation ev
    JOIN public.rating r_punctuality ON ev.punctuality = r_punctuality."ratingId"
    JOIN public.rating r_discipline ON ev.discipline = r_discipline."ratingId"
    JOIN public.rating r_social_service ON ev.social_service = r_social_service."ratingId"
    JOIN public.rating r_leadership_quality ON ev.leadership_quality = r_leadership_quality."ratingId"
    join public."User" uu on ev.subject_teacher_id=uu.id 
	join public.user_detail ud on (uu.id=ud.user_id and ev.subject_teacher_id=ud.user_id)
	join public.tbl_students_personal_info std 
	on ev.student_id=std.id 
	join public.tbl_academic_detail ac 
	on (std.id=ac.std_personal_info_id and ev.student_id=ac.std_personal_info_id)
	join public.class cl on (ac.admission_for_class=cl.class_id 
	and ud.grade=cl.class_id)
	join public.std_section sec on (ac.section=sec.section_id and ud.section_no=sec.section_id and cl.class_id=sec.class_id)
	join public.section_subject ss on (ud.subject=ss.section_subject_id and ss.section_id=ss.section_id)
	join public.tbl_subjects sub on ss.subject_id=sub.subject_code 
    where ev.student_id=%s
    and ss.section_subject_id=%s and cl.class_id=%s and sec.section_id=%s
    LIMIT %s::integer OFFSET %s::integer
    '''
    ratingValue = connection.execute(getRating, *params, row_per_page, row).fetchall()
    print(ratingValue, "***Rating")

    data = []
    ratings = list(ratingValue[0])  # Generate a list of incremental numbers
    slValue = []
    print(len(ratings),"*len")
    for i in range(1, len(ratings) + 1):
        slValue.append(i)
    array_value = [tuple(slValue)]
    print(ratingValue, "**RATINGVALUE*")
    print(array_value,"array**")
    for slvalue, rating_row in zip(array_value, ratingValue):
        for slno, personal_quality, rating in zip(slvalue, ['Punctuality', 'Discipline', 'Social Service', 'Leadership Quality'], rating_row):
            row_data = {
                'sl': [slno],  # Placeholder for sl values
                'personal': [personal_quality],  # Placeholder for personal qualities
                'rating': [rating]  # Placeholder for rating
            }
            data.append(row_data)  # Append to data list

    # Assign the sl value to the corresponding field in row_data
    # Iterate over personal qualities and rating values and append them separately

    print(data, '**data****')

    response = {
        "draw": draw,
        "recordsTotal": len(ratingValue),
        "recordsFiltered": len(ratingValue),
        "data": data,
    }
    return response

# fetch student details from database
def get_subject_teacher_info(id):
    sub_teacher = connection.execute('SELECT *, se.id FROM public.tbl_student_evaluation AS se '
                                     'INNER JOIN public."User" AS u ON u.id = se.subject_teacher_id '
                                     'INNER JOIN public.user_detail AS ud ON u.id = ud.user_id '
                                     'INNER JOIN public.tbl_students_personal_info AS sp ON sp.id = se.student_id '
                                     'INNER JOIN public.tbl_academic_detail AS ad ON sp.id = ad.std_personal_info_id '
                                     'WHERE se.id =%s',
                                     id).first()
    return render_template('/pages/add-student/view_std_mark.html', sub_teacher=sub_teacher)

def editTheTeacher(id):
    data = connection.execute('SELECT *, U.id FROM public."User" as U '\
        'inner join public.user_detail as ud on U.id = ud.user_id WHERE U.id=%s', id).fetchone()
   
    final = []
    final.append({'username': data.username,
                    'email': data.email,
                    'subject': data.subject,
                    'grade': data.grade,
                    'section': data.section,
                    'role':data.role,
                    'id': data.id})
    return jsonify({"data": final})

# update the modal
def update_editteacher():
    username = request.form.get('username')
    email = request.form.get('email')
    subject = request.form.get('subject')
    grade = request.form.get('grade')
    section = request.form.get('section')
    id = request.form.get('uu_id')
    connection.execute('UPDATE  public."User" SET username=%s, email=%s WHERE id=%s',
                        username, email, id )
    connection.execute('UPDATE  public.user_detail SET subject=%s, grade=%s, section=%s WHERE user_id=%s',
                        subject, grade,section, id )

    return "success"
    
# delete
def delete_Teacher(id):
    delete=connection.execute('DELETE FROM public."User" WHERE id=%s', id)
    return "done"

   
# delete student list
def students(id):
    delete=connection.execute('DELETE FROM public.tbl_academic_detail WHERE id=%s', id)
    return "done"

# upload time table

# timetable upload
def std_time_table():
    id = uuid4()
    for_class = request.form.get('for_class')
    class_section = request.form.get('class_section')
    timetable_photo = request.files.get('timetable_photo', '')
    img_url = os.path.join('./app/home/static/uploads/timetable/',
                         'for_class' + str(random_id) + timetable_photo.filename)
    timetable_photo.save(img_url)
    timetable_photo_url = '/static/uploads/timetable/'+ 'for_class' + \
            str(random_id) + timetable_photo.filename
    
    classTimeTable=connection.execute('INSERT INTO public.tbl_time_table("id","class_section", "for_class","timetable_photo") VALUES (%s,%s,%s, %s)',
                       (id, for_class,class_section, timetable_photo_url))
    print("**********",classTimeTable)
    return "success"+classTimeTable

def get_time_table():
    std_time_table = connection.execute(
        'SELECT *, t.id FROM public.tbl_time_table AS t WHERE t.id IS NOT NULL ')
    return render_template('/pages/user-management/view_time_table.html', student_timeing_table = std_time_table)


def subjectTeacher():

    user_query = '''SELECT grade, section_no FROM public.user_detail WHERE user_id = %s'''
    user = connection.execute(user_query, (current_user.id)).fetchone()

    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '

    if search_value:
        search_query = f"AND (U.username LIKE '%%{search_value}%%' OR U.email LIKE '%%{search_value}%%' OR UD.role LIKE '%%{search_value}%%')"

    # Modify your SQL query to filter by class_name and section
    str_query = f'''
        SELECT DISTINCT U.username,U.full_name, U.email, sub.subject_name, cl.class_name, sec.section, UD.grade, UD.role, U.type,UD.stream, count(*) OVER() AS count_all, U.id AS user_id
        FROM public."User" AS U
        JOIN public.user_detail AS UD ON U.id = UD.user_id
        LEFT JOIN public.class cl ON cl.class_id = UD.grade
        LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
        LEFT JOIN public.tbl_subjects sub ON sub.subject_code = UD.subject
        WHERE UD.stream = %s
        AND cl.class_id = %s
        AND sec.section_id = %s
    ''' + search_query + f'''
        LIMIT {row_per_page} OFFSET {row}
    '''

    subject_teacher = connection.execute(str_query, ('subject_teacher', user.grade, user.section_no)).fetchall()

    data = []
    count = 0

    for index, user in enumerate(subject_teacher):
        data.append({
            'sl': index + 1,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'subject': user.subject_name,
            'class_name': user.class_name,
            'section': user.section,
            'role': user.role,
            'id': user.user_id
        
        })
        count = user.count_all

    response = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }

    return jsonify(response)

def std_class(id):
    student_details = connection.execute(
        'SELECT *, P.id FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_present_dzongkhag '
        'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_present_gewog '
        'inner join public.tbl_village_list as village on village.village_id = P.student_present_village '
        'WHERE P.id =%s',
        id).first()
    print("ID_IS_THIS: ", id)
    #fetch student marks
    std_marks_query = '''select ev.*, sub.subject_name from public.tbl_student_evaluation ev 
                    join public."User" uu on ev.subject_teacher_id=uu.id 
                    join public.user_detail ud on uu.id=ud.user_id
                    join public.tbl_students_personal_info std on ev.student_id=std.id 
                    join public.tbl_academic_detail ac on std.id=ac.std_personal_info_id
                    join public.class cl on (ac.admission_for_class=cl.class_id and ud.grade=cl.class_id)
                    join public.std_section sec on (ac.section=sec.section_id and ud.section_no=sec.section_id and cl.class_id=sec.class_id)
					join public.tbl_subjects sub on ud.subject=sub.subject_code
                    WHERE ev.student_id = %s '''

    std_marks = connection.execute(std_marks_query, id).fetchall()
    #fetch student's academic details
    std_academic = connection.execute(
        'SELECT * FROM public.tbl_academic_summary WHERE std_id = %s',
        id).first()
    label_mapping = {
        1: 'Satisfactory',
        2: 'Good',
        3: 'Very Good',
        4: 'Outstanding'
        }
    print('leadership_id', std_academic, id )
    
    punctuality_id = int(std_academic['punctuality'])
    discipline_id = int(std_academic['discipline'])
    leadership_id = int(std_academic['leadership'])

    # Convert IDs to labels using the mapping dictionary
    punctuality_label = label_mapping.get(punctuality_id)
    discipline_label = label_mapping.get(discipline_id)
    leadership_label = label_mapping.get(leadership_id)
    return render_template('/pages/add-student/print_result.html', std=student_details, std_marks=std_marks, std_academic=std_academic,punctuality_label=punctuality_label,discipline_label=discipline_label, leadership_label=leadership_label )

def term_rating(stdId, termraringScale1, termratingScale2, termratingScale3, termratingScale4):
    id = uuid4()
    userId = current_user.id
    
    check_query = """
    SELECT COUNT(*) 
    FROM public.term_rating 
    WHERE subject_teacher_id = :userId and student_id = :stdId
    """
    count = engine.execute(text(check_query), userId=userId, stdId=stdId).scalar()
    print(f'Tis is the count: {count} {stdId} {userId}')
    if count > 0:
        update_query = """
        UPDATE public.term_rating SET
            block1 = :termraringScale1,
            block2 = :termraringScale2,
            block3 = :termraringScale3,
            block4 = :termraringScale4
        WHERE student_id = :stdId and subject_teacher_id=:userId
        """
        engine.execute(
            text(update_query),
            termraringScale1 = termraringScale1,
            termraringScale2 = termratingScale2,
            termraringScale3 = termratingScale3,
            termraringScale4 = termratingScale4,
            stdId=stdId,
            userId = userId
        )
        return 'updated'
    
    else:
        # If stdId does not exist, perform an insert
        insert_query = """
        INSERT INTO public.term_rating (id, subject_teacher_id, student_id, Block1, Block2, Block3, Block4)
        VALUES (:id, :userId, :stdId, :termraringScale1, :termratingScale2, :termratingScale3, :termratingScale4)
        """
        engine.execute(
            text(insert_query),
            id=id,
            userId=userId,
            stdId=stdId,
            termraringScale1=termraringScale1,
            termratingScale2=termratingScale2,
            termratingScale3=termratingScale3,
            termratingScale4=termratingScale4
        )
        return 'success'

# fetching student list in class
def get_std_cls_subject_teacher():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    class_id = request.form.get('class_id')
    section_id = request.form.get('section_id')
    print("This is the query:---", class_id, section_id)

    str_query = ''' SELECT *, count(*) OVER() AS count_all, P.id FROM
	public.tbl_students_personal_info P JOIN  
	public.tbl_academic_detail ac on P.id=ac.std_personal_info_id
	WHERE P.id IS NOT NULL
    AND ac.admission_for_class = %s AND section=%s
    LIMIT ''' + row_per_page + ''' OFFSET ''' + row + '''
    '''
    get_std = connection.execute(str_query,class_id,section_id).fetchall()
    print(get_std,'***GETSTD')
    data = []
    count = 0
    for index, user in enumerate(get_std):
        data.append({'sl': index + 1,
                     'student_code': user.student_code,
                     'student_cid': user.student_cid,
                     'first_name': user.first_name+ ' '+user.last_name,
                     'student_email': user.student_email,
                     'id': user.id})
        count = user.count_all
    respose_get_std = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }
    return respose_get_std







