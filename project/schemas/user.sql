create table user_info (
	username text not null,
	email text not null,
	password text not null,
	user_type text not null default "reg",

	PRIMARY KEY ('username')
);
	
