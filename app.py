from flask import Flask,redirect,render_template,url_for,session,request,flash
import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.wegsxzwhrdhqsvkuqweg:codexhusseinmartinnkya@aws-1-eu-central-1.pooler.supabase.com:5432/postgres",
)


app=Flask(__name__)
app.secret_key='mysecrete123'

@app.route('/')
def home():
    if 'username' in session:
        return render_template('new-entry.html',username=session['username'])

    return redirect(url_for('login')) 

@app.route('/login',methods=['GET','POST'])
def login():
    error=None
    if request.method == 'POST':
        

        username=request.form['username']
        passcode=request.form['password']

        users=user(username)
        
        if users and passcode==users['password']:
          session['username']=username
          return redirect(url_for('home',username=username))

        else:
            error="Invalid username or password!"


    return render_template('login.html',error=error)
@app.route('/new',methods=['GET','POST'])

def user(username):
    sql="""

     SELECT username,password
     FROM asset_login
    WHERE username=%s

"""
    try:
        with psycopg2.connect(DATABASE_URL,sslmode="require") as conn:
            with conn.cursor() as cur:
                cur.execute(sql,(username,))
                row=cur.fetchone()
        if row:
            return{'username':row[0],'password':row[1]}         

        return None
    
    except Exception as e:
        print(e)
        return None

def new_record():
 if request.method=='POST':
     uname=request.form['uname']
     usersj=request.form['usersj']
     deskno=request.form['deskno']
     chairno=request.form['chairno']
     level=request.form['level']
     stream=request.form['stream']

     values=[uname,usersj,deskno,chairno,level,stream]
     
     success,error=insert_patient_to_furndb(values)

     if success:
         return render_template('success.html',uname=uname)
     else:
         print(error)
         return render_template('error.html',uname=uname)
     
 return render_template('new-entry.html')



def insert_patient_to_furndb(values_tuple):
        sql= """
             INSERT INTO furndb(username,usersj,deskno,chairno,level,stream)
              VALUES (%s, %s, %s,%s,%s,%s)
              

    ON CONFLICT (username) 
DO UPDATE SET 
    usersj = EXCLUDED.usersj,
    deskno = EXCLUDED.deskno,
    chairno = EXCLUDED.chairno,
    level = EXCLUDED.level,
    stream = EXCLUDED.stream;

           
             """        
        try:
        # Using sslmode="require" for Supabase
         with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values_tuple)
                # conn.commit() is automatic when using with-block unless an exception occurs
         return True, None
        except Exception as e:
         return False, str(e)
 

@app.route('/access', methods=['GET', 'POST'])
def access():
    if request.method == 'POST':
        level = request.form['level']
        stream = request.form['stream']
        value = [level, stream]

        rows, error = fetch_students(value)

        if rows is not None:
            return render_template(
                'Access-record.html',
                data=rows,
                level=level,
                stream=stream
            )
            flash(f"{len(rows)} records found.", "success")
        else:
            return render_template('error.html', error=error)

    # GET request (first time page loads)
    return render_template('Access-record.html', data=[])

def fetch_students(value):
    sql = """
    SELECT username, usersj, deskno, chairno, level, stream
    FROM furndb
    WHERE level=%s AND stream=%s
    ORDER BY username ASC
    """
    try:
        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, value)
                rows = cur.fetchall()
                return rows, None
    except Exception as e:
        return None, str(e)

@app.route('/delete',methods=['GET','POST'])
def delete_page():
     if request.method == 'POST':
        level = request.form['level']
        stream = request.form['stream']
        value = [level, stream]

        rows, error = fetch_students(value)

        if rows is not None:
            return render_template(
                'Delete-record.html',
                data=rows,
                level=level,
                stream=stream
            )
        else:
            return render_template('error.html', error=error)

    # GET request (first time page loads)
     return render_template('Delete-record.html', data=[])



@app.route('/delete_selected', methods=['POST'])
def delete_selected():
    usernames = request.form.getlist('delete_ids')  # FIXED

    if usernames:
        sql = "DELETE FROM furndb WHERE username = ANY(%s)"
        try:
            with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (usernames,))
        except Exception as e:
            print(e)

    return redirect(url_for('delete_page'))  # FIXED





@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)