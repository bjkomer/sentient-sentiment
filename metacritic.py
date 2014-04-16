# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
import re
from urllib import quote
from lxml.html import document_fromstring

from ox.cache import read_url
from ox import find_re, strip_tags

## Original code, does not work for all cases
def get_url(id=None, imdb=None):
    if imdb:
        url = "http://www.imdb.com/title/tt%s/criticreviews" % imdb
        data = read_url(url)
        metacritic_url = find_re(data, '"(http://www.metacritic.com/movie/.*?)"')
        return metacritic_url or None
    return 'http://www.metacritic.com/movie/%s' % id

def get_id(url):
    return url.split('/')[-1]

def get_show_url(title):
    title = quote(title)
    url = "http://www.metacritic.com/search/process?ty=6&ts=%s&tfs=tvshow_title&x=0&y=0&sb=0&release_date_s=&release_date_e=&metascore_s=&metascore_e=" % title
    data = read_url(url)
    return find_re(data, '(http://www.metacritic.com/tv/shows/.*?)\?')

def get_data(url):
    data = read_url(url, unicode=True)
    doc = document_fromstring(data)
    score = filter(lambda s: s.attrib.get('property') == 'v:average',
                   doc.xpath('//span[@class="score_value"]'))
    if score:
        score = int(score[0].text)
    else:
        score = -1
    authors = [a.text
        for a in doc.xpath('//div[@class="review_content"]//div[@class="author"]//a')]
    sources = [d.text
        for d in doc.xpath('//div[@class="review_content"]//div[@class="source"]/a')]
    reviews = [d.text
        for d in doc.xpath('//div[@class="review_content"]//div[@class="review_body"]')]
    scores = [int(d.text.strip())
        for d in doc.xpath('//div[@class="review_content"]//div[contains(@class, "critscore")]')]
    urls = [a.attrib['href']
        for a in doc.xpath('//div[@class="review_content"]//a[contains(@class, "external")]')]

    metacritics = []
    for i in range(len(authors)):
        metacritics.append({
            'critic': authors[i],
            'url': urls[i],
            'source': sources[i],
            'quote': strip_tags(reviews[i]).strip(),
            'score': scores[i],
        })
        
    return {
        'critics': metacritics,
        'id': get_id(url),
        'score': score,
        'url': url,
    }

## Added specifically for CS 886 Project
def score_to_int( score ):
  if score == 'tbd':
    return -1
  else:
    return int( score )

def get_reviews(url):
    data = read_url(url, unicode=True)
    doc = document_fromstring(data)
    score = doc.xpath('//span[@itemprop="ratingValue"]')
    if score:
        score = int(score[0].text)
    else:
        score = -1
    # NOTE: some reviews may not have authors
    #       one solution is to track by source instead
    sources = [a.text
        for a in doc.xpath('//div[contains(@class, "critic_reviews")]'\
                           '//div[@class="review_content"]'\
                           '//div[@class="source"]//a|//span[@class="no_link"]')]
    reviews = [d.text
        for d in doc.xpath('//div[contains(@class, "critic_reviews")]//div[@class="review_content"]//div[@class="review_body"]')]
    scores = [score_to_int(d.text.strip())
        for d in doc.xpath('//div[contains(@class, "critic_reviews")]//div[@class="review_content"]//div[contains(@class, "metascore_w")]')]
    
    metacritics = []
    for i in range(len(reviews)):
      if scores[i] != -1: # Don't include TBD scores
        metacritics.append({
            'source': sources[i],
            'quote': strip_tags(reviews[i]).strip(),
            'score': scores[i],
        })
        
    return {
        'critics': metacritics,
        'id': get_id(url),
        'score': score,
        'url': url,
    }

def get_movie_list():
  """
  Searches Metacritic and retrieves a list of the movies available
  """
  base_url = "http://www.metacritic.com/browse/movies/title/dvd/"
  letters = "abcdefghijklmnopqrstuvwxyz"
  movie_list = []
  for letter in letters:
    url = base_url + letter
    data = read_url(url, unicode=True)
    doc = document_fromstring(data)
    movie_urls = [d.attrib['href']
        for d in doc.xpath('//div[contains(@class, "main_col")]'\
                           '//ol[contains(@class, "list_products")]'\
                           '//div[contains(@class, "product_title")]'\
                           '//a')]
    for m in movie_urls:
      movie_list.append( m.replace('/movie/', '')+'\n' )

  with open( 'movie_list.txt', 'w' ) as f:
    f.writelines( movie_list )

