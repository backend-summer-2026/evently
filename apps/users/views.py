from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.users.serializers import RegisterSerializer, UserProfileSerializer

User = get_user_model()


@extend_schema(
    summary="Yangi foydalanuvchi ro'yxatdan o'tishi",
    description="Foydalanuvchi email va parol orqali tizimdan ro'yxatdan o'tadi. Default rol: user.",
    responses={201: UserProfileSerializer}
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        output_serializer = UserProfileSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        summary="Joriy foydalanuvchi profili",
        description="Login qilgan foydalanuvchining shaxsiy ma'lumotlarini olish.",
        responses={200: UserProfileSerializer}
    ),
    patch=extend_schema(
        summary="Profil ma'lumotlarini tahrirlash",
        description="Ism, familiya va telefon raqamini tahrirlash (rol va email o'zgarmaydi).",
        responses={200: UserProfileSerializer}
    )
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_object(self):
        return self.request.user
