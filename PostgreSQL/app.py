from flask import Flask, jsonify, request
import psycopg2

from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth

#let's referes in this file
app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

USER_DATA = {
    'admin':'asdf@123'
}


@auth.verify_password
def verify(username,password):
    if not (username,password):
        return False
    return USER_DATA.get(username) == password


def connect_db():
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(database="test", user='postgres', password='Array @1234', host='127.0.0.1', port= '5432')
        print('Connection established...')
    except Expression as e:
        print("Connecting to the PostgreSQL database FAILD!!!")

    return conn
   


@app.route('/', methods =['GET','POST'])
@auth.login_required
def index():
    conn = connect_db()
    cursor = conn.cursor()

    if request.method=='GET':
        cursor.execute("SELECT * FROM book;")
        books = cursor.fetchall()
        print(f'Featch all books:-> {books}')
        all_books = [dict(id=book[0],author=book[1],language=book[2],edition=book[3]) for book in books]
        if all_books!=None:
            return jsonify(all_books)
        else:
            return "No DATA!!"

    elif request.method=='POST':
        #json_post = request.get_json()  ---> was trying for curl

        author = request.form['author']
        language = request.form['language']
        edition = request.form['edition']
        

        #HARD CODED--> sql_query = 'INSERT INTO book(author,language,edition) VALUES ('+"'"+author+"'"+','+ "'"+language+"'"+','+ "'"+edition+"'" +');'
        
        #make the sequence value as last id
        cursor.execute("SELECT MAX(id) FROM book;")
        books_last_id = cursor.fetchall()[-1][0]
        print(f'books_last_id--> {books_last_id}')
        cursor.execute('ALTER SEQUENCE book_id_seq RESTART WITH %s',(books_last_id+1, ))

        #%s are the place holder to pass parameter dynamicaly
        sql_query = 'INSERT INTO book(author,language,edition) VALUES (%s, %s, %s);'
        cursor.execute(sql_query,(author,language,edition))

        # Make the changes to the database persistent
        conn.commit()


        print(cursor.lastrowid)
        print('Successfully added a new row....')

        #after add a row into table let's see the data
        cursor.execute("SELECT * FROM book;")
        books = cursor.fetchall()
        print(f'Featch all books:-> {books}')
        all_books = [dict(id=book[0],author=book[1],language=book[2],edition=book[3]) for book in books]
        if all_books!=None:
            return jsonify(all_books)
        else:
            return "No DATA!!"

@app.route('/<int:id>', methods = ['GET','PUT','DELETE'])
@auth.login_required
def single_book(id):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method=='GET':
        cursor.execute("SELECT * FROM book WHERE id =  %s;",(id, ))
        books = cursor.fetchall()

        print(f'Featch all books:-> {books}')
        all_books = [dict(id=book[0],author=book[1],language=book[2],edition=book[3]) for book in books]
        if all_books!=None:
            return jsonify(all_books)
        else:
            return "No DATA!!"

    elif request.method=='PUT':
        language = request.form['language']
        edition = request.form['edition']
        author = request.form['author']
        
        cursor.execute("UPDATE book SET language = %s, edition= %s, author=%s WHERE id= %s;",(language,edition,author,id))
        # Make the changes to the database persistent
        conn.commit()
        updated_book = {
            'id':id,
            'language':language,
            'edition' : edition,
            'author' : author
        }
        return jsonify(updated_book)


    elif request.method=='DELETE':
        cursor.execute("DELETE FROM book WHERE id=%s;",(id,))
        
        # Make the changes to the database persistent
        conn.commit()

        return f'id {id} row has been Deleted Successfully...'

#this will give the book list as per the url
#http://127.0.0.1:5000/3  will give the 3rd book from the json list
# @app.route('/<id>')
# def each_book(id):
#     id_int = int(id)
#     return jsonify(book_list[id_int])


if __name__ == "__main__":
    #if there is any error pops up we want to see
    app.run(debug=True)
