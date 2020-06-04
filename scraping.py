#!/usr/bin/env python
# coding: utf-8


# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


def scrape_all():

    # Initiate browser with headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    # Get current new title and new paragraph
    news_title, news_paragraph = mars_news(browser)

    # Poplate the dictionary with all scraping data
    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres" : mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Close the browser
    browser.quit()

    return mars_data

def mars_news(browser):

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
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_p


def featured_image(browser):

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
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url


def mars_facts():
    
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

def mars_hemispheres(browser):

    # Mars' hemispheres webpage URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    # List of titles of the images to retrieve
    image_title_list = ["Cerberus Hemisphere", "Schiaparelli Hemisphere", "Syrtis Major Hemisphere", "Valles Marineris Hemisphere"]

    # List to store image data
    image_data_list = []

    for title in image_title_list:

        # Start on the hemisphere homepage
        browser.visit(url)

        # Find link to full size hemisphere image
        element = browser.links.find_by_partial_text(title)
        element.click()

        html = browser.html
        img_soup = BeautifulSoup(html, 'html.parser')

        try:
            
            # Get hemisphere full size image URL
            img_url = img_soup.select_one("div.downloads ul li a").get("href")

        except AttributeError:
            return None

        # Append the hemisphere image data dictionary to the list
        image_data_list.append({"title" : title, "img_url" : img_url})

    return image_data_list


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
