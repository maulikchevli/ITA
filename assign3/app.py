import os
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

@app.route('/search/<query>')
@login_required
def search(query):
	res = {'posts':[], 'users':[]}

	con = sql.connect('ensta.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	if query[0] == '#':
		query = query[1:]
		
		users = cur.execute('select username from users');
		users = users.fetchall()

		for user in users:
			post = cur.execute('select pid,tags from posts where username=?', (user['username'],))
			post = post.fetchall()

			if post:
				if query in post[0]['tags']:
					res['posts'].append(post[0]['pid'])

	else:
		users = cur.execute('select username,firstname,lastname from users');
		users = users.fetchall()
	
		for user in users:
			if query in user.values():
				res['users'].append(user['username'])

	print( res)
	con.close()
	return jsonify(res)

@app.route('/post', methods = ['POST', 'GET'])
def post():
	if request.method == 'GET':
		return render_template( 'post.html')
	else:
		image = request.files['image']
		title = request.form['title']
		username = session['username']
		tags = request.form['tags']

		if image:
			filename = secure_filename(image.filename)
			image.save( os.path.join(os.path.join( app.config['UPLOAD_FOLDER'], username), filename))

		try:
			with sql.connect("ensta.db") as con:
				cur = con.cursor()
				cur.execute("insert into posts (username, title, filename, tags) values (?,?,?,?)", (username,title,filename,tags))
				con.commit()
		except:
			con.rollback()
			session['flashErr'] = "Error in sql insertion"
		finally:
			con.close()
			session['flashMsg'] = "Sucess!"
			return redirect( url_for('index'))

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

					# Make folder for images using username
					os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], username))
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

