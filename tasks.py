from celery_app import celery

@celery.task(name='my_background_task')
def my_background_task(arg1, arg2):
    print('my_background_task')
    print(arg1)
    print('my_background_task')
    print('my_background_task')
    print('my_background_task')
    print('banana')
    print(arg2)
    print('my_background_task')
    print('my_background_task')
    print('my_background_task')
    return "potato"