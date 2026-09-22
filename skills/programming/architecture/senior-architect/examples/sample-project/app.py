from flask import Flask
app = Flask(__name__)

@app.route("/api/users")
def users():
    return {"users": []}
