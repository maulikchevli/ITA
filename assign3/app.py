import sqlite3 as sql
from functools import wraps
from flask import Flask, render_template, redirect, url_for, session, jsonify
from passlib.apps import custom_app_context as passHash

app = Flask( __name__)
app.secret_key = 'ensta'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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

@app.route('/login')
def login():
	return render_template( 'login.html')

if __name__ == "__main__":
	app.run( debug=True)

