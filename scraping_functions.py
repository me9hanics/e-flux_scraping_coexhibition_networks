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
        url = f"https://www.e-flux.com/announcements/?c[]=Contemporary%20Art&c[]=Data%20%26%20Information&c[]=Installation&c[]=Mixed%20Media&c[]=Posthumanism&c[]=Postmodernism&c[]=Technology&p[]={artist}"
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

def get_announcements_html(html):
    if isinstance(html, BeautifulSoup):
        soup = html
    else: #Also support soup as input
        soup = BeautifulSoup(html, "html.parser")

    announcements = soup.find_all("a", class_="preview-announcement__title") #All announcements are in <a> tags with this class, see website
    return announcements

def get_parts_of_soup_block(soup_block):
    parts = []
    for i in soup_block:
        parts.append(i)
    return parts

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

        #(after <a> tag, before </br> tag, but may not have a name) #TODO make it more robust
        announcement_dict['title_artists'] = None
        parts = get_parts_of_soup_block(announcement)
        num_of_artists = np.sum([1 for x in parts if x.name == "br"])
    
        if num_of_artists > 0:
            artist_names = []
            for part in parts:
                if part.name == "br":
                    artist_names += [last_part]
                else:
                    last_part = part.get_text().strip()
            announcement_dict['title_artists'] = ", ".join(artist_names)
        

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

def get_subtitles_and_announcement_dates(soup):
    subtitles = soup.findAll('div', class_='preview-announcement__subtitle')
    announcement_dates = soup.findAll('div', class_='preview-announcement__date')
    subtitles = [subtitle.text.strip() for subtitle in subtitles]
    announcement_dates = [announcement_date.text.strip() for announcement_date in announcement_dates]
    return subtitles, announcement_dates

### Scrolling functions:

def scroll_scrape_website(url):
    #Note: this is recommended only for 1-time use, because it takes time to open the browser.
    #For more artists the scroll_scrape_multiple_websites() function is recommended, and only if get_announcements_of_artist() is at its limit: 30
    driver = webdriver.Firefox()#Open Firefox
    driver.get(url) #Open the website

    #Scroll height: useful for scrolling
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #Scroll to "height"-> bottom of the page
        time.sleep(2)#Wait for loading
        #Calculate new height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height: #We didn't scroll anymore
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    return soup

def scroll_scrape_website_with_retry(url, driver = None, close_driver = True):
    #Note: this is recommended only for 1-time use, because it takes time to open the browser.
    #For more artists the scroll_scrape_multiple_websites() function is recommended, and only if get_announcements_of_artist() is at its limit: 30
    
    if driver is None:
        driver = webdriver.Firefox()
    driver.get(url)  #Open the website

    #Scroll height: useful for scrolling
    last_height = driver.execute_script("return document.body.scrollHeight")

    step_counter = 0

    while True:
        step_counter += 1
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  #Scroll to "height"-> bottom of the page
        time.sleep(2)  #Wait for loading
        #Calculate new height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  #We didn't scroll anymore
            if step_counter == 1: #We retry if this is first iteration. This is because the website may not have loaded properly
                continue
            else:
                break
        last_height = new_height
        

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    if close_driver:
        driver.quit()

    return soup

def scroll_scrape_multiple_websites(urls):
    #Note: this is recommended for multiple artists, because it takes time to open the browser only once.
    driver = webdriver.Firefox()  #Open Firefox

    all_soups = []
    for url in urls:
        driver.get(url)  #Open the website

        #Scroll height: useful for scrolling
        last_height = driver.execute_script("return document.body.scrollHeight")

        step_counter = 0
        while True:
            step_counter += 1
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  #Scroll to "height"-> bottom of the page
            time.sleep(2)  #Wait for loading
            #Calculate new height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  #We didn't scroll anymore
                if step_counter == 1:
                    continue
                else:
                    break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_soups.append(soup)

    driver.quit()

    return all_soups

def get_announcements_of_artist_scroll_if_needed(artist, driver=None, close_driver = True, subtitles_and_dates=True, contemporary = False, silent = True):
    if driver is None:
        driver = webdriver.Firefox()  #Open Firefox

    html = get_html_of_artist(artist, contemporary)
    soup = BeautifulSoup(html, "html.parser")
    artist_announcements = get_announcements_html(soup)
    if len(artist_announcements) == 30:
        url = f"https://www.e-flux.com/announcements/?p[]={artist}"
        if contemporary:
            url += "&c[]=Contemporary%20Art&c[]=Data%20%26%20Information&c[]=Installation&c[]=Mixed%20Media&c[]=Posthumanism&c[]=Postmodernism&c[]=Technology"

        if not silent:
            print(f"{artist}: over 30 announcements. Scrolling")
        soup = scroll_scrape_website_with_retry(url, driver = driver, close_driver = close_driver)
        artist_announcements = get_announcements_html(soup)
    processed_announcements = process_announcements(artist_announcements)
    if subtitles_and_dates:
        subtitles, announcement_dates = get_subtitles_and_announcement_dates(soup)
        if (len(subtitles) == len(processed_announcements)) and (len(announcement_dates) == len(processed_announcements)):
            for i, announcement in enumerate(processed_announcements):
                announcement['subtitle'] = subtitles[i]
                announcement['announcement_date'] = announcement_dates[i]
        else:
            print(f"Problem with amount of subtitles or announcement dates for:{artist}")
            for i, announcement in enumerate(processed_announcements):
                announcement['subtitle'] = None
                announcement['announcement_date'] = None
    return processed_announcements

def get_announcements_of_artists_scroll_if_needed(artists, contemporary = False):
    all_artists_announcements = []
    for artist in artists:
        artist_dict = {'name': artist, 'announcements': []}
        artist_dict['announcements'] = get_announcements_of_artist_scroll_if_needed(artist, contemporary = contemporary)
        all_artists_announcements.append(artist_dict)
    return all_artists_announcements

def get_announcements_of_artists_scrolling(artists, contemporary=False):
    all_artists_announcements = []
    driver = webdriver.Firefox()  #Open Firefox
    for artist in artists:
        artist_dict = {'name': artist, 'announcements': []}
        artist_dict['announcements'] = get_announcements_of_artist_scroll_if_needed(artist,driver, close_driver=False, contemporary=contemporary) 
        all_artists_announcements.append(artist_dict)
    driver.quit()
    return all_artists_announcements
