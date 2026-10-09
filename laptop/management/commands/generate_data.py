from django.core.management.base import BaseCommand

from faker import Faker

from django.contrib.auth.models import User

from laptop.models import (
    Brand,
    ProcessorBrand,
    ProcessorFamily,
    Laptop,
    Review
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])

        user = User.objects.get(username='generator')

        brands = []
        for name in [
            'Apple',
            'ASUS',
            'Lenovo',
            'Dell',
            'HP',
            'Acer',
            'MSI',
            'Gigabyte',
            'Samsung',
            'Xiaomi',
            'Huawei',
            'Razer',
            'Microsoft',
            'LG'
        ]:
            brand, _ = Brand.objects.get_or_create(name=name)
            brands.append(brand)

        processor_brands = []
        for name in [
            'Intel',
            'AMD',
            'Apple',
            'Qualcomm'
        ]:
            processor_brand, _ = ProcessorBrand.objects.get_or_create(
                name=name
            )
            processor_brands.append(processor_brand)

        processor_families = []

        processor_data = {
            'Intel': [
                'Pentium Gold',
                'Pentium Silver',
                'Celeron',
                'Core i3',
                'Core i5',
                'Core i7',
                'Core i9'
            ],
            'AMD': [
                'Athlon Gold',
                'Athlon Silver',
                'Athlon',
                'A-series',
                'E-series',
                'Ryzen 3',
                'Ryzen 5',
                'Ryzen 7',
                'Ryzen 9'
            ],
            'Apple': [
                'M1',
                'M2',
                'M3',
                'M4'
            ],
            'Qualcomm': [
                'Snapdragon 850',
                'Snapdragon 8cx',
                'Snapdragon X Elite',
                'Snapdragon X Plus'
            ]
        }

        for processor_brand in processor_brands:
            for family_name in processor_data[processor_brand.name]:
                family, _ = ProcessorFamily.objects.get_or_create(
                    name=family_name,
                    brand=processor_brand
                )
                processor_families.append(family)

        for _ in range(50):
            laptop = Laptop.objects.create(
                name=fake.word().capitalize() + ' ' + fake.word().capitalize(),
                description=fake.text(max_nb_chars=200),
                brand=fake.random_element(brands),
                processor_family=fake.random_element(processor_families),
                processor_model=fake.bothify(text='####??'),
                price=fake.random_int(min=30000, max=250000),
                ram=fake.random_element([
                    '4GB',
                    '8GB',
                    '16GB',
                    '32GB',
                    '64GB'
                ]),
                storage=fake.random_element([
                    '128GB',
                    '256GB',
                    '512GB',
                    '1TB',
                    '2TB'
                ]),
                user=user
            )

            for _ in range(fake.random_int(min=0, max=3)):
                Review.objects.create(
                    author_name=fake.name(),
                    text=fake.text(max_nb_chars=300),
                    laptop=laptop
                )

        self.stdout.write(
            self.style.SUCCESS('Тестовые данные успешно созданы.')
        )