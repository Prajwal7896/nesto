from main import app

@app.route("/sub" , methods = ["POST"])
def sub():
    return "Subtraction functionality to be implemented"
