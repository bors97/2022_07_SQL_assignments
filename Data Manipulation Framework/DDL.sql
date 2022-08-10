DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TABLE Users (
	user_id serial PRIMARY KEY,
	employer_number integer NOT NULL,
	creation_date TIMESTAMP default current_timestamp,
	username varchar UNIQUE NOT NULL,
	password varchar NOT NULL,
	level varchar
);

CREATE TABLE Platforms (
	platform_id serial PRIMARY KEY,
	courses integer,
	platform_name varchar NOT NULL,
	URL varchar
);

CREATE TABLE Courses (
	course_id serial PRIMARY KEY,
	course_name varchar NOT NULL,
	platform_id integer REFERENCES Platforms (platform_id) NOT NULL,
	duration interval NOT NULL,
	creation_date date NOT NULL,
	tags varchar,
	photo varchar
);

CREATE TABLE Pictures (
	course_id integer REFERENCES Courses (course_id),
	platform_id integer REFERENCES Platforms (platform_id),
	image_obj bytea --This should be not null but I don't have images for it
);

CREATE TABLE Ongoing_training (
	training_id serial PRIMARY KEY,
	user_id integer REFERENCES Users (user_id) NOT NULL,
	course_id integer REFERENCES Courses (course_id) NOT NULL,
	status boolean NOT NULL,
	completion_percentage real NOT NULL,
	start_date date,
	finish_date date,
	last_updated timestamp default current_timestamp,
	UNIQUE (user_id, course_id)
);

CREATE TABLE Certification_id (
	certification_id serial PRIMARY KEY,
	user_id integer REFERENCES Users (user_id) NOT NULL,
	course_id integer REFERENCES Courses (course_id) NOT NULL,
	completion_duration interval NOT NULL,
	completion_date date NOT NULL,
	UNIQUE (user_id, course_id)
);

CREATE TABLE Reviews (
	user_id integer REFERENCES Users (user_id),
	course_id integer REFERENCES Courses (course_id),
	feedback varchar,
	liked boolean NOT NULL,
	ranking_score integer NOT NULL,
	PRIMARY KEY(user_id, course_id)
);

CREATE OR REPLACE FUNCTION tg_courses_fn()
	RETURNS TRIGGER
AS
$$
	BEGIN
		IF (TG_OP = 'DELETE') THEN
			UPDATE platforms SET courses = courses - 1 WHERE Platforms.platform_id = OLD.platform_id;
			RETURN OLD;
		ELSIF (TG_OP = 'INSERT') THEN
			UPDATE platforms SET courses = courses + 1 WHERE Platforms.platform_id = NEW.platform_id;
			RETURN NEW;
		END IF;
	END;
$$
LANGUAGE PLPGSQL;


CREATE TRIGGER tg_courses
AFTER INSERT OR DELETE ON courses
	FOR EACH ROW
	EXECUTE PROCEDURE tg_courses_fn();