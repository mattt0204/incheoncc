from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from custom_logger import logger


class CronScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = set()

    def add(self, job_func, name, day_of_week, hour, minute, *args, **kwargs):
        """
        job_func: 실행할 함수
        name: job 이름(중복 방지용)
        day_of_week: 'tue,thu' 등 cron 형식
        hour: 정수(0~23)
        minute: 정수(0~59)
        """
        trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
        job = self.scheduler.add_job(
            job_func,
            trigger,
            id=name,
            replace_existing=True,
            args=args,
            kwargs=kwargs,
        )
        logger.info(f"job {name} added")
        self.jobs.add(name)
        return job

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()


# 사용 예시
def my_job():
    print("예약 실행!")
