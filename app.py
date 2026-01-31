from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# Charger les données
data = pd.read_csv("data.csv")
data["user_id"] = data["user_id"].astype(int)


@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/recommend", methods=["POST"])
@app.route("/recommend", methods=["POST"])
def recommend():
    user_id = int(request.json.get("user_id"))

    seen = data[data["user_id"] == user_id]["movie_title"]

    popular = data["movie_title"].value_counts().index

    recommendations = [m for m in popular if m not in seen][:5]

    return jsonify({"recommendations": recommendations})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


