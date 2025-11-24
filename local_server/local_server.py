from flask import Flask, jsonify

HOST = "0.0.0.0"
PORT = 5000

app = Flask(__name__)
toggle = {"state": True}

@app.route("/check", methods=["GET"])
def check():
    # TODO: Implement face recognition module and call here
    toggle["state"] = not toggle["state"]
    return jsonify({"result": "yes" if toggle["state"] else "no"})

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
