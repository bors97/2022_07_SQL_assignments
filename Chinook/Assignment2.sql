--Task 1
SELECT artists.Name AS "Artist Name", IFNULL(albums.Title, "No album") AS "Album Name" 
FROM artists 
LEFT JOIN albums ON albums.ArtistId = artists.ArtistId
ORDER BY artists.Name;


--Task 2
SELECT artists.Name AS "Artist Name", albums.Title AS "Album Name" 
FROM artists
INNER JOIN albums ON albums.ArtistId = artists.ArtistId
ORDER BY albums.Title;


--Task 3
SELECT artists.Name AS "Artist Name"
FROM artists
LEFT JOIN albums ON albums.ArtistId = artists.ArtistId
	WHERE albums.Title IS NULL
ORDER BY artists.Name;


--Task 4
SELECT artists.Name AS "Artist Name", COUNT(albums.Title) AS "No of albums"
FROM artists
LEFT JOIN albums ON albums.ArtistId = artists.ArtistId
GROUP BY artists.ArtistId
ORDER BY "No of albums" DESC,
		 "Artist Name" ASC;

		 
--Task 5
SELECT artists.Name AS "Artist Name", COUNT(albums.Title) AS "No of albums"
FROM artists
LEFT JOIN albums ON albums.ArtistId = artists.ArtistId
GROUP BY artists.ArtistId
HAVING "No of albums" >= 10
ORDER BY "No of albums" DESC,
		 "Artist Name" ASC;


--Task 6
SELECT artists.Name AS "Artist Name", COUNT(albums.Title) AS "No of albums"
FROM artists
LEFT JOIN albums ON albums.ArtistId = artists.ArtistId
GROUP BY artists.ArtistId
ORDER BY "No of albums" DESC
LIMIT 3;


--Task 7
SELECT tracks.Composer AS "Artist Name", albums.Title AS "Album Title", tracks.Name AS "Track"
FROM tracks
INNER JOIN albums ON tracks.AlbumId = albums.AlbumId
WHERE "Artist Name" LIKE "%Santana%"
ORDER BY tracks.TrackId;


--Task 8
SELECT employees.EmployeeId AS "Employee ID",
	(employees.FirstName || " " || employees.LastName) AS "Employee Name",
	employees.Title AS "Employee Title",
	(managers.FirstName || " " || managers.LastName) AS "Manager Name",
	managers.Title AS "Manager Title"
FROM employees
LEFT JOIN employees managers ON employees.ReportsTo = managers.EmployeeId
ORDER BY employees.EmployeeId;


--Task 9
CREATE VIEW top_employees AS
SELECT employees.EmployeeId AS emp_id,
	(employees.FirstName || " " || employees.LastName) AS emp_name,
	COUNT(customers.CustomerId) AS cust_count
FROM employees
LEFT JOIN customers ON employees.EmployeeId = customers.SupportRepId
GROUP BY employees.EmployeeId;

SELECT top_employees_sub.emp_name,
	(customers.FirstName || " " || customers.LastName) AS "Customer Name"
FROM (SELECT emp_id, emp_name, MAX(cust_count) FROM top_employees) AS top_employees_sub
INNER JOIN customers ON customers.SupportRepId = top_employees_sub.emp_id;


--Task 10
INSERT INTO media_types (Name)
VALUES ("MP3");

CREATE TRIGGER prevent_mp3_insertion BEFORE INSERT ON tracks
WHEN (NEW.MediaTypeId = (SELECT media_types.MediaTypeId FROM media_types WHERE media_types.Name = "MP3"))
BEGIN
	SELECT RAISE(ABORT, "You can't insert MP3 tracks!");
END;

INSERT INTO tracks (Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice)
VALUES ("Lorem Ipsum", 1, 4, 1, "John Doe", 10, 10, 0.99);


--Task 11
CREATE TABLE tracks_audit_log (
	operation TEXT NOT NULL,
	datetime TEXT DEFAULT CURRENT_TIMESTAMP,
	username TEXT NOT NULL,
	old_value TEXT,
	new_value TEXT
);

CREATE TRIGGER tracks_audit_delete AFTER DELETE ON tracks
BEGIN
	INSERT INTO tracks_audit_log (operation, datetime, username, old_value)
	VALUES ("DELETE", datetime("now"), "admin", OLD.name || " By " || OLD.Composer);
END;

CREATE TRIGGER tracks_audit_update AFTER UPDATE ON tracks
BEGIN
	INSERT INTO tracks_audit_log (operation, datetime, username, old_value, new_value)
	VALUES ("UPDATE", datetime("now"), "admin", OLD.name || " By " || OLD.Composer, NEW.name || " By " || NEW.Composer);
END;

CREATE TRIGGER tracks_audit_insert AFTER INSERT ON tracks
BEGIN
	INSERT INTO tracks_audit_log (operation, datetime, username, new_value)
	VALUES ("INSERT", datetime("now"), "admin", NEW.name || " By " || NEW.Composer);
END;

INSERT INTO tracks (Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice)
VALUES ("Lorem Ipsum", 1, 4, 1, "John Doe", 10, 10, 0.99);

UPDATE tracks SET Name = "The new Lorem Ipsum" WHERE Composer = "John Doe";

DELETE FROM tracks WHERE Composer = "John Doe";