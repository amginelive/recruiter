import os

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def get_upload_path(instance, filename):
    """
    This function gets the upload path of the image.
    Returns the image path.
    """
    model = instance._meta.model_name.lower()
    return os.path.join(model, filename)


def send_email(subject, send_to, template_name, data):
    """
    A utility function for sending an email.
    """
    msg_plain = render_to_string('{}.txt'.format(template_name), data)
    msg_html = render_to_string('{}.html'.format(template_name), data)
    send_mail(
        subject=subject,
        message=msg_plain,
        from_email=settings.NOREPLY_EMAIL,
        recipient_list=send_to,
        html_message=msg_html,
        fail_silently=False
    )
