#About
Convert posts from any public page in vk.com to atom feed without using restricted API (i.e. without authorization).
For now (Oct 2018) all API calls require authorization.

Currently in development.


#TODO:
1. determine relative time in case of different languages
1. beautiful get first sentence for title
1. get various numbers of posts (>10, need pager?)
1. allow html in description
1. update, when comment to post added
1. handle text on base page in case of repost
1. strange from field in thunderbird (encoding?)

#Run
1. run script (better in background)
1. add http://127.2:8000/<page_id> to your feed reader (tested on thunderbird) for all interested pages.

#Run tests
python -m unittest -v
