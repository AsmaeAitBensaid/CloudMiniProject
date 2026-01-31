from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle

app = Flask(__name__)

# Charger le modèle
with open("recommendation_model.pkl", "rb") as f:
    model = pickle.load(f)

# Charger les films (titre + id)
movies = pd.read_csv("data.csv")

def model_recommend(user_id, top_n=5):
    """Renvoie une liste de movie_id recommandés pour user_id"""
    # Exemple : suppose que model est un dictionnaire {user_id: [movie_id, ...]}
    return model.get(user_id, [])[:top_n]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    user_id = int(request.json.get("user_id"))
    recommended_ids = model_recommend(user_id)
    
    if not recommended_ids:
        return jsonify({"error": "No recommendations found"}), 404
    
    recs = movies[movies["movie_id"].isin(recommended_ids)][["movie_id", "movie_title"]].drop_duplicates()
    return jsonify(recs.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)




