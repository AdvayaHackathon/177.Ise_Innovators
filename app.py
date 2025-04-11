
from flask import Flask, render_template, request
import pickle

app = Flask(__name__)
model = pickle.load(open("model.pkl", "rb"))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/predict', methods=["POST"])
def predict():
    try:
        data = [float(x) for x in request.form.values()]
        result = model.predict([data])[0]
        return render_template("results.html", result="Success" if result == 1 else "Not Successful")
    except:
        return render_template("results.html", result="Invalid Input")

if __name__ == "__main__":
    app.run(debug=True)
