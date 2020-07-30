import psycopg2

#establishing the connection
conn = psycopg2.connect(
   database="test", user='postgres', password='Array @1234', host='127.0.0.1', port= '5432'
)
conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Preparing query to create a database
sql = '''CREATE TABLE book(
        Id BIGSERIAL PRIMARY KEY,
        Author VARCHAR(50) NOT NULL,
        Language VARCHAR(50) NOT NULL,
        Edition VARCHAR(50) NOT NULL
)''';

#Creating a database
cursor.execute(sql)
print("Database created successfully........")

#Closing the connection
#conn.close()