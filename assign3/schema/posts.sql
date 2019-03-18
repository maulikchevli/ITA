CREATE TABLE posts (
	pid integer primary key autoincrement,
	username text not null,
	title text not null,
	filename text not null,
	tags text not null,
	time timestamp default current_timestamp,

	foreign key ('username') references users('username') on delete cascade on update cascade
);
