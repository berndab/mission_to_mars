from flask import Flask, render_template, request
from flask_pymongo import PyMongo
import scraping

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

@app.route("/")
def index():

   # Get mars data dictionary from Mongo
   mars = mongo.db.mars.find_one()

   # Render the homepage with Mars data dictionary
   return render_template("index.html", mars=mars)

@app.route("/scrape")
def scrape():

   # Get Mars web data
   mars_data_dict = scraping.scrape_all()

   # Store Mars data in Mongo
   mongo.db.mars.update({}, mars_data_dict, upsert=True)
   
   # Render the scraping results page
   return render_template("scrape_results.html")

@app.route("/mars_hemispheres")
def hemi_image():

   # Get mars data from Mongo
   mars = mongo.db.mars.find_one()
   
   # Get the mars hemisphere dictionary list
   mars_hemispheres = mars["hemispheres"]

   # Render the Mars hemisphere full image display page
   # with mars hemisphere dist list
   return render_template("mars_hemispheres.html", mars_hemispheres=mars_hemispheres )


if __name__ == "__main__":
    app.run(debug=True)