from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Todo(models.Model):
    """TODOモデル"""

    class Meta:
        db_table = 'todo'
        verbose_name = verbose_name_plural = 'TODO'

    title = models.CharField(verbose_name='タイトル', max_length=255)
    # description = models.TextField(verbose_name='詳細', null=True, blank=True)
    expiration_date = models.DateField(verbose_name='期限日', null=True, blank=True)
    created_by = models.ForeignKey(User, verbose_name='登録ユーザー',
                                   on_delete=models.SET_NULL, null=True, blank=True,
                                   editable=False)

    def __str__(self):
        return self.title
