import os
import sqlite3 as sql
from functools import wraps
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from passlib.apps import custom_app_context as passHash
from SQL_execute import dict_factory, GetData

import ast
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/product_img'
ALLOWED_EXTENSIONS = set(['jpg','jpeg','gif'])

app = Flask( __name__)
app.secret_key = 'groceri'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
		print(session['user_type'])
		if session['user_type'] != "admin":
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

	return render_template('products.html',products=products)

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
	result["name"] = {}
	result["type"] = {}
	relop = None
	p_type = None

	q = request.args["q"]

	q = q.split(" ")

	print(len(q))

	if len(q) == 2:
		relop = q[1].split(":")[1]
		print(relop)
	elif len(q) == 3:
		relop = q[1].split(":")[1]
		p_type = q[2].split(":")[1]
		print(relop)
		print(p_type)

	q = q[0]

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	if relop == "not":
		search_result = con.execute('select * from products where name not like ?', ('%'+q+'%',))
		search_result = search_result.fetchall()
		result["name"] = search_result

	elif relop == "and":
		if p_type is None:
			pass
		else:
			search_result = con.execute('select * from products where name LIKE ? and p_type LIKE ?', ('%'+q+'%','%'+p_type+'%'))
			search_result = search_result.fetchall()
			result["name"] =  search_result

	elif relop == "or":
		if p_type is None:
			pass
		else:
			search_result = con.execute('select * from products where name like ?', ('%'+q+'%',))
			search_result = search_result.fetchall()
			result["name"] = search_result

			search_result = con.execute('select * from products where p_type like ?', ('%'+p_type+'%',))
			search_result = search_result.fetchall()
			result["type"] = search_result

	elif relop is None:
		search_result = con.execute('select * from products where name like ?', ('%'+q+'%',))
		search_result = search_result.fetchall()
		result["name"] = search_result

	return render_template('search.html',result=result)

@app.route('/cart/add', methods=["GET","POST"])
def add_to_cart():
	username = session["username"]
	pid = request.form["pid"]
	quantity = int(request.form["quantity"])

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	entry = con.execute('select * from cart where username=? and pid=?',(username,pid))
	entry = entry.fetchone()

	if entry is None:
		con.execute('insert into cart (username,pid,quantity) values (?,?,?)',(username, pid,quantity ))
		pass
	else:
		quantity += entry["quantity"]
		con.execute('update cart set quantity=? where username=? and pid=?',(quantity,username,pid))


	con.commit()
	con.close()

	return redirect(url_for('show_cart'))

@app.route('/cart/remove', methods=["GET","POST"])
@login_required
def remove_cart():
	c_id = request.form["c_id"]

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	con.execute('delete from cart where c_id=?',(c_id,))
	con.commit()
	con.close()

	session["flashMsg"] = "Deleted successfully"

	return redirect(url_for('show_cart'))

@app.route('/cart/show')
@login_required
def show_cart():
	username = session["username"]

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	products = con.execute('select * from cart,products where username=? and cart.pid=products.pid',(username,))
	products = products.fetchall();

	total_cost = 0
	for product in products:
		total_cost += product['price']*product['quantity']
	
	tmp = products
	products = {}
	products["list"] = tmp
	products["total_cost"] = total_cost

	con.close()
	print(products)

	return render_template('cart.html',products=products)

@app.route('/cart/buy', methods=["GET","POST"])
@login_required
def buy_cart():
	username = session["username"]

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	products = con.execute('select pid,quantity from cart where username=?',(username,))
	products = products.fetchall();

	order_dict = {}
	order_dict["products"] = products

	con.execute('delete from cart where username=?',(username,))
	con.execute('insert into order_history (username,order_dict) values (?,?)',(username,str(order_dict)))
	con.commit()

	con.close()

	session["flashMsg"] = "Your Order has been placed. It will be recevied by the admins shortly"
	return redirect(url_for('show_order_history'))

@app.route('/order_history')
@login_required
def show_order_history():
	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	orders = con.execute('select * from order_history where username=?',(session["username"],))
	orders = orders.fetchall()


	for order in orders:
		order['order_dict'] = eval(order['order_dict'])
		for product in order['order_dict']['products']:
			info = con.execute('select * from products where pid=?',(product['pid'],)).fetchone()
			product.update(info)

	print(orders)

	con.close()
	return render_template('order_history.html', orders=orders)

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
			address = request.form['address']
			city = request.form['city']
			pincode = request.form['pincode']
			
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
					cur.execute("insert into user_info (username,email,password,address,city,pincode) values (?,?,?,?,?,?)", (username,email,password,address,city,pincode))
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

@app.route('/admin')
@login_required
@admin_required
def admin():
	return "Hello admin"

@app.route('/admin/product/add', methods=["GET","POST"])
@login_required
@admin_required
def add_product():
	if request.method == "GET":
		return render_template('admin_add.html')
	else:
		name = request.form["name"]
		info = request.form["info"]
		price = request.form["price"]
		p_type = request.form["p_type"]
		image = request.files["image"]

		if image:
			filename = secure_filename(image.filename)
			img_path = "product_img/" + filename
			image.save(os.path.join( app.config['UPLOAD_FOLDER'], filename))

		con = sql.connect('groceri.db')
		con.row_factory = dict_factory
		cur = con.cursor()

		con.execute('insert into products (name,info,price,p_type,img_path) values (?,?,?,?,?)',(name,info,price,p_type,img_path))
		con.commit()

		con.close()

		return redirect(url_for('get_products'))

@app.route('/admin/product/unlink', methods=["GET","POST"])
def unlink_product():
	pid = request.form["pid"]

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	con.execute('update products set to_delete=1 where pid=?',(pid,))
	con.commit()
	con.close()
	return redirect(url_for('get_products'))

@app.route('/admin/product/link', methods=["GET","POST"])
def link_product():
	pid = request.form["pid"]

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	con.execute('update products set to_delete=0 where pid=?',(pid,))
	con.commit()
	con.close()
	return redirect(url_for('get_products'))

@app.route('/admin/review_order', methods=["GET","POST"])
def review_order():
	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	orders = con.execute('select * from order_history where approved=0 order by time asc')
	orders = orders.fetchall()

	for order in orders:
		order['order_dict'] = eval(order['order_dict'])
		for product in order['order_dict']['products']:
			info = con.execute('select * from products where pid=?',(product['pid'],)).fetchone()
			product.update(info)

	con.close()
	return render_template('review_order.html', orders=orders)

@app.route('/admin/accept_order', methods=["GET","POST"])
def accept_order():
	o_id = request.form['o_id']

	con = sql.connect('groceri.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	con.execute('update order_history set approved=1 where o_id=?',(o_id,))
	con.commit()

	session["flashMsg"] = "order no " + o_id + "approved!"
	con.close()
	return redirect(url_for('review_order'))

if __name__ == "__main__":
	app.run( debug=True)
