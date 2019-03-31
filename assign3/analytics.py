import sqlite3 as sql
from SQL_execute import dict_factory

def update_hashtag(tag):
	con = sql.connect('analytics.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	tag_row = cur.execute('select * from tags where tag=?', (tag,))
	tag_row = tag_row.fetchone()

	if tag_row:
		tag_cnt = tag_row['count'] + 1
		cur.execute('update tags set count=? where tag=?', (tag_cnt, tag))
		con.commit()
	else:
		cur.execute('insert into tags (tag, count) values (?,?)', (tag,1))
		con.commit()
	
	con.close()

def update_downloads(file_id):
	con = sql.connect('analytics.db')
	con.row_factory = dict_factory
	cur = con.cursor()

	file_row = cur.execute('select * from downloads where file_id=?', (file_id,))
	file_row = file_row.fetchone()

	if file_row is not None:
		file_cnt = file_row['count'] + 1
		cur.execute('update downloads set count=? where file_id=?', (file_cnt, file_id))
		con.commit()
	else:
		cur.execute('insert into downloads (file_id, count) values (?,?)', (file_id,1))
		con.commit()
	
	con.close()

