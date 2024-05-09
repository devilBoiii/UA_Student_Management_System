import os
import base64
from flask import jsonify, request, render_template, url_for, redirect, session
from flask_login import current_user
from sqlalchemy import create_engine,text
from config import Config
import datetime
from uuid import uuid4
from random import randint
from decouple import config
from flask_mail import Message
from app.admin.service import send_application_mail
from app import mail
import io
import re


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
random_id = randint(000, 999)
def getStartDate():
    getEnrollStartDate =text('SELECT enrollment_start_date FROM public."enrollmentDate"')
    getStartDates = connection.execute(getEnrollStartDate).fetchall()
    result = getStartDates[0][0]  # Extract the date value from the result
    formatted_date = result.strftime('%Y-%m-%d')  # Convert to desired date format
    return formatted_date
    
def getEndDate():
    getEnrollEndDate=text('SELECT enrollment_end_date FROM public."enrollmentDate"')
    getEndDates=connection.execute(getEnrollEndDate).fetchall()
    result = getEndDates[0][0]  # Extract the date value from the result
    formatted_date = result.strftime('%Y-%m-%d')  # Convert to desired date format
    return formatted_date

#This is the route for storing student detials into tbl_student_personal_info 
def store_student_details():
    id = uuid4()
    student_cid = request.form.get("cid")
    student_code = request.form.get("student_code")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    dob = request.form.get("dob")
    student_email = request.form.get("email")
    student_phone_number = request.form.get("phone_number")
    student_dzongkhag = request.form.get("permanent_dzongkhag")
    student_gewog = request.form.get("permanent_gewog")
    student_village = request.form.get("permanent_village")
    created_at = datetime.datetime.now()
    parent_cid = request.form.get('parent_cid')
    parent_full_name    = request.form.get('parent_name')
    parent_contact_number = request.form.get('parent_number')
    parent_email = request.form.get("parent_email")
    student_present_dzongkhag = request.form.get("present_dzongkhag")
    student_present_gewog = request.form.get("present_gewog")
    student_present_village = request.form.get("present_village")
    status = 'submitted'
    gender = request.form.get('gender')
     # marksheet passport size photo
    half_photo = request.files.get('half_photo')

    img_url = os.path.join('./app/home/static/uploads/halfphoto/',
                         student_cid +str(random_id) + half_photo.filename)
    half_photo.save(img_url)
    halfphoto_url = '/static/uploads/halfphoto/'+ student_cid + \
            str(random_id) + half_photo.filename

    engine.execute("INSERT INTO public.tbl_students_personal_info (id, student_cid, first_name, last_name, dob, student_email, student_phone_number,  student_dzongkhag, student_gewog, student_village, parent_cid,"
                    "parent_full_name, parent_contact_number, parent_email, student_present_dzongkhag, student_present_gewog, student_present_village, created_at, status,gender, half_photo,student_code) "
                   "VALUES (""%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s)",
                   (id, student_cid, first_name, last_name,dob, student_email, student_phone_number, student_dzongkhag, student_gewog, student_village, parent_cid, parent_full_name, parent_contact_number, 
                   parent_email,student_present_dzongkhag,  student_present_gewog, student_present_village,  created_at, status, gender, halfphoto_url, student_code))

    return id

# This is the route for storing student detials into tbl_academic_detail 
def store_academic_details(id_personal):
    id = uuid4()
    name =request.form.get("first_name")+' '+request.form.get("last_name")
    user_mail=request.form.get("email")
    index_number = request.form.get("index_number")
    student_code = request.form.get("student_code")
    previous_school_name = request.form.get("previous_school")
    status='submitted'
    narration=''
     # marksheet upload
    marksheet = request.files.get('marksheet')

    img_url = os.path.join('./app/home/static/uploads/marksheet/',
                         index_number +str(random_id) + marksheet.filename)
    marksheet.save(img_url)
    marksheet_url = '/static/uploads/marksheet/'+ index_number + \
            str(random_id) + marksheet.filename
    supw_grade = request.form.get("supw") 
    percentage_obtained = request.form.get("percent")
    created_at = datetime.datetime.now()
    admission_for = request.form.get('admission_for')
    accommodation = request.form.get('accommodation')
    # student_code = request.form.get ('std_code')
    bcse_x = request.form.get('previous_school_X')
    bhsec_xii = request.form.get('previous_school_XII')
    engine.execute("INSERT INTO public.tbl_academic_detail (id, std_personal_info_id, index_number, previous_school_name, marksheet, supw_grade, percentage_obtained,"
                    "created_at, admission_for_class, accommodation, student_code, bcse_x, bhsec_xii) "
                   "VALUES ("
                   "%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s)",
                   (id, id_personal, index_number, previous_school_name, marksheet_url, supw_grade, percentage_obtained,  created_at,
                    admission_for, accommodation, student_code, bcse_x,bhsec_xii))
    class_id='select class_name from public.class where class_id=%s'
    getClass=connection.execute(class_id,admission_for).scalar()
    send_application_mail(name,status,getClass,narration, user_mail)
    return "success"


# storing contact details
def store_contact_details():
    id = uuid4()
    full_name = request.form.get("Username")
    user_email = request.form.get("Useremail")
    phone_no = request.form.get("phone_number")
    comment = request.form.get("comment")
    created_date = datetime.datetime.now()
    updated_date = datetime.datetime.now()

    engine.execute("INSERT INTO public.tbl_contact_form (id, full_name, user_email, phone_no, comment, created_date, updated_date) "
                   "VALUES ("
                   "%s,%s,%s,%s,%s,%s,%s)",
                   (id, full_name, user_email, phone_no, comment, created_date, updated_date))

    return 'successful'


# Fetching Dzongkhag/gewog/village list from the database
import datetime
def get_dzo_list():
    dzongkhag = text('SELECT * FROM public.tbl_dzongkhag_list')
    dzo_List = connection.execute(dzongkhag).fetchall()

    get_user_info = text('select * from public.tbl_dzongkhag_list as dl ' \
                    'inner join public.tbl_gewog_list as gl on dl.dzo_id = gl.dzo_id ' \
                    'inner join public.tbl_village_list as vl on gl.gewog_id = vl.gewog_id')
    get_details = connection.execute(get_user_info).fetchall()

    slot_query = '''SELECT id, class7, class8, class9, class10, class11_arts, class11_com, class11_sci, class12_arts, class12_com, class12_sci FROM public.tbl_std_slots'''
    slot = engine.execute(slot_query).fetchall()
    # Pass the slot data to the template
    return render_template('enroll_student.html', dzo_List=dzo_List, get_details=get_details, slot=slot)

# Fetching gewog list from database
def get_gewog():
    if request.method == 'POST':
        gewog_id = request.form['gewog_id']
        query = text('SELECT * FROM public.tbl_gewog_list WHERE "dzo_id" = :gewog_id ORDER BY "gewog_name" ASC')
        gewog_list = connection.execute(query, {'gewog_id': gewog_id}).fetchall()
        gewog_list_dicts = [row._asdict() for row in gewog_list]
        print("REACHINGHEREGEWOG: ", gewog_list_dicts,'----', gewog_id)
    else:
        gewog_list_dicts = []

    return jsonify({"gewogList": gewog_list_dicts})

def get_gewog_std():
    if request.method == 'POST':
        gewog_id = request.form['gewog_id']
        query = text('SELECT * FROM public.tbl_gewog_list WHERE "gewog_id" = :gewog_id ORDER BY "gewog_name" ASC')
        gewog_list = connection.execute(query, {'gewog_id': gewog_id}).fetchall()
        gewog_list_dicts = [row._asdict() for row in gewog_list]
    else:
        gewog_list_dicts = []

    return jsonify({"gewogList": gewog_list_dicts})

# # Fetching village list from the database
def get_village():
    if request.method == 'POST':
        village_id = request.form['village_id']
        query = text('SELECT * FROM public.tbl_village_list WHERE "gewog_id" = :village_id ORDER BY "village_name" ASC')
        village_list = connection.execute(query, {'village_id': village_id}).fetchall()
        village_list_dicts = [row._asdict() for row in village_list]
    else:
        village_list_dicts=[]    
    return jsonify({"villageList": village_list_dicts})

def get_village_std():
    if request.method == 'POST':
        village_id = request.form['village_id']
        query = text('SELECT * FROM public.tbl_village_list WHERE "village_id" = :village_id ORDER BY "village_name" ASC')
        village_list = connection.execute(query, {'village_id': village_id}).fetchall()
        village_list_dicts = [row._asdict() for row in village_list]
        print("REACHINGHEREGEWOG: ", village_list_dicts,'----', village_id)
    else:
        village_list_dicts=[]    
    return jsonify({"villageList": village_list_dicts})


def track_std():
    student_cid = request.form['std_cid']
    student_code = request.form['std_code']
    checkcodeorCid='''
        SELECT spp.student_cid, ac.student_code FROM public.tbl_students_personal_info AS spp INNER JOIN public.tbl_academic_detail AS ac ON ac.std_personal_info_id = spp.id WHERE spp.student_cid = %s OR ac.student_code = %s '''
    codeorCid=engine.execute(checkcodeorCid,student_cid,student_code).fetchall()
    if codeorCid ==[]:
        return {"error": "Either CID or Index number is incorrect."}    
    else:
     str_query = '''SELECT *, spp.id as std_id FROM public.tbl_students_personal_info AS spp INNER JOIN public.tbl_academic_detail AS ac ON ac.std_personal_info_id = spp.id WHERE spp.student_cid = %s OR ac.student_code = %s'''
     std_list = engine.execute(str_query, student_cid, student_code).fetchall()
     print(std_list, "stdList#####")
     std_list = [dict(row) for row in std_list]  # Convert each row to a dictionary
     print(std_list, "stdList***")

    data = []
    count = 0
    for index, user in enumerate(std_list):
        data.append({
        'sl': index + 1,
        'student_code': user['student_code'],
        'student_cid': user['student_cid'],
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'student_email': user['student_email'],
        'id': user['std_id']
        })
        count += 1

    respose_std_list = {
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }
    return respose_std_list

def getClassId():
    query = text("SELECT class_id,class_name FROM public.class WHERE class_name LIKE '%XII%'")
    result = connection.execute(query)
    # Convert the result into a list of dictionaries
    dropdown_values = [
        {'id': row.class_id, 'name': row.class_name}
        for row in result
    ]

    # Return the dropdown values as JSON
    return jsonify(dropdown_values)

def getClassIdx():
    query = text("SELECT class_id,class_name FROM public.class WHERE class_name='X'")
    result = connection.execute(query)
    # Convert the result into a list of dictionaries
    dropdown_values = [
        {'id': row.class_id, 'name': row.class_name}
        for row in result
    ]
    # Return the dropdown values as JSON
    return jsonify(dropdown_values)

def getClassIdxi():
    query = text("SELECT class_id,class_name FROM public.class WHERE class_name IN('XI Science','XI Commerce','XI Arts')")
    result = connection.execute(query)
    # Convert the result into a list of dictionaries
    dropdown_values = [
        {'id': row.class_id, 'name': row.class_name}
        for row in result
    ]

    # Return the dropdown values as JSON
    return jsonify(dropdown_values)

def getClassIdGeneral():
    query = text("SELECT class_id,class_name FROM public.class where class_id IN (1,2,3)ORDER BY CASE class_id WHEN 1 THEN 'VII' WHEN 2 THEN 'VIII' WHEN 3 THEN 'IX' END")
    result = connection.execute(query)
    # Convert the result into a list of dictionaries
    dropdown_values = [
        {'id': row.class_id, 'name': row.class_name}
        for row in result
    ]
    # Return the dropdown values as JSON
    return jsonify(dropdown_values)


def checkIndexorCid(id):

    # Continue with the database query for other cases
    checkStatus ="SELECT status FROM public.tbl_students_personal_info as sp left join public.tbl_academic_detail as ad on ad.std_personal_info_id = sp.id WHERE sp.student_cid = %s OR ad.student_code = %s"
    checkStatusCid = engine.execute(checkStatus, id, id).scalar()

    if checkStatusCid is None:
        return {"error": "No student found with the provided CID/Student Code"}
    elif checkStatusCid != 'approved':
        return {"error": "Your application is not yet approved. Please wait for the administrators to approve it."}
    else:
        str_query = "SELECT std.student_cid, \
            string_agg(std.first_name || ' ' || std.last_name, ' ') AS std_name, cl.class_name \
            FROM public.tbl_students_personal_info std \
            LEFT JOIN public.tbl_academic_detail b ON std.id = b.std_personal_info_id \
            JOIN public.class cl ON cl.class_id = b.admission_for_class \
            WHERE std.student_cid = %s OR b.student_code = %s AND std.status = 'approved' \
            GROUP BY std.student_cid, cl.class_name"
        std_index = connection.execute(str_query, id, id).fetchall()

        # Convert the result to a list of dictionaries
        result = []
        for row in std_index:
            dict_row = {
                "student_cid": row[0],
                "std_name": row[1],
                "class_name": row[2]
            }
            result.append(dict_row)

        # Return the data in JSON format
        return jsonify(result)

def getstudentDetail():
     str_query = "select std.student_cid,b.student_code from public.tbl_students_personal_info std LEFT JOIN \
     public.tbl_academic_detail b ON std.id=b.std_personal_info_id \
     where (std.student_cid =%s OR b.student_code=%s) AND std.status='approved'"
     std_index = connection.execute(str_query, (id, id)).fetchall()

#checking for cid already exist in database
def check_exist(identification_number):
    check_exist_data = text('SELECT COUNT(*) FROM public.tbl_students_personal_info as sp INNER JOIN public.tbl_academic_detail as ac ON ac.std_personal_info_id = sp.id  WHERE student_cid = :identification_number')
    results = connection.execute(check_exist_data, {"identification_number": identification_number}).fetchone()[0]
    output = int(results)
    if output > 0:
        return True
    else:
        return False
    
def getpaymentHistory(id):
    getHistory = 'SELECT jrn_number, bank_type, acc_holder, amount, paymentmodes FROM public.tbl_acc_detail WHERE std_cid = %s'
    results = connection.execute(getHistory, id).fetchall()
    print(results,"*****RESult")
    data = []
    for i, row in enumerate(results):
        history = {
            "Sl No.": i + 1,
            "Account Holder": row[2],
            "Bank Type": row[1],
            "Journal No.": row[0],
            "Amount": str(row[3]),
            "Payment Mode": row[4]
        }
        data.append(history)
    print(data,"**DATA")
    return jsonify({"data": data})

# printing student result
def printing_result():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    user_id = request.form.get('user_id')
    search_query = ' '
    if (search_value != ''):
        search_query = "AND (A.subject LIKE '%%" + search_value + "%%' "

    str_query = 'SELECT *, count(*) OVER() AS count_all, se.id from public.tbl_student_evaluation as se, public.tbl_students_personal_info as sp, public."User" as U ,public.tbl_academic_detail as ad, '\
                'public.user_detail as ud where se.id IS NOT NULL '\
                '' + search_query + '' \
                "AND sp.id = se.student_id AND U.id = se.subject_teacher_id AND sp.id = ad.std_personal_info_id AND U.id = ud.user_id  LIMIT " + \
        row_per_page + " OFFSET " + row + ""

    get_std_marks = connection.execute(str_query, user_id).fetchall()

    data = []
    count = 0
    for index, user in enumerate(get_std_marks):
        data.append({'sl': index + 1,
                     'subject': user.subject,
                     'class_test_one': user.class_test_one,
                     'mid_term': user.mid_term,
                     'class_test_two': user.class_test_two,
                     'annual_exam': user.annual_exam,
                     'cont_assessment': user.cont_assessment,
                     'total': int(user.class_test_one) + int(user.mid_term) + int(user.class_test_two) + int(user.annual_exam) + int(user.cont_assessment),
                     'id': user.id})
        count = user.count_all

    respose_get_marks = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }
    return respose_get_marks

# paying student fee
import datetime
def pay_std_fee(studentCid):
    id = uuid4()
    std_name = request.form.get('studentName')
    name=std_name.split()
    fname=name[0]
    lname=' '.join(name[1:])
    std_class=request.form.get('std_class')
    jrn_number = request.form.get('jrn_number')
    bank_type = request.form.get('bank_type')
    acc_holder = request.form.get('acc_holder')
    amount=request.form.get('amount')
    paymentModes=request.form.get('paymentModes')
    current_datetime = datetime.datetime.now()
    screenshot=request.files.get('screenShot')
    img_url = os.path.join('./app/home/static/uploads/screenshots/',
                         studentCid +str(random_id) + screenshot.filename)
    screenshot.save(img_url)
    screenshot_url = '/static/uploads/screenshots/'+ studentCid + \
            str(random_id) + screenshot.filename
    print(paymentModes,"*********paymentModes")
    countedFull=0
    countedInstall=0
    countedSeatConfirm=0
    countSeatConfirm='''SELECT COUNT(*) FROM public.tbl_acc_detail where std_cid=%s and paymentmodes='Seat Confirm' '''
    countedSeatConfirm=int(connection.execute(countSeatConfirm,studentCid).fetchone()[0])
    countFull='''SELECT COUNT(*) FROM public.tbl_acc_detail where std_cid=%s and paymentmodes='Full' '''
    countedFull=int(connection.execute(countFull,studentCid).fetchone()[0])
    countInstall='''SELECT COUNT(*) FROM public.tbl_acc_detail where std_cid=%s and paymentmodes='Installment' ''' 
    countedInstall=int(connection.execute(countInstall,studentCid).fetchone()[0])
    if paymentModes=='Seat Confirm' and countedSeatConfirm>0:
        return {"error": "You have already paid for the Seat Confirmation Fee."}    
    elif paymentModes !='Seat Confirm' and countedSeatConfirm<1:
        return {"error": "You have to pay for Seat Confirmation Fee first."} 
    else:     
        if paymentModes=='Full':
            if countedInstall>=1 and countedInstall != 4:
                return {"error": "You have paied the school fee in installments and you cannot pay it in full payment"}
            if countedFull>=1:
                return {"error": "You have already paied all the school fee in full payment"}
            if countedInstall==4:
                return {"error": "You have paied all the school fee in installments"}
        if paymentModes=='Installment':
            if countedInstall>=4:
                return {"error": "You have already paied all the school fee in installments"}
            if countedFull>=1:
                return {"error": "You have already paied all the school fee in full payment"}
        
    # if paymentModes=='Seat Confirm' and countedSeatConfirm>=1:
    #     return {"error": "You have already paied for the Seat Confirmation Fee."}
    # elif paymentModes=='Installment' and countedInstall>=4:
    #     return {"error": "You have already paied all the school fee in installments"}
    # elif paymentModes=='Full' and countedFull>=1:
    #     return {"error": "You have already paied all the school fee in full payment"}
    connection.execute("INSERT INTO public.tbl_acc_detail (id, f_name, l_name, jrn_number, bank_type, acc_holder, std_class, std_cid, amount, paymentModes, screen_shot, date_added) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
               (id, fname, lname, jrn_number, bank_type, acc_holder, std_class, studentCid, amount, paymentModes, screenshot_url, current_datetime))

    return "success"

# fetch student details from database
def get_std_class(id):
    student_details = connection.execute(
        'SELECT *, P.id FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_present_dzongkhag '
        'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_present_gewog '
        'inner join public.tbl_village_list as village on village.village_id = P.student_present_village '
        'WHERE P.id =%s',
        id).first()
    print('Gettinghere', student_details)
    #fetch student   s
    std_marks_query = '''SELECT * FROM public.tbl_students_personal_info AS sp INNER JOIN public.tbl_student_evaluation AS se on sp.id = se.student_id
    INNER JOIN public.tbl_academic_detail AS ad ON ad.std_personal_info_id = sp.id 
    INNER JOIN public.tbl_academic_summary AS tas ON tas.std_id = se.student_id 
    INNER JOIN public.user_detail AS ud ON ud.user_id = se.subject_teacher_id AND ud.section_no = ad.section
    INNER JOIN public.tbl_subjects AS s ON s.subject_code = ud.subject
    WHERE se.student_id = %s '''
    #ErrorHERE!Above One!!!
    std_marks = connection.execute(std_marks_query, id).fetchall()

    #fetch student's academic details
    std_academic = connection.execute(
        'SELECT * FROM public.tbl_academic_summary AS std_result '
        'WHERE std_id = %s',
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
    return render_template('student_result.html', std=student_details, std_marks=std_marks, std_academic=std_academic, punctuality_label=punctuality_label, discipline_label=discipline_label, leadership_label=leadership_label)

#today
def view_std_result(stdId):
    str_query = '''select ev.*, sub.*, ss.* from public.tbl_student_evaluation ev 
                    join public."User" uu on ev.subject_teacher_id=uu.id 
                    join public.user_detail ud on (uu.id=ud.user_id and ev.subject_teacher_id=ud.user_id)
                    join public.tbl_students_personal_info std on ev.student_id=std.id 
                    join public.tbl_academic_detail ac on (std.id=ac.std_personal_info_id and ev.student_id=ac.std_personal_info_id)
                    join public.class cl on (ac.admission_for_class=cl.class_id and ud.grade=cl.class_id)
                    join public.std_section sec on (ac.section=sec.section_id and ud.section_no=sec.section_id and cl.class_id=sec.class_id)
                    join public.section_subject ss on (ud.subject=ss.section_subject_id and ss.section_id=sec.section_id)
                    join public.tbl_subjects sub on ss.subject_id=sub.subject_code
                    WHERE ev.student_id = %s '''

    get_std_marks = connection.execute(str_query, stdId).fetchall()

    data = []
    for index, users in enumerate(get_std_marks):
        data.append({
            'sl_no': index + 1,
            'subject': users.subject_name,
            'class_test_one': users.class_test_one,
            'ca1': users.ca1,
            'ratingScale1': users.ratingScale1,
            'mid_term': users.mid_term,
            'class_test_two': users.class_test_two,
            'ca2': users.ca2,
            'ratingScale2': users.ratingScale2,
            'annual_exam': users.annual_exam,
            'student_id': users.student_id,
            'id': users.id
        })
    if len(data) == 0:
        response = {
            "recordsTotal": 0,
            "recordsFiltered": 0,
        }
    else:
        response = {
            "data": data,
        }

    return response
    

def marks_results(stdId):
    draw = request.args.get('draw')
    row = request.args.get('start')
    row_per_page = request.args.get('length')

    getUsersub = '''select ud.subject, ud.grade, ud.section_no, ud.role 
                    from public."User" uu 
                    join public.user_detail ud on uu.id=ud.user_id where uu.id=%s'''

    getuserSub = connection.execute(getUsersub, None).fetchall()

    if getuserSub:
        getData = getuserSub[0]
        class_value = getData['grade']
        section_value = getData['section_no']
        subject_value = getData['subject']

        params = [stdId, class_value, section_value]
        str_query = '''select ev.*, sub.*, ss.*, COUNT(*) OVER() AS count_all from public.tbl_student_evaluation ev 
                        join public."User" uu on ev.subject_teacher_id=uu.id 
                        join public.user_detail ud on (uu.id=ud.user_id and ev.subject_teacher_id=ud.user_id)
                        join public.tbl_students_personal_info std on ev.student_id=std.id 
                        join public.tbl_academic_detail ac on (std.id=ac.std_personal_info_id and ev.student_id=ac.std_personal_info_id)
                        join public.class cl on (ac.admission_for_class=cl.class_id and ud.grade=cl.class_id)
                        join public.std_section sec on (ac.section=sec.section_id and ud.section_no=sec.section_id and cl.class_id=sec.class_id)
                        join public.section_subject ss on (ud.subject=ss.section_subject_id and ss.section_id=sec.section_id)
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
                'ratingScale1': users.ratingScale1,
                'mid_term': users.mid_term,
                'class_test_two': users.class_test_two,
                'ca2': users.ca2,
                'ratingScale2': users.ratingScale2,
                'annual_exam': users.annual_exam,
                'student_id': users.student_id,
                'id': users.id
            })
            count = users.count_all

        if count == 0:
            response = {
                "draw": draw,
                "recordsTotal": 0,
                "recordsFiltered": 0,
            }
        else:
            response = {
                "draw": draw,
                "recordsTotal": count,
                "recordsFiltered": count,
                "data": data,
            }

        return response
    else:
        # Handle the case where getuserSub is empty
        # You might want to return an error response or handle it in some way
        return {"error": "No data found for the specified user"}

def get_std_results(id):
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
    
def gettermrating(id):
    std_class = connection.execute(
        'SELECT *, P.id FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_present_dzongkhag '
        'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_present_gewog '
        'inner join public.tbl_village_list as village on village.village_id = P.student_present_village '
        'WHERE P.id =%s',
        id).first()
     
    student_details = connection.execute(
        '''SELECT *, s.section,c.class_name, P.id FROM public.tbl_students_personal_info AS P 
            inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id 
            inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_present_dzongkhag 
            inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_present_gewog 
            inner join public.tbl_village_list as village on village.village_id = P.student_present_village
            inner join public.std_section as s on s.section_id = A.section
            inner join public.class as c on c.class_id = A.admission_for_class WHERE P.id =%s''',
        id).first()
    
    std_term_query = '''SELECT DISTINCT tr.*, ac.*, std.*, uus.*, sec.*, cl.*, uus.*, ts.*
                    FROM public.term_rating tr
                    JOIN public."User" uus ON tr.subject_teacher_id = uus.id
                    JOIN public.user_detail ud ON (uus.id = ud.user_id AND tr.subject_teacher_id = ud.user_id)
                    JOIN public.tbl_students_personal_info std ON tr.student_id = std.id 
                    JOIN public.tbl_academic_detail ac ON (std.id = ac.std_personal_info_id AND tr.student_id = ac.std_personal_info_id)
                    JOIN public.class cl ON (ac.admission_for_class = cl.class_id AND ud.grade = cl.class_id)
                    JOIN public.std_section sec ON (ac.section = sec.section_id AND ud.section_no = sec.section_id AND cl.class_id = sec.class_id)
                    JOIN public.tbl_subjects ts ON (ud.subject = ts.subject_code AND ts.subject_code = ud.subject)
                    WHERE tr.student_id = %s
                    '''
    result_set = connection.execute(std_term_query, id).fetchall()

    # result_proxy = connection.execute(
    # 'SELECT * FROM public.term_rating WHERE student_id = %s', id)
    # result_set = result_proxy.fetchall()

    term_mapping = {
        'Exceeding': 5,
        'Advancing': 4,
        'Meeting': 3,
        'Approaching': 2,
        'Beginning': 1
    }


    return render_template('termrating.html',std=std_class, result_set=result_set, student_details=student_details,term_mapping=term_mapping )






