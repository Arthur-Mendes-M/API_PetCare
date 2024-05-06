-- create database if not exists PetCare;

create table
  Product (
    id bigint primary key generated always as identity,
    code varchar(255) unique not null,
    image_url varchar(255) unique,
    name varchar(255) not null,
    description text,
    quantity_in_stock int not null,
    sale_price decimal(10, 2) not null,
    purchase_price decimal(10, 2) not null,
    last_refill timestamp with time zone
);

create table
  Employee (
    id bigint primary key generated always as identity,
    avatar_url varchar(255) unique,
    name varchar(255) not null,
    email varchar(255) unique not null,
    password varchar(255) not null,
    role varchar(100)
);

create table 
  Client (
    id bigint primary key generated always as identity,
    avatar_url varchar(255) unique,
    name varchar(255) not null,
    email varchar(255) unique not null,
    password varchar(255) not null
);

create table
  Sale (
    id bigint primary key generated always as identity,
    client_id bigint,
    date_time timestamp with time zone not null,
    total decimal(10, 2) not null,
    payment_method text,
    products json[] not null,
    foreign key (client_id) references Client (id)
);