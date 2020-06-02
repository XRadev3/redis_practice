#!/usr/bin/env python3

from crontab import CronTab
import os
import sys

python_dir = os.getcwd()
python_path = python_dir + "/../venv/bin/python3"
job_path = ' /home/hristo/virtualenvironments/personal_training/redis_practice/app/cron_cache.py >/dev/null 2>&1'


def cron_clean_cache():
    """
    This simple cron job will start the cleaning script 'cron_cache.py'
    This job will be executed each minute.
    """
    cron_minion = CronTab(user='hristo')
    job = cron_minion.new(command=python_path + job_path)

    job.minute.every(1)
    cron_minion.write()

cron_clean_cache()