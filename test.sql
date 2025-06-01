CREATE TABLE students (id INT PRIMARY KEY, name VARCHAR(50) NOT NULL, age INT);

INSERT INTO students (id, name, age) VALUES (1, 'Alice', 21);
INSERT INTO students (id, name, age) VALUES (2, 'Bob', 22);
INSERT INTO students (id, name, age) VALUES (3, 'Charlie', 23);

SELECT * FROM students;

UPDATE students SET age = 25 WHERE id = 1;

DELETE FROM students WHERE id = 2;

SELECT * FROM students;