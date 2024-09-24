# backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User  # Import your custom user model

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            print(username)
            user = User.objects.get(email=username)  # Here, we assume the user logs in with email
            # Check if the provided password matches the hashed password in the database
            if user.check_password(password):
                return user
            
        except User.DoesNotExist:
            return None  # No such user exists

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
