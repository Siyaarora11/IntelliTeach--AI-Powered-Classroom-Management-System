from django.contrib.auth.models import BaseUserManager
# from django.contrib.auth.backends import ModelBackend
# from django.core.exceptions import ValidationError
# from .models import AuthUser

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_hod', True)

        return self.create_user(email=email, password=password, **extra_fields)


# class AuthBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         UserModel = AuthUser

#         try:
#             # Check if username is an email
#             email_validator = UserModel.email.field.validators[0] # type: ignore
#             email_validator(username)
#             user = UserModel.objects.get(email=username)
#         except ValidationError:
#             # If not an email, assume it's a roll number
#             try:
#                 user = UserModel.objects.get(student__roll_number=username)
#             except UserModel.DoesNotExist:
#                 return None

#         if user.check_password(password): # type: ignore
#             return user

#     def get_user(self, user_id):
#         UserModel = AuthUser
#         try:
#             return UserModel.objects.get(pk=user_id)
#         except UserModel.DoesNotExist:
#             return None
