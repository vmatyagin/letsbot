create table if not exists location (
        id integer primary key autoincrement,
        name varchar(255),
        latitude float,
        longitude float,
        user_pk integer,
        foreign key(user_pk) references person(id)
    );


create table if not exists person(
    id integer primary key autoincrement,
    name varchar(255),
    username varchar(255),
    tg_id integer(255),
    family_status varchar(255) DEFAULT 'unset',
    about varchar(255) DEFAULT '',
    is_admin integer(1) DEFAULT 0
);