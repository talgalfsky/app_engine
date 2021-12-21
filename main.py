from flask import Flask, render_template
from flask_restful import Resource, Api
# from googleapiclient import discovery
from google.cloud import bigquery
# from oauth2client.client import GoogleCredentials
client = bigquery.Client()

app = Flask(__name__)
api = Api(app)

# parser = reqparse.RequestParser()
# parser.remove_argument('user_id')
# parser.remove_argument('baby_sex')
# parser.remove_argument('name')

@app.route("/")
def homepage():
    return render_template("index.html", title="HOME PAGE")

@app.route("/docs")
def docs():
    return render_template("index.html", title="docs page")

@app.route("/about")
def about():
    return render_template("index.html", title="about page")

class PrintNames(Resource):
    def get(self):
        query = """
        SELECT * 
        FROM `sbx-nameswipe-1.tal_dev.baby_features` 
        LIMIT 5
        """
        query_res = client.query(query)

        results = {} #empty dic
        for row in query_res:
            results[row.name] = row.name
        return({'res': results},200)
    
# class CreateUser(Resource):
#     def get(self):
#         parser.remove_argument('user_id')
#         parser.remove_argument('baby_sex')
#         parser.add_argument('name', required=True, help="Name cannot be blank!")
#         args = parser.parse_args()
#         user_name = args['name']
#         query = """
#             SELECT max(user_id) max_id
#             FROM `sbx-nameswipe-1.main.users` 
#         """
#         query_res = client.query(query)
#         for row in query_res:
#             print(row)

#         user_id = int(row.max_id)+1
#         print(user_id)

#         row_to_insert = [
#             {u"user_id": user_id, u"user_name": user_name},
#         ]

#         table_id = "sbx-nameswipe-1.main.users"
#         errors = client.insert_rows_json(table_id, row_to_insert)  # Make an API request.
        
#         parser.remove_argument('name')
        
#         if errors == []:
#             return ({'user_id':user_id},200)
#         else:
#             return ({'error':f"{errors}"},400)
        

# class CreateBaby(Resource):
#     def get(self):
#         parser.remove_argument('name')
#         parser.add_argument('user_id', required=True, help="user_id cannot be blank!")
#         parser.add_argument('baby_sex', required=True, help="baby_sex cannot be blank!")
#         args = parser.parse_args()
#         user_id = args['user_id']
#         baby_sex = args['baby_sex']
        
#         query = """
#             SELECT max(baby_id) max_id
#             FROM `sbx-nameswipe-1.main.babies` 
#         """
#         query_res = client.query(query)
#         for row in query_res:
#             print(row)

#         baby_id = int(row.max_id)+1
#         print(baby_id)

#         row_to_insert = [
#             {u"user_id": user_id, u"baby_id": baby_id, u"baby_sex": baby_sex},
#         ]

#         table_id = "sbx-nameswipe-1.main.babies"

#         errors = client.insert_rows_json(table_id, row_to_insert)
        
#         parser.remove_argument('user_id')
#         parser.remove_argument('baby_sex')
        
#         if errors == []:
#             return ({'baby_id':baby_id},200)
#         else:
#             return ({'error':f"{errors}"},400)

api.add_resource(Users, '/users')  # '/users' is our entry point for Users
api.add_resource(Locations, '/locations')  # and '/locations' is our entry point for Locations
api.add_resource(PrintNames, '/printnames')  # and '/printnames' is our entry point to print names
# api.add_resource(CreateUser, '/createuser')  # '/createuser' is our entry point to create user
# api.add_resource(CreateBaby, '/createbaby')  # '/createbaby' is our entry point to create baby

if __name__ == "__main__":
    app.run(debug=True)
