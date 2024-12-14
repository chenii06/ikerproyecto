# Django
from django import forms

# Models
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseBadRequest
from django.template import loader
from django.template.loader import render_to_string
from django.urls import resolve, get_resolver, Resolver404
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from apps.users.models import Profile

# Utils
from django_recaptcha.fields import ReCaptchaField
import re
import unicodedata

UserModel = get_user_model()

def _unicode_ci_compare(s1, s2):
    """
    Perform case-insensitive comparison of two identifiers, using the
    recommended algorithm from Unicode Technical Report 36, section
    2.11.2(B)(2).
    """
    return (
        unicodedata.normalize("NFKC", s1).casefold()
        == unicodedata.normalize("NFKC", s2).casefold()
    )

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username or Email')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            # If the username contains '@', consider it an email and validate it
            try:
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                raise ValidationError("No user found with this email address.")
            return user.username
        return username

class SignupForm(forms.Form):
    # Signup Form
    username = forms.CharField(label=False, min_length=4, max_length=20, widget = forms.TextInput(attrs={'placeholder':'Username', 'onkeyup': 'without_space(this);'}))
    password = forms.CharField(label=False, max_length=70, widget = forms.PasswordInput(attrs={'placeholder':'Password'}))
    password_confirmation = forms.CharField(label=False, max_length=70, widget = forms.PasswordInput(attrs={'placeholder':'Password confirmation'}))
    email = forms.CharField(label=False, min_length=6, max_length=70, widget = forms.EmailInput(attrs={'placeholder':'Email'}))
    captcha = ReCaptchaField(label=False)

    def clean_username(self):
        # Username must be unique
        username = self.cleaned_data["username"]
        if not username:
            raise ValidationError("The username cannot be empty.")
        if len(username) > 20:
            raise forms.ValidationError("Username must be at most 20 characters long")
        if not re.match("^\w+$", username):
            raise forms.ValidationError("Username must be alphanumeric")
        if ' ' in username or '/' in username:
            raise forms.ValidationError("Username cannot contain spaces or '/'")
        username_taken = User.objects.filter(username__iexact=username).exists()
        if username_taken:
            raise forms.ValidationError("Username is already in use")

        resolver = get_resolver()

        # Obtener todas las URLs
        urls = []
        for url_pattern in resolver.url_patterns:
            if hasattr(url_pattern, 'url_patterns'):  # Verificar si es un include()
                for sub_url_pattern in url_pattern.url_patterns:
                    if hasattr(sub_url_pattern, 'pattern'):
                        url = sub_url_pattern.pattern.describe()
                        url_without_name = url.split('[name=')[0].strip().strip("'")
                        urls.append(url_without_name)

        # Crear una respuesta con la lista de URLs

        categories = [r'^demons/?$', r'^all/?$', r'^rated/?$', r'^unrated/?$', r'^challenge/?$', r'^easiest/?$', r'^shitty/?$', r'^future/?$', r'^tiny/?$', r'^deathless/?$', r'^impossible/?$', r'^spam/?$', r'^impossible_tiny/?$', r'^pemonlist/?$', r'^platformer_challengelist/?$', r'^tiny_demonlist/?$', r'^platformer_deathlesslist/?$', r'^impossible_platformerlist/?$', r'^spam_challengelist/?$', r'^impossible_tiny_list/?$', r'^tiny_pemonlist/?$', r'^platformerlist/?$']

        urls.remove('')
        urls.remove('')
        urls.remove('')
        urls.remove('^(?P<value>[^/]+)/?$')
        urls.remove('(?P<url>.*)$')
        urls.extend(categories)

        for pattern in urls:
            if re.match(pattern, username):
                raise forms.ValidationError("Username is not available")

        return username

    def clean(self):
        # Verify password confirmation match
        data = super().clean()

        password = data["password"]
        password_confirmation = data["password_confirmation"]

        if password != password_confirmation:
            raise forms.ValidationError("Passwords do not match")
        
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long and include at least one digit and one uppercase letter.")

        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must be at least 8 characters long and include at least one digit and one uppercase letter.")

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must be at least 8 characters long and include at least one digit and one uppercase letter.")

        return data

    def save(self):
        # Create user and profile
        data = self.cleaned_data
        data.pop("password_confirmation")
        data.pop("captcha")

        user = User.objects.create_user(**data)
        profile = Profile(user=user)
        profile.save()

class PasswordResetForm(forms.Form):
    # PasswordReset Form
    email = forms.EmailField(label=False, max_length=254, widget = forms.EmailInput(attrs={'placeholder':'Email', 'onkeyup': 'without_space(this);', 'autocomplete': 'email'}))

    def send_mail(
        self,
        subject_template_name,
        html_email_template_name,
        context,
        from_email,
        to_email,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """

        subject = render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        html_message = render_to_string(html_email_template_name, context)
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,
            to=[to_email]
        )
        message.attach_alternative(html_message, "text/html")
        message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
            and _unicode_ci_compare(email, getattr(u, email_field_name))
        )
    
    def save(
        self,
        domain_override=None,
        subject_template_name=None,
        email_template_name=None,
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        extra_email_context = extra_email_context or {'option': 'password'}

        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name=subject_template_name,
                html_email_template_name=html_email_template_name,
                context=context,
                from_email=from_email,
                to_email=user_email,
            )

class SetPasswordForm(forms.Form):
    """
    A form that lets a user set their password without entering the old
    password
    """

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    new_password1 = forms.CharField(
        label=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'placeholder':'New password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'placeholder':'New password confirmation'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
    

class EmailResetForm(forms.Form):
    # EmailReset Form
    email = forms.CharField(label=False, max_length=254, widget = forms.EmailInput(attrs={'placeholder':'Email', 'onkeyup': 'without_space(this);', 'autocomplete': 'email'}))

    def send_mail(
        self,
        subject_template_name,
        html_email_template_name,
        context,
        from_email,
        to_email,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        html_message = render_to_string(html_email_template_name, context)
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,
            to=[to_email]
        )
        message.attach_alternative(html_message, "text/html")
        message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
            and _unicode_ci_compare(email, getattr(u, email_field_name))
        )
    
    def save(
        self,
        domain_override=None,
        subject_template_name=None,
        email_template_name=None,
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        extra_email_context = extra_email_context or {'option': 'email'}
        
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name=subject_template_name,
                html_email_template_name=html_email_template_name,
                context=context,
                from_email=from_email,
                to_email=user_email,
            )

class SetEmailForm(forms.Form):
    """
    A form that lets a user set their email without entering the old
    email
    """

    new_email = forms.CharField(
        label=False,
        widget=forms.EmailInput(attrs={"autocomplete": "new-email", 'placeholder':'New email'}),
        strip=True,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        new_email = self.cleaned_data.get("new_email")

        return new_email

    def save(self, commit=True):
        new_email = self.cleaned_data["new_email"]
        self.user.email = new_email
        self.user.save()
        return self.user

class AnnouncementForm(forms.Form):
    # PasswordReset Form
    email = forms.EmailField(label=False, max_length=254, widget = forms.EmailInput(attrs={'placeholder':'Email', 'onkeyup': 'without_space(this);', 'autocomplete': 'email'}))

    def send_mail(
        self,
        subject_template_name,
        html_email_template_name,
        context,
        from_email,
        to_email,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """

        subject = render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        html_message = render_to_string(html_email_template_name, context)
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,
            to=[to_email]
        )
        message.attach_alternative(html_message, "text/html")
        message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
            and _unicode_ci_compare(email, getattr(u, email_field_name))
        )
    
    def save(
        self,
        domain_override=None,
        subject_template_name=None,
        email_template_name=None,
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        extra_email_context = extra_email_context or {'option': 'password'}

        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name=subject_template_name,
                html_email_template_name=html_email_template_name,
                context=context,
                from_email=from_email,
                to_email=user_email,
            )
