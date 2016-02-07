drop table if exists entries;
drop table if exists users;
create table IF NOT EXISTS users (
  id integer primary key autoincrement,
  username text not null,
  password text not null,
  UNIQUE(username)
);
create table entries (
  id integer primary key autoincrement,
  title text not null,
  owner integer not null,
  text text not null,
  FOREIGN KEY(owner) REFERENCES users(id)
);
insert into users (username, password) values ('admin', 'default')