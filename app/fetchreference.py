import urllib.request
# import urllib
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from http.client import RemoteDisconnected
from html import escape

# from app.models import Reference



def fetchreferencetitle(url):
    if 'pdf' in url:
        return 'error: not a html file'

    try:
        url = escape(url)
        url = url.replace(' ', '%20')
        print(url)
        q = urllib.request.Request(url)
        q.add_header('User-Agent', 'Mozilla/5.0')
        r = urllib.request.urlopen(q).read()
        soup = BeautifulSoup(r, "html.parser")
        title = soup.title.string
    except HTTPError as e:
        title = 'error: ' + str(e)
    except RemoteDisconnected as e:
        title = 'error: ' + str(e)

    return title