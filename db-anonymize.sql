-- A SQL script that is used to remove sensitive data from a public database
-- For example, the database on http://www.mantisbt.org/bugs/
-- The assumption here is that the sensitive data includes:
-- Email addresses, passwords, cookies, and real names.

DELETE FROM mantis_email_table;

UPDATE mantis_user_table
SET
	password = '63a9f0ea7bb98050796b649e85481845',
	email = CONCAT(username, '@localhost'),
	cookie_string = CONCAT('cookie_', id),
	realname = CONCAT('Realname', username);
