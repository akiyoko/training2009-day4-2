from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from todo.models import Todo

User = get_user_model()


class TestTodoListView(TestCase):
    """TodoListViewのテストクラス"""

    def setUp(self):
        self.password = 'pass12345'
        # ログイン用のユーザー
        self.user = User.objects.create_user(username='user', email='user@example.com',
                                             password=self.password)
        self.today = date(2020, 9, 1)

    def create_todo_list(self):
        """テスト用のTODOレコードを作成する"""
        self.todo_list = [
            Todo.objects.create(title='test-1', expiration_date=self.today, created_by=self.user),
            Todo.objects.create(title='test-2', expiration_date=self.today + timedelta(days=7),
                                created_by=self.user),
            Todo.objects.create(title='test-3', expiration_date=self.today + timedelta(days=1),
                                created_by=self.user),
        ]

    @patch('todo.views.timezone.localdate')
    def test_get_if_todo_list_is_empty(self, mock_localdate):
        """/todo/へのGETリクエスト

        TODOリストが0件の場合"""

        # timezone.localdateの戻り値をモック化
        mock_localdate.return_value = self.today

        # テストクライアントでログインをシミュレート
        self.client.login(username=self.user.username, password=self.password)
        # テストクライアントでGETリクエストをシミュレート
        response = self.client.get('/todo/')

        # TODOリスト画面に遷移することを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_list.html')
        self.assertContains(response, '<h1>TODOリスト</h1>')
        self.assertContains(response, 'TODOリストがありません。')

        # テンプレートに渡すコンテキストを検証
        # ↓は厳密にはよくないのでモックを使う方がベター
        # self.assertEqual(response.context_data['today'], timezone.localdate())
        self.assertEqual(response.context_data['today'], self.today)
        self.assertEqual(len(response.context_data['todo_list']), 0)

    @patch('todo.views.timezone.localdate')
    def test_get_if_todo_is_not_empty(self, mock_localdate):
        """/todo/へのGETリクエスト

        TODOリストが1件以上ある場合"""

        # timezone.localdateの戻り値をモック化
        mock_localdate.return_value = self.today
        # テスト用のTODOレコードを作成
        self.create_todo_list()

        # テストクライアントでログインをシミュレート
        self.client.login(username=self.user.username, password=self.password)
        # テストクライアントでGETリクエストをシミュレート
        response = self.client.get('/todo/')

        # TODOリスト画面に遷移することを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_list.html')
        self.assertContains(response, '<h1>TODOリスト</h1>')
        self.assertNotContains(response, 'TODOリストがありません。')

        # レスポンスを検証
        self.assertEqual(response.context_data['today'], self.today)
        self.assertEqual(
            [todo.title for todo in response.context_data['todo_list']],
            ['test-1', 'test-3', 'test-2']
        )


class TestTodoCreateView(TestCase):
    """TodoCreateViewのテストクラス"""

    def setUp(self):
        self.password = 'pass12345'
        # ログイン用のユーザー
        self.user = User.objects.create_user(username='user', email='user@example.com',
                                             password=self.password)

    def test_get_success(self):
        """/todo/create/へのGETリクエスト（正常系）"""
        # テストクライアントでログインをシミュレート
        self.client.login(username=self.user.username, password=self.password)
        # テストクライアントでGETリクエストをシミュレート
        response = self.client.get('/todo/create/')

        # TODO追加画面に遷移することを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_create.html')
        self.assertContains(response, '<h1>TODO追加</h1>')

    def test_post_success(self):
        """/todo/create/へのPOSTリクエスト（正常系）"""
        # テストクライアントでログインをシミュレート
        self.client.login(username=self.user.username, password=self.password)
        # テストクライアントでPOSTリクエストをシミュレート
        response = self.client.post('/todo/create/', {
            'title': 'test-1',
        }, follow=True)

        # TODOリスト画面にリダイレクトされることを検証
        self.assertRedirects(response, '/todo/')
        self.assertTemplateUsed(response, 'todo/todo_list.html')
        self.assertContains(response, '<h1>TODOリスト</h1>')

        # 対象オブジェクトが保存されていることを検証
        todo = Todo.objects.get()
        self.assertEqual(todo.title, 'test-1')

    def test_post_if_title_is_blank(self):
        """/todo/create//へのPOSTリクエスト（バリデーションNG）"""
        # テストクライアントでログインをシミュレート
        self.client.login(username=self.user.username, password=self.password)
        # テストクライアントでPOSTリクエストをシミュレート
        response = self.client.post('/todo/create/', {
            'title': '',
        })

        # TODO追加画面に遷移することを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/todo_create.html')
        self.assertContains(response, '<h1>TODO追加</h1>')

        # エラーメッセージが表示されることを検証
        self.assertEqual(
            response.context_data['form'].errors,
            {'title': ['このフィールドは必須です。']}
        )

        # 対象オブジェクトが保存されていないことを検証
        with self.assertRaises(ObjectDoesNotExist):
            Todo.objects.get()
