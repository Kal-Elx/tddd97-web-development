/* Drop all created tables */
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tokens;
DROP TABLE IF EXISTS messages;


CREATE TABLE users (
	email VARCHAR(50) PRIMARY KEY,
   	psw VARCHAR(50) NOT NULL,
   	firstname VARCHAR(50) NOT NULL,
   	familyname VARCHAR(50) NOT NULL,
   	gender VARCHAR(10) NOT NULL,
   	city VARCHAR(50) NOT NULL,
   	country VARCHAR(50) NOT NULL,
    CONSTRAINT psw_length CHECK (length(psw) >= 6)
);

CREATE TABLE tokens (
	email VARCHAR(50) PRIMARY KEY,
    token VARCHAR(36) UNIQUE,
	CONSTRAINT token_length CHECK (length(token) == 36),
	FOREIGN KEY (email) REFERENCES users(email)
);

CREATE TABLE messages (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	writer VARCHAR(50),
	recipient VARCHAR(50),
	content VARCHAR(500),
	geolocation VARCHAR(100),
	FOREIGN KEY (writer) REFERENCES users(email),
	FOREIGN KEY (recipient) REFERENCES users(email)
);