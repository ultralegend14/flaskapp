from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
import os

app = Flask(__name__)

# Configure MongoDB Atlas connection string.
# Recommended: set the MONGO_URI as an environment variable.
uri = "mongodb+srv://bharshavardhanreddy924:516474Ta@data-dine.5oghq.mongodb.net/?retryWrites=true&w=majority&ssl=true"

client = MongoClient(uri)
db = client["deepfake_db"]
# We'll use a single document with _id "latest" to store the current ngrok link.
collection = db["ngrok_links"]

def update_latest_link(new_link):
    collection.update_one({"_id": "latest"}, {"$set": {"ngrok_url": new_link}}, upsert=True)

def get_latest_link():
    doc = collection.find_one({"_id": "latest"})
    return doc.get("ngrok_url") if doc else ""

# Home page with embedded HTML/CSS/JS that displays deepfake info and a button linking to the model.
@app.route("/")
def index():
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Deepfake Detection Model</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: #f0f4f8;
          margin: 0;
          padding: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
        }
        .container {
          background: #fff;
          padding: 40px;
          border-radius: 8px;
          box-shadow: 0 4px 10px rgba(0,0,0,0.1);
          max-width: 700px;
          text-align: center;
        }
        h1 {
          color: #333;
        }
        p {
          color: #555;
          font-size: 18px;
          line-height: 1.6;
        }
        .btn {
          display: inline-block;
          background-color: #007bff;
          color: #fff;
          padding: 12px 24px;
          text-decoration: none;
          border-radius: 5px;
          margin-top: 30px;
          transition: background-color 0.3s ease;
        }
        .btn:hover {
          background-color: #0056b3;
        }
      </style>
      <script>
        // Fetch the latest ngrok URL from the server and update the button.
        async function updateModelLink() {
          try {
            const res = await fetch('/get-ngrok');
            const data = await res.json();
            const btn = document.getElementById('modelLink');
            if (data.ngrok_url && data.ngrok_url !== "") {
              btn.href = data.ngrok_url;
              btn.innerText = "Try the Model";
            } else {
              btn.innerText = "Model not available yet";
            }
          } catch (error) {
            console.error("Error fetching model link:", error);
            document.getElementById('modelLink').innerText = "Error loading model link";
          }
        }
        window.onload = updateModelLink;
      </script>
    </head>
    <body>
      <div class="container">
        <h1>Deepfake Detection</h1>
        <p>
          Deepfakes are synthetic media in which a person's likeness is replaced with someone else’s. 
          While this technology offers creative possibilities, it also poses significant risks for misinformation and privacy breaches. 
          It is essential to employ robust detection methods to verify authenticity and protect against potential abuse.
        </p>
        <a id="modelLink" class="btn" href="#">Loading model link...</a>
      </div>
    </body>
    </html>
    '''
    return render_template_string(html_content)

# Endpoint for Codespaces (or another process) to update the ngrok URL.
@app.route("/update-ngrok", methods=["POST"])
def update_ngrok():
    data = request.get_json()
    if data and 'ngrok_url' in data:
        new_link = data["ngrok_url"]
        update_latest_link(new_link)
        return jsonify({"message": "Ngrok URL updated successfully", "ngrok_url": new_link}), 200
    return jsonify({"message": "Invalid data"}), 400

# Endpoint to retrieve the latest ngrok URL.
@app.route("/get-ngrok", methods=["GET"])
def get_ngrok():
    latest_link = get_latest_link()
    return jsonify({"ngrok_url": latest_link})

if __name__ == "__main__":
    # Run on the port assigned by Render or default to 5000.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
