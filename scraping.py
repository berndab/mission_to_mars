# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate browser with headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    # Poplate the dictionary with all scraping data
    mars_data = {
        "news"          : get_mars_news(False, browser),
        "featured_image": get_mars_featured_image(False, browser),
        "facts"         : get_mars_facts(),
        "hemispheres"   : get_mars_hemispheres(browser),
    }

    # Close the browser
    browser.quit()

    return mars_data

# Once mars facts and mars hemisphere data has been retrieved that information 
# DOES NOT change and does not need to be scrapped.  Because of this, this function 
# has been updates to enable functionality to get the mars news data in a standalone 
# request. The mars news data DOES change and must be re-scrapped periodically. 
# 
# However it is more efficient to re-scrape mars news data individually 
# without calling scrape_all() since the function unnecessarily re-scrapes mar facts 
# and mars hemisphere data that has already been stored in mongo and does not change. 
#
# Future enhancement: Updating app.py to just create an endpoint that re-scrapes for 
# updated mars news idividually.
def get_mars_news(news_only, browser):

    # If news_only is true than the request 
    # is for updated mars news only
    if news_only == True:
        browser = Browser("chrome", executable_path="chromedriver", headless=True)

    # Mars' NASA newsite webpage URL
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    try:

        # Find first element in the html list
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent element to find the div containing the new title
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_content = slide_elem.find('div', class_="article_teaser_body").get_text()
    
    except AttributeError:

        return None, None

    finally:
    
        # If new_only is True then the request 
        # is for updated mars news only.
        # The function created the browser
        # and must close the browser
        if news_only == True:
            browser.quit()

    return {
        "title"   : news_title, 
        "content" : news_content,
        "datetime": dt.datetime.now()
    }

# Once mars facts and mars hemisphere data has been retrieved that information 
# DOES NOT change and does not need to be scrapped.  Because of this, this function 
# has been updates to enable functionality to get the mars image data in a standalone 
# request. The mars featured image DOES change and must be re-scrapped periodically. 
# 
# However it is more efficient to re-scrape the featured image data individually 
# without calling scrape_all() since the function unnecessarily re-scrapes mar facts 
# and mars hemisphere data that has already been stored in mongo and does not change. 
#
# Future enhancement: Updating app.py to just create an endpoint that re-scrapes for 
# updated mars featured image idividually.
def get_mars_featured_image(img_only, browser):


    # If image_only is True then the request 
    # is for an updated mars featured image only
    if img_only == True:
        browser = Browser("chrome", executable_path="chromedriver", headless=True)

    # Mars' featured image webpage URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find the full image button and click
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()


    # Find the more info button and click
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()


    # Parse the resulting html
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try:

        # Find the relative image url
        img = img_soup.select_one('figure.lede a img')
        img_url_rel = img.get("src")
        img_text    = img.get("title")

    except AttributeError:
        return None

    finally:
    
        # If new_only is True then the request 
        # is for updated mars news only.
        # The function created the browser
        # and must close the browser
        if img_only == True:
            browser.quit()
   
    return {
        "img_url"   : f'https://www.jpl.nasa.gov{img_url_rel}',
        "text"      : img_text,
        "datetime"  : dt.datetime.now()
    }

def get_mars_facts():
    
    try:
        # Read the Mars data html table into a DataFrame
        # using the Mars' fact webpage URL
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    # Add DataFrame column names
    df.columns=['Description', 'Value']

    # Convert the Mars fact DataFrame to a list
    # of dictionaries with one fact per row
    return df.to_dict("records")

def get_mars_hemispheres(browser):

    # Mars' hemispheres webpage URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    # Start on the hemisphere homepage
    browser.visit(url)

    hemi_soup = BeautifulSoup(browser.html, 'html.parser')

    image_hemi_URL_List = []

    div_descript_list = hemi_soup.find_all("div", class_="description")

    for div_description in div_descript_list:
        image_hemi_URL_List.append("https://astrogeology.usgs.gov" + div_description.find("a")["href"])

    image_hemi_data_list = []
    
    for url in image_hemi_URL_List:
    
        browser.visit(url)

        img_soup = BeautifulSoup(browser.html, 'html.parser')

        try:
            
            # Get hemisphere full size image URL
            img_url = img_soup.select_one("div.downloads ul li a").get("href")

            image_title = img_soup.select_one("div.content h2.title").text
            
            image_description = img_soup.select_one("div.content p").text

        except AttributeError:
            return None

        # Append the hemisphere image data dictionary to the list
        image_hemi_data_list.append({"title" : image_title, "description": image_description, "img_url" : img_url})

    return image_hemi_data_list


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
