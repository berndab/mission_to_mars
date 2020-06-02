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
   mars_hemispheres = mongo.db.mars_hemisphere.find()
   mars_data = {
      "mars" : mars,
      "mars_hemispheres" : mars_hemispheres
   }
   return render_template("index.html", mars_data=mars_data)

@app.route("/scrape")
def scrape():
   mars_data_dict = scraping.scrape_all()
   mongo.db.mars.update({}, mars_data_dict["mars"], upsert=True)

   for hemisphere_data in mars_data_dict["mars_hemisphere"]:
      mongo.db.mars_hemisphere.update({"title" : hemisphere_data["title"] }, hemisphere_data, upsert=True)
   
   return "Scraping Successful!"


if __name__ == "__main__":
    app.run(debug=True)