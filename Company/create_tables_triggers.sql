CREATE TABLE Employer (
	Employer_ID	INTEGER PRIMARY KEY AUTOINCREMENT,
	Full_Name TEXT NOT NULL,
	Joining_Date TEXT DEFAULT CURRENT_TIMESTAMP,
	Current_Position TEXT NOT NULL,
	Department TEXT NOT NULL,
	Assigned_Project_Client TEXT
);

CREATE TABLE "Services" (
	Software_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Name TEXT NOT NULL,
	Category TEXT NOT NULL,
	Size INTEGER NOT NULL,
	Installments_Count INTEGER DEFAULT 0
);

CREATE TABLE "Software_Requests" (
	Employer_ID INTEGER NOT NULL,
	Software_ID INTEGER NOT NULL,
	Request_Start_Date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	Request_Close_Date TEXT NOT NULL,
	Status INTEGER DEFAULT 0 NOT NULL,
	FOREIGN KEY(Employer_ID) REFERENCES Employer(Employer_ID),
	FOREIGN KEY (Software_ID) REFERENCES Services(Software_ID)
);

CREATE TRIGGER "Increment_Installments_Count" AFTER INSERT ON Software_Requests
	BEGIN
		UPDATE Services SET Installments_Count = (SELECT COUNT(Software_ID) FROM Software_Requests WHERE Software_Requests.Software_ID = Services.Software_ID AND Software_Requests.Status <> 0);
	END;
	
CREATE TRIGGER "Refresh_Installments_Count" AFTER UPDATE ON Software_Requests
	BEGIN
		UPDATE Services SET Installments_Count = (SELECT COUNT(Software_ID) FROM Software_Requests WHERE Software_Requests.Software_ID = Services.Software_ID AND Software_Requests.Status <> 0);
	END;


