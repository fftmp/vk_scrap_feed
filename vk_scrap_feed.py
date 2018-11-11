#!/usr/bin/env python3
"""
Get data from public vk.com pages without API usage
(because API requires authorization and token and have some limits) and
translate page posts to atom feed.
"""

from feedgen.feed import FeedGenerator
from vk_parse.vk_parse import get_posts
import logging as log
from pprint import pprint

def write_atom(vk_posts, filename):
    fg = FeedGenerator()
    fg.id('http://lernfunk.de/media/654321')
    fg.title('Some Testfeed')
    fg.author({'name':'John Doe', 'email':'john@example.de'})
    fg.link(href='http://example.com', rel='alternate')
    fg.logo('http://ex.com/VK_Logo.png')
    fg.subtitle('This is a cool feed!')
    fg.link(href='http://larskiesow.de/test.atom', rel='self')
    fg.language('ru')

if __name__ == '__main__':
    #updater receive info (commands, text, may be pictures?) from telegram
    #and send responses during polling
    log.basicConfig(level=log.DEBUG)

    posts = get_posts('darcor')
    #pprint(posts)
    posts = get_posts('tassagency')
    #pprint(posts)
    posts = get_posts('id210700286') # Lindsey Stirling
    #pprint(posts)
    posts = get_posts('skepticon')
    #pprint(posts)
    #write_atom(posts, './atom.xml')
