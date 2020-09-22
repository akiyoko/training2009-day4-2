from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = '__all__'

    def clean_title(self):
        title = self.cleaned_data['title']
        # 入力値が3文字より短ければバリデーションエラー
        if len(title) < 3:
            raise forms.ValidationError('タイトルは3文字以上で入力してください')
        return title
