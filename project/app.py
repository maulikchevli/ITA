import sqlite3 as sql
from functools import wraps
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from passlib.apps import custom_app_context as passHash
from SQL_execute import dict_factory, GetData

app = Flask( __name__)
app.secret_key = 'groceri'

def login_required(f):
	@wraps(f)
	def fn( *args, **kwargs):
		if 'username' not in session:
			return redirect( url_for('login'))
		return f( *args, **kwargs)
	return fn

def admin_required(f):
	@wraps(f)
	def fn( *args, **kwargs):
		if session['user_type'] is not "admin":
			session['flashErr'] = "You are not admin"
			return redirect( url_for('index'))
		return f( *args, **kwargs)
	return fn

@app.route('/')
def index():
	return render_template( 'index.html')

@app.route('/products')
def get_products():
	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	products = con.execute('select * from products')
	products = products.fetchall();

	con.close()

	return jsonify(products)

@app.route('/product/<pid>')
def product_info(pid):
	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	product = con.execute('select * from products where pid=?', (pid,))
	product = product.fetchone();

	con.close()

	return jsonify(product)

@app.route('/search')
def search():
	# the result of search
	result = {}

	q = request.args["q"]

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	search_result = con.execute('select * from products where name LIKE ?', ('%'+q+'%',))
	search_result = search_result.fetchall()
	result["name"] = search_result;

	if 'type' in request.args:
		type = request.args["type"]

		search_result = con.execute('select * from products where name LIKE ? and p_type LIKE ?', ('%'+q+'%','%'+type+'%'))
		search_result = search_result.fetchall()

		result["type"] = search_result;

	return jsonify(result)

@app.route('/cart/add')
def add_to_cart():
	username = request.args["username"]
	pid = request.args["pid"]
	quantity = int(request.args["quantity"])
	price = request.args["price"]

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	entry = con.execute('select * from cart where username=? and pid=?',(username,pid))
	entry = entry.fetchone()

	if entry is None:
		con.execute('insert into cart (username,pid,quantity,price) values (?,?,?,?)',(username, pid,quantity, price))
		pass
	else:
		print(quantity)
		print(entry["quantity"])
		quantity += entry["quantity"]
		con.execute('update cart set quantity=? where username=? and pid=?',(quantity,username,pid))


	con.commit()
	con.close()

	return "success"

@app.route('/cart/show')
@login_required
def show_cart():
	username = session["username"]

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	items = con.execute('select * from cart where username=?',(username,))
	items = items.fetchall();

	con.close()

	return jsonify(items)

@app.route('/login', methods = ['POST', 'GET'])
def login():
	if request.method == 'GET':
		return render_template( 'login.html')
	else:
		try:
			enteredPassword = request.form['password']
			username = request.form['username']

			con = sql.connect('groceri.db')
			con.row_factory = sql.Row

			cur = con.cursor()
			data = cur.execute('SELECT * FROM user_info WHERE username=?',(username,))
			data = data.fetchall()

			storedPassword = data[0]['password'] #Throws IndexError if no entry is found

			con.close()

			if passHash.verify(enteredPassword,storedPassword):
				session['username'] = username
				session['user_type'] = data[0]['user_type']
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
			username = request.form['username']
			email = request.form['email']
			password = passHash.hash(request.form['password'])
			password2 = request.form['password2']
			
			# TODO validate passes
			registered = False
			with sql.connect("groceri.db") as con:
				con.row_factory = dict_factory
				cur = con.cursor()

				cur.execute("SELECT * from user_info where username=? OR email=?",(username,email))
				users = cur.fetchall()
				if users:
					print("already!")
					registered = False
					alreadyUser = True
				else:
					cur.execute("insert into user_info (username,email,password) values (?,?,?)", (username,email,password))
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
	session.pop('user_type',None)
	return redirect( url_for('index'))

if __name__ == "__main__":
	app.run( debug=True)

