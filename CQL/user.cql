CREATE KEYSPACE Glimpse WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };

USE Glimpse;

CREATE TABLE User (

   user_id text,
   username text,
   email text,
   date timestamp,

   PRIMARY KEY (user_id)

);