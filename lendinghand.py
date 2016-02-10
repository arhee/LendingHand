from flask import Flask, render_template
import processor

application = Flask(__name__)

@application.route('/listings')
def listings():
    loans = processor.run()
    return render_template("listings.html", loans=loans)


@application.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)