from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle

app = Flask(__name__)

# Charger le CSV avec les titres
data = pd.read_csv("data.csv")

# Charger le modèle entraîné
with open("recommendation_model.pkl", "rb") as f:
    model = pickle.load(f)  # doit contenir un dict: user_id -> liste de movie_id

# Fonction pour obtenir les recommandations
def get_recommendations(user_id, top_n=5):
    # Récupérer les films recommandés par le modèle
    recommended_ids = model.get(user_id, [])[:top_n]
    
    # Obtenir les titres correspondants
    recommended_titles = data[data["movie_id"].isin(recommended_ids)]["movie_title"].unique()
    return list(recommended_titles)

# Page d'accueil
@app.route("/")
def home():
    return render_template("index.html")

# Endpoint pour récupérer les recommandations
@app.route("/recommend", methods=["POST"])
def recommend():
    user_id = int(request.json.get("user_id"))
    recs = get_recommendations(user_id)
    return jsonify({"recommendations": recs})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)



