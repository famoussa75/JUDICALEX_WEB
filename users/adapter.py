# users/adapter.py
from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        """
        template_prefix est fourni par allauth (ex: 'account/email/email_confirmation_message')
        On cherche template_prefix + '_subject.txt', template_prefix + '.txt', template_prefix + '.html'
        """
        subject = render_to_string(f"{template_prefix}_subject.txt", context).strip()
        text_body = render_to_string(f"{template_prefix}.txt", context)
        html_body = None
        try:
            html_body = render_to_string(f"{template_prefix}.html", context)
        except Exception:
            html_body = None

        msg = EmailMultiAlternatives(subject, text_body, self.get_from_email(), [email])
        if html_body:
            msg.attach_alternative(html_body, "text/html")
        msg.send()

    def get_email_confirmation_url(self, request, emailconfirmation):
        # Optionnel : personnaliser l'URL absolue renvoyée dans l'email
        return super().get_email_confirmation_url(request, emailconfirmation)
