#!/usr/bin/env python3
"""
Get data from public vk.com pages without API usage
(because API requires authorization and token and have some limits) and
translate page posts to atom feed.
"""

from base64 import b64encode
import os
import logging as log
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from requests import get as requests_get
from vk_parse.vk_parse import parse_posts, get_first_sentence

SITE = 'https://vk.com/'


def generate_atom(page_id):
    """
    Generate atom feed. return it as str
    page_id can be both in string form (like 'darcor' in https://vk.com/darcor) and
    in number form (like 'id210700286' in https://vk.com/id210700286).
    """

    log.debug('generate atom for %s', page_id)
    #vk.com discriminates its output depending on user-agent
    resp = requests_get(SITE + page_id, headers={'user-agent': 'Mozilla/5.0 (Linux x86_64)',
                                                 'Accept-Charset': 'utf-8',
                                                 'Accept-Language': 'ru'})
    posts = parse_posts(resp.text)
    if not posts:
        log.warning('no posts - parsing failed or empty page')
        return ''

    _fg = FeedGenerator()
    _fg.id('https://vk.com/' + str(page_id))
    _fg.title(str(page_id))

    _fg.language('ru')
    for post in posts:
        _fe = _fg.add_item()
        _fe.id(post['id'])
        post['title'] = ' '
        if post['is_repost'] and post['orig_post']['text_content']:
            post['title'] = get_first_sentence(post['orig_post']['text_content'])
        elif post['text_content']:
            post['title'] = get_first_sentence(post['text_content'])
        _fe.title(post['title'] or ' ')
        _fe.link(href='https://vk.com/' + post['href'], rel='alternate')
        _fe.updated(datetime.fromtimestamp(post['ts'], tz=timezone.utc))
        author = None
        if post['is_repost'] and post['orig_post']['text_content']:
            _fe.description((post['text_content'] or '') + '\n\n' + post['orig_post']['text_content'])
            author = post['orig_post']['author']
        else:
            _fe.description(post['text_content'])
            author = post['author']
            _fe.author(name='=?UTF-8?B?' + b64encode(author.encode()).decode() + '=?=')
        if 'image_url' in post.keys():
            _fe.enclosure(url=post['image_url'], type='image/jpeg')
    return _fg.atom_str(pretty=True)


class _HttpProcessor(BaseHTTPRequestHandler):
    """
    Handler for http.server. Perform only GET requests.
    """
    _favicon = None
    @staticmethod
    def get_favicon():
        if _HttpProcessor._favicon is None:
            with open(os.path.dirname(__file__) + '/vk.com.png', 'rb') as _f:
                _HttpProcessor._favicon = _f.read()
        return _HttpProcessor._favicon
    def do_GET(self):
        """
        For each request try to get posts from vk.com  using page_id from GET path.
        """
        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('content-type', 'image/png')
            self.end_headers()
            self.wfile.write(self.get_favicon())
            return
        request = self.path[1:]
        atom_feed = generate_atom(str(request))
        if atom_feed:
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(atom_feed)
        else:
            log.warning('Fail generate atom for %s', str(request))
            self.send_response(202)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes('Can\'t feed to ' + request, 'utf-8'))


def main():
    """
    Run simple http server to return atom feeds. Worked at localhost.
    """
    log.basicConfig(level=log.DEBUG,
                    format='%(asctime)s %(levelname)-s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=os.path.dirname(__file__) + '/vk_scrap_feed.log')
    server_address = ('127.2', 8000)
    httpd = HTTPServer(server_address, _HttpProcessor)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
