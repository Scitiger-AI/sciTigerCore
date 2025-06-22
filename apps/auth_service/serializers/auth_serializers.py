"""
认证序列化器
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.auth_service.models import User


class LoginSerializer(serializers.Serializer):
    """
    登录序列化器
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)


class TokenRefreshSerializer(serializers.Serializer):
    """
    令牌刷新序列化器
    """
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """
    登出序列化器
    """
    refresh = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    """
    注册序列化器
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False}
        }
    
    def validate(self, attrs):
        """
        验证两次密码输入是否一致
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "两次密码输入不一致"})
        return attrs 