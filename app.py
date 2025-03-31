from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Test Généalogie - Ça marche sur Carnac !"

if __name__ == "__main__":
    app.run()
