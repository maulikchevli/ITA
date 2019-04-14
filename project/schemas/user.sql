create table user_info (
	username text not null,
	email text not null,
	password text not null,
	user_type text not null default "reg",
	address text not null,
	city text not null,
	pincode char(6) not null,

	PRIMARY KEY ('username')
);
	
