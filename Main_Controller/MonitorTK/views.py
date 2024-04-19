import random

from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.sessions.models import Session
from datetime import datetime, timedelta, time, date
from MonitorTK.models import BDProductions

# Данные для генерации СЗ
product_list = ['LR-1245', 'Кожух', 'Кронштейн 144', 'RX-4412', 'Диффузор', 'Инжектор']
operation_list = ['Сварка', 'Сверловка', 'Сборка', 'Фрезерная обработка', 'Токарная обработка', 'Нанесение покрытия']
equipment_list = ['CV-5000', 'HURON NX40', 'Стапель 331', 'Станок 1114', 'Станок 555', 'Станок 99']
worker_list = ['Смирнов К.К.', 'Брюханов Б.Б.', 'Колесник К.К.', 'Жданов Ж.Ж.', 'Стоянов С.С.', 'Лобанов Л.Л.']
master_list = ['Трифанов К.К.', 'Лукьянов Б.Б.', 'Судаков К.К.', 'Журавлев Ж.Ж.', 'Самсонов С.С.', 'Логинов Л.Л.']




@csrf_protect
def start(request):

    # Получение вводных данных
    database, time_now, workload_list = time_control()
    user_name = request.session.get('user_name',
                                    'Иванов И.И.')  # Получение user_name из сеанса или установка значения по умолчанию




    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        operation_create = request.POST.get('operation')

        # Генерация вызова контроллера
        if operation_create == "create":
            create_task()

        # Взятие контроллером СЗ в работу
        if operation_create == "controller is selected":
            order_id = request.POST.get('order_id')
            # Присвоение задачи отвественного контроллера
            BDProductions.objects.filter(id=order_id).update(controller_name_response=user_name)
            # Фиксация времени взятия задачи в работу
            BDProductions.objects.filter(id=order_id).update(datetime_controller_response=datetime.now())

        # Фиксация результата
        if operation_create == "controller result":

            fix_result(request)

        print(user_name)
        request.session['user_name'] = user_name
        return redirect('start')
    else:
        return render(request,'MonitorTK/index.html',
                      {'user_name': user_name,
                       'database': database, 'time_now': time_now, 'workload_list': workload_list})



@csrf_protect
def result(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        order_id = request.POST.get('order_id')

        production = BDProductions.objects.get(id=order_id)


    return render(request, 'MonitorTK/result.html', context={'user_name': user_name, 'position': production})



def create_task():
    create = BDProductions(
    order = random.randint(11111, 55555),# Номер заказа
    workshop = random.randint(1, 40),  # Номер Цеха
    area = random.randint(1, 10),  # Номер участка
    product = product_list[random.randint(0, 5)],  # Название изделия

    operation = random.randrange(5, 5000, 5),  # Номер операции
    operation_name = operation_list[random.randint(0, 5)],  # Название операции
    equipment = equipment_list[random.randint(0, 5)],  # Название обрабатывающего центра

    worker_name = worker_list[random.randint(0, 5)],  # ФИО Исполнителя
    master_name_request = worker_list[random.randint(0, 5)],  # ФИО вызвавшего Мастера
    master_name = master_list[random.randint(0, 5)],  # ФИО Мастера

    priority = random.randint(1, 10),  # Приоритет СЗ
    value = round(random.uniform(0.5, 3), 2),  # объем работ для контроллера, ч

    datetime_master_request = datetime(2024,
                                       4,
                                       19,
                                       random.randint(0, 20),
                                       random.randint(1, 59)),  # Время и дата вызова Мастера
    datetime_controller_request = datetime.now(),  # Время и дата вызова Контроллера
    )



    print("Номер заказа:", create.order)
    print("Номер Цеха:", create.workshop)
    print("Номер участка:", create.area)
    print("Название изделия:", create.product)

    print("Номер операции:", create.operation)
    print("Название операции:", create.operation_name)
    print("Название обрабатывающего центра:", create.equipment)

    print("ФИО Исполнителя:", create.worker_name)
    print("ФИО вызвавшего Мастера:", create.master_name_request)
    print("ФИО Мастера:", create.master_name)

    print("Приоритет СЗ:", create.priority)
    print("Объем работ для контроллера, ч:", create.value)

    print("Время и дата вызова Мастера:", create.datetime_master_request)
    print("Время и дата вызова Контроллера:", create.datetime_controller_request)

    create.save()



# Обновляем время СЗ взятых в работу
def time_control():

    time_now = datetime.now()  # текущее время
    database = BDProductions.objects.all()

    # Задаем переменные для просчета эффективности
    val_task = 0
    workload_task = float(0)

    val_work = 0
    workload_work = float(0)

    val_done = 0
    workload_done = float(0)


    for obj in database:

        # Просчет заказов на ожидании
        if not obj.controller_name_response:
            val_task += 1
            workload_task += obj.value

        if obj.controller_name_response and not obj.decision:
            val_work += 1
            workload_work += obj.value

        if obj.datetime_controller_in_work and obj.datetime_controller_in_work.day == time_now.day:
            val_done += 1
            workload_done += obj.value

        if obj.datetime_controller_response and not obj.decision:
            obj.value_fact = round((time_now - obj.datetime_controller_response).total_seconds() / 3600, 2)
            obj.save()

    workload_list = [val_task, workload_task, val_work, workload_work, val_done, workload_done]

    return database, time_now, workload_list


# Фиксация результата
def fix_result(request):

    order_id = request.POST.get('order_id')
    user_name = request.POST.get('user_name')

    # Фиксация имени ответственного контроллера за результат
    BDProductions.objects.filter(id=order_id).update(controller_name_result=user_name)

    # Фиксация результата проверки контроллера
    selected_option = request.POST.get('status')
    BDProductions.objects.filter(id=order_id).update(decision=selected_option)

    # Фиксация описание решения
    text_result = request.POST.get('comment')
    BDProductions.objects.filter(id=order_id).update(decision_text=text_result)

    # Фиксация даты и времени
    time_now = datetime.now()
    BDProductions.objects.filter(id=order_id).update(datetime_controller_in_work=time_now)

    # Фиксация фактического времени выполнения
    try:
        production = BDProductions.objects.get(id=order_id)
        datetime_controller_response = production.datetime_controller_response
        print(datetime_controller_response)
    except BDProductions.DoesNotExist:
        print("Запись с указанным id не найдена")

    time_result_fact = round((time_now - datetime_controller_response).total_seconds() / 3600, 2)
    BDProductions.objects.filter(id=order_id).update(value_fact=time_result_fact)







def page_not_found (request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1><br>'
                                '<h2>Проверьте свой запрос или обратитесь к администратору</h2>')
