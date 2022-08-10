import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta
import json

fake = Faker()

conn = psycopg2.connect(user="postgres",
                        password="postgres",
                        host="127.0.0.1",
                        port="5432",
                        database="Test"
)


cur = conn.cursor()

#By default this will generate:
#20 Users
#5 Platforms
#5 Courses for each platform
#10 Reviews for each user
#


def insert(table: str, dict: dict, commit: bool = True) -> bool:
    """
    Inserts values into a table.
    Parameters:
        table: string
        dict: dictionary
        commit: boolean
    """

    columns = ", ".join(dict.keys())
    values = ", ".join(['%({})s'.format(k) for k in dict.keys()])
    SQL = "INSERT INTO {0} ({1}) VALUES ({2});".format(table, columns, values)
    cur.execute(SQL, dict)
    if commit:
        conn.commit()
    return True

def select(table: str, columns: list = [], conditions: list = []) -> list:
    """
    Works as a SELECT statement for one table
    Parameters:
        table: table name (str)
        conditions: valid SQL comparisons ([str])
        columns: name of selected columns ([str])

        returns: a list of rows (represented as key-value pairs) which fulfill the conditions ([dict])
    """

    SQL = "SELECT {0} FROM {1} {2}"
    if len(columns) == 0:
        selected = "*"
    else:
        selected = ", ".join(columns)

    if len(conditions) == 0:
        where = ""
    else:
        where = "WHERE " + " AND ".join(conditions)
    SQL = SQL.format(selected, table, where)

    cur.execute(SQL)
    values = cur.fetchall()
    cur.execute("Select {0} FROM {1} LIMIT 0".format(selected, table))
    colnames = [desc[0] for desc in cur.description]
    result = []
    for value in values:
        value_dict = {}
        for i in range(0, len(value)):
            value_dict[colnames[i]] = value[i]
        result.append(value_dict)

    return result

def delete(table: str, conditions: list = [], commit: bool = True) -> bool:
    """
    Backups then deletes rows from the selected table. The backups are stored in the archive.json file.
    Parameters:
        table: string
        conditions: list
    """
    
    data = {}
    with open("archive.json", "r") as file:
        try:
            data = json.load(file)
        except ValueError:
            data = {}
        if table not in data:
            data[table] = []

    data[table] += select(table, [], conditions)
    deleted = deletePermanent(table, conditions, commit)
    if deleted:
        with open("archive.json", "w+") as file:
            json.dump(data, file, default=str)
    return deleted

def deletePermanent(table: str, conditions: list = [], commit: bool = True) -> bool:
    SQL = "DELETE FROM {0} {1};"
    if len(conditions) == 0:
        confirmation = input("You did not give conditions! Are you sure you want to delete every entry in the table? Type 'Yes' if so\n")
        if confirmation != "Yes":
            print("Delete aborted!")
            return False
        where = ""
    else:
        where = "WHERE " + " AND ".join(conditions)
    SQL = SQL.format(table, where)
    cur.execute(SQL.format())
    
    if commit:
        conn.commit()
    return True

def update(table: str, dict: dict, conditions: list = [], commit: bool = True) -> bool:
    SQL = "UPDATE {0} SET {1}{2};"
    if len(conditions) == 0:
        confirmation = input("You did not give conditions! Are you sure you want to update every entry in the table? Type 'Yes' if so\n")
        if confirmation != 'Yes':
            print("Update aborted!")
            return False
    
    columns = ", ".join(dict.keys())
    values = ", ".join(['{0} = %({0})s'.format(k) for k in dict.keys()])
    if len(conditions) == 0:
        where = ""
    else:
        where = " WHERE " + " AND ".join(conditions)
    SQL = SQL.format(table, values, where)
    print(SQL)
    print(cur.mogrify(SQL, dict))
    cur.execute(SQL, dict)
    if commit:
        conn.commit()
    return True

def restore(table: str, conditions: dict = {}) -> bool:
    """Restores a table's deleted rows. The deleted rows are stored in the 'archive.json' file.

    Args:
        table (str): Specifies which table to restore rows for.
        conditions (dict, optional): Specifies which rows should be restored. Defaults to {}.
    """
    data = {}
    with open("archive.json", "r") as file:
        try: 
            data = json.load(file)
        except ValueError:
            print("There are no backups!")
            return False

    try:
        table_json = data[table]
    except KeyError:
        print("There hasn't been any backups from this table!")
        return False
    
    new_table = []
    for entry in table_json:
        valid = True
        for k, v in conditions.items():
            if entry[k] != v:
                valid = False
                new_table.append(entry)
                break
        if valid:
            insert(table, entry, False)
            data[table]
    

    data[table] = new_table
    
    with open("archive.json", "w+") as file:
        json.dump(data, file, default=str)
    conn.commit()
    return False

def generateTable(table: str, rows: int, dateStart: datetime = datetime.now() - timedelta(365) , dateFinish: datetime = datetime.now(), seed: int = random.randint(0, 10000), commit: bool = True) -> list:
    """_summary_

    Args:
        table (str): _description_
        rows (int): _description_
        dateStart (datetime, optional): _description_. Defaults to datetime.now()-timedelta(365).
        dateFinish (datetime, optional): _description_. Defaults to datetime.now().
        seed (int, optional): _description_. Defaults to random.randint(0, 10000).
        commit (bool, optional): _description_. Defaults to True.

    Returns:
        list: _description_
    """
    
    if dateStart > dateFinish:
        raise Exception("Start date can not be later than finish date!")
    if rows < 1:
        raise Exception("Number of rows must be greater than 1!")
    random.seed(seed)
    Faker.seed(seed)
    
    cur.execute("TRUNCATE {0} RESTART IDENTITY CASCADE;".format(table))
    result = []
    match table:
        case "users":
            #There are 4 levels, the number of each is evenly distributed
            #for example: 6 Senior, 6 Medior, 6 Junior, 6 intern
            levels = ["Senior", "Medior", "Junior"]
            for i in range(0, rows):
                result.append({
                    "employer_number": random.randrange(1, i+2, 1),
                    "creation_date": fake.date_between_dates(dateStart, dateFinish),
                    "username": fake.email(),
                    "password": fake.password(),
                    "level": random.choice(levels)
                })
            result[0]["level"] = "Senior"
        case "platforms":
            for i in range(0, rows):
                result.append({
                    "courses": 0,
                    "platform_name": fake.catch_phrase(),
                    "url": fake.domain_name() + "/courses"
                })
        case "courses":
            platforms = select("platforms")
            platforms_count = len(platforms)
            if platforms_count == 0:
                raise Exception("You need to generate platforms first!")
            
            tags = ["algorithms", "design", "science", "programming", "machine learning", "virtual reality", "web development", "software design", "sql", "data engineering", "data science", "maths", "computer science"]

            for i in range(0, rows):
                platform = fake.random_element(platforms)
                result.append({
                    "course_name": fake.catch_phrase(),
                    "platform_id": platform["platform_id"],
                    "duration": fake.time_delta(timedelta(hours = 8)),
                    "creation_date": fake.date_between_dates(dateStart, dateFinish),
                    "tags": ", ".join(fake.random_elements(elements=tags, length=3, unique=True)),
                    "photo": platform["url"] + "/" + str(i+1) + "/photos/thumbnail.jpg"
                })
        case "pictures":
            platforms = select("platforms")
            
            if len(platforms) == 0:
                raise Exception("You need to generate platforms first!")

            courses = select("courses")

            if len(courses) == 0:
                raise Exception("You need to generate courses first!")
            
            for i in range(0, rows):
                result.append({
                    "course_id": fake.random_element(courses)["course_id"],
                    "platform_id": fake.random_element(platforms)["platform_id"]
                })
        case "ongoing_training":
            users = select("users")

            if len(users) == 0:
                raise Exception("You need to generate users first!")
            
            courses = select("courses")

            if len(courses) == 0:
                raise Exception("You need to generate courses first!")
            
            if rows > len(users)*len(courses):
                raise Exception("It's impossible to generate this many rows with the current number of users and courses!")
            
            counter = 0
            while counter < rows:
                user_id = fake.random_element(users)["user_id"]
                course_id = fake.random_element(courses)["course_id"]
                contains = False
                for training in result:
                    if ("user_id", user_id) in training.items() and ("course_id", course_id) in training.items():
                        contains = True
                        break
                if contains:
                    continue
                result.append({
                    "user_id": user_id,
                    "course_id": course_id,
                    "status": fake.pybool(),
                    "completion_percentage": fake.pyfloat(min_value=0, max_value=99),
                    "start_date": dateStart,
                    "finish_date": dateFinish
                })
                counter += 1
        case "certification_id": 
            users = select("users", ["user_id"])

            if len(users) == 0:
                raise Exception("You need to generate users first!")
            
            courses = select("courses", ["course_id", "duration"])

            if len(courses) == 0:
                raise Exception("You need to generate courses first!")
            
            ongoing_trainings = select("ongoing_training", ["user_id", "course_id"])
            
            if rows > len(users)*len(courses) + len(ongoing_trainings):
                raise Exception("It's impossible to generate this many rows with the current number of users, courses and ongoing trainings!")
            
            counter = 0
            while counter < rows:
                user = fake.random_element(users)["user_id"]
                course = fake.random_element(courses)
                contains = False
                for training in ongoing_trainings:
                    if ("user_id", user) in training.items() and ("course_id", course["course_id"]) in training.items():
                        contains = True
                        break
                if contains:
                    continue
                for certification in result:
                    if("user_id", user) in certification.items() and ("course_id", course["course_id"]) in certification.items():
                        contains = True
                        break
                if contains:
                    continue
                result.append({
                    "user_id": user,
                    "course_id": course["course_id"],
                    "completion_duration": course["duration"] + fake.time_delta(timedelta(days=5)),
                    "completion_date": dateFinish
                })
                counter += 1
        case "reviews":
            certifications = select("certification_id", ["user_id", "course_id"])
            if rows > len(certifications):
                raise Exception("Only certified users can post reviews! The number of reviews can not be greater than the number of certifications!")

            for i in range(0, rows):
                cert_index = random.randint(0, len(certifications)-1)
                liked = fake.pybool()
                score = 0
                if liked:
                    score = random.randint(4, 10)
                else:
                    score = random.randint(1, 7)
                result.append({
                    "user_id": certifications[cert_index]["user_id"],
                    "course_id": certifications[cert_index]["course_id"],
                    "feedback": fake.text(max_nb_chars = 180),
                    "liked": liked,
                    "ranking_score": score
                })
                del certifications[cert_index]
        case _table:
            raise Exception("{0} is not supported!".format(_table))
    
    for res in result:
        insert(table, res, False)
    if commit:
        conn.commit()
    return result

def generateAllFresh(seed: int = random.randint(0, 100000)):
    """ Runs the DDL.sql file (which drops then regenerates all the tables) then inserts new values."""
    
    cur.execute(open("DDL.sql", "r").read())

    print("Generating users...")
    generateTable("users",              50,  seed=seed)
    print("Generating platforms...")
    generateTable("platforms",          10,  seed=seed)
    print("Generating courses...")
    generateTable("courses",            50,  seed=seed)
    print("Generating pictures...")
    generateTable("pictures",           100,  seed=seed)
    print("Generating ongoing trainings...")
    generateTable("ongoing_training",   150, seed=seed)
    print("Generating certification IDs...")
    generateTable("certification_id",   200, seed=seed)
    print("Generating reviews...")
    generateTable("reviews",            100, seed=seed)
    print("Data generated successfully!")