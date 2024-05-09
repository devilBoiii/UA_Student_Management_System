from cgitb import text
from flask import request, render_template,jsonify
from config import Config
from sqlalchemy import create_engine
from datetime import datetime
from flask_login import current_user
from uuid import uuid4,UUID



engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()


# fetching student list in class
def get_std_subject_teacher():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    class_id = request.form.get('class_id')
    section_id = request.form.get('section_id')
    # user_id = current_user.id
    #Retrieve the values of class and section
    # getClassSection='''select grade,section_no from public."User" uu
    # join public.user_detail ud 
    # on uu.id=ud.user_id where uu.id=%s'''
    # getclassSects=connection.execute(getClassSection,user_id).first()
    # class_value = getclassSects[0]  # Grade
    # section_value = getclassSects[1]  # Section No.
    # print(f'This is the Class Value: {class_value} /n This is the Section Value: {user_id}')

    search_query = ' '
    if (search_value != ''):
        search_query = "AND (A.student_code LIKE '%%" + search_value + "%%' " \
            "OR P.student_cid LIKE '%%" + search_value + "%%' "\
            "OR P.first_name LIKE '%% " + search_value+"%%') "\
            "OR P.student_email LIKE '%%" + search_value + "%%' "
    str_query = ''' SELECT *, count(*) OVER() AS count_all, P.id FROM
	public.tbl_students_personal_info P JOIN  
	public.tbl_academic_detail ac on P.id=ac.std_personal_info_id
	WHERE P.id IS NOT NULL ''' + search_query + '''
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

def get_std_classes():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']

    user_id = current_user.id
    class_query = '''SELECT U.id, U.username, UD.role,C.class_id, C.class_name,ss.section,TS.subject_name, UD.section_no
            FROM public."User" as U 
            left join public.user_detail as UD on U.id = UD.user_id
            left join public.class as C on UD.grade = C.class_id
            left join public.section_subject as SSub on SSub.section_subject_id = UD.subject
			left join public.std_section as ss on ss.section_id = UD.section_no
            left join public.tbl_subjects as TS on TS.subject_code = UD.subject where U.id = %s'''
    get_class = connection.execute(class_query, (user_id,)).fetchall()
    data = []
    count = 0
    for index, user in enumerate(get_class):
        data.append({
            'sl': index + 1,
            'class_name':user.class_name,
            'section':user.section,
            'subject_name':user.subject_name,
            'id': user.class_name,
            'class_id': user.class_id,
            'section_id': user.section_no
        })
        print(f'These are the data details-----: {data}')

        respose_get_std = {
                "draw": int(draw),
                "iTotalRecords": count,
                "iTotalDisplayRecords": count,
                "aaData": data
            }
    return respose_get_std

def update_marks(id):
    class_test_one = request.form.get('editclass_test_1')
    CA1 = request.form.get('editCA1')
    mid_term = request.form.get('editmid_term')
    ratingScale1 = request.form.get('ratingScale1')
    class_test_two = request.form.get('editclass_test_2')
    CA2 = request.form.get('editCA2')
    annual_exam = request.form.get('editannual_exam')
    ratingScale2 = request.form.get('ratingScale2') 
    userId=current_user.id
    print("Reached Here!!")
    check_query = """
    SELECT COUNT(*) 
    FROM public.tbl_student_evaluation where subject_teacher_id = :userId AND student_id = :id
    """
    count = engine.execute(check_query, userId=userId, id=id).scalar()
    print(userId, id, 'Count: ',count)
    if count>0:
        connection.execute('UPDATE public."tbl_student_evaluation" SET class_test_one=%s, ca1=%s, mid_term=%s, "ratingscale1"=%s, class_test_two=%s, ca2=%s, annual_exam=%s, "ratingscale2"=%s WHERE student_id=%s',
                       (class_test_one, CA1, mid_term, ratingScale1, class_test_two, CA2, annual_exam, ratingScale2, id))
        return ("Updated!")
    else:
        query = 'UPDATE public."tbl_student_evaluation" SET class_test_one=%s, ca1=%s, mid_term=%s, "ratingscale1"=%s, class_test_two=%s, ca2=%s, annual_exam=%s, "ratingscale2"=%s WHERE id=%s'
        params = (class_test_one, CA1, mid_term, ratingScale1, class_test_two, CA2, annual_exam, ratingScale2, id)
        print('Executing SQL Query:', query, 'with parameters', params)

        connection.execute(query, params)

        return ("Inserted!")
    
 
# This is the route for storing student into tbl_student_personal_info
def store_student_assessment_details(stdId):
    id = uuid4()
    stdId=stdId
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
    userId=current_user.id
    created_at = datetime.now()
    check_query = """
    SELECT COUNT(*) 
    FROM public.tbl_student_evaluation where subject_teacher_id = %s AND student_id = %s """
    count = engine.execute(check_query, userId, stdId).scalar()
    print(userId, stdId, 'Count: ',count)
    if count>0:
        connection.execute("UPDATE public.tbl_student_evaluation SET class_test_one=%s, ca1=%s, mid_term=%s, ratingscale1=%s, class_test_two=%s, ca2=%s, annual_exam=%s, ratingscale2=%s, status_remarks=%s, punctuality=%s,discipline=%s,social_service=%s,leadership_quality=%s,created_at=%s WHERE student_id=%s AND subject_teacher_id = %s",
                       (class_test_one, ca1, mid_term, rate1, class_test_two, ca2, annual_exam, rate2,status_remarks,punctuality,discipline,social_service,leadership_quality,created_at, stdId, userId))
        
        return ("Updated!")
    else:
        connection.execute("INSERT INTO public.tbl_student_evaluation (id, subject_teacher_id, student_id, class_test_one,  class_test_two, mid_term, annual_exam, ca1,"
                    "ca2, \"ratingscale1\", \"ratingscale2\", status_remarks, punctuality, discipline, social_service, leadership_quality, created_at) "
                   "VALUES ("
                   "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s)",
                   (id, userId, stdId, class_test_one, class_test_two, mid_term, annual_exam, ca1,ca2, rate1, rate2,status_remarks, punctuality, discipline, 
                   social_service,leadership_quality,created_at ))

        return "successfully inserted!"

#checking for cid already exist in database
def check_exist(stdId):
    getUser=current_user.id
    getUsersub='''select ud.subject,ud.grade,ud.section_no,ud.role 
	from public."User" uu 
    join public.user_detail ud  
    on uu.id=ud.user_id where uu.id=%s'''
    getuserSub=connection.execute(getUsersub,getUser).fetchall()
    print(getUser,"****GETUSER******")
    print(stdId,"**STUDENTID******")
    print(connection,"CONNECTION***")
    getData = getuserSub[0]
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
	join public.std_section sec on (ud.section_no=sec.section_id and cl.class_id=sec.class_id)
	join public.section_subject ss on (ud.subject=ss.section_subject_id and ss.section_id=ss.section_id)
	join public.tbl_subjects sub on ss.subject_id=sub.subject_code 
	where cl.class_id =%s and sec.section_id=%s and ss.section_subject_id=%s
	and ud.role=%s 
	and ev.subject_teacher_id=%s
	and student_id=%s'''
    results = connection.execute(
        check_exist_data,class_value,section_value,subject_value,role,getUser,stdId).fetchone()[0]
    output = int(results)
    if output > 0:
        return True
    else:
        return False

def get_std_marks(id):
    std_class = connection.execute(
        'SELECT * FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        # 'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_present_dzongkhag '
        # 'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_present_gewog '
        # 'inner join public.tbl_village_list as village on village.village_id = P.student_present_village '
        'WHERE P.id =%s',
        id)
    data = list(std_class)
    std_id = []
    for rows in data:
        ids = rows[0]
        std_id.append(ids)
    std_id = std_id[0]
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    # search_value = request.form['search[value]']
    # print(search_value, "**SEARCHVALUE**")
    getUser = current_user.id
    getUsersub='''select ud.subject,ud.grade,ud.section_no,ud.role 
	from public."User" uu 
    join public.user_detail ud  
    on uu.id=ud.user_id where uu.id=%s'''
    getuserSub=connection.execute(getUsersub,getUser).fetchall()

    getData = getuserSub[0]
    #Retrieve the values of class and section
    class_value = getData['grade']
    section_value = getData['section_no']
    subject_value = getData['subject']
    search_query = ''
    params = [class_value,section_value, subject_value,getUser,std_id]

    str_query = '''SELECT *, 
       u.username, 
       c.class_name, 
       ss.section,
       ts.subject_name, 
       COUNT(*) OVER() AS count_all     
        FROM 
            public.tbl_student_evaluation as te
        JOIN 
            public."User" as u ON u.id = te.subject_teacher_id
        JOIN 
            public.user_detail as ud ON ud.user_id = u.id
        JOIN 
            public.class as c ON c.class_id = ud.grade
        JOIN 
            public.std_section as ss ON ss.section_id = ud.section_no
        JOIN 
            public.tbl_subjects as ts ON ts.subject_code = ud.subject
        WHERE 
            ud.grade = %s 
            AND ud.section_no = %s 
            AND ud.subject = %s
            AND ud.user_id = %s
            AND te.student_id = %s ORDER BY 
        te.created_at DESC LIMIT 1;
            '''
    #params.extend(getUser)
    get_std_marks = connection.execute(str_query, *params).fetchall()
    data = []
    ratings = []
    count = 0
    for index, user in enumerate(get_std_marks):
        data.append({
            'sl_no': index + 1,
            'subject': user.subject_name,
            'class_test_one': user.class_test_one,
            'ca1': user.ca1,
            'ratingscale1': user.ratingscale1,
            'mid_term': user.mid_term,
            'class_test_two': user.class_test_two,
            'ca2': user.ca2,
            'ratingscale2': user.ratingscale2,
            'annual_exam': user.annual_exam,
            'student_id': user.student_id,
            'subjectId':user.subject_code,
            'id': user.id
        })
        count = user.count_all

    response = {
        "data": data,
    }
    return jsonify(response)

def load_std_marks(studentId,subject):
    draw = request.args.get('draw')
    row = request.args.get('start')
    row_per_page = request.args.get('length')
    userId=current_user.id
    print(f"This is the user_id: {userId}")
    getUsersub='''select ud.grade,ud.section_no
	from public."User" uu 
    join public.user_detail ud  
    on uu.id=ud.user_id where uu.id=%s'''
    getuserSub=connection.execute(getUsersub,userId).fetchall()
    print(studentId,"**STUDENTID******", userId,"****GETUSER******")
    getData = getuserSub[0]
    #Retrieve the values of class and section
    class_value = getData['grade']
    section_value = getData['section_no']
    params = [studentId,class_value, section_value, subject,userId]
    print('***These are the params:---', params)
    str_query = '''select ev.*, sub.*, COUNT(*) OVER() AS count_all from public.tbl_student_evaluation ev 
	join public."User" uu on ev.subject_teacher_id=uu.id 
	join public.user_detail ud on (uu.id=ud.user_id and ev.subject_teacher_id=ud.user_id)
	join public.tbl_students_personal_info std 
	on ev.student_id=std.id 
	join public.tbl_academic_detail ac 
	on (std.id=ac.std_personal_info_id and ev.student_id=ac.std_personal_info_id)
	join public.class cl on (ac.admission_for_class=cl.class_id 
	and ud.grade=cl.class_id)
	join public.std_section sec on (ud.grade=sec.class_id and ac.admission_for_class=sec.class_id and cl.class_id=sec.class_id)
	join public.section_subject ss on (ac.section=ss.section_id and sec.section_id=ss.section_id and ud.section_no=ss.section_id)
	join public.tbl_subjects sub on ss.subject_id=sub.subject_code
    where ev.student_id = %s and ac.admission_for_class=%s and ac.section=%s and ss.section_subject_id=%s and ev.subject_teacher_id=%s
   ''' 
    get_std_marks = connection.execute(str_query, *params).fetchall()
    print(get_std_marks, "***STDMARKS")
    data = []
    ratings = []
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
        count = users.count_all

    response = {
        "draw": draw,
        "recordsTotal": count,
        "recordsFiltered": count,
        "data": data,
    }

    print(response, "GETRESPONSES**YO******")
    return response

def get_std_rating(studentId, subject):
    draw = request.args.get('draw')
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
    print(class_value,'*class',section_value,'*section',userId,'*user',studentId,'stdId',subject,'*subject')
    params = [studentId, userId,subject,class_value,section_value]
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
	join public.std_section sec on (ud.section_no=sec.section_id and cl.class_id=sec.class_id)
	join public.section_subject ss on (ud.subject=ss.section_subject_id and sec.section_id=ss.section_id)
	join public.tbl_subjects sub on ss.subject_id=sub.subject_code 
    where ev.student_id=%s and ev.subject_teacher_id=%s
    and ss.section_subject_id=%s and cl.class_id=%s and sec.section_id=%s
    '''
    ratingValue = connection.execute(getRating, *params).fetchall()
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
        "recordsTotal": len(data),
        "recordsFiltered": len(data),
        "data": data,
    }
    return response

def getRatingValue():
    query = 'SELECT "ratingId", rating FROM public.rating'
    result = connection.execute(query)
    dropdown_values = [{'id': row.ratingId, 'name': row.rating} for row in result]
    return jsonify(dropdown_values)

def getStdGrade(id):
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '
    if search_value != '':
        search_query = "AND (A.subject LIKE '%%" + search_value + "%%') "
    str_query = '''
     SELECT *, count(*) OVER() AS count_all, se.id
     FROM public.tbl_student_evaluation AS se
     JOIN public.tbl_students_personal_info AS sp ON sp.id = se.student_id
     JOIN public."User" AS U ON U.id = se.subject_teacher_id
     JOIN public.tbl_academic_detail AS ad ON sp.id = ad.std_personal_info_id
     JOIN public.user_detail AS ud ON U.id = ud.user_id
     WHERE se.id IS NOT NULL
     AND sp.id = %s
     ''' + search_query + '''
     LIMIT %s OFFSET %s
    '''
    get_std_marks = connection.execute(str_query, id, row_per_page, row).fetchall()
    print(get_std_marks, "******GETSTDMARKS**********")

    data = []
    count = 0
    for index, user in enumerate(get_std_marks):
        data.append({
            'sl': index + 1,
            'subject': user.subject,
            'class_test_one': user.class_test_one,
            'mid_term': user.mid_term,
            'class_test_two': user.class_test_two,
            'annual_exam': user.annual_exam,
            'cont_assessment': user.cont_assessment,
            'total': int(user.class_test_one) + int(user.mid_term) + int(user.class_test_two) + int(user.annual_exam) + int(user.cont_assessment),
            'id': user.id
        })
        count = user.count_all

    response = {
        "recordsTotal": count,
        "recordsFiltered": count,
        "data": data
    }

    return response

#function for termrating 
def term_rating(stdId, termraringScale1, termratingScale2, termratingScale3, termratingScale4):
    id = uuid4()
    userId = current_user.id
    
    # Check if subject_teacher_id and student_id combination exists
    check_query = """
    SELECT COUNT(*) 
    FROM public.term_rating 
    WHERE subject_teacher_id = :userId
    """
    count = engine.execute(text(check_query), userId=userId).scalar()

    if count > 0:
        # If the combination exists, perform an update
        update_query = """
        UPDATE public.term_rating SET
            Block1 = :termraringScale1,
            Block2 = :termratingScale2,
            Block3 = :termratingScale3,
            Block4 = :termratingScale4
        WHERE subject_teacher_id = :userId AND student_id = :stdId
        """
        engine.execute(
            text(update_query),
            termraringScale1=termraringScale1,
            termratingScale2=termratingScale2,
            termratingScale3=termratingScale3,
            termratingScale4=termratingScale4,
            userId=userId,
            stdId=stdId
        )
        return 'updated'
    else:
        # If the combination does not exist, perform an insert
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
        return 'successfully'







