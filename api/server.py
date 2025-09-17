import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Render!"

if __name__ == "__main__":
    # Render provides a $PORT env var — default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
