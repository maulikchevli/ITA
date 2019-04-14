create table order_history (
	o_id integer primary key autoincrement,
	username text not null,
	order_dict text not null,
	approved boolean default false,
	time timestamp default current_timestamp
);
