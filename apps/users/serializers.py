import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import User

PHONE_REGEX = re.compile(r"^\+998\d{9}$")


def validate_uz_phone_number(value: str) -> str:
    if value and not PHONE_REGEX.fullmatch(value):
        raise serializers.ValidationError("Telefon raqami +998XXXXXXXXX formatida bo'lishi kerak.")
    return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone_number",
            "role",
        )
        # API orqali foydalanuvchi o'ziga admin rolini bera olmasligi uchun role read-only qilinadi
        read_only_fields = ("id", "role")

    def validate_phone_number(self, value: str) -> str:
        return validate_uz_phone_number(value)

    def validate(self, attrs: dict) -> dict:
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Parollar bir-biriga mos kelmadi."}
            )
        return attrs

    def create(self, validated_data: dict) -> User:
        # password_confirm model maydoni emas, faqat tasdiqlash uchun ishlatiladi
        validated_data.pop("password_confirm")
        return User.objects.create_user(**validated_data)


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
        )
        # Foydalanuvchi o'z profilini tahrirlaganda email va role ni o'zgartira olmasligi shart
        read_only_fields = ("id", "email", "role")

    def validate_phone_number(self, value: str) -> str:
        return validate_uz_phone_number(value)
