import unittest

from vk_parse.vk_parse import parse_posts
import os
import json

class Test_parse_whole_page(unittest.TestCase):
    _test_dir = os.path.dirname(os.path.realpath(__file__))
    def test_parse_darcor(self):
        with open(self._test_dir + '/darcor.html') as f_req, \
             open(self._test_dir + '/darcor.parsed') as f_resp:
            parsed = parse_posts(f_req.read())
            #print(json.dumps(parsed, ensure_ascii=False))
            self.assertEqual(parsed, json.load(f_resp))
    def test_parse_club62008434(self):
        with open(self._test_dir + '/club62008434.html') as f_req, \
             open(self._test_dir + '/club62008434.parsed') as f_resp:
            parsed = parse_posts(f_req.read())
            #print(json.dumps(parsed, ensure_ascii=False))
            self.assertEqual(parsed, json.load(f_resp))


