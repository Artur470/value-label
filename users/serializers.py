from users.models import *
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
import random
from datetime import timedelta
from django.utils import timezone
import re

class PasswordMixinRegister(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        password = attrs['password']
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({'password': "Password must contain at least one uppercase letter."})
        if not re.search(r'[!@#$%^&*]', password):
            raise serializers.ValidationError(
                {'password': "Password must contain at least one special character (!@#$%^&*)."})
        if len(password) < 8:
            raise serializers.ValidationError({'password': "Password must be at least 8 characters long."})
        return attrs


class PasswordMixin(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"error": "Password fields didn't match."})

        password = attrs['password']
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({'password': "Password must contain at least one uppercase letter."})
        if not re.search(r'[!@#$%^&*]', password):
            raise serializers.ValidationError(
                {'password': "Password must contain at least one special character (!@#$%^&*)."})
        if len(password) < 8:
            raise serializers.ValidationError({'password': "Password must be at least 8 characters long."})
        return attrs


# Profile
class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9!@#$%^&*()_+.-]+$',
            message='Username can only contain English letters, numbers, and special characters (!@#$%^&*()_+.-)',
        )],
        min_length=6,
        max_length=20,
    )
    email = serializers.EmailField()
    number = serializers.IntegerField()
    wholesaler = serializers.BooleanField()

    class Meta:
        model = User
        fields = ['id', 'username', 'gender', 'age', 'email', 'number', 'wholesaler']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9!@#$%^&*()_+.-]+$',
            message='Username can only contain English letters, numbers, and special characters (!@#$%^&*()_+.-)',
        )],
        min_length=6,
        max_length=20,
        required=False
    )
    email = serializers.EmailField(required=False)
    age = serializers.IntegerField(required=False)
    number = serializers.IntegerField(required=False)
    wholesaler = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'gender', 'age', 'email', 'number', 'wholesaler']

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.age = validated_data.get('age', instance.age)
        instance.email = validated_data.get('email', instance.email)
        instance.number = validated_data.get('number', instance.number)
        instance.wholesaler = validated_data.get('wholesaler', instance.wholesaler)

        instance.save()
        return instance


# Register
class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9!@#$%^&*()_+.-]+$',
            message='Username can only contain English letters, numbers, and special characters (!@#$%^&*()_+.-)',
        )],
        min_length=6,
        max_length=20,
    )
    password = serializers.CharField(write_only=True)
    wholesaler = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = [ 'username', 'email', 'gender', 'age', 'number', 'wholesaler', 'password']

    def create(self, validated_data):
        wholesaler = validated_data.pop('wholesaler', False)
        password = validated_data.pop('password')

        otp_code = None
        if wholesaler:
            otp_code = str(random.randint(100000, 999999))
            validated_data['is_active'] = False
            validated_data['otp_code'] = otp_code
            validated_data['otp_created_at'] = timezone.now()


            send_mail(
                'Новый ОПТОВЫЙ ПОКУПАТЕЛЬ!',
                f"Пользователь с именем {validated_data['username']} хочет зарегистрироваться как новый оптовик.\nEmail: {validated_data['email']}\nНомер телефона: {validated_data['number']}\nКод: {otp_code}",
                'email',
                ['homelife.site.kg@gmail.com'],
                fail_silently=False,
            )

        user = User.objects.create(
            password=make_password(password),
            wholesaler=wholesaler,
            **validated_data
        )

        return user


class WholesalerOTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        otp_code = attrs.get('otp_code')

        try:
            user = User.objects.get(email=email, is_active=False, wholesaler=True)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or this account is not pending activation.')

        # Проверка срока действия OTP
        if user.otp_created_at is None:
            raise serializers.ValidationError('OTP code was not created or is invalid.')

        otp_lifetime = timedelta(days=3)  # Время жизни OTP: 3 дня
        if timezone.now() > user.otp_created_at + otp_lifetime:
            raise serializers.ValidationError('OTP code has expired.')

        # Проверка OTP-кода
        if not user.otp_code or user.otp_code != otp_code:
            raise serializers.ValidationError('Invalid OTP code.')

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        user.is_active = True
        user.otp_code = None
        user.otp_created_at = None
        user.save()
        return user


class UserLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = self.user
        return data


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            token = RefreshToken(attrs['refresh'])
            token.blacklist()  # Поместите токен в черный список
        except Exception as e:
            raise serializers.ValidationError({'refresh': str(e)})
        return attrs


# Forgot password
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4)

    def validate(self, data):
        code = data.get('code')

        try:
            otp_obj = OTP.objects.get(otp=code)
            if otp_obj.is_expired:
                raise serializers.ValidationError({'error': "OTP has expired."})
        except OTP.DoesNotExist:
            raise serializers.ValidationError({'error': "Invalid OTP."})

        return data


class ChangeForgotPasswordSerializer(serializers.ModelSerializer, PasswordMixin):
    class Meta:
        model = User
        fields = ['password', 'confirm_password']


class ChangePasswordSerializer(serializers.ModelSerializer, PasswordMixin):
    old_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError({"error": "Invalid old password."})
        return value

    class Meta:
        model = User
        fields = ['old_password', 'password', 'confirm_password']


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "password",
            "last_login",
            "is_superuser",
            "username",
            "age",
            "email",
            "number",
            "wholesaler",
            "is_active",
            "is_staff",
            "gender",
        ]
