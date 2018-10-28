import urllib.request
from bs4 import BeautifulSoup
from urllib.error import HTTPError


# from app.models import Reference



def fetchreferencetitle(url):

    try:
        webpage = urllib.request.urlopen(url)
        soup = BeautifulSoup(webpage)
        title = soup.title.string
    except HTTPError as e:
        title = str(e)

    return title