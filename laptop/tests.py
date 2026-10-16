from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Brand,
    ProcessorBrand,
    ProcessorFamily,
    Laptop,
    Review,
)


class BrandApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )

        self.client.force_authenticate(user=self.user)

    def test_create_brand(self):
        url = reverse("brand-list")

        data = {
            "name": "ASUS"
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Brand.objects.count(),
            1
        )

        self.assertEqual(
            Brand.objects.first().name,
            "ASUS"
        )

    def test_get_brands(self):
        Brand.objects.create(name="ASUS")
        Brand.objects.create(name="Lenovo")

        url = reverse("brand-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )

    def test_update_brand(self):
        brand = Brand.objects.create(name="ASUS")

        url = reverse(
            "brand-detail",
            kwargs={"pk": brand.pk}
        )

        response = self.client.patch(
            url,
            {
                "name": "ASUS ROG"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        brand.refresh_from_db()

        self.assertEqual(
            brand.name,
            "ASUS ROG"
        )

    def test_delete_brand(self):
        brand = Brand.objects.create(name="ASUS")

        url = reverse(
            "brand-detail",
            kwargs={"pk": brand.pk}
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertEqual(
            Brand.objects.count(),
            0
        )


class ProcessorBrandApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="processoruser",
            password="testpassword"
        )

        self.client.force_authenticate(user=self.user)

    def test_create_processor_brand(self):
        url = reverse("processorbrand-list")

        response = self.client.post(
            url,
            {
                "name": "Intel"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            ProcessorBrand.objects.count(),
            1
        )

        self.assertEqual(
            ProcessorBrand.objects.first().name,
            "Intel"
        )

    def test_get_processor_brands(self):
        ProcessorBrand.objects.create(name="Intel")
        ProcessorBrand.objects.create(name="AMD")

        url = reverse("processorbrand-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )


class LaptopApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="laptopuser",
            password="testpassword"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword"
        )

        self.client.force_authenticate(user=self.user)

        self.brand = Brand.objects.create(
            name="ASUS"
        )

        self.processor_brand = ProcessorBrand.objects.create(
            name="AMD"
        )

        self.processor_family = ProcessorFamily.objects.create(
            name="Ryzen 7",
            brand=self.processor_brand
        )

    def test_get_only_current_user_laptops(self):
        Laptop.objects.create(
            name="ASUS TUF",
            description="Gaming laptop",
            brand=self.brand,
            processor_family=self.processor_family,
            processor_model="7735HS",
            price=90000,
            ram="16GB",
            storage="512GB",
            user=self.user
        )

        Laptop.objects.create(
            name="Other laptop",
            description="Another laptop",
            brand=self.brand,
            processor_family=self.processor_family,
            processor_model="5600H",
            price=70000,
            ram="16GB",
            storage="512GB",
            user=self.other_user
        )

        url = reverse("laptop-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]["name"],
            "ASUS TUF"
        )

    def test_laptop_stats(self):
        Laptop.objects.create(
            name="Laptop 1",
            description="Test",
            brand=self.brand,
            processor_family=self.processor_family,
            processor_model="7735HS",
            price=80000,
            ram="16GB",
            storage="512GB",
            user=self.user
        )

        Laptop.objects.create(
            name="Laptop 2",
            description="Test",
            brand=self.brand,
            processor_family=self.processor_family,
            processor_model="7735HS",
            price=100000,
            ram="32GB",
            storage="1TB",
            user=self.user
        )

        url = reverse("laptop-stats")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["count"],
            2
        )

        self.assertEqual(
            response.data["avg"],
            90000.0
        )


class ReviewApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reviewuser",
            password="testpassword"
        )

        self.client.force_authenticate(user=self.user)

        self.laptop = Laptop.objects.create(
            name="Test Laptop",
            description="Test description",
            price=50000,
            user=self.user
        )

    def test_create_review(self):
        url = reverse("review-list")

        response = self.client.post(
            url,
            {
                "author_name": "Alexander",
                "text": "Хороший ноутбук",
                "laptop": self.laptop.id
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Review.objects.count(),
            1
        )