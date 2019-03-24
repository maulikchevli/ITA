- Database: analytics.db

create table tags (
	tag TEXT primary key,
	count integer not null
);

create table downloads (
	file_id integer primary key,
	count integer not null,

	foreign key ('file_id') references posts('pid') on delete cascade on update cascade 
);

