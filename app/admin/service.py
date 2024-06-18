import json 
import os
from flask import request, render_template,jsonify, redirect
from flask_login import current_user
from datetime import datetime
import app
from config import Config
from flask_mail import Message
from app import mail
from sqlalchemy import create_engine,text,null
from app.admin.util import hash_pass
from uuid import uuid4
from random import randint
from cryptography.fernet import Fernet,InvalidToken
from urllib.parse import quote

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
random_id = randint(000, 999)

def save_user_table(password):
    id = uuid4()
    username = request.form['username']
    email = request.form['email']
    full_name = request.form['full_name']
    cid = request.form['cid']
    password = request.form['password']
    email = request.form['email']
    username = request.form['username']
    dob = request.form['date']
    saved = connection.execute('INSERT INTO public."User" ("id","username", "full_name", "email", "password", "CID", "DOB") VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id', (id,username, full_name, email, hash_pass(password), cid, dob))
    user_id = saved.fetchone()
    print(user_id, "returning************")
    return user_id['id']

def save_user_table_list(user_id, password):
    id = uuid4()
    role = request.form['role']
    full_name = request.form['full_name']
    cid = request.form['cid']
    password = request.form['password']
    email = request.form['email']
    username = request.form['username']
    dob = request.form['date']
    print('CID_DOB:', full_name, cid, dob, password)
    ip = request.remote_addr
    browser = request.headers.get('User-Agent')
    connection.execute(
        'INSERT INTO public.user_detail ("id", "user_id", "role", "ip_address", "browser", "created_at") VALUES (%s, %s, %s, %s, %s, %s)',
        (id, user_id, role, ip, browser, datetime.now())
    )

    getUser = 'SELECT username, email, password FROM public."User" WHERE id = %s'
    userName = connection.execute(getUser, user_id).fetchone()
    email = userName['email']
    user_name = userName['username']
    passwords = userName['password'].tobytes()
    
    getHash = passwords.decode('utf-8')

    status = 'User Created'
    send_application_mailUser(user_name, email, password, status, role)

    return "saved"


#belong to HR page
def save_user_detail_table(user_id, password, role, section, grade, subject):
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
    send_application_mailUser(user_name,email,password,status,role)
    return "saved"

def save_subuser_detail_table(user_id, password, role, section, grade, subject):
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
    send_application_mailUser(user_name,email,password,status,role)
    return "saved"


def send_application_mailUser(user_name, email, password,status, role):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    userUrl = cipher_suite.encrypt(user_name.encode('utf-8'))
    status_code = "User Created"
    reset_url = 'http://127.0.0.1:5000/resetuserPassword?userUrl=' + quote(userUrl) + '&pwd=' + quote(key)
    message='Your user for role '+ role + '''  is created successfully.'''+ "\n"  +'And your default user name and password is:' +"\n"+'User Name: '+ str(user_name)+ "\n"  +'Password: '+str(password)+' . '+ "\n" +'You can visit follwoing link to reset your password:'+"\n"+ reset_url     
    msg = Message(subject='Application Status', sender='uchiadendup@gmail.com',
                recipients=[email])
    print(status,"***STATUS")
    msg.body = "Dear " + str(user_name)+"," + "\n" + str(message) + "\nStatus: " + str(status_code)  
    mail.send(msg)   

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
                "AND U.id = UD.user_id AND UD.role in ('admin', 'human_resource') LIMIT " + row_per_page + " OFFSET " + row + ""

    users = connection.execute(str_query).fetchall()

    data = []
    count = 0
    for index, user in enumerate(users):
        formatted_dob = user.DOB.strftime("%d %b %Y") if user.DOB else ""
        data.append({'sl': index + 1,
                     'cid': user.CID,
                     'username': user.username,
                     'full_name': user.full_name,
                     'email': user.email,
                     'dob': formatted_dob,
                     'role': user.role,
                     'id': user.user_id})
        count = user.count_all
    print(data, 'THISONEYO')

    respose = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }

    return respose

# fetch user details

def get_user_by_id(id):
    user = connection.execute(
        'SELECT *, U.id as user_id FROM public."User" AS U, public.user_detail as UD WHERE U.id = UD.user_id AND user_id = %s',
        id).first()
    return user

def getSection(gradeId):
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


def getSubjects(sectionId):
    try:
        sectionId = int(sectionId)
    except ValueError:
        return jsonify({'error': 'Invalid sectionId'}), 400
    query=text("SELECT sub.subject_code,sub.subject_name FROM public.section_subject secSub \
            LEFT JOIN public.tbl_subjects sub \
            ON secSub.subject_id=sub.subject_code \
            WHERE secSub.section_id=:sectionId")
    result = connection.execute(query, sectionId=sectionId)

    # Convert the result into a list of dictionaries
    subject = [{'id': row.subject_code, 'name': row.subject_name} for row in result]
    print(subject,"_________GetSubjects_____________")


    # Return the dropdown values as JSON
    return jsonify(subject)


def edit_the_user(id):
    data = connection.execute('SELECT *, U.id FROM public."User" as U '\
        'inner join public.user_detail as ud on U.id = ud.user_id WHERE U.id=%s', id).fetchone()
    final = []
    final.append({'username': data.username,
                    'email': data.email,
                    'role':data.role,
                    'id': data.id})
    return jsonify({"data": final})

def getClasses():
  query = text("SELECT class_id,class_name FROM public.class")
  result = connection.execute(query)
    # Convert the result into a list of dictionaries
  dropdown_values = [
    {'id': row.class_id, 'name': row.class_name}
        for row in result
    ]
    # Return the dropdown values as JSON
  sorted_dropdown_values = sorted(dropdown_values, key=lambda x: x['name'])

  print(dropdown_values,"*****************DropDown Values")
  return jsonify(sorted_dropdown_values)
# defining user roles

def user_role():
    if current_user.is_authenticated:
        user = connection.execute(
            'SELECT UD.role FROM public."User" AS U, public.user_detail as UD WHERE U.id = UD.user_id AND U.username = %s LIMIT 1',
            str(current_user)).fetchone()
        if user is not None:
            return user['role']
        else:
            # Handle the case when the user is authenticated but the role is not found
            # You can return a default role or redirect to an appropriate page
            return redirect('User not found')
    else:
        return redirect('login-user')


def is_admin():
    if(user_role() == 'admin'):
        return True
    else:
        return False


def is_classTeacher():
    if(user_role() == 'class_teacher' or user_role() == 'Class Teacher & Subject Teacher'):
        return True
    else:
        return False
   
def is_subjectTeacher(): 
    if(user_role() == 'subject_teacher' or user_role() == 'Class Teacher & Subject Teacher' ):
        return True
    else:
        return False
        
def is_human_resource():
    if(user_role() == 'human_resource'):
        return True
    else:
        return False

def all_std():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ''
    params = {}

    if search_value:
        search_query = "AND (cc.class_name LIKE :search_value " \
                    "OR P.student_cid LIKE :search_value " \
                    "OR (P.first_name || ' ' || P.last_name) LIKE :search_value " \
                    "OR P.status LIKE :search_value) "
        params['search_value'] = f"%{search_value}%"


    str_query = f'''SELECT P.*, COUNT(*) OVER() AS count_all, P.id, cc.class_name 
                    FROM public.tbl_students_personal_info AS P
                    INNER JOIN public.tbl_academic_detail AS A ON P.id = A.std_personal_info_id
                    INNER JOIN public.class AS cc ON A.admission_for_class = cc.class_id 
                    WHERE P.id IS NOT NULL {search_query}
                    ORDER BY status DESC 
                    LIMIT :limit OFFSET :offset'''

    params['limit'] = int(row_per_page)
    params['offset'] = int(row)

    users_std = connection.execute(text(str_query), params).fetchall()

    data = []
    count = 0
    for index, user in enumerate(users_std):
        data.append({
            'sl': int(row) + index + 1,
            'student_code': user.student_code,
            'student_cid': user.student_cid,
            'class': user.class_name,
            'first_name': user.first_name + " " + user.last_name,
            'student_email': user.student_email,
            'status': user.status,
            'id': user.id
        })
        count = user.count_all

    response_std = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }
    return jsonify(response_std)


def application_update():
    status = request.form.get('action')
    narration = request.form.get('narration')
    id = request.form.get('app_id')
    user_mail = request.form.get('email')
    full_name = engine.execute("SELECT CONCAT(first_name, ' ', last_name) FROM tbl_students_personal_info WHERE ID=%s", (id,))
    name = full_name.fetchone()
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
        connection.execute('UPDATE public.tbl_students_personal_info SET status=%s, narration=%s, updated_at=%s, approved_at=%s WHERE id=%s',
                    status, narration, datetime.now(), datetime.now(), id)
    classId='''select cl.class_name from public.tbl_students_personal_info std
    join public.tbl_academic_detail ac on std.id=ac.std_personal_info_id
	join public.class cl on ac.admission_for_class=cl.class_id 
	where std.id=%s'''
    print("Herebro!!!___!!")
    getClass=connection.execute(classId,id).scalar()
    send_application_mail(name, status, getClass,narration, user_mail)
    
    return 'success'


def send_application_mail(name, status, getClass, narration, user_mail):
    if status == "submitted":
        status_code = "Submitted"
        message='Your application for class '+ getClass+ ''' in Ugyen Academy is successfully submitted. Thank you.'''           
    elif status == 'reject':
        status_code = "Rejected"
        message = "We are sorry to inform you that your application has been rejected , Thank you."
    elif status=='reject For Amendment':
        status_code="Rejected for Amendment"
        message = "We are sorry to inform you that your application is returned for amendment to update informtaion."
    else:
        status_code = "Approved"
        message='Your admission for class '+ getClass+ ''' in Ugyen Academy is approved. Kindly do the following needful within 7 working days.\n 1. Payment for confirmation of seats(10% of fees)\n 2. Update the payment details online(http://127.0.0.1:5000/fees-detail) \n 3. For any enquiry, kindly contact at : 17467322. Thank you.'''
    msg = Message(subject='Application Status', sender='karma123karma456@gmail.com',
                recipients=[user_mail])
    print(status,"***STATUS")
    if status == "submitted":
     msg.body = "Dear " + str(name) + "\n" + str(message) + "\nStatus: " + str(status_code)
     print(msg,"***MESAGE",msg.body,'**BODY')
    else: 
     msg.body = "Dear " + str(name) + "\n" + str(message) + "\nStatus: " + str(status_code) + "\nMessage: " + str(narration)  
    mail.send(msg)   

# user Enquires
def user_quries():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '
    if (search_value != ''):
        search_query = "AND (full_name LIKE '%%" + search_value + "%%' " \
            "OR user_email LIKE '%%" + search_value + "%%' "\
            "OR phone_no LIKE '%% " + search_value+"%%') "
            

    str_query = 'SELECT *, count(*) OVER() AS count_all, id FROM public.tbl_contact_form WHERE id IS NOT NULL  '\
                '' + search_query + '' \
                "LIMIT " + \
        row_per_page + " OFFSET " + row + ""

    users_query = connection.execute(str_query).fetchall()

    data = []
    count = 0
    for index, user in enumerate(users_query):
        data.append({'sl': index + 1,
                     'full_name': user.full_name,
                     'user_email': user.user_email,
                     'phone_no': user.phone_no,
                     'comment': user.comment,
                     'id': user.id})
        count = user.count_all

    respose_query = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }
    return respose_query
 
#  editing the userlist
def edit_the_user(id):
    data = connection.execute('SELECT *, U.id FROM public."User" as U '\
        'inner join public.user_detail as ud on U.id = ud.user_id WHERE U.id=%s', id).fetchone()
    final = []
    final.append({'cid': data.CID,
                'username': data.username,
                  'full_name':data.full_name,
                    'email': data.email,
                    'dob': data.DOB,
                    'role':data.role,
                    'id': data.id})
    dob = final[0]['dob']
    try:
        final[0]['dob'] = final[0]['dob'].strftime('%Y-%m-%d')
    except AttributeError:
        # Handle the case where DOB is not in the expected format
        pass
    print('final:===', final[0]['dob'])
    return jsonify({"data": final})

# update the modal
def update_editfunction():
    # Get data from the form
    username = request.form.get('username')
    email = request.form.get('email')
    role = request.form.get('role')
    full_name = request.form.get('full_name')
    cid = request.form.get('cid')
    dob = request.form.get('dob')
    id = request.form.get('u_id')

    # Update the User table
    connection.execute('UPDATE  public."User" SET username=%s, email=%s, "CID"=%s, full_name=%s,"DOB"=%s WHERE id=%s',username,email,cid,full_name,dob, id )

    # Update the user_detail table
    connection.execute('UPDATE  public.user_detail SET role=%s WHERE user_id=%s',
                        role, id )

    # Return a success message
    return "success"

class deleteUser:
    @staticmethod
    def delete_user_by_id(id):
        try:

            # Delete from tbl_academic_detail
            delete_academic_detail = connection.execute('DELETE FROM public."tbl_academic_detail" WHERE  std_personal_info_id=%s', id)
            
            # Delete from tbl_students_personal_info
            delete_personal_info = connection.execute('DELETE FROM public."tbl_students_personal_info" WHERE id=%s', id)
            
            
            # Commit the changes to the database
            connection.commit()
            
            return "done"
        except Exception as e:
            # Handle any exceptions, e.g., log the error or return an error message
            return str(e)

class deleteadminuser:
    @staticmethod
    def delete_admin_user(id):
        try:
            # Delete from tbl_students_personal_info
            delete_User = connection.execute('DELETE FROM public."User" WHERE id=%s', id)
                        
            # Commit the changes to the database
            connection.commit()
            return "done"
        except Exception as e:
            # Handle any exceptions, e.g., log the error or return an error message
            print("This is the error being caused: ", e)
            return str(e)
        

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
        SELECT U.username, U.email, sub.subject_name, cl.class_name, sec.section, UD.grade, UD.role, count(*) OVER() AS count_all, U.id AS user_id
        FROM public."User" AS U
        JOIN public.user_detail AS UD ON U.id = UD.user_id
        LEFT JOIN public.class cl ON cl.class_id = UD.grade
        LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
        LEFT JOIN public.section_subject ss ON UD.subject = ss.section_subject_id
        LEFT JOIN public.tbl_subjects sub ON ss.subject_id = sub.subject_code
        WHERE U.type IS NULL AND UD.role = %s
    ''' + search_query + f'''
        LIMIT {row_per_page} OFFSET {row}
    '''

    subject_teacher = connection.execute(str_query, 'subject_teacher').fetchall()

    data = []
    count = 0

    for index, user in enumerate(subject_teacher):
        data.append({
            'sl': index + 1,
            'username': user.username,
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
        "aaData": data,
    }

    return jsonify(response)

def get_std_id(id):
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
    return render_template('/pages/student-applications/print.html', std=std_details, std_info=std_info)


def save_std_slot():
    try:
        # Access form data from the request
        class7 = request.form['class7']
        class8 = request.form['class8']
        class9 = request.form['class9']
        class10 = request.form['class10']
        class11_Arts = request.form['class11Arts']
        class11_Com = request.form['class11Commerce']
        class11_Sci = request.form['class11Science']
        class12_Arts = request.form['class12Arts']
        class12_Com = request.form['class12Commerce']
        class12_Sci = request.form['class12Science']

        # Insert a new record
        id = str(uuid4())
        saved = engine.execute(
        text('UPDATE public."tbl_std_slots" SET class7 = :class7, class8 = :class8, class9 = :class9, class10 = :class10, class11_Arts = :class11_Arts, class11_Com = :class11_Com, class11_Sci = :class11_Sci, class12_Arts = :class12_Arts, class12_Com = :class12_Com, class12_Sci = :class12_Sci WHERE id = :id RETURNING id'),
        {'id': '7245b788-1c16-4afa-a934-073f8dcf68d4', 'class7': class7, 'class8': class8, 'class9': class9, 'class10': class10, 'class11_Arts': class11_Arts, 'class11_Com': class11_Com, 'class11_Sci': class11_Sci, 'class12_Arts': class12_Arts, 'class12_Com': class12_Com, 'class12_Sci': class12_Sci}
    )

        std_slot_id = saved.fetchone()
        return f"Data submitted successfully with ID: {std_slot_id['id']}"

    except Exception as e:  
        return f"Error: {str(e)}"

def get_std_slot():
    try:
        # Execute the SQL query to retrieve data from the std_slots table
        result = engine.execute('SELECT id, class7, class8, class9, class10, class11_arts, class11_com, class11_sci, class12_arts, class12_com, class12_sci FROM public."tbl_std_slots"')

        # Fetch all rows from the result
        rows = result.fetchall()

        # Process the retrieved data and format it as a list of dictionaries
        data = []
        for row in rows:
            slot_data = {
                'id': (row['id']),  # Convert UUID to string
                'class7': row['class7'],
                'class8': row['class8'],
                'class9': row['class9'],
                'class10': row['class10'],
                'class11_arts': row['class11_arts'],
                'class11_com': row['class11_com'],
                'class11_sci': row['class11_sci'],
                'class12_arts': row['class12_arts'],
                'class12_com': row['class12_com'],
                'class12_sci': row['class12_sci'],
            }
            data.append(slot_data)

        return jsonify(data)

    except Exception as e:
        response = {
            'error': f"Error: {str(e)}"
        }
        return jsonify(response)

def update_std_slot():
    try:
        # Access form data from the request
        class7 = request.form['editClass7']

        class8 = request.form['editClass8']
        class9 = request.form['editClass9']
        class10 = request.form['editClass10']
        class11_Arts = request.form['editClass11_arts']
        class11_Com = request.form['editClass11_com']
        class11_Sci = request.form['editClass11_sci']
        class12_Arts = request.form['editClass12_arts']
        class12_Com = request.form['editClass12_com']
        class12_Sci = request.form['editClass12_sci']

        # Get the ID from the form
        id = request.form.get('id')

        # Update the existing record
        connection.execute(
        text('UPDATE public."tbl_std_slots" SET class7 = :class7, class8 = :class8, class9 = :class9, class10 = :class10, class11_Arts = :class11_Arts, class11_Com = :class11_Com, class11_Sci = :class11_Sci, class12_Arts = :class12_Arts, class12_Com = :class12_Com, class12_Sci = :class12_Sci WHERE id = :id'),
        {'id': '7245b788-1c16-4afa-a934-073f8dcf68d4', 'class7': class7, 'class8': class8, 'class9': class9, 'class10': class10, 'class11_Arts': class11_Arts, 'class11_Com': class11_Com, 'class11_Sci': class11_Sci, 'class12_Arts': class12_Arts, 'class12_Com': class12_Com, 'class12_Sci': class12_Sci})
        return jsonify({"success": True, "message": f"Data updated successfully for ID: {id}"})

    except Exception as e:  
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)

class delete_slot:
    def delete_slot(id):
        delete = connection.execute('DELETE FROM public."tbl_std_slots" WHERE id=%s', id)
        return "done"

def deleteFeedback(id):
        connection.execute('DELETE FROM public."tbl_contact_form" WHERE id=%s', id)

        return "done"

import uuid

def save_subTeacher():
    id = str(uuid.uuid4())
    #ss
    print("ADMIN")
    # grade = request.form.getlist('grade[]')
    user_id = current_user.id
    cid = request.form.get('cid')
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    dob = request.form.get('date')
    password = request.form.get('password')
    role = request.form.get('role')
    # # grade_sections_subjects = []
    connection.execute('INSERT INTO public."User" ("id", "username", "full_name" , "email", "password", "CID", "DOB") VALUES (%s, %s,%s, %s, %s,%s,%s)',(id, username, full_name, email, hash_pass(password), cid, dob))

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
                connection.execute('INSERT INTO public.teaching_stats ("user_id","username", "password","role", "class_name", "section", "subject_name") VALUES (%s, %s, %s, %s, %s, %s,%s)',(user_id, username, password, role, grade, section, subject))

                uid = uuid4()
                connection.execute('INSERT INTO public.user_detail ("id", "user_id", "role","grade", "section_no",  "subject", "ip_address", "browser", "created_at") VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)',
                (uid, user_id, role, grade,section,subject, ip, browser, datetime.now()))
            
    return "Class Teacher Successfully Saved!"

def update_edit_subfunction():
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    role = "subject_teacher"
    id = request.form.get('uu_id')
    # Check if the ID is valid
    if id is None:
        return "Error: Invalid user ID"
    # Update the "User" table
    connection.execute('UPDATE public."User" SET username=%s, full_name=%s, email=%s WHERE id=%s', (username, full_name, email, id)) 
    for key, value in request.form.items():
        if key.startswith('user_detail_id['):
            index = key[key.index('[') + 1:key.index(']')]
            grade = request.form.get('grade[' + str(index) + ']')
            section = request.form.get('section[' + str(index) + ']')
            subject = request.form.get('subject[' + str(index) + ']')
            uid = current_user.id  # Assuming current_user is correctly populated
            user_detail_id = request.form.get('user_detail_id['+str(index)+']')
            if user_detail_id == '':
                new_id = uuid4()
                connection.execute('INSERT INTO public.user_detail (id, user_id, role, grade, section_no, subject) VALUES (%s, %s, %s, %s, %s,%s)', (new_id, id, role, grade, section, subject))
                print("For insering the new data")
            else:
                 # Update the "user_detail" table
                connection.execute('UPDATE public.user_detail SET role=%s, grade=%s, section_no=%s, subject=%s WHERE user_id=%s', (role, grade, section, subject, id))
    return "Success: User details updated"
