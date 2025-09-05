from django.utils.translation   import gettext as _
from django.core.mail           import send_mail, EmailMultiAlternatives
from django.core.exceptions     import ValidationError
from django.urls                import reverse
from django.conf                import settings
from django.template            import RequestContext
from django.template.loader     import get_template
from rest_framework.views       import APIView

class MailBase:
    def __init__(self, request, recipient, title, template="mails/base.html"):
        self.request = request
        self.title = title
        self.recipient = [recipient] if not type(recipient) is list and not type(recipient) is tuple else recipient
        self.template = get_template(template)
        self.data = {
            # 'request':self.request,
            'title':self.title,
            'recipient':self.recipient
        }
    
    def send(self, **kwargs):
        data = self.data|kwargs
        send_mail(_(self.title), '', settings.FROM_EMAIL, self.recipient, fail_silently=False, html_message=self.template.render({
            'request': self.request,
            'control': {
                'content': data
            }
        }))

class MailLogin(MailBase):
    pass

class MailRegister(MailBase):
    pass