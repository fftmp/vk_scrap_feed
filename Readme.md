# About
Convert posts from any public page in vk.com to atom feed without using restricted API (i.e. without authorization).
For now (Oct 2018) all API calls require authorization.

Currently in development.


# TODO:
1. determine relative time in case of languages other than russian.
1. get various numbers of posts (>10, need pager?)
1. optional update, when comment to post added
1. cache results for work as server for multiple users
1. defense against XML vulnerabilities (defuxedxml ?)

# Run
1. run script (better in background). Also can add it to autostart. For example I add it to openbox autostart (.config/openbox/autostart).
1. add http://127.2:8000/<page_id> to your feed reader (tested on thunderbird) for all interested pages.

# Run tests
`python -m unittest -v`
