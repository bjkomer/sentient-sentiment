drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	movie text not null,
	source text not null,
	quote text unique not null,
	score integer not null,
	positive_nb1 float,
	negative_nb1 float,
	label_nb1 text,
	positive_nb2 float,
	negative_nb2 float,
	label_nb2 text,
	positive_nb12 float,
	negative_nb12 float,
	label_nb12 text,
	positive_dt1 float,
	negative_dt1 float,
	label_dt1 text,
	positive_dt2 float,
	negative_dt2 float,
	label_dt2 text,
	positive_dt3 float,
	negative_dt3 float,
	label_dt3 text,
	positive_dt12 float,
	negative_dt12 float,
	label_dt12 text,
	positive_knn1 float,
	negative_knn1 float,
	label_knn1 text,
	positive_knn12 float,
	negative_knn12 float,
	label_knn12 text,
	positive_svc12 float,
	negative_svc12 float,
	label_svc12 text,
	positive_gbc12 float,
	negative_gbc12 float,
	label_gbc12 text
);
