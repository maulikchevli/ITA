import os
import sqlite3 as sql
from functools import wraps
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from passlib.apps import custom_app_context as passHash
import math
from SQL_execute import dict_factory, GetData
import analytics

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
			session["flashErr"] = "Please login first!"
			return redirect( url_for('login'))
		return f( *args, **kwargs)
	return fn

@app.route('/')
def index():
	return render_template( 'index.html')

@app.route('/search', methods = ['POST', 'GET'])
@login_required
def search():
	if request.method == "GET":
		return "HEllO"

	else:
		res = {'posts':[], 'users':[]}
		
		query = request.form["query"]
		con = sql.connect('ensta.db')
		con.row_factory = dict_factory
		cur = con.cursor()

		if query == "":
			return

		if query[0] == '#':
			query = query[1:]
			
			users = cur.execute('select username from users');
			users = users.fetchall()

			for user in users:
				posts = cur.execute('select pid,title,tags from posts where username LIKE ?', (user['username'],))
				posts = posts.fetchall()
				for post in posts:
					if query in post['tags']:
						analytics.update_hashtag(query)
						res['posts'].append({'pid':post['pid'], 'title':post['title']})

		else:
			users = cur.execute('select username,firstname,lastname from users');
			users = users.fetchall()
		
			for user in users:
				if query in user.values():
					res['users'].append(user['username'])

		print( res)
		con.close()
		return render_template("search.html", result=res)

@app.route('/profile/<username>', defaults={'page':1, 'filterAtt':[]})
@app.route('/profile/<username>/page/<int:page>', defaults={'filterAtt':[]})
@app.route('/profile/<username>/page/<int:page>/filter/<filterAtt>')
@app.route('/profile/<username>/filter/<filterAtt>', defaults={'page':1})
@login_required
def profile(username, page, filterAtt):
	PER_PAGE = 2

	if not filterAtt:
		con = sql.connect('ensta.db')
		cur = con.cursor()
		cur.row_factory = sql.Row

		total_posts = cur.execute('select count(*) as count from posts where username=?',(username,)).fetchone()
		total_posts = total_posts["count"]

		total_pages = math.ceil(total_posts/PER_PAGE)

		if page < 1:
			page = 1
		elif page > total_pages:
			page = total_pages

		start_at = (page-1)*PER_PAGE

		user = cur.execute('select username,firstName,lastName,email,birthDate,bio from users where username=?', (username,))
		user = user.fetchone()
		
		posts = cur.execute('select * from posts where username=? order by pid desc LIMIT ?, ?', (username, start_at, PER_PAGE))
		posts = posts.fetchall()

	else:
		filter = filterAtt.split(',')
		if filter[0] == 'time':
			time_from = filter[1] + " 00:00:00"
			time_to = filter[2] + " 00:00:00"

			print(time_from)
			print(time_to)

			con = sql.connect('ensta.db')
			cur = con.cursor()
			cur.row_factory = dict_factory

			total_posts = cur.execute('select count(*) as count from posts where username=? and time >= ? and time <= ?',(username, time_from, time_to)).fetchone()
			total_posts = total_posts["count"]

			print(total_posts)

			total_pages = math.ceil(total_posts/PER_PAGE)

			if page < 1:
				page = 1
			elif page > total_pages:
				page = total_pages

			start_at = (page-1)*PER_PAGE

			user = cur.execute('select username,firstName,lastName,email,birthDate,bio from users where username=?', (username,))
			user = user.fetchone()
			
			posts = cur.execute('select * from posts where username=? and time >= ? and time <= ? order by pid desc LIMIT ?, ?', (username, time_from, time_to, start_at, PER_PAGE))
			posts = posts.fetchall()

		elif filter[0] == 'hashtag':
			tag = filter[1]

			con = sql.connect('ensta.db')
			cur = con.cursor()
			cur.row_factory = dict_factory

			total_posts = cur.execute('select count(*) as count from posts where username=? and tags LIKE ?',(username, '%'+tag+'%')).fetchone()
			total_posts = total_posts["count"]

			total_pages = math.ceil(total_posts/PER_PAGE)

			if page < 1:
				page = 1
			elif page > total_pages:
				page = total_pages

			start_at = (page-1)*PER_PAGE

			user = cur.execute('select username,firstName,lastName,email,birthDate,bio from users where username=?', (username,))
			user = user.fetchone()
			
			posts = cur.execute('select * from posts where username=? and tags LIKE ? order by pid desc LIMIT ?, ?', (username, '%'+tag+'%', start_at, PER_PAGE))
			posts = posts.fetchall()
	

	# finally
	con.close()
	pagination = {"cur_page": page, "total_pages": total_pages}
	return render_template('profile.html',user=user, posts=posts, pagination=pagination, filterAtt=filterAtt)

@app.route('/blog/<pid>')
@login_required
def blog(pid):
	con = sql.connect('ensta.db')
	cur = con.cursor()
	cur.row_factory = dict_factory

	post = cur.execute('select * from posts where pid=?', (pid,))
	post = post.fetchone()

	con.close()
	return render_template('blog.html', post=post)

@app.route('/post', methods = ['POST', 'GET'])
def post():
	if request.method == 'GET':
		return render_template('post.html')
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

@app.route('/delete/<pid>', methods=['POST', 'GET'])
@login_required
def delete(pid):
	if request.method == "POST":
		con = sql.connect('ensta.db')
		cur = con.cursor()
		cur.row_factory = dict_factory

		isOwner = cur.execute('select pid from posts where pid=? and username=?', (pid, session["username"]))
		isOwner = isOwner.fetchall()
		if isOwner:
			cur.execute('delete from posts where pid=?', (pid,))
			con.commit()
			session["flashMsg"] = "Deleted"
		else:
			session["flashErr"] = "Sorry, you dont have the previlage to delete the post"
		return redirect( url_for('profile', username=session["username"]))	

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

@app.route('/analytics/file', methods=["POST"])
def update_file_analytics():
	file_id = request.form['file_id']
	analytics.update_downloads(file_id)
	return jsonify({"res":"true"})

if __name__ == "__main__":
	app.run( debug=True)

