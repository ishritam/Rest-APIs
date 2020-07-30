
# import the required modules
try:
    import os
    import sys
    from flask import Flask, jsonify, request
    import requests
    import json
    import uuid
    from flask_restful import Resource, Api
    from flask_httpauth import HTTPBasicAuth
     
    import elasticsearch
    from elasticsearch import Elasticsearch,helpers

    print("All Modules Loaded ! ")
except Exception as e:
    print("Some Modules are Missing {}".format(e))

#Connect to the ES database
def connect_elasticsearch():
    es = None
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if es.ping():
        print('Yupiee  Connected ')
    else:
        print('Awww it could not connect!')
    return es


#let's referes in this file
app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()


USER_DATA = {
    'admin':'asdf@123'
}

@auth.verify_password
def verify(username,password):
    '''
    This function will verify the username and password
    '''
    if not (username,password):
        return False
    return USER_DATA.get(username) == password

@app.route('/', methods =['GET','POST'])
@auth.login_required
def index():
    es = connect_elasticsearch()
    if request.method=='GET':
        result = es.search(
        index="my_netflix",
        body={
            "query": {
                "match_all": {}
            }
        }, size=3774
        )
        res = result.get('hits')["hits"]

        all_res = []
        for b in res:
            all_res.append({'id': b["_id"], "title":b.get('_source')["title"],"duration":b.get('_source')["duration"],"release_year":b.get('_source')["release_year"]})
        return jsonify(all_res)

    elif request.method=='POST':
        act = request.get_json()

        actions = [
        {
            "_index": "my_netflix",
            "_type": "_doc",
            "_id": uuid.uuid4(),
            "_source": {
                "title": j['title'],
                "release_year": j['release_year'],
                "duration": j['duration']
            }
        }
        for j in act
        ]
        add = helpers.bulk(es,actions)

        if len(act)==add[0]:
            return 'All iteams has been added to ES Record...'
        else:
            return "Couldn't added!!!"


@app.route('/<int:id>', methods = ['GET','PUT','DELETE'])
@auth.login_required
def single_book(id):
    es = connect_elasticsearch()
    result = es.search(
        index="my_netflix",
        body={
            "query": {
                "match_all": {}
            }
        }, size=3774
        )
    res = result.get('hits')["hits"]

    # get all the ids in ELK records. And check if that id is present or not
    #this will return all the id's in a list
    if id in [int(i['_id']) for i in res]: 
        if request.method=='GET':
            result_id = es.search(index="my_netflix",body={"query": {"match": {"_id": id}}})
            
            result = result_id.get('hits')["hits"]
            return jsonify(result)


        elif request.method=='PUT':

            doc_dic = {}
            
            doc_dic['title'] = request.form['title']
            doc_dic['release_year'] = request.form['release_year']
            doc_dic['duration'] = request.form['duration']

            source_to_update = {"doc" : doc_dic }

            response = es.update(index='my_netflix', doc_type="_doc", id=id, body=source_to_update)
            
            if response.get('_shards')['failed'] == 0:
                return f'id {id} has been Updated Successfully...'
            else:
                return "Opps! Update failed!!"

        elif request.method=='DELETE':
            resss = es.delete(index='my_netflix', doc_type="_doc", id= id)
            
            if resss.get('_shards')['failed'] == 0:
                return f'id {id} has been Deleted from the DB Successfully...'
            else:
                return "Opps! Id couldn;t be deleted!!!"
    else:
        return "No Data Found!"    

        
if __name__ == "__main__":
    #It'll automatic re-run once we resave this file 
    app.run(debug=True)
