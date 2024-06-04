from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import time
from bs4 import BeautifulSoup

driver_path = "D:\chromedriver-win32\chromedriver-win32\chromedriver.exe"
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

jetstar_pacific_url = "https://www.airlinequality.com/airline-reviews/jetstar-pacific/?sortby=post_date%3ADesc&pagesize=100"
bamboo_airways_url = "https://www.airlinequality.com/airline-reviews/bamboo-airways/?sortby=post_date%3ADesc&pagesize=100"
vietjet_air_url = "https://www.airlinequality.com/airline-reviews/vietjetair/?sortby=post_date%3ADesc&pagesize=100"
vietnam_airlines_url = "https://www.airlinequality.com/airline-reviews/vietnam-airlines/?sortby=post_date%3ADesc&pagesize=100"
singapore_airlines_url = "https://www.airlinequality.com/airline-reviews/singapore-airlines/?sortby=post_date%3ADesc&pagesize=100"
quatar_airways_url = "https://www.airlinequality.com/airline-reviews/qatar-airways/?sortby=post_date%3ADesc&pagesize=100"
emirates_url = "https://www.airlinequality.com/airline-reviews/emirates/?sortby=post_date%3ADesc&pagesize=100"
japan_airlines_url = "https://www.airlinequality.com/airline-reviews/japan-airlines/?sortby=post_date%3ADesc&pagesize=100"
air_asia_url = "https://www.airlinequality.com/airline-reviews/airasia/?sortby=post_date%3ADesc&pagesize=100"
korean_air_url = "https://www.airlinequality.com/airline-reviews/korean-air/?sortby=post_date%3ADesc&pagesize=100"
eitihad_airways_url = "https://www.airlinequality.com/airline-reviews/etihad-airways/?sortby=post_date%3ADesc&pagesize=100"
cathay_pacific_url = "https://www.airlinequality.com/airline-reviews/cathay-pacific-airways/?sortby=post_date%3ADesc&pagesize=100"
bangkok_airways_url = "https://www.airlinequality.com/airline-reviews/bangkok-airways/?sortby=post_date%3ADesc&pagesize=100"
malaysia_airlines_url = "https://www.airlinequality.com/airline-reviews/malaysia-airlines/?sortby=post_date%3ADesc&pagesize=100"
eva_air_url = "https://www.airlinequality.com/airline-reviews/eva-air/?sortby=post_date%3ADesc&pagesize=100"
air_china_url = "https://www.airlinequality.com/airline-reviews/air-china/?sortby=post_date%3ADesc&pagesize=100"
air_india_url = "https://www.airlinequality.com/airline-reviews/air-india/?sortby=post_date%3ADesc&pagesize=100"
hongkong_airlines_url = "https://www.airlinequality.com/airline-reviews/hong-kong-airlines/?sortby=post_date%3ADesc&pagesize=100"
indigo_airlines_url = "https://www.airlinequality.com/airline-reviews/indigo-airlines/?sortby=post_date%3ADesc&pagesize=100"
gulf_air_url = "https://www.airlinequality.com/airline-reviews/gulf-air/?sortby=post_date%3ADesc&pagesize=100"

# url_list = [jetstar_pacific_url, 
#             bamboo_airways_url, 
#             vietjet_air_url, 
#             vietnam_airlines_url, 
#             singapore_airlines_url, 
#             quatar_airways_url, 
#             emirates_url, 
#             japan_airlines_url, 
#             air_asia_url, 
#             korean_air_url]

driver.get(gulf_air_url)

def scrape_all_ratings():
    ratings_div = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".review-stats")))

    all_ratings = []
    for rating in ratings_div:
        rows = rating.find_elements(By.TAG_NAME, "tr")

        info = {}
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 1:
                header = cells[0].text
                if 'review-rating-stars stars' in cells[1].get_attribute('class'):
                    filled_stars = cells[1].find_elements(By.CSS_SELECTOR, ".star.fill")
                    highest_value = max([int(star.text) for star in filled_stars]) if filled_stars else None
                    info[header] = highest_value
                else:
                    info[header] = cells[1].text
        all_ratings.append(info)

    return all_ratings

all_ratings = scrape_all_ratings()

ratings_df = pd.DataFrame(all_ratings)

ratings_df.fillna(0, inplace=True)
ratings_df['Aircraft'] = ratings_df['Aircraft'].astype(str)
ratings_df['Type Of Traveller'] = ratings_df['Type Of Traveller'].astype(str)
ratings_df['Seat Type'] = ratings_df['Seat Type'].astype(str)
ratings_df['Route'] = ratings_df['Route'].astype(str)
ratings_df['Date Flown'] = ratings_df['Date Flown'].astype(str)

def scrape_all_titles():
    titles_div = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".body")))

    all_titles = []

    for title in titles_div:
        titles_h2 = title.find_elements(By.TAG_NAME, "h2")
        for h2 in titles_h2:
            all_titles.append(h2.text)

    return all_titles

all_titles = scrape_all_titles()

titles_df = pd.DataFrame(all_titles, columns=['Title'])

# print(titles_df)

def scrape_all_contents():
    content_div = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".text_content")))

    all_contents = []

    for content in content_div:
        all_contents.append(content.text)

    return all_contents

all_contents = scrape_all_contents()

contents_df = pd.DataFrame(all_contents, columns=['Content'])
# print(contents_df)

def scrape_all_info():
    info_div = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".text_sub_header.userStatusWrapper")))

    all_customer_name = []
    all_country = []
    all_post_date = []

    for info in info_div:
        customer_name = info.find_element(By.CSS_SELECTOR, "span[itemprop='name']").text
        all_customer_name.append(customer_name)

        full_text = info.text
        # Start after the customer name and the space and opening parenthesis
        start = full_text.find(customer_name) + len(customer_name) + 2  
        # Find the closing parenthesis after the start index
        end = full_text.find(')', start)  
        
        country = full_text[start:end]
        all_country.append(country)

    for post_date in info_div:
        post_date = post_date.find_element(By.CSS_SELECTOR, "time").get_attribute('datetime')
        all_post_date.append(post_date)

    return all_customer_name, all_country, all_post_date

all_customer_name, all_country, all_post_date = scrape_all_info()

info_df = pd.DataFrame({
    'Customer Name': all_customer_name,
    'Country': all_country,
    'Post Date': all_post_date,
})
# print(info_df)

def scrape_airline_name():
    airline_name_element = driver.find_element(By.XPATH,'//h1[@itemprop="name"]')
    airline_name = airline_name_element.text
    return airline_name

def scrape_all_reviews_on_all_page():
    all_customer_name = []
    all_country = []
    all_post_date = []
    all_ratings = []
    all_titles = []
    all_contents = []
    
    while True:
        customer_name, country, post_date = scrape_all_info()
        all_customer_name.extend(customer_name)
        all_country.extend(country)
        all_post_date.extend(post_date)
        all_ratings.extend(scrape_all_ratings())
        all_titles.extend(scrape_all_titles())
        all_contents.extend(scrape_all_contents())

        try:
            next_page_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '>>')]"))
            )
            if 'off' in next_page_button.get_attribute('class'):
                print("No more pages.")
                break
            driver.execute_script("arguments[0].click();", next_page_button)
            time.sleep(2)  # Allow time for the page to load
        except (NoSuchElementException, TimeoutException):
            print("No more pages or button not found.")
            break

    info_df = pd.DataFrame({
        'Customer Name': all_customer_name,
        'Country': all_country,
        'Post Date': all_post_date,
    })

    airline_name = scrape_airline_name()

    ratings_df = pd.DataFrame(all_ratings)
    titles_df = pd.DataFrame(all_titles, columns=['Title'])
    contents_df = pd.DataFrame(all_contents, columns=['Content'])

    all_reviews_df = pd.concat([info_df, ratings_df, titles_df, contents_df], axis=1)
    all_reviews_df['Airline Name'] = airline_name
    return all_reviews_df

all_reviews_df = scrape_all_reviews_on_all_page()
# print(all_reviews_df)

alchemy_engine = create_engine('postgresql://postgres:dnproject@localhost:5432/airlines_reviews')

all_reviews_df.to_sql('airlines_reviews', alchemy_engine, if_exists='append', index=True)

try:
    connection = psycopg2.connect(user="postgres",
                                  password="dnproject",
                                  host="localhost",
                                  port="5432",
                                  database="airlines_reviews")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM airlines_reviews;")

    records = cursor.fetchall()

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
    if connection:
        cursor.close()
        connection.close()
