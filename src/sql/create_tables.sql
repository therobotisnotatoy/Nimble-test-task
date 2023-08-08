DROP TABLE IF EXISTS contacts;
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(40) NOT NULL,
    last_name VARCHAR(40) NOT NULL,
    email VARCHAR(150)
);
