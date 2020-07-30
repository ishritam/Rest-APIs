import pymongo

#establishing the connection
clint = pymongo.MongoClient('mongodb://127.0.0.1:27017/')

#creating a database
db = clint['test_0']

#creating a collection or table
collection = db.books
print(f'collection--> {collection}')
#Preparing query to create a database
query = [{
    'title': 'Python and MongoDB',
    'content': 'PyMongo is fun, you guys are awasome',
    'author': 'Krish'
    },
    {
    'title': 'PostgreSQL',
    'content': 'PostgreSQL is Realtional DB, ',
    'author': 'African'
    },
    {
    'title': 'Flask',
    'content': 'Making an API was not that easy, untill i learnt Flask',
    'author': 'Abdul'
    }
    ]
result = collection.insert_many(query)
print(f"Result id: {id(result)}")

print("Database created successfully........")

