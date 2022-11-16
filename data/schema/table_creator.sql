DROP TABLE IF EXISTS "completes";
DROP TABLE IF EXISTS "reactions";
DROP TABLE IF EXISTS "comments";
DROP TABLE IF EXISTS "posts";
DROP TABLE IF EXISTS "tasks";
DROP TABLE IF EXISTS "users";

CREATE TABLE "users"(
handle TEXT PRIMARY KEY,
password VARCHAR(255),
email VARCHAR(255),
salt VARCHAR(255),
first_name VARCHAR(20),
last_name VARCHAR(50),
profile_pic TEXT
);

CREATE TABLE tasks(
task_id SERIAL PRIMARY KEY,
title TEXT,
description TEXT,
active BOOLEAN
);

CREATE TABLE posts(
post_id SERIAL PRIMARY KEY,
free_text VARCHAR(255),
image_url VARCHAR(255),
created_at TIMESTAMP,
posted_by VARCHAR(50),
    CONSTRAINT fk_user
        FOREIGN KEY(posted_by)
            REFERENCES "users"(handle),
activity INT,
	FOREIGN KEY(activity) REFERENCES tasks(task_id)
);

CREATE TABLE reactions(
react_id INT PRIMARY KEY,
emoji TEXT,
reacted_by VARCHAR(50), FOREIGN KEY(reacted_by) REFERENCES "users"(handle),
reacted_to INT, FOREIGN KEY(reacted_to) REFERENCES posts(post_id)
);

CREATE TABLE comments(
comment_id INT PRIMARY KEY,
created_at TIMESTAMP,
free_text VARCHAR(300),
parent INT DEFAULT NULL,
	CONSTRAINT Fk_user_2
		FOREIGN KEY(parent)
			REFERENCES comments(comment_id),
comment_by VARCHAR(50), FOREIGN KEY(comment_by) REFERENCES "users"(handle),
comment_to INT, FOREIGN KEY(comment_to) REFERENCES posts(post_id)
);

CREATE TABLE completes(
completed_by VARCHAR(50) REFERENCES "users",
completed_task INT REFERENCES tasks,
PRIMARY KEY(completed_by,completed_task)
);
