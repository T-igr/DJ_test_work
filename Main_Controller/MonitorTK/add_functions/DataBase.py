from datetime import datetime
from MonitorTK.models import BDProductions
from django.core.cache import cache



def cache_database():
    """
    Функция работы БД загруженной в КЭШ с ключом 'bdproductions'
    Если КЭШ еше не создан, он создается выгрузкой из БД
    Если КЭШ создан, то мы работаем с данными из него.

    Возвращает список с базой данных
    """
    # Получаем текущий кэш
    cached_database = cache.get('bdproductions')

    # Проверка на наличие кэша
    if cached_database:
        print('КЭШ уже создан')

    else:
        # Если кэш пустой (возможно, из-за первого вызова функции cache_database),
        print('КЭШ еще не создан, исправляю ситуацию...')
        # делаем выгрузку всех позиций из БД
        database = BDProductions.objects.all()

        # Помещаем выгруженную БД в КЭШ с ключом 'bdproductions'
        cache.set('bdproductions', list(database))

        # Получаем данные из КЭШа с ключом 'bdproductions'
        cached_database = cache.get('bdproductions')


    for obj in cached_database:
        print(f'Номер заказ из кэша: {obj.order}')

    return cached_database


def separation_BD(database: object) -> object:
    """
    Принимаемая database - это объект модели Django выгруженный из КЭШа

    1. Функция создает три списка СЗ и наполняет их согласно проставленным статусам
    2. Производится подсчет кол-ва СЗ по каждому списку
    3. Просчитывается общий объем трудоемкости выполнения операций контроля по каждому списку
    4. Фиксируется время фактического нахождения СЗ в работе и передает в кэш и БД

    Возвращаются три списка СЗ и к ним по 2 параметра (кол-во и объем трудоемкости)
    """

    database = database

    # Предварительно создаем пустые списки для наполнения СЗ
    status_task = []
    status_work = []
    status_done = []

    # Переменные для подсчета количества и суммы значений
    count_task = count_work = count_done = 0
    sum_task = sum_work = sum_done = 0

    time_now = datetime.now()

    # Заполняем списки в соответствии со статусом
    for item in database:
        status = item.status
        value = item.value
        value_fact = item.value_fact
        datetime_controller_in_work = item.datetime_controller_in_work

        if 'Ожидает приемку' in status:
            status_task.append(item)
            count_task += 1
            sum_task += value
        elif 'В работе' in status:
            status_work.append(item)
            count_work += 1
            sum_work += value

            # Определяем время нахождения СЗ в работе
            if item.datetime_controller_response is not None:
                item.value_fact = round((time_now - item.datetime_controller_response).total_seconds() / 3600, 2)

                # Фиксируем данные в БД
                BDProductions.objects.filter(id=item.id).update(value_fact=item.value_fact)
            else:
                item.value_fact = None



        elif status in ['Принято', 'Брак', 'Отправлено на доработку'] and datetime_controller_in_work.day == time_now.day:
            status_done.append(item)
            count_done += 1
            if value_fact is not None:
                sum_done += value_fact

    # Обновляем кэш:
    cache.set('bdproductions', database)

    # Выводим результат
    # print("Список со статусом Ожидает приемку:", status_task)
    # print("Количество и сумма значений в статусе Ожидает приемку:", count_task, sum_task)
    # print("Список со статусом В работе:", status_work)
    # print("Количество и сумма значений в статусе В работе:", count_work, sum_work)
    # print("Список со статусом Принято, Брак или Отправлено на доработку:", status_done)
    # print("Количество и сумма значений в статусе Принято, Брак или Отправлено на доработку:", count_done, sum_done)

    return (status_task, count_task, sum_task,
            status_work, count_work, sum_work,
            status_done, count_done, sum_done,)


