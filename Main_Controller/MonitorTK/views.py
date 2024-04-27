from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from MonitorTK.add_functions.DataBase import cache_database, separation_BD
from MonitorTK.add_functions.OperationsStart import create_task, controller_is_selected, fix_result
from django.core.cache import cache
from MonitorTK.forms import ResultForm



@csrf_protect
def start(request):
    """
    Представление загрузки основной страницы мониторинга состояния заказов.

    Перед началом происходит выгрузка из КЭШа актуального состояния переменных на основе которых
        происходит рендер страницы

    Основные операции обращений (через кнопки на странице) происходят через POST запросы с назначением операции
    идентификация выполняемой операции происходит через if операторы
    """
    # Получение user_name из сеанса или установка значения по умолчанию
    user_name = request.session.get('user_name', 'Иванов И.И.')

    # Получаем БД из КЭШа
    database = cache_database()

    # Производим фильтрацию БД по статусу выполнения СЗ
    (status_task, count_task, sum_task,
     status_work, count_work, sum_work,
     status_done, count_done, sum_done,) = separation_BD(database)

    if request.method == 'POST':
        user_name = request.POST.get('user_name')

        # Получаем запрос на выполнение необходимой операции из index.html
        operation_create = request.POST.get('operation')

        # Генерация вызова контроллера
        if operation_create == "create":
            create_task()

        # Взятие контроллером СЗ в работу
        if operation_create == "controller is selected":
            order_id = request.POST.get('order_id')
            status = request.POST.get('status')

            # Фиксируем контроллера и время взятия задачи в БД и КЭШ
            controller_is_selected(user_name, order_id, status)

        print(user_name)
        request.session['user_name'] = user_name
        return redirect('start')
    else:
        return render(request, 'MonitorTK/index.html',
                      {'user_name': user_name,
                       'status_task': status_task, 'count_task': count_task, 'sum_task': sum_task,
                       'status_work': status_work, 'count_work': count_work, 'sum_work': sum_work,
                       'status_done': status_done, 'count_done': count_done, 'sum_done': sum_done,
                       })


@csrf_protect
def result(request):
    """
    Представление валидации формы и загрузки данных из страницы result.html

    Тут так же применяется POST запрос и определение наличия команды через if оператор
    Когда данные формы проходят валидацию, они записываются в БД и КЭШ после чего мы перенаправляемся
        на главную страницу.
    """
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        order_id = int(request.POST.get('order_id'))
        operation_create = request.POST.get('operation')
        status = request.POST.get('status')


        cached_database = cache.get('bdproductions')
        product = None
        if cached_database:
            for item in cached_database:
                order = item.id
                # Проверить, совпадает ли order_id с нужным значением
                if order_id == order:
                    product = item
                    break
        if operation_create == 'controller is worked':
            form = ResultForm()
        else:
            form = ResultForm(request.POST)
            if form.is_valid():
                # Обработка данных формы
                status_fix = form.cleaned_data['status_fix']
                comment_fix = form.cleaned_data['comment_fix']
                # Ваш код сохранения данных в БД или выполнения других действий

                fix_result(user_name, order_id,  status_fix, comment_fix)

                return redirect('start')  # Перенаправление на страницу успеха


    return render(request, 'MonitorTK/result.html', context={'user_name': user_name,
                                                             'position': product,
                                                             'form': form,
                                                             'status': status})


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1><br>'
                                '<h2>Проверьте свой запрос или обратитесь к администратору</h2>')
