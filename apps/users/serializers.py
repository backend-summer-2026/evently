import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password',
            'password_confirm',
            'role',
        )
        read_only_fields = ('id', 'role')

    def validate_phone_number(self, value):
        if value:
            # +998XXXXXXXXX formati
            pattern = r'^\+998\d{9}$'
            if not re.match(pattern, value):
                raise serializers.ValidationError("Telefon raqami +998XXXXXXXXX formatida bo'lishi kerak.")
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Kiritilgan parollar bir-biriga mos kelmadi."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        # Yangi ro'yxatdan o'tgan foydalanuvchi doim 'user' bo'ladi
        validated_data['role'] = 'user'
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'telegram_chat_id',
        )
        read_only_fields = ('id', 'email', 'role', 'telegram_chat_id')

    def validate_phone_number(self, value):
        if value:
            pattern = r'^\+998\d{9}$'
            if not re.match(pattern, value):
                raise serializers.ValidationError("Telefon raqami +998XXXXXXXXX formatida bo'lishi kerak.")
        return value
