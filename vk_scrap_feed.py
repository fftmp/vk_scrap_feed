#!/usr/bin/env python3
"""
Get data from public vk.com pages without API usage
(because API requires authorization and token and have some limits) and
translate page posts to atom feed.
"""

import os
import logging as log
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from vk_parse.vk_parse import get_posts

def generate_atom(page_id):
    """
    Generate atom feed. return it as str
    """
    posts = get_posts(page_id)
    if not posts:
        return ''
    log.debug('generate atom for %s', page_id)
    _fg = FeedGenerator()
    _fg.id('https://vk.com/' + page_id)
    _fg.title(page_id)
    _fg.logo('http://ex.com/VK_Logo.png')
    _fg.language('ru')
    for post in posts:
        _fe = _fg.add_item()
        _fe.id(post['id'])
        _fe.title(post['title'] or ' ')
        _fe.description(post['text_content'])
        _fe.link(href='https://vk.com/' + post['href'], rel='alternate')
        _fe.updated(datetime.fromtimestamp(post['ts'], tz=timezone.utc))
        _fe.author(name=post['author'])
        if 'image_url' in post.keys():
            _fe.enclosure(url=post['image_url'], type='image/jpeg')
    return _fg.atom_str(pretty=True)


class _HttpProcessor(BaseHTTPRequestHandler):
    """
    Handler for http.server. Perform only GET requests.
    """
    def do_GET(self):
        """
        For each request try to get posts from vk.com  using page_id from GET path.
        Ignore requests to favicon.ico
        """
        if self.path == '/favicon.ico':
            self.send_response(404)
            return
        request = self.path[1:]
        atom_feed = generate_atom(request)
        if atom_feed:
            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(atom_feed)
        else:
            self.send_response(202)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes('Can\'t feed to ' + request, 'utf-8'))


def main():
    """
    Run simple http server to return atom feeds. Worked at localhost.
    """
    log.basicConfig(level=log.DEBUG, filename=os.path.dirname(__file__) + '/vk_scrap_feed.log')
    server_address = ('127.2', 8000)
    httpd = HTTPServer(server_address, _HttpProcessor)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
