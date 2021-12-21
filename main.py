from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
# from googleapiclient import discovery
from google.cloud import bigquery
# from oauth2client.client import GoogleCredentials
client = bigquery.Client()

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

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

# class PrintNames(Resource):
#     def get(self):
#         return({'res': 'snoi'},200)

api.add_resource(PrintNames, '/printnames')  # and '/printnames' is our entry point for printnames

if __name__ == "__main__":
    app.run(debug=True)
