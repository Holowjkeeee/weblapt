from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from laptop.views import ShowLaptopsView
from laptop.api import (
    LaptopViewset,
    BrandViewset,
    ProcessorBrandViewset,
    ProcessorFamilyViewset,
    ReviewViewset,
    AuthViewSet,
)

router = DefaultRouter()
router.register("laptops", LaptopViewset, basename="laptop")
router.register("brands", BrandViewset, basename="brand")
router.register("processor-brands", ProcessorBrandViewset, basename="processorbrand")
router.register("processor-families", ProcessorFamilyViewset, basename="processorfamily")
router.register("reviews", ReviewViewset, basename="review")
router.register("auth", AuthViewSet, basename="auth")

urlpatterns = [
    path('', ShowLaptopsView.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)