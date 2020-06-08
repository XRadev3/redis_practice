#!/usr/bin/env python3

from crontab import CronTab
import os

python_dir = os.getcwd()
python_path = python_dir + "/../venv/bin/python3"
job_path = ' /home/hristo/virtualenvironments/personal_training/redis_practice/app/cache_cleaner.py >/dev/null 2>&1'
command = python_path + job_path


def job_clean_cache():
    """
    This simple cron job will start the cleaning script 'cache_cleaner.py'
    This job will be executed each minute.
    Temporary: To stop the jobs, GET request to '/redis/clean' must be send.
    """
    try:
        cron_minion = CronTab(user=True)
        job = cron_minion.new(command=command)
        job.minute.every(1)
        cron_minion.write()

    except Exception as message:
        return False

    return True


def cron_stop_job():
    """
    This function removes a job from crontab by its command.
    """
    try:
        cron_minion = CronTab(user=True)
        job_instances = cron_minion.find_command(command)

        while True:
            job = next(job_instances)
            cron_minion.remove(job)
            cron_minion.write()

    except StopIteration as message:
        return True

    except Exception as message:
        return False
