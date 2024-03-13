import numpy as np
import html
import requests
from bs4 import BeautifulSoup

### Scrolling:
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def get_html_of_artist(artist, contemporary = False):
    if contemporary:
        url = f"https://www.e-flux.com/announcements/?c[]=Contemporary%20Art&p[]={artist}"
    else:
        url = f"https://www.e-flux.com/announcements/?p[]={artist}"

    response = requests.get(url)
    html = response.text
    return html

def get_announcements_of_artist(artist, contemporary = False):
    html = get_html_of_artist(artist, contemporary)
    soup = BeautifulSoup(html, "html.parser")
    announcements = soup.find_all("a", class_="preview-announcement__title") #All announcements are in <a> tags with this class, see website
    return announcements

def process_announcements(announcements):
    announcements_list = []
    for announcement in announcements:
        announcement_dict = {}
        announcement_dict['id'] = announcement["href"].split("/")[2] #the link is in the form of /announcements/123456/linktext.../
        announcement_dict['link'] = announcement["href"]
    
        try:
            announcement_dict['id']= int(announcement_dict['id'])
        except:
            print(f"'ID' problem with announcement: {announcement}, id: {announcement_dict['id']}")

        #TODO announcement_dict['artist_name'] = TODO (after <a> tag, before </br> tag, but may not have a name)
            
        announcement_dict['title'] = None
        try:
            announcement_dict['title'] = announcement.find("em").text.strip()
        except:
            try:
                announcement_dict['title'] = announcement.text.strip()
            except:
                print(f"Problem with announcement: {announcement}")
        
        announcements_list.append(announcement_dict)

    return announcements_list


def scroll_scrape_website(url):
    #Note: this is recommended only for 1-time use, because it takes time to open the browser.
    #For more artists the scroll_scrape_multiple_websites() function is recommended, and only if get_announcements_of_artist() is at its limit: 30
    driver = webdriver.Firefox()

    # Go to your page url
    driver.get(url)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Now you can parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    return soup
