#!/usr/bin/env python3

from crontab import CronTab


def cron_clean_cache():
    """
    This simple cron job will start the cleaning script 'cron_cache.py'
    This job will be executed each minute.
    """
    cron_minion = CronTab(user='hristo')
    job = cron_minion.new(command='/usr/bin/python3 /home/hristo/virtualenvironments/personal_training/redis_practice/app/cron_cache.py')

    job.minute.every(1)
    cron_minion.write()
