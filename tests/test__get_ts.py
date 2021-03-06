import unittest

from vk_parse.vk_parse import _get_ts
from bs4 import BeautifulSoup
from datetime import date, datetime

# use lxml-xml parser here, because it doesn't auto-wrap html fragment with html + body tags
# see https://stackoverflow.com/a/51836552
class Test_get_ts(unittest.TestCase):
  def test_abs_ts(self):
      abs_ts = '<span class="rel_date rel_date_needs_update" abs_time="сегодня в 10:35" time="1541835300">две минуты назад</span>'
      self.assertEqual(_get_ts(BeautifulSoup(abs_ts, features='lxml-xml')), 1541835300)
  def test_today(self):
      rel_date_today = '<span class="rel_date">сегодня в 0:06</span>'
      _t = date.today()
      _ts = datetime(_t.year, _t.month, _t.day, hour=0, minute=6, second=0).timestamp()
      self.assertEqual(_get_ts(BeautifulSoup(rel_date_today, features='lxml-xml')),  int(_ts))
  def test_yesterday(self):
      rel_date_yesterday = '<span class="rel_date">вчера в 22:51</span>'
      _t = date.today()
      _ts = datetime(_t.year, _t.month, _t.day - 1, hour=22, minute=51, second=0).timestamp()
      self.assertEqual(_get_ts(BeautifulSoup(rel_date_yesterday, features='lxml-xml')), int(_ts))
  def test_date_current_year(self):
      rel_date_cur_year = '<span class="rel_date">8 ноя в 20:37</span>'
      _t = date.today()
      _ts = datetime(_t.year, 11, 8, hour=20, minute=37, second=0).timestamp()
      self.assertEqual(_get_ts(BeautifulSoup(rel_date_cur_year, features='lxml-xml')), int(_ts))
  def test_date_with_year(self):
      rel_date_with_year = '<span class="rel_date">3 ноя 2017</span>'
      self.assertEqual(_get_ts(BeautifulSoup(rel_date_with_year, features='lxml-xml')), 1509656400)
