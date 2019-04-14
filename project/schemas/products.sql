create table products (
	pid integer primary key autoincrement,
	name text not null,
	info text,
	price float not null,
	p_type text,
	img_path text not null,
	to_delete boolean default false
);

