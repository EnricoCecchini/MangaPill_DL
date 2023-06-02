# Import necessary modules
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import configparser

# Set up the Chrome driver
def make_browser(url):
    # Set webdriver options
    options = Options()
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--start-minimized')
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36")

    # Create webdriver
    browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)
    browser.get(url)
    return browser

def get_manga():
    # input comic URL of 1st page
    while True:
        url = input('URL: ')

        # Test if URL is valid
        try:
            requests.get(url)
            break
        except requests.exceptions.MissingSchema:
            print("Invalid URL")
        except requests.ConnectionError:
            print("Invalid URL")
    
    # input name
    name = input('Comic Name: ')
    name = name.replace('/',' ').replace("?",'').replace(":",' -')

    return url, name

# Create root folder for manga
def make_folder(name):
    # Create root folder for manga
    if not os.path.exists(name):
        os.makedirs(name)

# Download chapter
def download_chapter(browser, name):
    nextChapter = ActionChains(browser)
    oldURL = ''

    config = configparser.ConfigParser()
    config.read('config.ini')
    user_agent = config['Settings']['user_agent']
    referer = config['Settings']['referer']
    while True:
        url = browser.page_source

        # Check if the page has changed
        if oldURL == url:
            break
        # Find all pages with BS4
        soup = BeautifulSoup(url, 'html.parser')
        chapterTitle = soup.find('h1').text
        chapterTitle = chapterTitle.replace('/',' ').replace("?",'').replace(":",' -')
        print(chapterTitle)
        
        make_folder(f'{name}/{chapterTitle}')
        
        pageHTML = soup.find_all('picture')
        header = {
            "user-agent": user_agent,
            "referer": referer
        }
        i = 0
        for p in pageHTML:
            img = p.find('img')
            #print(img, type(img))
            imgURL = img['data-src']

            # Download page
            page = requests.get(imgURL, headers=header)
            imgTitle = f'{name}/{chapterTitle}/{chapterTitle} pg{i+1}.jpg'

            #print(page)
            with open(f'{name}/{chapterTitle}/{chapterTitle} pg{i+1}.jpg', 'wb') as f:
                f.write(page.content)

            i += 1

        # Click next chapter right-arrow hotkey
        nextChapter.send_keys(Keys.ARROW_RIGHT).perform()
        oldURL = url

def main():
    # Get manga URL and name
    url, name = get_manga()

    browser = make_browser(url)

    # Create root folder for manga
    make_folder(name)

    # Download chapter
    download_chapter(browser, name)

    print('Done!')

main()
