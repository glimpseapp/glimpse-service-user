CREATE KEYSPACE User WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };

CREATE TABLE user.user_info_by_id (
   user_id TEXT,
   username TEXT,
   email TEXT,
   create_date timestamp,

   PRIMARY KEY (user_id)
);

CREATE TABLE user.user_info_by_username (
   user_id TEXT,
   username TEXT,
   PRIMARY KEY (user_id, username)
) WITH CLUSTERING ORDER BY (username ASC);