from flask import Flask, render_template

from flask import Flask
import stellar_net

app = Flask(__name__)
app.register_blueprint(stellar_net)

if __name__ == "__main__":
    app.run(debug=True)

