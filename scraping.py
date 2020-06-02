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
        "last_modified": dt.datetime.now()
    }

    data_dict = {"mars" : mars_data,
                 "mars_hemisphere" : mars_hemispheres(browser)
                }

    # Close the browser
    browser.quit()

    return data_dict

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    slide_elem = news_soup.select_one('ul.item_list li.slide')
    slide_elem.find("div", class_='content_title')

    try:

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_p


def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()


    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()


    # Parse the resulting html with soup
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
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe       
    df.columns=['Description', 'Value']
    df.set_index('Description', inplace=True)
    
    return df.to_html()

def mars_hemispheres(browser):

    # Mars’ hemispheres webpage
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    image_title_list = ["Cerberus Hemisphere Enhanced", "Schiaparelli Hemisphere Enhanced", "Syrtis Major Hemisphere Enhanced", "Valles Marineris Hemisphere Enhanced"]

    image_data_dict = []

    for title in image_title_list:
        browser.visit(url)

        element = browser.links.find_by_partial_text(title)
        element.click()

        html = browser.html
        parser = BeautifulSoup(html, 'html.parser')
        img_url = parser.select_one("div.downloads ul li a").get("href")

        image_data_list.append({"title" : title, "img_url" : img_url})

    return image_data_list

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
