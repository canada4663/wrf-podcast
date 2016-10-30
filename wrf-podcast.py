import requests
import BeautifulSoup as bs4
from feedgen.feed import FeedGenerator
import datetime
import pytz
import boto
central_tz = pytz.timezone('US/Central')
WRF_WEBSITE = "http://www.whiterock.org/sermons/"

def print_enc(s):
	'''Print function compatible with both python2 and python3 accepting strings
	and byte arrays.
	'''
	print(s.decode('utf-8') if type(s) == type(b'') else s)

def autogen():
    # Setup Feed
    feed = FeedGenerator()
    feed.id('http://www.whiterock.org/sermons/')
    feed.title('White Rock Fellowship Sermon Podcast')
    feed.description("Sunday Sermons from White Rock Fellowship Dallas")
    feed.link( href='localhost', rel='self')
    feed.language('en-US')

    user_agent = {'User-agent': 'Mozilla/5.0'}
    html = requests.get(WRF_WEBSITE, headers=user_agent).text
    soup = bs4.BeautifulSoup(html, convertEntities=bs4.BeautifulSoup.HTML_ENTITIES)

    feed.load_extension('podcast')

    feed.podcast.itunes_subtitle('Sermon Recordings from White Rock Followship Dallas, TX')
    feed.podcast.itunes_category('Religion & Spirituality', 'Christianity')
    feed.podcast.itunes_author('White Rock Fellowship')
    feed.podcast.itunes_explicit('no')
    feed.podcast.itunes_owner('Ryan Hoium', 'ryanhoium@gmail.com')
    feed.podcast.itunes_summary('Sunday Sermons from White Rock Fellowship Dallas')
    feed.podcast.itunes_subtitle('White Rock Fellowship Sermon Podcast')
    feed.podcast.itunes_image('http://www.whiterock.org/wp-content/uploads/2015/05/Logo_Web-Header-e1406239129390.png')

    series_pagelinks =[]
    series_sidebar = soup.find('div', {'id':'custom_category-2'})
    for series in series_sidebar.findAll('a'):
        series_link = series['href']
        series_name = series.text
        series_html = requests.get(series_link, headers=user_agent).text
        series_soup = bs4.BeautifulSoup(series_html, 
                                        convertEntities=bs4.BeautifulSoup.HTML_ENTITIES)
        pagination = series_soup.find('ul', {'class':'pagination'})
        series_pagelinks.append({'series_name': series_name,
                                 'series_link': series_link})
        if pagination is not None:
            for series_page in pagination.findAll('a', {'class':''}):
                series_pagelinks.append({'series_name': series_name,
                                         'series_link': series_page['href']})

    postings =[]
    for series_page in series_pagelinks:
        series_link = series_page['series_link']
        series_name = series_page['series_name']
        series_html = requests.get(series_link, headers=user_agent).text
        series_soup = bs4.BeautifulSoup(series_html, convertEntities=bs4.BeautifulSoup.HTML_ENTITIES)
    for posting in series_soup.findAll('article', {'class':'post sermon'}):
        for link in posting.findAll('a', {'data-original-title':'Audio'}):
            try:
                inner_html = requests.get(link['href'], headers=user_agent).text
                inner_soup = bs4.BeautifulSoup(inner_html, convertEntities=bs4.BeautifulSoup.HTML_ENTITIES)
                title = series_name + ' : ' + inner_soup.find('h2', {'class':'post-title'}).text
                download_link = inner_soup.find('a', {'data-original-title':'Download Audio'})['href']
                download_link = download_link.split('=')[1]
                length = requests.head(download_link).headers.get('content-length', None)
                staff_data = inner_soup.find('div', {'class':'staff-data'}).text
                author = staff_data.split(' on ')[0]
                author = author.split('by ')[1]
                date = staff_data.split(' on ')[1]
                date = datetime.datetime.strptime(date,'%B %d, %Y') #.strftime('%m/%d/%Y')
                date = central_tz.localize(datetime.datetime.combine(date,datetime.time.min))
            except:
                print "Error processing: ", link
                continue
            try:
                entry = feed.add_entry()
                entry.id(download_link)
                entry.title(title + " by " + author)
                entry.enclosure(download_link, length, 'audio/mpeg')
                entry.podcast.itunes_author(itunes_author=author)
                entry.pubdate(pubDate=date)
            except:
                print "Error Generating Feed Entry: ", title
                continue
            postings.append({'title':title, 
                             'download_link':download_link,
                             'date': date,
                             'author': staff_data})

    rssString = feed.rss_str(pretty=True)
    s3 = boto.connect_s3()
    wrf = s3.get_bucket('wrf-autogen')
    s3key = wrf.get_key('wrf-podcast.rss')
    s3key.set_contents_from_string(rssString)
    s3key.make_public()

if __name__ == "__main__":
    autogen()
