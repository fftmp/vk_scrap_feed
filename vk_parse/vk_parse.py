"""
routines for parse vk.com pages
"""

from time import mktime
import datetime
import locale
import logging as log
import re
from bs4 import BeautifulSoup


def _get_ts(ts_section):
    # for some posts (seems recent ones) header info contain UNIX timestamp. Try get it first.
    _ts = ts_section.span.get('time')
    if _ts:
      return int(_ts)

    rel_ts = ts_section.span.get_text()
    locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
    date_parts = rel_ts.split(' ')
    # seems, that relative date is relative against user localtime
    if date_parts[0] == 'сегодня': #today
        day = datetime.datetime.now().strftime('%Y-%b-%d')
        time = date_parts[2]
    elif date_parts[0] == 'вчера': #yesterday
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        day = yesterday.strftime('%Y-%b-%d')
        time = date_parts[2]
    else:
        day_number = date_parts[0]
        month = date_parts[1]
        if date_parts[2] == 'в':
            # '8 ноя в 20:37'
            year = datetime.datetime.now().year
            time = date_parts[3]
        else:
            # '3 ноя 2017'
            year = date_parts[2]
            time = '00:00'
        day = str(year) + '-' + month + '-' + day_number
    _ts = mktime(datetime.datetime.strptime(day + ' ' + time, '%Y-%b-%d %H:%M').timetuple())
    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
    return _ts


def get_first_sentence(text):
    """
    Return first part of text till the first occurence one of '.', '!', '?'
    with space or newline after it. Return full text if can't see end of sentence.
    Cannot deal with abbreviations and direct speech (quotes).
    """
    sentence_end_pos = len(text)
    for _i in range(len(text)):
      if text[_i] in ('.', '!', '?') and \
         (_i == len(text) -1 or text[_i + 1] in (' ', '\n')):
           sentence_end_pos = _i
           break

    return text[0:sentence_end_pos + 1]


def _prettify_text_content(text_content_subtree):
    if text_content_subtree is None:
        return None
    line_breaks = text_content_subtree.findAll('br')
    [br.replaceWith(' ') for br in line_breaks]
    return text_content_subtree.get_text()


def parse_one_post(post_html):
    post_info = {}
    post_info['id'] = post_html['id']
    hdr = post_html.div.find('div', class_='post_header_info')
    date_fragment = hdr.find('div', class_='post_date').a
    post_info['ts'] = _get_ts(date_fragment)
    #usually or may be always href == '/wall' + post_info['id']
    post_info['href'] = date_fragment['href'] # somewhy href located inside 'post_date' subtree
    post_info['author'] = hdr.find('a', class_='author').get_text()

    quote_subtree = post_html.find('div', class_='copy_quote')
    post_info['is_repost'] = True if quote_subtree else False
    text_tree = post_html.find('div', class_='wall_post_cont').find('div', class_='wall_post_text')
    post_info['text_content'] = _prettify_text_content(text_tree)

    if post_info['is_repost']:
      post_info['orig_post'] = {}
      post_info['orig_post']['author'] = quote_subtree.find('a', class_='copy_author').get_text()
      text_tree = quote_subtree.find('div', class_='wall_post_text')
      post_info['orig_post']['text_content'] = _prettify_text_content(text_tree)

    # try to get *any* image from post
    _img_wo_ext = re.search(r'background-image: url\((.+?)\.jpg\)', str(post_html))
    if _img_wo_ext:
        post_info['image_url'] = _img_wo_ext.group(1) + '.jpg'
    return post_info


def parse_posts(page_text):
    page_text = page_text.replace('\xa0', ' ') # change non-breaking space to normal space
    page = BeautifulSoup(page_text, features='lxml')
    page_title = page.head.title.contents[0]
    log.debug('parse page with title = %s', page_title)
    post_blocks = page.find('div', id='page_wall_posts')
    posts = []
    for post in post_blocks.find_all('div', class_='post'):
        post_info = parse_one_post(post)
        posts.append(post_info)
    return posts

