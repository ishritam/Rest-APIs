from flask import Flask, jsonify, request
import pymongo
import json


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


def conn_db():
    print('Started..')
    coll = None
    try:
        print('Connecting to the Mongo database...')
        #establishing the connection
        clint = pymongo.MongoClient('mongodb://127.0.0.1:27017/')

        #creating a database
        db = clint['test_0']

        #creating a collection or table
        coll = db.books
        print('Connection established...')
    except Expression as e:
        print("Connecting to the Mongo database FAILD!!!",e)
    
    return coll
   


@app.route('/', methods =['GET','POST'])
@auth.login_required
def index():
    coll = conn_db()
 
    if request.method=='GET':
        books_coll = coll.find({})
        #print(f'Featch all books:-> {books_coll}')
        all_books = []
        for b in books_coll:
            all_books.append({'id': b['id'], 'language':b['language'],'author':b['author'],'edition':b['edition']})

        if len(all_books) !=0:
            return jsonify(all_books)
        else:
            return "No Data!!"

    elif request.method=='POST':
        json_post = request.get_json()  #---> was trying for curl
        #print(f'json_post books:-> {json_post}')

        new_json = []
        for i in json_post:
            id = i['id']
            author = i['author']
            language = i['language']
            edition = i['edition']

            new_json.append({'id':id,'author':author,'language':language,'edition':edition})

        obj_id = coll.insert_many(new_json)
        return f'{len(new_json)} new data has been Added Successfully...'

@app.route('/<int:id>', methods = ['GET','PUT','DELETE'])
@auth.login_required
def single_book(id):
    coll = conn_db()
    # get all the ids in MongoDB document. And check if that id is present or not
    if id in [i['id'] for i in coll.find({},{'id':1})]: #this will return all the id's in a list
        if request.method=='GET':
            result = coll.find({'id':id})
            results = []
            for data in result:
                results.append({'id':data['id'],'author':data['author'],'language':data['language'],'edition':data['edition']})
            print(f'Featch result:-> {results}')
            return jsonify(results)


        elif request.method=='PUT':
            json_post = request.get_json()  #---> was trying for curl
            #print(f'json_post books:-> {json_post}')

            #new_json = []
            for i in json_post:
                #id = i['id']
                author = i['author']
                language = i['language']
                edition = i['edition']

                coll.update_many({'id':id},
                        {'$set':{'author':author,'language':language,'edition':edition},'$currentDate':{'UpdatedTime':True}})

            
            return f'id {id} has been Updated Successfully...'

        elif request.method=='DELETE':
            coll.delete_many({'id':id})
            books_coll = coll.find({})
            #print(f'Featch all books:-> {books_coll}')
            all_books = []
            for b in books_coll:
                all_books.append({'id': b['id'], 'language':b['language'],'author':b['author'],'edition':b['edition']})
            
            return f'id {id} has been Deleted from the DB Successfully...{len(all_books)} data left in DB'
    else:
        return "No Data Found!"
if __name__ == "__main__":
    #if there is any error pops up we want to see
    app.run(debug=True)
