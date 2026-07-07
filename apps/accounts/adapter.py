from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class AutoSignupAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def is_open_for_signup(self, request, sociallogin):
        return True

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = data.get("email") or sociallogin.account.extra_data.get("email", "")
        if email and not user.email:
            user.email = email
        if not user.username:
            base = (email.split("@")[0] if email else "") or "user"
            username = base
            while User.objects.filter(username=username).exists():
                username = f"{base}{uuid.uuid4().hex[:6]}"
            user.username = username
        return user

    def save_user(self, request, sociallogin, form=None):
        return super().save_user(request, sociallogin, form)

    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return
        email = sociallogin.account.extra_data.get("email")
        if email:
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass
