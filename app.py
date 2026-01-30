from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import pickle
import os

# 🔹 Configuration Flask
app = Flask(__name__, static_folder="")  # "" = racine pour index.html
CORS(app)

# 🔹 Charger les données et le modèle
# Assurez-vous que vos fichiers sont à la racine du projet
MOVIES_FILE = "u.item"
RATINGS_FILE = "u.data"
MODEL_FILE = "recommendation_model.pkl"

movies = pd.read_csv(MOVIES_FILE, sep='|', encoding='latin-1', header=None,
                     names=['movie_id','movie_title','release_date','video_release_date','IMDb_URL'] + list(range(19)))
ratings = pd.read_csv(RATINGS_FILE, sep='\t', names=['user_id','movie_id','rating','timestamp'])

with open(MODEL_FILE, "rb") as f:
    model = pickle.load(f)

# 🔹 Route principale pour la page web
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# 🔹 Endpoint pour récupérer les recommandations
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    user_id = data.get("user_id")
    if user_id is None:
        return jsonify({"error": "user_id is required"}), 400

    # Exemple simple : ici tu peux remplacer par ton vrai modèle
    # candidate_movies = ... (logique du modèle)
    # recommended = model.predict(user_id) ...
    recommended = ["Toy Story (1995)", "GoldenEye (1995)", "Four Rooms (1995)"]

    return jsonify({"recommendations": recommended})

# 🔹 Lancer l'application (nécessaire pour Azure)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Azure définit automatiquement la variable PORT
    app.run(host="0.0.0.0", port=port)

