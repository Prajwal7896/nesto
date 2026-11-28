from main import app

@app.route("/export" , methods = ["GET"])
def export():
    return "Export functionality to be implemented"