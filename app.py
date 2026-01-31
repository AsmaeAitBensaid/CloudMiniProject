from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")  # cherche dans templates/

@app.route("/recommend", methods=["POST"])
def recommend():
    user_id = int(request.json.get("user_id"))
    data = pd.read_csv("data.csv")
    recs = data[data["user_id"] == user_id].head(5).to_dict(orient="records")
    return jsonify(recs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)



