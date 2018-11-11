"""
routines for parse vk.com pages
"""

from time import mktime
import datetime
import locale
import logging as log
import re
from requests import get as requests_get
from lxml import html

SITE = 'https://vk.com/'

def _get_ts(header_info):
    _ts = 0
    if header_info.attrib['class'] == 'rel_date rel_date_needs_update':
        _ts = int(header_info.get('time'))
    elif header_info.attrib['class'] == 'rel_date':
        rel_ts = header_info.text
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

    else:
        log.error('Error determine timestamp. header = %s',
                  html.tostring(header_info, encoding='unicode'))
    return _ts

def _get_first_sentence(text):
    sent_len = len(text)
    for _c in ('.', '!', '?'):
        _i = text.find(_c)
        if 0 < _i < sent_len:
            sent_len = _i
    return text[0:sent_len + 1]

# command to test picture posting
def get_posts(page_id, count=10):
    """
    Get count posts from page_id. Return dict with parsed information.
    page_id can be both in string form (like 'darcor' in https://vk.com/darcor) and
    in number form (like 'id210700286' in https://vk.com/id210700286).
    """

    log.debug('Try to get posts from page %s', page_id)
    #vk.com discriminates its output depending on user-agent
    resp = requests_get(SITE + page_id, headers={'user-agent': 'Mozilla/5.0 (Linux x86_64)'})
    page = html.fromstring(resp.text)
    page_title = page.xpath("head/title")[0].text
    log.debug("got posts from page with title = %s", page_title)

    post_blocks = page.xpath("//body/div[@id='page_wrap']/div/div[@class='scroll_fix']" +
                             "/div[@id='page_layout']/div[@id='page_body']/div[@id='wrap3']" +
                             "/div[@id='wrap2']/div[@id='wrap1']/div[@id='content']" +
                             "/div[@id='public' or @id='profile' or @id='group']" +
                             "/div[@class='wide_column_left' or @class='wide_column_right']" +
                             "/div[@class='wide_column_wrap']/div[@id='wide_column']" +
                             "/div[@id='public_wall' or @id='group_wall' or @id='profile_wall']" +
                             "/div[@id='page_wall_posts']/div"
                            )
    posts = []
    for post in post_blocks:
        if post.attrib['class'] == 'page_block no_posts':
            log.info('have no more posts')
            break
        count -= 1
        post_info = {}
        post_info['id'] = post.get('data-post-id')
        header = post.xpath(".//div[@class='_post_content']/div[@class='post_header']" +
                            "/div[@class='post_header_info']/div[@class='post_date']")[0]
        post_info['ts'] = _get_ts(header.xpath(".//a[@class='post_link']/node()")[0])

        #usually or may be always href == '/wall' + post_info['id']
        post_info['href'] = header.xpath("a[@class='post_link']/@href")[0]

        post_info['author'] = header.xpath("../h5[@class='post_author']" +
                                           "/a[@class='author']/text()")[0]

        _wt = post.xpath("./div[@class='_post_content']/div[@class='post_content']" +
                         "/div[@class='post_info']/div[@class='wall_text']")[0]



        if _wt.xpath("div[@class='copy_quote']"):
            # Repost. Will use author, title, description and content from original message
            post_info['author'] = _wt.xpath("./div[@class='copy_quote']" +
                                            "/div[@class='copy_post_header']" +
                                            "/div[@class='copy_post_header_info']" +
                                            "/h5[@class='copy_post_author']" +
                                            "/a[@class='copy_author']/text()")[0]
            post_content = _wt.xpath("./div[@class='copy_quote']")[0]
        else:
            post_content = _wt.xpath("./div[@class='wall_post_cont _wall_post_cont']")[0]

        if post_content.xpath("./div[@class='wall_marked_as_ads']"):
            log.debug('Ads. Skipping.')
            continue

        _tc = post_content.xpath("./div[@class='wall_post_text']/text()")
        post_info['text_content'] = _tc[0].replace('\n', ' ') if _tc else ''

        post_info['title'] = _get_first_sentence(post_info['text_content'])


        _img_style = post_content.xpath("div[@class='page_post_sized_thumbs  clear_fix']/a/@style")
        if _img_style:
            _img_wo_ext = re.search(r'background-image: url\((.+?)\.jpg\)', _img_style[0])
            if _img_wo_ext:
                post_info['image_url'] = _img_wo_ext.group(1) + '.jpg'

        posts.append(post_info)
        if count == 0:
            break
    return posts
