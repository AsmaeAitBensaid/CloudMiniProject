from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# Charger les données
data = pd.read_csv("data.csv")

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    user_id = request.json.get("user_id")

    # Films vus par l'utilisateur
    seen = data[data["user_id"] == user_id]["movie_title"]

    # Films populaires
    popular = (
        data["movie_title"]
        .value_counts()
        .index
    )

    # Recommandations
    recommendations = [m for m in popular if m not in seen][:5]

    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


