from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import get_recommendation
import pandas as pd
import json

app = Flask(__name__)

CORS(app)

@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":
        data = json.loads(request.data)
        movie_name = data["movie_name"]
        print("Movie name recieved from website: ",movie_name)
        movies_dictionary = get_recommendation(str(movie_name))
        return jsonify(movies_dictionary)

if __name__ == "__main__":
    app.run(debug=True)