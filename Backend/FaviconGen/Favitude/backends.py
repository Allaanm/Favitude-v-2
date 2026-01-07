from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Check if the "username" (which comes from the form) is an email
            # We look up user by email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # If user not found by email, return None
            # Optionally, fall back to checking by username here if you want mixed login
            return None
        except UserModel.MultipleObjectsReturned:
            # Handle edge case where multiple accounts might have same email (shouldn't happen with unique constrained)
            return None

        # Verify the password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
