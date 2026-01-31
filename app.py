from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

# Charger le modèle au démarrage
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def home():
    return "API de recommandation de films"

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        # Adaptez selon votre modèle
        user_id = data.get('user_id')
        # Utilisez votre modèle pour générer des recommandations
        recommendations = model.predict(user_id)  # Exemple
        return jsonify({'recommendations': recommendations.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

**`requirements.txt` :**
```
Flask==3.0.0
pandas
numpy
scikit-learn
gunicorn




