#
# Top 250 movies on Hulu
#
# Source: Rotten Tomatoes <https://editorial.rottentomatoes.com/guide/best-movies-on-hulu>
# Written by Arul John { 2020-05-23 }
#
# This is a Python web scraping tutorial. 
# It uses requests to get the webpage and pandas for exporting to different formats
# Output formats are CSV, XLSX, JSON and HTML

import time, requests
import re
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

# User-agent
user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'
base_url = f'https://editorial.rottentomatoes.com/guide/best-movies-on-hulu'
headers = {'User-Agent': user_agent}

# Vars
base_path = 'output'
base_image_path = f'{base_path}/images'
outfile = 'hulu-top-250'

# Clean up HTML
def cleanup(str=str, type=None):
    switcher = {
        'index': re.sub(r'#', '', str),
        'synopsis': re.sub(r'(Synopsis: |\.{3} \[More\])', '', str),
        'braces': re.sub(r'\(|\)', '', str)
    }
    return switcher.get(type, str)

# Download images
def download_image(url, filename):
    filename = f'{base_image_path}/{filename}'
    with requests.get(url, stream=True) as r:
        with open(filename, "wb") as f:
            f.write(r.content)

# Parse the HTML
def parse_html(html=None):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find_all('div', {'class': 'countdown-item'})
    for item in items:
        movie_id = int(cleanup(item.find('div', class_='countdown-index').get_text(), 'index'))
        movie_div = item.find('div', {'class': 'article_movie_title'})
        movie = movie_div.h2
        title = movie.a.text # movie title
        link = movie.a.get('href') # URL to rotten tomatoes
        year = int(cleanup(movie.find('span', class_='start-year').get_text(), 'braces')) # movie year
        synopsis = cleanup(item.find('div', class_='synopsis').get_text(), 'synopsis') # synopsis/description
        image_url = item.find('img', class_='article_poster').get('src')
        image_filename = f"{link.split('/')[4]}.jpg" # images are stored in output/images
        movies.append((movie_id, title, year, synopsis, image_filename, link)) # append this tuple to movies[]
        download_image(image_url, image_filename)
        time.sleep(2) # don't overload the server

# Create output directory first
Path(base_image_path).mkdir(parents=True, exist_ok=True)

# Initialize array of movies
movies = []

# Get web page
for x in range(4):
    response = requests.get(f'{base_url}/{x}/', headers=headers)
    html = response.text
    parse_html(html)

# Dataframe
df = pd.DataFrame(movies)
df.columns = ['Index', 'Title', 'Year', 'Synopsis', 'Image Filename', 'URL']
df.sort_values('Index', ascending=True, inplace=True) # sort by index in ascending order

# Export of all these formats
df.to_csv(f'{base_path}/{outfile}.csv', index=False)
df.to_excel(f'{base_path}/{outfile}.xlsx', index=False)
df.to_json(f'{base_path}/{outfile}.json')
df.to_html(f'{base_path}/{outfile}.html', index=False)

exit(0)
