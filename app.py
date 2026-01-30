from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

data = pd.read_csv("data.csv")

@app.route("/recommend", methods=["POST"])
def recommend():
    content = request.json
    user_id = int(content["user_id"])
    top_n = int(content.get("top_n", 5))

    if user_id not in data["user_id"].values:
        return jsonify({"recommendations": []})

    user_movies = set(data[data["user_id"] == user_id]["movie_id"])

    similar_users = data[
        (data["movie_id"].isin(user_movies)) &
        (data["user_id"] != user_id)
    ]["user_id"].unique()

    candidate_movies = data[data["user_id"].isin(similar_users)]["movie_id"]

    recommended_ids = (
        candidate_movies[~candidate_movies.isin(user_movies)]
        .value_counts()
        .head(top_n)
        .index
    )

    titles = (
        data[data["movie_id"].isin(recommended_ids)]
        ["movie_title"]
        .unique()
        .tolist()
    )

    return jsonify({"recommendations": titles})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
