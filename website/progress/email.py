
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.http.request import HttpRequest
from django.template import loader

from premailer import Premailer

if settings.DEBUG:
    url = "http://"
else:
    url = "https://"
url += settings.PRIMARY_HOST

transformer = Premailer(base_url=url, base_path=url,
                        disable_leftover_css=True, disable_validation=True,
                        include_star_selectors=True, keep_style_tags=False,
                        align_floating_images=False)


def generate_email_body(context, template_txt, template_html):
    request = HttpRequest()
    request.META['HTTP_HOST'] = settings.PRIMARY_HOST
    text = loader.render_to_string(template_txt, context, request)
    html = loader.render_to_string(template_html, context, request)
    html = transformer.transform(html)
    return text, html


def send_mass_html_mail(datatuple, fail_silently=False, auth_user=None,
                        auth_password=None, connection=None):
    """
    Given a datatuple of (subject, message, html_message, from_email,
    recipient_list), send each message to each recipient list.
    Return the number of emails sent.
    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user and auth_password are set, use them to log in.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.
    """
    connection = connection or mail.get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    messages = [
        mail.EmailMultiAlternatives(subject, message, sender, recipient,
                                    alternatives=[(html_message, 'text/html')],
                                    connection=connection)
        for subject, message, html_message, sender, recipient in datatuple
    ]
    return connection.send_messages(messages)


def send_template_mail(subject_template_name, email_template_name,
                       context, to_email, from_email=None, html_email_template_name=None):
    """
    Send a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    if html_email_template_name is not None:
        body, html_email = generate_email_body(context, email_template_name, html_email_template_name)
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        email_message.attach_alternative(html_email, 'text/html')
        email_message.send()
    else:
        body = loader.render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        email_message.send()
