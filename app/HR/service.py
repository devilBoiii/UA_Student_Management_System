from operator import add
from uuid import uuid4
from flask import request,jsonify
from app.admin.service import send_application_mailUser, send_application_mail
from config import Config
from sqlalchemy import create_engine,text
from datetime import datetime
from random import randint
import os
from app.HR.util import hash_pass
from flask_login import current_user

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
random_id = randint(000, 999)

def assignSection(studentCID,selectedSection,selectedHostel,accomodation):      
  
    check_section_query = 'SELECT section FROM public.tbl_academic_detail WHERE student_code = %s'
    section_exists = connection.execute(check_section_query, studentCID).scalar()
    print(studentCID,"**index",selectedSection,"**sectioN",section_exists,"**ifSection")
    select_query = 'SELECT no_ofstds FROM public.std_section WHERE section_id = %s'
    count_data = connection.execute(select_query, selectedSection).scalar()
    
    if count_data is not None:
        current_no_ofstds = int(count_data)
    else:
        current_no_ofstds=40
    print(current_no_ofstds,'***CURENt Std No.')
    if accomodation =="Boarder":
        checkHostelExist='select hostel_no from public.tbl_academic_detail where student_code=%s'
        hostelExists=connection.execute(checkHostelExist,studentCID).scalar()
        selectHostel='select no_of_std from public.tbl_hostel where hostel_no=%s'
        countHostel=connection.execute(selectHostel,selectedHostel).scalar()
        if countHostel==500 and current_no_ofstds==40:
            return {"error": "Both section and hostel is full"}
        elif hostelExists is not None and countHostel==500:
            return {"error": "There is already a Hostel assigned for this student and also the hostel is full"}
        elif countHostel==40:
            return {"error": "This hostel is full. Please select other hostels"}
    if section_exists is not None and current_no_ofstds==40:
        print("****BOTH SECTION assigned and Section FULL****") 
        return {"error": "There is already a section assigned for this student and also the section is full"}
    elif current_no_ofstds==50:
        print("***Section FULL***")
        return {"error": "This section is full. Please select Other sections" }
    else:
        if accomodation=="Boarder":
            updateSection=connection.execute('''UPDATE public.tbl_academic_detail AS tad
                SET section = %s, hostel_no = %s
                FROM public.tbl_students_personal_info AS sp
                WHERE tad.std_personal_info_id = sp.id
                AND sp.student_cid = %s''',selectedSection,selectedHostel, studentCID)
            print("Reaching Here!:---", studentCID, selectedSection, selectedHostel)
        else:
            updateSection=connection.execute('''UPDATE public.tbl_academic_detail AS tad
                            SET section = %s
                            FROM public.tbl_students_personal_info AS sp
                            WHERE tad.std_personal_info_id = sp.id
                            AND sp.student_cid = %s;
                                ''',
                        selectedSection, studentCID)
            print("Reached Here!---: ", studentCID, selectedSection, selectedHostel)
        if updateSection:
         # Step 2: Decrement the value by 1
            #for i in range():
            decremented_no_ofstds = current_no_ofstds - 1
            
            connection.execute('UPDATE public.std_section SET no_ofstds = %s WHERE section_id = %s',
                        decremented_no_ofstds, selectedSection)
            if accomodation=="Boarder":
                decremented_HostelNo=countHostel-1
                connection.execute('UPDATE public.tbl_hostel set no_of_std=%s where hostel_no=%s',
                               decremented_HostelNo,selectedHostel)
        return 'Success'    
    
#belong to HR page
def save_user_detail_table(user_id,password):
    id = uuid4()
    role = request.form['role']
    section = request.form['section']
    print(section,"######SECTION#####")
    grade = request.form['grade']
    subject = request.form['subject']
    grade = request.form['grade']
    # subject = request.form['subject']
    if grade=='2':
        section=3
        print(section,"*****SECTIONSECTION")
    else:
        section = request.form['section']       
    print(role,'**ROLE',grade,'**Grade',section,'*SECTION',subject,'***subject')
    ip = request.remote_addr
    browser = request.headers.get('User-Agent')
    connection.execute('INSERT INTO public.user_detail ("id", "user_id", "role","grade", "section_no",  "subject", "ip_address", "browser", "created_at") VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)',
                       (id, user_id, role, grade,section,subject, ip, browser, datetime.now()))
    getUser='select username,email,password from public."User" where id= %s'
    userName=connection.execute(getUser,user_id).fetchone()
    email = userName['email']
    user_name = userName['username']
    passwords=userName['password'].tobytes()
    print(passwords,"**original")
    getHash=passwords.decode('utf-8')
    print(getHash,'**getHash')
    # bytes_password =bytes.fromhex(getHash)
    # decoded_password = bytes_password.decode('utf-8')
    status='User Created'
    # send_application_mailUser(user_name,email,password,status,role)
    return "saved"

def dropdownHostels():
    getHostel='select hostel_no,hostel_name from public.tbl_hostel'
    getAllHostels=connection.execute(getHostel).fetchall()
    print(getAllHostels,'**HHHHH')
    dropdown_values = [
        {'id': row.hostel_no, 'name': row.hostel_name}
        for row in getAllHostels
    ]
    return jsonify(dropdown_values)


def getModaldetails(stdCid):
    getDetails='''select cl.class_name,sec.section,sec.section_id,acc.accommodation from public.tbl_students_personal_info std 
        join public.tbl_academic_detail acc on std.id=acc.std_personal_info_id
        join public.class cl on acc.admission_for_class=cl.class_id
        join public.std_section sec on sec.class_id=cl.class_id
        where std.student_cid=%s '''
    getsectionClass=connection.execute(getDetails,stdCid).fetchall()
    print(getsectionClass,"***CLASSSSSS")
    # Extracting class_name and collecting sections into a list
    class_name = getsectionClass[0][0]  # Access the 'class_name' using index 0 of the first row
    sections = [row[1] for row in getsectionClass]  # Access the 'section' using index 1 of each row
    section_id = [row[2] for row in getsectionClass]  # Access the 'section_id' using index 2 of each row
    boarder=[row[3] for row in getsectionClass]
    getdetail = {
        'class_name': class_name,
        'sections': sections,
        'section_id': section_id,
        'boarder': boarder
    }
    print(getdetail,'====iieiieiieiie')
    return getdetail

def get_student_fee(paymentmodes):
    # Define SQL query to retrieve student fee-related information
    getHistory = '''
    SELECT acc.std_cid, concat(std.first_name, std.last_name) as student_name, acc.jrn_number, acc.bank_type, acc.acc_holder, acc.amount, acc.paymentmodes, acd.admission_for_class,c.class_name,acd.section, acd.student_code, acc.screen_shot
    FROM public.tbl_acc_detail acc
    JOIN public.tbl_students_personal_info std 
    ON acc.std_cid = std.student_cid
    JOIN public.tbl_academic_detail acd
    ON std.id = acd.std_personal_info_id
    JOIN public.class AS c ON c.class_id = acd.admission_for_class
    WHERE 
    (
        paymentmodes = %s
        AND (paymentmodes <> 'Seat Confirm' OR paymentmodes = 'Seat Confirm' AND acd.section IS NULL)
    )
    '''

    # Execute the SQL query with the specified payment mode
    results = connection.execute(getHistory, paymentmodes).fetchall()

    # Initialize an empty list to store the formatted data
    data = []

    # If the payment mode is 'Installment', organize data into a nested dictionary
    if paymentmodes == 'Installment':
        student_data = {}  # To store data for each student
        slNo = 0

        # Iterate through the query results
        for row in results:
            std_cid = row[0]

            # If the student is encountered for the first time, create a new entry in the dictionary
            if std_cid not in student_data:
                slNo += 1
                student_data[std_cid] = {
                    "Sl No.": slNo,
                    "Student CID": std_cid,
                    "Student Code": row[0],
                    "Student Name": row[1],
                    "Class": row[8],
                    "Installments": []
                }

            # Extract installment details and add them to the student's entry in the dictionary
            installment_data = {
                "Journal No.": row[3],
                "Bank Type": row[5],
                "Account Holder": row[0],
                "Amount": row[4],
                "Payment Mode": row[2],
                "Screenshot": row[11]
            }

            student_data[std_cid]["Installments"].append(installment_data)
        # Convert the dictionary values into a list to match the format you provided
        data = list(student_data.values())
    else:
        # If the payment mode is not 'Installment', organize data into a list of dictionaries
        for i, row in enumerate(results, start=1):
            amount_with_comma = row[5]
            amount_with_comma = amount_with_comma.replace(",","")
            history = {
                "Sl No.": i,
                "Student CID": row[0],
                "Student Code": row[8],
                "Student Name": row[1],
                "Class": row[8],
                "Journal No.": row[2],
                "Bank Type": row[3],
                "Account Holder": row[4],
                "Amount": str(amount_with_comma),
                "Payment Mode": row[6],
                "Class": row[8],
                "Screenshot": row[11]
            }
            data.append(history)
            print("SEEHERE!", data)
    # Return the JSON response instead of printing it
    return jsonify({"data": data})

def save_user_table():
    id = uuid4()
    username = request.form['username']
    name = request.form['full_name']
    email = request.form['email']
    password = request.form['password']
    saved = connection.execute(
        'INSERT INTO public."User" ("id", "username", "email", "password", "full_name") VALUES (%s, %s, %s, %s,%s) RETURNING id',
        (id, username, email, hash_pass(password), name))
    user_id = saved.fetchone()
    print(user_id, "returning************")
    return user_id['id']


def save_user_detail_table(user_id):
    id = uuid4()
    role = request.form['role']
    if role=='human_resource':
     grade= None
     section = request.form['section']
     subject = request.form['subject']
     print(grade,"***GARDE")
    if is_classTeacher():
     role='subject_teacher'
     grade = request.form['grades']
     section = request.form['sections']
     subject = request.form['subject']
    if role!='human_resource' and not is_classTeacher(): 
     role = request.form['role']
     grade = request.form['grade']
     section = request.form['section']
     subject = request.form['subject']
    #stream = request.form['stream']
    print(role,'**ROLE',grade,'**Grade',section,'*SECTION',subject,'***subject')
    ip = request.remote_addr
    browser = request.headers.get('User-Agent')
      
    connection.execute('INSERT INTO public.user_detail ("id", "user_id", "role","grade", "section",  "subject", "ip_address", "browser", "created_at") VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)',(id, user_id, role, grade,section,subject, ip, browser, datetime.now()))
    return "saved"


# for users search


def all_users():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '
    if (search_value != ''):
        search_query = "AND (U.username LIKE '%%" + search_value + "%%' " \
            "OR U.email LIKE '%%" + search_value + \
            "%%' OR UD.role LIKE '%% "+search_value+"%%') "

    str_query = 'SELECT *, count(*) OVER() AS count_all, U.id as user_id FROM public."User" AS U, public.user_detail as UD WHERE U.type IS NULL '\
                '' + search_query + '' \
                "AND U.id = UD.user_id LIMIT " + row_per_page + " OFFSET " + row + ""

    users = connection.execute(str_query).fetchall()

    data = []
    count = 0
    for index, user in enumerate(users):
        data.append({'sl': index + 1,
                     'username': user.username,
                     'email': user.email,
                     'role': user.role,
                     'id': user.user_id})
        count = user.count_all

    respose = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }

    return respose

from datetime import datetime

def class_teacher():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '
    user_id = current_user.id
    getClass='select grade from public.user_detail where user_id=%s'
    getClassId=engine.execute(getClass,user_id).scalar()
    getSection='select section_no from public.user_detail where user_id=%s'
    getSectionId=engine.execute(getSection,user_id).scalar()
    print(user_id,"********USERID", "class", getClassId, "Section", getSectionId)
    if (search_value != ''):
        search_query = "AND (U.username LIKE '%%" + search_value + "%%' " \
            "OR U.email LIKE '%%" + search_value + \
            "%%' OR UD.role LIKE '%% "+search_value+"%%') "

    str_query = '''
    SELECT distinct on (U.username) username,U.*, sub.subject_name, cl.class_name, sec.section as section_name, UD.grade,UD.role, UD.stream, count(*) OVER() AS count_all, U.id AS user_id
        FROM public."User" AS U
        JOIN public.user_detail AS UD ON U.id = UD.user_id
        LEFT JOIN public.class cl ON cl.class_id = UD.grade
        LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
        LEFT JOIN public.section_subject ss ON UD.subject = ss.section_subject_id
        LEFT JOIN public.tbl_subjects sub ON UD.subject = sub.subject_code
        WHERE U.type = %s AND U.user_id IS NOT NULL AND UD.stream = %s
        ''' + search_query + '''
    LIMIT ''' + row_per_page + ''' OFFSET ''' + row

    class_teacher = connection.execute(str_query,'Class Teacher', 'class_teacher').fetchall()
    print(f'This is the result of the class_treacher:--------{class_teacher}')

    data = []
    count = 0
    for index, user in enumerate(class_teacher):
        formatted_dob = user.DOB.strftime("%d %b %Y") if user.DOB else ""
        data.append({'sl': index + 1,
                     'cid': user.CID,
                     'username': user.username,
                     'full_name': user.full_name,
                     'email': user.email,
                     'dob': formatted_dob,
                     'subject': user.subject_name,
                     'class_name': user.class_name,
                     'section_name': user.section_name,
                     'role': user.type,
                     'id': user.user_id})
        count = user.count_all

    respose = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }
    return jsonify(respose)

def subjectTeacher():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '

    user_id = current_user.id

    if search_value:
        search_query = f"AND (U.username LIKE '%%{search_value}%%' OR U.email LIKE '%%{search_value}%%' OR UD.role LIKE '%%{search_value}%%')"
        
    str_query = f'''
        SELECT distinct on (U.username) username,U.*, sub.subject_name, cl.class_name, sec.section as section_name, UD.grade, UD.role, UD.stream, count(*) OVER() AS count_all, U.id AS user_id
        FROM public."User" AS U
        JOIN public.user_detail AS UD ON U.id = UD.user_id
        LEFT JOIN public.class cl ON cl.class_id = UD.grade
        LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
        LEFT JOIN public.section_subject ss ON UD.subject = ss.section_subject_id
        LEFT JOIN public.tbl_subjects sub ON UD.subject = sub.subject_code
        WHERE UD.stream = %s OR U.type = %s
    ''' + search_query + f'''
        LIMIT {row_per_page} OFFSET {row}
    '''

    subject_teacher = connection.execute(str_query, 'subject_teacher', 'Subject Teacher').fetchall()

    data = []
    count = 0

    for index, user in enumerate(subject_teacher):
        formatted_dob = user.DOB.strftime("%d %b %Y") if user.DOB else ""
        data.append({
            'sl': index + 1,
            'cid': user.CID,
            'section_name': user.section_name,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'dob': formatted_dob,
            'subject': user.subject_name,
            'class_name': user.class_name,
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

 
#  editing the userlist
def edit_the_sub_teacher(id):
    user_id = id  # pass the user_id as a parameter

    # SQL query to retrieve user data with subject, class, and section details
    str_query = '''
    SELECT U.*, 
    sub.subject_name, sub.subject_code, cl.class_name, 
    sec.section, sec.section_id, UD.section_no, UD.grade, UD.role, 
    U.id AS user_id
    FROM public."User" AS U
    JOIN public.user_detail AS UD ON U.id = UD.user_id 
    LEFT JOIN public.class cl ON cl.class_id = UD.grade
    LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
    LEFT JOIN public.tbl_subjects sub ON UD.subject = sub.subject_code
    WHERE U.id = %s
    '''
    print('ThisID', id)

    # Execute the SQL query to fetch user data
    user_data = engine.execute(str_query, user_id).fetchone()

    if user_data:
        sections_query = '''SELECT U.*, sub.subject_name, sub.subject_code,cl.class_name, sec.section,sec.section_id, UD.section_no, UD.grade, UD.role, U.id as user_id, UD.id
            FROM public."User" AS U
            JOIN public.user_detail as UD ON U.id = UD.user_id
            LEFT JOIN public.class cl ON cl.class_id = UD.grade
            LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
            LEFT JOIN public.tbl_subjects sub ON UD.subject = sub.subject_code WHERE U.id = %s AND UD.stream = %s'''
        sections = engine.execute(sections_query, user_id, 'subject_teacher').fetchall()
        sections = [{'class_id':row.grade,'class':row.class_name,'section_id': row.section_id, 'section_name': row.section, 'subject_id':row.subject_code, 'subject_name':row.subject_name, 'user_detail_id':row.id} for row in sections]
        # class_id = user_data['class_id']  # Assuming 'class_id' is the correct attribute name
        user_info = {
            'cid': user_data.CID,
            'username': user_data.username,
            'full_name': user_data.full_name,
            'email': user_data.email,
            'dob': user_data.DOB,
            'subject': user_data.subject_name,
            'class_name': user_data.class_name,
            'section': user_data.section,
            'section_id' : user_data.section_id,
            'subject_id' : user_data.subject_code,
            'grade': user_data.grade,
            'role': user_data.role,
            'id': user_data.user_id,
        }
        dob = user_info['dob']
        try:
            user_info['dob'] = user_info['dob'].strftime('%Y-%m-%d')
        except AttributeError:
            # Handle the case where DOB is not in the expected format
            pass
        return jsonify({"data": user_info, "sections": sections, "dob":dob})
    else:
        return jsonify({"error": "User not found"})

def edit_the_user(id):
    user_id = id  # pass the user_id as a parameter

    # SQL query to retrieve user data with subject, class, and section details
    str_query = '''
    SELECT U.*, 
    sub.subject_name, sub.subject_code, cl.class_name, 
    sec.section, sec.section_id, UD.section_no, UD.grade, UD.role, 
    U.id AS user_id
    FROM public."User" AS U
    JOIN public.user_detail AS UD ON U.id = UD.user_id AND U.user_id::uuid = UD.id
    LEFT JOIN public.class cl ON cl.class_id = UD.grade
    LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
    LEFT JOIN public.tbl_subjects sub ON UD.subject = sub.subject_code
    WHERE U.id = %s
    '''
    print('ThisID', id)

    # Execute the SQL query to fetch user data
    user_data = engine.execute(str_query, user_id).fetchone()

    if user_data:
        sections_query = '''SELECT * FROM public.user_detail AS ud 
                            INNER JOIN public."User" AS uu ON uu.id = ud.user_id
                            INNER JOIN public.class AS cc ON cc.class_id = ud.grade 
                            INNER JOIN public.std_section AS ss ON ss.section_id = ud.section_no 
                            INNER JOIN public.tbl_subjects AS ts ON ts.subject_code = ud.subject WHERE ud.user_id = %s 
                            AND ud.stream = %s'''
        sections = engine.execute(sections_query, user_id, "subject_teacher").fetchall()
        sections = [{'class_id':row.grade,'class':row.class_name,'section_id': row.section_id, 'section_name': row.section, 'subject_id':row.subject_code, 'subject_name':row.subject_name, 'user_detail_id':row.id} for row in sections]
        # class_id = user_data['class_id']  # Assuming 'class_id' is the correct attribute name
        user_info = {
            'cid': user_data.CID,
            'username': user_data.username,
            'full_name': user_data.full_name,
            'email': user_data.email,
            'dob': user_data.DOB,
            'subject': user_data.subject_name,
            'class_name': user_data.class_name,
            'section': user_data.section,
            'section_id' : user_data.section_id,
            'subject_id' : user_data.subject_code,
            'grade': user_data.grade,
            'role': user_data.role,
            'id': user_data.user_id,
        }
        dob = user_info['dob']
        try:
            user_info['dob'] = user_info['dob'].strftime('%Y-%m-%d')
        except AttributeError:
            # Handle the case where DOB is not in the expected format
            pass
        print('final:===', user_info['dob'])
        return jsonify({"data": user_info, "sections": sections, "dob":dob})
    else:
        return jsonify({"error": "User not found"})

def edit_the_sub_user(id):
    user_id = id  # pass the user_id as a parameter

    # SQL query to retrieve user data with subject, class, and section details
    str_query = '''
    SELECT U.*, 
    sub.subject_name, sub.subject_code, cl.class_name, 
    sec.section, sec.section_id, UD.section_no, UD.grade, UD.role, 
    U.id AS user_id
    FROM public."User" AS U
    JOIN public.user_detail AS UD ON U.id = UD.user_id AND U.user_id::uuid = UD.id
    LEFT JOIN public.class cl ON cl.class_id = UD.grade
    LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
    LEFT JOIN public.tbl_subjects sub ON UD.subject = sub.subject_code
    WHERE U.id = %s
    '''
    print('ThisID', id)

    # Execute the SQL query to fetch user data
    user_data = engine.execute(str_query, user_id).fetchone()

    if user_data:
        sections_query = '''SELECT * FROM public.user_detail AS ud 
                            INNER JOIN public."User" AS uu ON uu.id = ud.user_id
                            INNER JOIN public.class AS cc ON cc.class_id = ud.grade 
                            INNER JOIN public.std_section AS ss ON ss.section_id = ud.section_no 
                            INNER JOIN public.tbl_subjects AS ts ON ts.subject_code = ud.subject WHERE ud.user_id = %s 
                            AND ud.stream = %s'''
        sections = engine.execute(sections_query, user_id, "subject_teacher").fetchall()
        sections = [{'class_id':row.grade,'class':row.class_name,'section_id': row.section_id, 'section_name': row.section, 'subject_id':row.subject_code, 'subject_name':row.subject_name, 'user_detail_id':row.id} for row in sections]
        # class_id = user_data['class_id']  # Assuming 'class_id' is the correct attribute name
        user_info = {
            'cid': user_data.CID,
            'username': user_data.username,
            'full_name': user_data.full_name,
            'email': user_data.email,
            'dob': user_data.DOB,
            'subject': user_data.subject_name,
            'class_name': user_data.class_name,
            'section': user_data.section,
            'section_id' : user_data.section_id,
            'subject_id' : user_data.subject_code,
            'grade': user_data.grade,
            'role': user_data.role,
            'id': user_data.user_id,
        }
        dob = user_info['dob']
        try:
            user_info['dob'] = user_info['dob'].strftime('%Y-%m-%d')
        except AttributeError:
            # Handle the case where DOB is not in the expected format
            pass
        print('final:===', user_info['dob'])
        return jsonify({"data": user_info, "sections": sections, "dob":dob})
    else:
        return jsonify({"error": "User not found"})
# fetch user details
def get_user_by_id(id):
    user = connection.execute(
        'SELECT *, U.id as user_id FROM public."User" AS U, public.user_detail as UD WHERE U.id = UD.user_id AND user_id = %s',
        id).first()
    return user
def getSection(gradeId):
    query = text("SELECT section_id, section FROM public.std_section WHERE class_id=:gradeId")
    result = connection.execute(query, gradeId=gradeId)

    # Convert the result into a list of dictionaries
    section = [{'id': row.section_id, 'name': row.section} for row in result]

    # Return the dropdown values as JSON
    return jsonify(section)


def getClasses():
  query = text("SELECT class_id,class_name FROM public.class")
  result = connection.execute(query)
    # Convert the result into a list of dictionaries
  dropdown_values = [
    {'id': row.class_id, 'name': row.class_name}
        for row in result
    ]
    # Return the dropdown values as JSON
  print(dropdown_values,"*****************DropDown Values")
  return jsonify(dropdown_values)
# defining user roles
def user_role():
    con = engine.connect()
    user = con.execute(
        'SELECT UD.role FROM public."User" AS U, public.user_detail as UD WHERE U.id = UD.user_id AND U.username = %s LIMIT 1',
        str(current_user)).fetchone()
    return user['role']


def is_admin():
    if(user_role() == 'admin'):
        return True
    else:
        return False


def is_classTeacher():
    if(user_role() == 'class_teacher' or user_role() == 'Class Teacher & Subject Teacher' ):
        return True
    else:
        return False
   

def is_subjectTeacher():
    if(user_role() == 'subject_teacher'):
        return True
    else:
        return False
        
def is_human_resource():
    if(user_role() == 'human_resource'):
        return True
    else:
        return False

# update the modal
def update_editfunction():
    cid = request.form.get('cid')
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    dob = request.form.get('date')
    role = "class_teacher"
    id = request.form.get('uu_id_id')
    subject = request.form.get('subject')
    grade = request.form.get('grade')
    section = request.form.get('section')
    # uid = current_user.id  # Assuming current_user is correctly populated
    # Update the "User" table
    connection.execute('UPDATE public."User" SET "CID"=%s,username=%s,full_name=%s, email=%s, "DOB"=%s WHERE id=%s',(cid,username,full_name, email, dob, id))
    print("updateQuery_Finished", subject, grade, section, id)
    connection.execute('UPDATE public.user_detail SET grade=%s, section_no=%s, subject=%s WHERE user_id=%s', (grade, section, subject, id))
                # return "Insert has been complete"
    return "Success: User details updated"


class deleteUser:
    def delete_user_by_id(id):
        connection.execute('DELETE FROM public.tbl_student_evaluation WHERE subject_teacher_id = %s', id)
        check_teacher_str ='''Select COUNT(*) from public.user_detail WHERE user_id = %s'''
        check_teacher = connection.execute(check_teacher_str, id).fetchone()
        print("Here Checking ", check_teacher[0], id)
        if check_teacher[0] > 1:
            connection.execute('DELETE FROM public.user_detail WHERE user_id = %s AND stream = %s', id, 'subject_teacher')
            connection.execute('DELETE FROM public."User" WHERE id=%s', id)
            connection.execute('UPDATE public.user_detail SET role = %s WHERE user_id = %s','class_teacher', id)
        else:
            connection.execute('DELETE FROM public.user_detail WHERE user_id = %s AND stream = %s', id, 'subject_teacher')
            connection.execute('DELETE FROM public."User" WHERE id=%s', id)
            pass
        return "done"

class deleteSubjectUser:
    def delete_sub_user_by_id(id):
        connection.execute('DELETE FROM public.tbl_student_evaluation WHERE subject_teacher_id = %s', id)
        check_teacher_str ='''Select COUNT(*) from public.user_detail WHERE user_id = %s'''
        check_teacher = connection.execute(check_teacher_str, id).fetchone()
        print("Here Checking ", check_teacher[0], id)
        if check_teacher[0] > 1:
            connection.execute('DELETE FROM public.user_detail WHERE user_id=%s AND stream =%s ', id, 'subject_teacher')
            connection.execute('UPDATE public.user_detail SET role = %s WHERE user_id = %s','class_teacher', id)
        else:
            connection.execute('DELETE FROM public."User" WHERE id=%s', id)
            connection.execute('DELETE FROM public.user_detail WHERE user_id=%s', id)
        return "done" 

class deletePastPayments:
    def past_payments_del_by_id(id):
        print("Reaching Here", id)
        connection.execute('DELETE FROM public.tbl_acc_detail WHERE id=%s', id)
        return "done" 

import uuid

def save_subTeacher_hr():
    print("Reaching Here!!!")
    id = str(uuid.uuid4())
    # grade = request.form.getlist('grade[]')
    user_id = current_user.id
    cid = request.form.get('cid')
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    dob = request.form.get('date')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
    user_type = 'Class Teacher'
    # # grade_sections_subjects = []
    connection.execute('INSERT INTO public."User" ("id", "username", "email", "password", "full_name", "CID", "DOB", type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',(id, username, email, hash_pass(password), full_name, cid, dob, user_type))

    ip = request.remote_addr

    browser = request.headers.get('User-Agent')

    for key, value in request.form.items():
            if key.startswith('grade['):
                index = key[key.index('[')+1:key.index(']')]
                grade = request.form.get('grade['+str(index)+']')
                section = request.form.get('section['+str(index)+']')
                subject = request.form.get('subject['+str(index)+']')
                #insert query .....

                print(key,'This is the Grade: ', grade, 'This is the section: ', section, 'This is the subject: ', subject)
                user_id = id
                uid = uuid4()
                connection.execute('INSERT INTO public.user_detail ("id", "user_id", "role","stream","grade", "section_no",  "subject", "ip_address", "browser", "created_at") VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s)',
                (uid, user_id, role,"class_teacher", grade,section,subject, ip, browser, datetime.now()))
                user_id_str = '''Select id from public.user_detail where user_id = %s'''
                user_id_id = connection.execute(user_id_str, id).fetchone()
                user_id = str(user_id_id[0])
                connection.execute('UPDATE public."User" SET user_id = %s where id = %s', user_id, id)
    status='User Created'
    send_application_mailUser(username,email,password,status,role)
    return "Class Teacher Successfully Saved!"

def save_subjectTeacher():
    id = str(uuid.uuid4())
    # grade = request.form.getlist('grade[]')
    user_id = current_user.id
    cid = request.form.get('cid')
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    dob = request.form.get('date')
    password = request.form.get('password')
    role = request.form.get('role')
    user_type = 'Subject Teacher'
    check_user = '''SELECT count(*) FROM public."User" WHERE username=%s AND "CID"=%s'''
    user_check_row = connection.execute(check_user,username,cid).fetchone()
    user_count = user_check_row[0]
    tbl_user_id = []
    print("COUNTHERE!----", user_count)
    tbl_user_id_str = '''SELECT id FROM public."User" WHERE "CID" = %s AND username = %s AND email=%s'''
    tbl_user = connection.execute(tbl_user_id_str, cid,username,email).fetchone()
    if tbl_user == None:
        connection.execute('INSERT INTO public."User" ("id", "username", "email", "password", "full_name", "CID", "DOB", type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',(id, username, email, hash_pass(password), full_name, cid, dob, user_type))
    else:
        tbl_user_idd=str(tbl_user[0])
        tbl_user_id.append(tbl_user_idd)
    try:
        tbl_uid = tbl_user_id[0]
    except IndexError:
        pass

    ip = request.remote_addr

    browser = request.headers.get('User-Agent')

    for key, value in request.form.items():
            if key.startswith('grade['):
                index = key[key.index('[')+1:key.index(']')]
                grade = request.form.get('grade['+str(index)+']')
                section = request.form.get('section['+str(index)+']')
                subject = request.form.get('subject['+str(index)+']')
                #insert query .....

                print(key,'This is the Grade: ', grade, 'This is the section: ', section, 'This is the subject: ', subject)
                user_id = id
                uid = uuid4()
                if tbl_user == None:
                    #Inserting for the new user..
                    print("Inserting for the new user")
                    connection.execute('INSERT INTO public.user_detail ("id", "user_id", "role","grade", "section_no",  "subject", "ip_address", "browser", "created_at","stream") VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s,%s)',
                (uid, user_id, role, grade,section,subject, ip, browser, datetime.now(), 'subject_teacher'))
                    user_id_str = '''Select id from public.user_detail where user_id = %s'''
                    user_id_id = connection.execute(user_id_str, id).fetchone()
                    user_id = str(user_id_id[0])
                    print('userIDhere', user_id, id)
                    connection.execute('UPDATE public."User" SET user_id = %s where id = %s', user_id, id)
                else:
                    #Inserting for the already logged user
                    print("Inserting for the already logged user")
                    connection.execute('INSERT INTO public.user_detail ("id", "user_id", "role","grade","stream", "section_no",  "subject", "ip_address", "browser", "created_at") VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s)',
                (uid, tbl_uid, "Class Teacher & Subject Teacher", grade,"subject_teacher",section,subject, ip, browser, datetime.now()))
                    update_str='''UPDATE public.user_detail SET role = 'Class Teacher & Subject Teacher' WHERE user_id=%s'''
                    connection.execute(update_str, tbl_uid)
                    print("Reached Here and the tbl_id:---", tbl_uid)
                    
    status='User Created'
    send_application_mailUser(username,email,password,status,role)

    return "Subject Teacher Successfully Saved!"

def update_edit_subfunction():
    cid = request.form.get('cid')
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    dob = request.form.get('date')
    role = "subject_teacher"
    id = request.form.get('uu_id')
    # Check if the ID is valid
    if id is None:
        return "Error: Invalid user ID"
    for key, value in request.form.items():
        if key.startswith('user_detail_id['):
            index = key[key.index('[') + 1:key.index(']')]
            grade = request.form.get('grade[' + str(index) + ']')
            section = request.form.get('section[' + str(index) + ']')
            subject = request.form.get('subject[' + str(index) + ']')
            uid = current_user.id  # Assuming current_user is correctly populated
            user_detail_id = request.form.get('user_detail_id['+str(index)+']')
            print("USER_ID:", user_detail_id)
            # Update the "User" table
            connection.execute('UPDATE public."User" SET "CID"=%s,username=%s,full_name=%s, email=%s, "DOB"=%s WHERE id=%s',(cid,username,full_name, email, dob, id))
            new_id = uuid4()
            #Do from here on out 30//04/2024
            if user_detail_id == '':
                connection.execute('INSERT INTO public.user_detail (id, user_id, role, grade, section_no, subject) VALUES (%s, %s, %s, %s, %s,%s)', (new_id, id, role, grade, section, subject))
                #insert to user detail table --- 
            else:
                 # Update the "user_detail" table
                connection.execute('UPDATE public.user_detail SET role=%s, grade=%s, section_no=%s, subject=%s WHERE id=%s', (role, grade, section, subject, user_detail_id))
                # return "Insert has been complete"
    return "Success: User details updated"

def past_payment():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '

    user_id = current_user.id

    if search_value:
        search_query = f"AND (ad.acc_holder LIKE '%%{search_value}%%' OR ad.date_added LIKE '%%{search_value}%%' OR ad.f_name LIKE '%%{search_value}%%' OR sp.parent_cid LIKE '%%{search_value}%%')"
        
    str_query = f'''
         SELECT *,ad.id as ad_id,sp.*,count(*) OVER() AS count_all FROM public.tbl_acc_detail AS ad INNER JOIN public.tbl_students_personal_info AS sp ON ad.std_cid = sp.student_cid
    ''' + search_query + f'''
        LIMIT {row_per_page} OFFSET {row}
    '''

    past_payment = connection.execute(str_query).fetchall()

    data = []
    count = 0

    for index, user in enumerate(past_payment):
        timestamp_str = "2024-04-08 16:51:06.766553+06"
        # Remove the timezone offset before parsing
        timestamp_str_no_offset = timestamp_str[:-6]
        timestamp_obj = datetime.strptime(timestamp_str_no_offset, "%Y-%m-%d %H:%M:%S.%f")

        # Convert to a normal date and time format
        normal_format = timestamp_obj.strftime("%Y-%m-%d %H:%M:%S")                                                                                                  
        full_name = f"{user.f_name} {user.l_name}"
        data.append({
            'sl': index + 1,
            'parent_cid': user.parent_cid,
            'amount': user.amount,
            'acc_holder': user.acc_holder,
            'paymentmodes': user.paymentmodes,
            'name': full_name,
            'std_class': user.std_class,
            'date_added': normal_format,
            'screen_shot': user.screen_shot,
            'ad_id': user.ad_id
        })
        count = user.count_all

    response = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }

    return jsonify(response)

def application_update_hr():
    print("See Here")
    status = request.form.get('action')
    narration = request.form.get('narration')
    id = request.form.get('app_id')
    user_mail = request.form.get('email')
    name = engine.execute("SELECT CONCAT(first_name, ' ', last_name) FROM tbl_students_personal_info WHERE ID=%s", (id,))
    full_name = name.fetchone()
    # reject
    #approved
    #reject For Amendment
    if(status == 'reject'):
        # reject
        connection.execute('UPDATE public.tbl_students_personal_info SET status=%s,  narration=%s, updated_at=%s, rejected_at=%s WHERE id=%s',
                    status, narration, datetime.now(), datetime.now(), id)
    elif (status=='reject For Amendment'):
        #reject for Amendment
        connection.execute('UPDATE public.tbl_students_personal_info SET status=%s,  narration=%s, updated_at=%s, rejectforamend_at=%s WHERE id=%s',
                    status, narration, datetime.now(), datetime.now(), id)    
    else:
        # approved
        print("reachedHere!!")
        connection.execute('UPDATE public.tbl_students_personal_info SET status=%s, narration=%s, updated_at=%s, approved_at=%s WHERE id=%s',
                    status, narration, datetime.now(), datetime.now(), id)
    classId='''select cl.class_name from public.tbl_students_personal_info std
    join public.tbl_academic_detail ac on std.id=ac.std_personal_info_id
	join public.class cl on ac.admission_for_class=cl.class_id 
	where std.id=%s'''
    print("Herebro!!!___!!")
    getClass=connection.execute(classId,id).scalar()
    send_application_mail(full_name, status, getClass,narration, user_mail)
    
    return 'success'