from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, password, **other_fields):
        if not username:
            raise ValueError("Required Field username is not set")
        if not password:
            raise ValueError("Required Field password is not set")
        user = self.model(username=username, **other_fields)
        user.set_password(password)
        user.is_active=False
        user.save()
        return user

    def create_superuser(self, username, password, **other_fields):
        if not username:
            raise ValueError("Required Field username is not set")
        if not password:
            raise ValueError("Required Field password is not set")
        user = self.create_user(username, password, **other_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save()