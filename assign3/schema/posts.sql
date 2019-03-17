CREATE TABLE posts (
	username text not null,
	title text not null,
	filename text not null,
	tags text not null,

	foreign key ('username') references users('username') on delete cascade on update cascade
);
