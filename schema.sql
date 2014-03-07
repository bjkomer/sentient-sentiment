drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	tweet text unique not null,
	positive float,
	negative float,
	neutral float,
	label text,
	location text,
	screen_name text not null,
	post_date date not null
);
