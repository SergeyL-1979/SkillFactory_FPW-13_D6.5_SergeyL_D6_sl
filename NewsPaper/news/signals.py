# ============ D6.4 Сигналы ==========================
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver  # импортируем нужный декоратор
from django.core.mail import *
from .models import *


@receiver(post_save, sender=Post)
def sub_send(sender, instance, created, **kwargs):
    if created:
        subject = f'{instance.preview_name} {instance.dateCreation.strftime("%d %m %Y")}'
    else:
        subject = f'Изменено  {instance.preview_name} {instance.dateCreation.strftime("%d %m %Y")}'

    send_mail(
        subject=subject,
        message=instance.text,
        from_email='skillfactory@gmail.com',
        recipient_list=['testovuj@gmail.com'],
        html_message='',
    )


@receiver(post_delete, sender=Post)
def sub_del(sender, instance, **kwargs):
    subject = f'{instance.preview_name} удалено!'

    send_mail(
        subject=subject,
        message=f'Удалено {instance.dateCreation.strftime("%d %m %Y")}',
        from_email='skillfactory@gmail.com',
        recipient_list=['testovuj@gmail.com']
    )


