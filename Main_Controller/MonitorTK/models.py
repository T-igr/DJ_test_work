from django.db import models

class BDProductions(models.Model):

    order = models.IntegerField(blank=False)  # Номер заказа
    workshop = models.IntegerField(blank=False)  # Номер Цеха
    area = models.IntegerField(blank=False)  # Номер участка
    product = models.CharField(max_length=15, blank=False)  # Название изделия

    operation = models.IntegerField(blank=False)  # Номер операции
    operation_name = models.CharField(max_length=30, blank=False)  # Название операции
    equipment = models.CharField(max_length=15, blank=False)  # Название обрабатывающего центра

    worker_name = models.CharField(max_length=40, blank=False)  # ФИО Исполнителя
    master_name_request = models.CharField(max_length=40, blank=False)  # ФИО вызвавшего Мастера
    master_name = models.CharField(max_length=40, blank=False)  # ФИО Мастера
    controller_name_response = models.CharField(max_length=40, null=True)  # ФИО Контроллера взявшего СЗ в работу

    decision = models.CharField(max_length=40, null=True)  # Решение
    decision_text = models.CharField(max_length=2000, blank=True, null=True)  # Описание решения

    priority = models.IntegerField(blank=True, null=True)  # Приоритет СЗ
    status = models.CharField(max_length=40, null=True)  # Статус СЗ

    datetime_master_request = models.DateTimeField(null=True)  # Время и дата вызова Мастера
    datetime_controller_request = models.DateTimeField(null=True)  # Время и дата вызова Контроллера
    datetime_controller_response = models.DateTimeField(null=True)  # Время и дата ответа Контроллера

    datetime_controller_in_work = models.DateTimeField(null=True)  # Время и дата фиксации результата контроллером
    value = models.FloatField(blank=True, null=True)  # объем работ для контроллера, ч
    controller_name_result = models.CharField(max_length=40, null=True)  # ФИО Контроллера принявшего решение
    value_fact = models.FloatField(blank=True, null=True)  # фактическое время принятия решения, ч

    def __str__(self):
        return str(self.order)



