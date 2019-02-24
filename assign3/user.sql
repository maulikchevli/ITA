create table users (
	firstName text not null,
	lastName text not null, 
	username text not null,
	email text not null,
	password text not null,
	birthDate date not null,
	bio text,

	PRIMARY KEY ('username')
);
	
