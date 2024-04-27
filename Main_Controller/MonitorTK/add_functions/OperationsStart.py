import random

from datetime import datetime
from MonitorTK.models import BDProductions
from django.core.cache import cache

# Данные для генерации СЗ
product_list = ['LR-1245', 'Кожух', 'Кронштейн 144', 'RX-4412', 'Диффузор', 'Инжектор']
operation_list = ['Сварка', 'Сверловка', 'Сборка', 'Фрезерная обработка', 'Токарная обработка', 'Нанесение покрытия']
equipment_list = ['CV-5000', 'HURON NX40', 'Стапель 331', 'Станок 1114', 'Станок 555', 'Станок 99']
worker_list = ['Смирнов К.К.', 'Брюханов Б.Б.', 'Колесник К.К.', 'Жданов Ж.Ж.', 'Стоянов С.С.', 'Лобанов Л.Л.']
master_list = ['Трифанов К.К.', 'Лукьянов Б.Б.', 'Судаков К.К.', 'Журавлев Ж.Ж.', 'Самсонов С.С.', 'Логинов Л.Л.']
status_list = ['Ожидает приемку', 'Ожидает приемку (Доработка)']

def create_task():
    """
    Функция генерации нового СЗ в листе ожидания:

    1. Создание новой позиции
    2. Созданная позиция добавляется в БД
    3. Созданная позиция добавляется в КЭШ
    """

    create = BDProductions(
        order=random.randint(11111, 55555),  # Номер заказа
        workshop=random.randint(1, 40),  # Номер Цеха
        area=random.randint(1, 10),  # Номер участка
        product=product_list[random.randint(0, 5)],  # Название изделия

        operation=random.randrange(5, 5000, 5),  # Номер операции
        operation_name=operation_list[random.randint(0, 5)],  # Название операции
        equipment=equipment_list[random.randint(0, 5)],  # Название обрабатывающего центра

        worker_name=worker_list[random.randint(0, 5)],  # ФИО Исполнителя
        master_name_request=worker_list[random.randint(0, 5)],  # ФИО вызвавшего Мастера
        master_name=master_list[random.randint(0, 5)],  # ФИО Мастера

        status=status_list[random.randint(0, 1)],  # Статус заказа
        priority=random.randint(1, 10),  # Приоритет СЗ
        value=round(random.uniform(0.5, 3), 2),  # объем работ для контроллера, ч

        datetime_master_request=datetime(2024,
                                         4,
                                         19,
                                         random.randint(0, 20),
                                         random.randint(1, 59)),  # Время и дата вызова Мастера
        datetime_controller_request=datetime.now(),  # Время и дата вызова Контроллера
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
    print("Статус СЗ:", create.status)
    print("Объем работ для контроллера, ч:", create.value)

    print("Время и дата вызова Мастера:", create.datetime_master_request)
    print("Время и дата вызова Контроллера:", create.datetime_controller_request)

    create.save()

    # Получаем текущий кэш
    cached_database = cache.get('bdproductions')

    # Если кэш уже существует, добавляем новый объект в него
    if cached_database:
        cached_database.append(create)
        cache.set('bdproductions', cached_database)
    else:
        # Если кэш пустой (возможно, из-за первого вызова функции cache_database),
        # создаем новый список и добавляем в него новый объект
        cache.set('bdproductions', [create])


def controller_is_selected(user_name, order_id, status):
    """
    Функция взятия контроллером СЗ из листа ожидания:

    1. Получаем вводные данные, user_name(str), order_id(str), status(str)
    2. Обновляем позиции соответствующие order_id в БД
    3. Проверяем наличие order_id в КЭШе
    4. При обнаружении обновляем позиции соответствующие order_id в КЭШе
    """

    now = datetime.now()
    order_id = int(order_id)

    if 'Доработка' in status:
        status = 'В работе (Доработка)'
    else:
        status = 'В работе'

    # Сбор данных в словарь для отправки в БД
    update_data = {
        'controller_name_response': user_name,
        'datetime_controller_response': now,
        'status': status
    }

    BDProductions.objects.filter(id=order_id).update(**update_data)


    # Обновление данных в кэше
    cached_database = cache.get('bdproductions')

    if cached_database:
        # Проверяем, есть ли объект с указанным order_id в кэше
        found = False
        for obj in cached_database:
            if obj.id == order_id:
                obj.controller_name_response = user_name
                obj.datetime_controller_response = now
                obj.status = status
                found = True
                break

        if not found:
            print(f"Ошибка: объект с order_id {order_id} не найден в кэше")
    else:
        print("Ошибка: кэш не содержит данных")

    # Обновляем кэш с обновленными данными
    cache.set('bdproductions', cached_database)


# Фиксация результата
def fix_result(user_name, order_id,  status_fix, comment_fix):
    """
    Функция регистрации принятия решения контроллером

    1. Получаем из формы принятия решения user_name(str), order_id(str),
        и валидные данные status_fix(str), comment_fix(str)
    2. Получаем расчетные данные о времени регистрируемого результата
    3. Формируем словарь для отправки в БД
    3. Отправляем словарь в БД
    4. Обновляем КЭШ с учетом полученных данных о принятии решения
    """
    now = datetime.now()
    order_id = int(order_id)
    user_name = user_name
    selected_option = status_fix
    text_result = comment_fix
    status = status_fix


    # Расчет и фиксация фактического времени потраченное на принятие решения
    production = BDProductions.objects.get(id=order_id)
    datetime_controller_response = production.datetime_controller_response
    time_result_fact = round((now - datetime_controller_response).total_seconds() / 3600, 2)


    # Сбор данных в словарь для отправки в БД
    update_data = {
        'controller_name_result': user_name,
        'decision': selected_option,
        'decision_text': text_result,
        'datetime_controller_in_work': now,
        'status': status,
        'value_fact': time_result_fact,
    }

    # Перенос информации в БД
    BDProductions.objects.filter(id=order_id).update(**update_data)


    # Обновление данных в кэше
    cached_database = cache.get('bdproductions')

    if cached_database:
        # Проверяем, есть ли объект с указанным order_id в кэше
        found = False
        for obj in cached_database:
            if obj.id == order_id:
                obj.controller_name_result = user_name
                obj.decision = selected_option
                obj.decision_text = text_result
                obj.datetime_controller_in_work = now
                obj.status = status
                obj.value_fact = time_result_fact

                found = True
                break

        if not found:
            print(f"Ошибка: объект с order_id {order_id} не найден в кэше")
    else:
        print("Ошибка: кэш не содержит данных")

    # Обновляем кэш с обновленными данными
    cache.set('bdproductions', cached_database)