show databases;
create database drdl;
select drdl;
use drdl;
CREATE TABLE ASTRA(QUESTION TEXT(2147483648),ANSWER TEXT(2147483648));
SHOW TABLES;
SELECT * FROM faq;
INSERT INTO ASTRA VALUES("WHAT IS ASTRA","ASTRA Labs Defence Research & Development Laboratory (DRDL) Technology Cluster Missiles and Strategic Systems (MSS) ASTRA is a Beyond Visual Range (BVR) class of Air-to-Air Missile (AAM) system designed to be mounted on fighter aircraft. The missile is designed to engage and destroy highly manoeuvring supersonic aircraft.")

CREATE TABLE faq (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255),
    answer TEXT
);

INSERT INTO faq (question, answer) VALUES
('What is a laptop?', 'A laptop is a portable computer that can be easily carried around and used in various locations.'),
('What is Python?', 'Python is a high-level programming language known for its simplicity and readability.'),
('What is a database?', 'A database is an organized collection of data, typically stored and accessed electronically from a computer system.'),
('what is Astra?', 'Astra is an organization to research for the defence perpose in DRDL');

