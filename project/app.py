import sqlite3 as sql
from functools import wraps
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from passlib.apps import custom_app_context as passHash
from SQL_execute import dict_factory, GetData

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = set(['jpg','jpeg','gif'])

app = Flask( __name__)
app.secret_key = 'ensta'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def login_required(f):
	@wraps(f)
	def fn( *args, **kwargs):
		if 'username' not in session:
			return redirect( url_for('login'))
		return f( *args, **kwargs)
	return fn

@app.route('/')
def index():
	return render_template( 'index.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
	if request.method == 'GET':
		return render_template( 'login.html')
	else:
		try:
			enteredPassword = request.form['password']
			username = request.form['username']

			con = sql.connect('ensta.db')
			con.row_factory = sql.Row

			cur = con.cursor()
			data = cur.execute('SELECT * FROM users WHERE username=?',(username,))
			data = data.fetchall()

			storedPassword = data[0]['password'] #Throws IndexError if no entry is found

			con.close()

			if passHash.verify(enteredPassword,storedPassword):
				session['username'] = username
				return redirect(url_for('index'))

			else:
				session['flashErr'] = "Wrong password"
				return render_template('login.html')

		except IndexError as es:
			#print(es)
			session['flashErr'] = "user not found"
			return render_template('login.html')

@app.route('/register', methods = ['POST', 'GET'])
def register():
	if request.method == 'GET':
		return render_template( 'register.html')
	else:
		try:
			firstName = request.form['firstName']
			lastName = request.form['lastName']
			username = request.form['username']
			email = request.form['email']
			birthDate = request.form['birthDate']
			bio = request.form['bio']
			password = passHash.hash(request.form['password'])
			password2 = request.form['password2']
			
# TODO validate passes
			registered = False
			with sql.connect("ensta.db") as con:
				con.row_factory = dict_factory
				cur = con.cursor()

				cur.execute("SELECT * from users where username=? OR email=?",(username,email))
				users = cur.fetchall()
				if users:
					print("already!")
					registered = False
					alreadyUser = True
				else:
					cur.execute("insert into users (firstName,lastName,username,birthDate,bio,email,password) values (?,?,?,?,?,?,?)", (firstName,lastName,username,birthDate,bio,email,password))
					con.commit()
					registered = True
					alreadyUser = False
		except:
			con.rollback()
			msg = "Error"
		finally:
			con.close()
			if registered:
				session['username'] = username
				return redirect(url_for('index'))
			else:
				return redirect(url_for('register'))
			# elif for akreadyUser

@app.route('/logout')
def logout():
	# remove user from session
	session.pop('username',None)
	return redirect( url_for('index'))

if __name__ == "__main__":
	app.run( debug=True)

