import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3
from yattag import Doc

current_date = datetime.today()
url = 'https://www.dvdsreleasedates.com/releases/2019/---month---/'
url = url.replace('---month---',str(current_date.month))
res = requests.get(url)

movie_imdb_search = re.compile(r'http://www.imdb.com/title/.*?/')
imdb_results = movie_imdb_search.findall(res.text)

dir_temp = os.getcwd()
dir_temp = dir_temp + '/temp_pages'
os.chdir(dir_temp)

filename = 'new_movie.html'
f= open(filename,"w+", encoding="utf-8")
doc, tag, text = Doc().tagtext()

#beginning of the html page
temp_html_content = """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>亮晶晶乾洗店</title>
</head>
<body>
"""
f.write(temp_html_content)

#電影發行日期
f.write('<table border=1>')
with tag('tr'):
    with tag('td', align = 'center'):
        text('Movie Title')
    with tag('td', align = 'center'):
        text('rating')
    with tag('td', align = 'center'):
        text('votes')

for imdb_result in imdb_results:
    print('Cool down for requesting web content')
    time.sleep(3)
    imdb_content = requests.get(imdb_result)
    soup = bs4.BeautifulSoup(imdb_content.text, "lxml")
    title = soup.find('meta', attrs={'name': 'title'})
    title_search = re.compile(r'<meta content="(.*?) - IMDb" name="title"/>')
    title_result = title_search.search(str(title))
    print(title_result.group(1))
    rating = soup.find('div', attrs={'class': 'imdbRating'})
    rating_search = re.compile(r'<strong title="(.*?) based on (.*?) user ratings">')
    rating_result = rating_search.search(str(rating))
    if rating_result == None:
        continue
    rating_float = float(rating_result.group(1))
    voting_int = int(rating_result.group(2).replace(',',''))
    print(rating_result.group(1) + ' ' + rating_result.group(2))
    if 'TV' in title_result.group(1) and 'Series' in title_result.group(1):
        continue
    if ((rating_float > 8.0) and (voting_int > 3000))\
    or ((rating_float > 7.5) and (voting_int > 10000))\
    or ((rating_float > 7.0) and (voting_int > 20000))\
    or ((rating_float > 6.5) and (voting_int > 60000)):
        print(title_result.group(1) + ' matched!!')
        with tag('tr'):
            with tag('td', align = 'center'):
                text(title_result.group(1))
            with tag('td', align = 'center'):
                text(rating_result.group(1))
            with tag('td', align = 'center'):
                text(rating_result.group(2))
f.write(doc.getvalue())
f.write('</table>')
#end of the html page
temp_html_content = """
</body>
</html>
"""
f.write(temp_html_content)
f.close()