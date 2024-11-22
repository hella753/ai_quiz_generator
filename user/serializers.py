from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ModelSerializer
import re
from user.models import User


class RegistrationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, data):
        username = data.get("username")
        normalized_username = re.sub(r'[^a-zA-Z]', '', username).lower()
        if normalized_username == "tornike":
            raise PermissionDenied

