from builtins import float

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Max, Min
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from openpyxl import Workbook
from openpyxl.styles import Font

from rest_framework import mixins, serializers, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Laptop, Brand, ProcessorBrand, ProcessorFamily, Review
from .serializers import (
    LaptopSerializer,
    BrandSerializer,
    ProcessorBrandSerializer,
    ProcessorFamilySerializer,
    ReviewSerializer,
)

class LaptopFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = filters.NumberFilter(field_name="price", lookup_expr='lte')
    brand = filters.NumberFilter(field_name="brand__id")
    processor_family = filters.NumberFilter(field_name="processor_family__id")
    processor_brand = filters.NumberFilter(field_name="processor_family__brand__id")  
    processor_model = filters.CharFilter(lookup_expr='icontains')
    ram = filters.CharFilter(lookup_expr='icontains')
    storage = filters.CharFilter(lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Laptop
        fields = [
            'brand', 'processor_family', 'processor_model',
            'ram', 'storage', 'price_min', 'price_max', 'name', 'description'
        ]

class LaptopViewset(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    queryset = Laptop.objects.all()
    serializer_class = LaptopSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LaptopFilter

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            user_id = self.request.GET.get("user")
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg = serializers.FloatField(allow_null=True)
        max = serializers.FloatField(allow_null=True)
        min = serializers.FloatField(allow_null=True)

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        stats = queryset.aggregate(
            count=Count("*"),
            avg=Avg("price"),
            max=Max("price"),
            min=Min("price"),
        )
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="export-excel")
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Laptops"

        headers = [
            "ID", "Модель", "Описание", "Бренд",
            "Производитель CPU", "Линейка CPU", "Модель CPU",
            "Цена", "ОЗУ", "SSD"
        ]
        worksheet.append(headers)
        for cell in worksheet[1]:
            cell.font = Font(bold=True)

        for laptop in queryset:
            worksheet.append([
                laptop.id,
                laptop.name,
                laptop.description,
                laptop.brand.name if laptop.brand else "",
                laptop.processor_family.brand.name if laptop.processor_family and laptop.processor_family.brand else "",
                laptop.processor_family.name if laptop.processor_family else "",
                laptop.processor_model,
                float(laptop.price),
                laptop.ram,
                laptop.storage,
            ])

        widths = [8, 30, 50, 15, 20, 20, 20, 15, 12, 12]
        for i, col in enumerate(['A','B','C','D','E','F','G','H','I','J']):
            worksheet.column_dimensions[col].width = widths[i]

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="laptops.xlsx"'
        workbook.save(response)
        return response

class BrandViewset(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        stats = Brand.objects.aggregate(count=Count("*"))
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

class ProcessorBrandViewset(mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            GenericViewSet):
    queryset = ProcessorBrand.objects.all()
    serializer_class = ProcessorBrandSerializer
    permission_classes = [IsAuthenticated]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        stats = ProcessorBrand.objects.aggregate(count=Count("*"))
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

class ProcessorFamilyViewset(mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             mixins.DestroyModelMixin,
                             GenericViewSet):
    queryset = ProcessorFamily.objects.all()
    serializer_class = ProcessorFamilySerializer
    permission_classes = [IsAuthenticated]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        stats = ProcessorFamily.objects.aggregate(count=Count("*"))
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

class ReviewViewset(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        stats = Review.objects.aggregate(count=Count("*"))
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Неверный логин или пароль"},
                status=status.HTTP_400_BAD_REQUEST
            )
        login(request, user)
        return Response({
            "id": user.id,
            "username": user.username,
            "is_superuser": user.is_superuser,
        })

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response({"detail": "Вы вышли"})

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "is_superuser": user.is_superuser,
        })

    @method_decorator(ensure_csrf_cookie)
    @action(detail=False, methods=["get"])
    def csrf(self, request):
        return Response({"detail": "CSRF cookie set"})

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")

        if not username or not password:
            return Response(
                {"detail": "Логин и пароль обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "Пользователь с таким логином уже существует"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(username=username, password=password, email=email)
        user.is_superuser = False
        user.is_staff = False
        user.save()

        login(request, user)
        return Response({
            "id": user.id,
            "username": user.username,
            "is_superuser": user.is_superuser,
        }, status=status.HTTP_201_CREATED)