create table
  Animal (
    id bigint primary key generated always as identity,
    name varchar(255) not null,
    breed varchar(255),
    age int,
    weight decimal(10, 2),
    owner varchar(255),
);

create table
  Appointment (
    id bigint primary key generated always as identity,
    dateTime timestamp with time zone not null,
    servicesID int[] not null,
    animalID int,
    status varchar(20),
    foreign key (animalID) references Animal (id)
);

create table
  Product (
    id bigint primary key generated always as identity,
    imageURL varchar(255) unique,
    name varchar(255) not null,
    description text,
    price decimal(10, 2) not null,
    quantityInStock int,
    purchasePrice float,
    salePrice decimal(10, 2),
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
  Service (
    id bigint primary key generated always as identity,
    name varchar(255) not null,
    description text,
    price decimal(10, 2) not null
);

create table
  Sale (
    id bigint primary key generated always as identity,
    dateTime timestamp with time zone not null,
    total decimal(10, 2) not null,
    paymentMethod text,
    products json[] not null
);