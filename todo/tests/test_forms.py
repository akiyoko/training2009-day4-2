from datetime import date

from django.test import SimpleTestCase

from todo.forms import TodoForm


class TestTodoForm(SimpleTestCase):
    """TodoFormのテストクラス"""

    def setUp(self):
        self.today = date(2020, 9, 1)

    def test_valid(self):
        """バリデーションOK"""
        params = {
            'title': 'title-1',
            'expiration_date': self.today,
        }
        form = TodoForm(params)
        self.assertTrue(form.is_valid())

    def test_valid_if_expiration_date_is_not_specified(self):
        """バリデーションOK

        期限日が指定されていない場合
        """
        params = {
            'title': 'title-1',
        }
        form = TodoForm(params)
        self.assertTrue(form.is_valid())

    def test_invalid_if_title_is_empty(self):
        """バリデーションNG

        タイトルが空文字の場合
        """
        params = {
            'title': '',
            'expiration_date': self.today,
        }
        form = TodoForm(params)
        self.assertFalse(form.is_valid())
