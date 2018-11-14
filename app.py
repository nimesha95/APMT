from flask import Flask, render_template,request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb

import bcrypt

from forms import SignupForm, LoginForm, TaskForm, ProjectForm

import yaml

import sys

app = Flask(__name__)

#Configure DB
db = yaml.load (open('db.yaml'))
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/index')
def main():
    return render_template('dashboard.html')

@app.route('/signup', methods= ['GET','POST'])
def signup():
    
    form = SignupForm(request.form)
    
    if request.method  == 'GET':
        #Fetch data
        userDetails = request.form

        username = userDetails['username']
        email = userDetails['email']
        password = userDetails['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT `UserId` FROM `user`")
        #maxid = cur.fetchone()
        cur.execute ("INSERT INTO `user`(`UserName`, `Email`, `Password`) VALUES (%s, %s, %s)",(username ,email, hash_password ))
        mysql.connection.commit()

        session['name'] = username
        session['email'] = email

        cur.close()

        return redirect(url_for('main' )) 
    else:
        #use the below function to see the errors in validation
        print(form.errors)
        return render_template('signup.html' , form = form )
        
@app.route('/', methods= ['GET','POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':

        userDetails1 = request.form

        #email = form.email.data
        #password = (form.password.data).encode('utf-8')
        email =userDetails1['email']
        password = userDetails1['pass'].encode('utf-8')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute ("SELECT * FROM `user` WHERE Email= %s",(email,))
        user = cur.fetchone()
        cur.close() 
        
        if (user):
            
            if(bcrypt.hashpw(password,user['Password'].encode('utf-8'))== user['Password'].encode('utf-8')):
                return redirect(url_for('main'))
                
            else:
                return redirect(url_for('login'))

        else:
            return redirect(url_for('login'))     

    else:
        return render_template('login.html', form = form)

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/table-list')
def tableList():
    cur = mysql.connection.cursor()
    resultValue = cur.execute ("SELECT `userId`, `UserName`, `email` FROM `user`")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('tables.html' , userDetails=userDetails)

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/task', methods= ['GET','POST'])
def tasks():
    form =TaskForm()

    if request.method == 'GET': 
        
        task_name = request.args.get('task_name', '')
        project = request.args.get('project', '')
        assignee = request.args.get('assignee', '')
        due_date = request.args.get('due_date', '')
        status = request.args.get('status', '')
        task_description = request.args.get('task_description', '')
    
        cur = mysql.connection.cursor()
        cur.execute ("INSERT INTO `task`(`Task_Name`, `Task_description`, `Due_Date`, `Status`, `Project_Name`, `Assignee`) VALUES (%s, %s, %s, %s, %s, %s)",(task_name, task_description, due_date, status, project, assignee  ))
        mysql.connection.commit()

        cur.close()

        redirect(url_for('project'))

    return render_template('task.html', form=form)

@app.route('/project', methods= ['GET','POST'])
def project():

    form =ProjectForm()

    if request.method == 'GET': 
        
        project_name = request.args.get('project_name', '')
        client_name = request.args.get('client_name', '')
        technology = request.args.get('technology', '')
    
        print(project_name)
        print(client_name)
        print(technology)    
        cur = mysql.connection.cursor()
        cur.execute ("INSERT INTO `project`(`Project_Name`, `Client_Name`, `Technology`) VALUES (%s, %s, %s)",(project_name ,client_name, technology ))
        mysql.connection.commit()

        cur.close()

        return redirect(url_for('main'))

    return render_template('project.html', form=form)

if __name__ == "__main__":
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.run(debug=True)
