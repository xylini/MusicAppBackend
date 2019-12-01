from django.db.models import Q
from rest_framework import viewsets, permissions, status
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response

from api.exceptions.auth import UserNameOrEmailExistsException
from api.exceptions.generic import RequiredDataNotProvidedException


class CustomAuthViewSet(viewsets.ViewSet):
    permission_classes = [
        permissions.AllowAny
    ]

    @action(detail=False, methods=['POST'])
    def register(self, request):
        data = request.data
        data_keys = set(data)
        required_data_keys = {'username', 'email', 'password', 'first_name', 'last_name'}
        is_required_data = len(required_data_keys - data_keys) == 0

        if not is_required_data:
            raise RequiredDataNotProvidedException

        if User.objects.filter(Q(username=data['username']) | Q(email=data['email'])):
            raise UserNameOrEmailExistsException

        user = User.objects.create_user(data['username'], data['email'], data['password'])
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.save()

        response_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email
        }

        return Response(data=response_data, status=status.HTTP_200_OK)
