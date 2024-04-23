create table
  Product (
    id bigint primary key generated always as identity,
    code varchar(255) unique not null,
    imageURL varchar(255) unique,
    name varchar(255) not null,
    description text,
    quantityInStock int not null,
    salePrice decimal(10, 2) not null,
    purchasePrice decimal(10, 2),
    lastRefill timestamp with time zone
);

create table
  Employee (
    id bigint primary key generated always as identity,
    avatarURL varchar(255) unique,
    name varchar(255) not null,
    email varchar(255) unique not null,
    password varchar(255) not null,
    role varchar(100),
    salesCount int
);

create table 
  Client (
    id bigint primary key generated always as identity,
    avatarURL varchar(255) unique,
    name varchar(255) not null,
    email varchar(255) unique not null,
    password varchar(255) not null
);

create table
  Sale (
    id bigint primary key generated always as identity,
    clientID bigint,
    dateTime timestamp with time zone not null,
    total decimal(10, 2) not null,
    paymentMethod text,
    products json[] not null,
    foreign key (clientID) references Client (id)
);