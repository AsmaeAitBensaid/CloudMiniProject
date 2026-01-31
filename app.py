from flask import Flask, request, jsonify, render_template
import pickle
import os

app = Flask(__name__)

# Charger le modèle
with open('recommandation_model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        user_input = data.get('input')
        
        if user_input is None:
            return jsonify({'error': 'Input manquant'}), 400
        
        recommendations = model.predict([user_input])
        
        return jsonify({
            'recommendations': recommendations.tolist() if hasattr(recommendations, 'tolist') else list(recommendations)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()




