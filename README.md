# RSHU Schedule / Расписание РГГМУ
Нобольшой скрипт, проверяюший расписание на сайте РГГМУ и, если оно изменилось присылает файл с новым расписанием и уведомление в telegram.

## Установка
Установите с помощью команды:
```sh
$ git clone https://github.com/cosmickitten/rshu_schedule.git
$ cd rshu_schedule
$ mv .env_example .env
$ pip install -r requirements.txt 
```
Настройте .env файл:

group   -   название вашей группы на сайте с расписанием

ids - ваш telegram id(можно указать несколько через запятую)

token - токен вашего telegram бота, берётся у @botfather



## Совет
Добавьте выполнение скрипта в планировщик задач, чтобы знать, когда расписание изменилось. Например на 5 утра каждый день =)

Пример для cron:
```sh
0 5 * * * /usr/bin/python /opt/rshu_schedule/main.py
```