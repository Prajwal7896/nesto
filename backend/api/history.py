from main import app

@app.route("/history" , methods = ["GET"])
def get_history():
    return "History functionality to be implemented"