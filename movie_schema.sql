drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	movie text not null,
	positive float,
	negative float,
	label text,
	source text not null,
	quote text unique not null,
	score integer not null
);
