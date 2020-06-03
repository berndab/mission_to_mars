from flask import Flask, render_template
from flask_pymongo import PyMongo
import scraping

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

@app.route("/")
def index():
   mars = mongo.db.mars.find_one()
   return render_template("index.html", mars=mars)

@app.route("/scrape")
def scrape():
   mars_data_dict = scraping.scrape_all()

   mongo.db.mars.update({}, mars_data_dict, upsert=True)
   
   return render_template("scrape_results.html")


if __name__ == "__main__":
    app.run(debug=True)