import unittest

from vk_parse.vk_parse import _get_ts
from lxml import html
from datetime import date, datetime
class Test_get_ts(unittest.TestCase):
  def test_abs_ts(self):
      abs_ts = '<span class="rel_date rel_date_needs_update" abs_time="сегодня в 10:35" time="1541835300">две минуты назад</span>'
      self.assertEqual(_get_ts(html.fromstring(abs_ts)), 1541835300)
  def test_today(self):
      rel_date_today = '<span class="rel_date">сегодня в 0:06</span>'
      _t = date.today()
      _ts = datetime(_t.year, _t.month, _t.day, hour=0, minute=6, second=0).timestamp()
      self.assertEqual(_get_ts(html.fromstring(rel_date_today)),  int(_ts))
  def test_yesterday(self):
      rel_date_yesterday = '<span class="rel_date">вчера в 22:51</span>'
      _t = date.today()
      _ts = datetime(_t.year, _t.month, _t.day - 1, hour=22, minute=51, second=0).timestamp()
      self.assertEqual(_get_ts(html.fromstring(rel_date_yesterday)), int(_ts))
  def test_date_current_year(self):
      rel_date_cur_year = '<span class="rel_date">8 ноя в 20:37</span>'
      _t = date.today()
      _ts = datetime(_t.year, 11, 8, hour=20, minute=37, second=0).timestamp()
      self.assertEqual(_get_ts(html.fromstring(rel_date_cur_year)), int(_ts))
  def test_date_with_year(self):
      rel_date_with_year = '<span class="rel_date">3 ноя 2017</span>'
      self.assertEqual(_get_ts(html.fromstring(rel_date_with_year)), 1509656400)
