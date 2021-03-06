from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
# from googleapiclient import discovery
from google.cloud import bigquery
# from oauth2client.client import GoogleCredentials
client = bigquery.Client()

app = Flask(__name__)
api = Api(app)

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
        client = bigquery.Client()
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

class CreateUser(Resource):
    def get(self):
        client = bigquery.Client()
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help="Name cannot be blank!")
        args = parser.parse_args()
        user_name = args['name']
        query = """
            SELECT max(user_id) max_id
            FROM `sbx-nameswipe-1.main.users` 
        """
        query_res = client.query(query)
        for row in query_res:
            print(row)

        user_id = int(row.max_id)+1
        print(user_id)

        row_to_insert = [
            {u"user_id": user_id, u"user_name": user_name},
        ]

        table_id = "sbx-nameswipe-1.main.users"
        errors = client.insert_rows_json(table_id, row_to_insert)  # Make an API request.
        
        parser.remove_argument('name')
        
        if errors == []:
            return ({'user_id':user_id},200)
        else:
            return ({'error':f"{errors}"},400)
        

class CreateBaby(Resource):
    def get(self):
        client = bigquery.Client()
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', required=True, help="user_id cannot be blank!")
        parser.add_argument('baby_sex', required=True, help="baby_sex cannot be blank!")
        args = parser.parse_args()
        user_id = args['user_id']
        baby_sex = args['baby_sex']
        
        query = """
            SELECT max(baby_id) max_id
            FROM `sbx-nameswipe-1.main.babies` 
        """
        query_res = client.query(query)
        for row in query_res:
            print(row)

        baby_id = int(row.max_id)+1

        row_to_insert = [
            {u"user_id": user_id, u"baby_id": baby_id, u"baby_sex": baby_sex},
        ]

        table_id = "sbx-nameswipe-1.main.babies"
        errors_babies = client.insert_rows_json(table_id, row_to_insert)
        
        table_id = "sbx-nameswipe-1.main.decisions"
        row_to_insert = [
            {u"baby_id": baby_id, u"user_id": user_id, u"name": ""},
        ]
        errors_decisions = client.insert_rows_json(table_id, row_to_insert)
        
        parser.remove_argument('user_id')
        parser.remove_argument('baby_sex')
        
        if errors_babies == [] and errors_decisions == []:
            return ({'baby_id':baby_id},200)
        else:
            return ({'error':f"error_babies {errors_babies}, error_decisions {errors_decisions}"},400)

class SetDecisions(Resource):
    def get(self):
        client = bigquery.Client()
        parser = reqparse.RequestParser()
        parser.add_argument('baby_id', required=True, help="baby_id cannot be blank!")
        parser.add_argument('user_id', required=True, help="user_id cannot be blank!")
        parser.add_argument('names', required=True, help="names needs to be an array seperate by commas")
        parser.add_argument('scores', required=True, help="scores needs to be a numeric array seperate by commas")
        args = parser.parse_args()
        baby_id = args['baby_id']
        user_id = args['user_id']
        names = args['names']
        scores = args['scores']
        
        return_names = names.replace(" ","").split(',')
        return_scores = scores.replace(" ","").split(',')

        rows_to_insert = []
        for ind,score in enumerate(return_scores):
            row_to_insert = {u"baby_id": baby_id, u"user_id": user_id, u"name": return_names[ind].lower(), u"score" :float(score)}
            rows_to_insert.append(row_to_insert)

        table_id = "sbx-nameswipe-1.main.decisions"

        errors = client.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
        if errors == []:
            return ({'status':"success"},200)
        else:
            return ({'error':f"{errors}"},400)
        
        parser.remove_argument('user_id')
        parser.remove_argument('baby_id')
        parser.remove_argument('names')
        parser.remove_argument('scores')

class GetRecommendations(Resource):
    def get(self):
        client = bigquery.Client()
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', required=True, help="user_id cannot be blank!")
        parser.add_argument('baby_id', required=True, help="baby_id cannot be blank!")
        args = parser.parse_args()
        user_id = args['user_id']
        baby_id = args['baby_id']
        
        query = f"""
            WITH past_decisions AS(
            SELECT 
              name,
              baby_sex
            FROM
            `sbx-nameswipe-1.main.decisions` AS decisions
            JOIN
            `sbx-nameswipe-1.main.babies` AS babies
            USING (baby_id)
            WHERE decisions.user_id = {user_id} AND baby_id = {baby_id}
            )
            SELECT name
            FROM `sbx-nameswipe-1.tal_dev.baby_features`
            WHERE name_lower NOT IN (SELECT name FROM past_decisions)
            AND sex = (select distinct baby_sex FROM past_decisions)
            AND rank_bracket > 0.8
            ORDER BY RAND()
            LIMIT 50                
        """
        
        query_res = client.query(query)
        
        parser.remove_argument('user_id')
        parser.remove_argument('baby_id')
        
        results = {} #empty dic
        counter = 0
        for row in query_res:
            counter += 1
            results[f"name_{counter}"] = row.name
        return({'res': results},200)
        
# api.add_resource(Users, '/users')  # '/users' is our entry point for Users
# api.add_resource(Locations, '/locations')  # and '/locations' is our entry point for Locations
api.add_resource(PrintNames, '/printnames')  # and '/printnames' is our entry point to print names
api.add_resource(CreateUser, '/createuser')  # '/createuser' is our entry point to create user
api.add_resource(CreateBaby, '/createbaby')  # '/createbaby' is our entry point to create baby
api.add_resource(GetRecommendations, '/getrecommendations')  # '/getrecommendations' is our entry point to get 10 random recs
api.add_resource(SetDecisions, '/setdecisions')  # '/setdecisions is used to update user scores per name list

if __name__ == "__main__":
    app.run(debug=True)
