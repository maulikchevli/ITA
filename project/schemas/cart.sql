create table cart (
	c_id integer primary key autoincrement,
	username text not null, 
	pid integer not null,
	quantity integer not null,
	price float not null
);
