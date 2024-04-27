from django import forms


class ResultForm(forms.Form):
    """
    Создаем форму валидации полей для страницы result.html
    Это единственные поля, которые заполняются человеком и подвержены ошибкам ввода.
    """
    status_fix = forms.ChoiceField(choices=[
        ('Принято', 'Принято'),
        ('Отправлено на доработку', 'Отправить на доработку'),
        ('Брак', 'Брак'),
    ], label='Примите решение', initial='', widget=forms.RadioSelect, error_messages={'custom_error': '23123fffff'})

    comment_fix = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Введите комментарий (до 2000 символов)'}),
                                  min_length=1, max_length=2000, label="Добавьте описание по принятому решению:")