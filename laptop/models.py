from django.db import models

class Brand(models.Model):
    name = models.TextField("Бренд")
    picture = models.ImageField("Логотип", upload_to="brands/", null=True, blank=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name


class ProcessorBrand(models.Model):
    name = models.CharField("Производитель процессора", max_length=50)
    picture = models.ImageField("Логотип", upload_to="processor_brands/", null=True, blank=True)

    class Meta:
        verbose_name = "Производитель процессора"
        verbose_name_plural = "Производители процессоров"

    def __str__(self):
        return self.name


class ProcessorFamily(models.Model):
    name = models.CharField("Линейка процессора", max_length=50)
    brand = models.ForeignKey(
        ProcessorBrand,
        on_delete=models.CASCADE,
        verbose_name="Производитель",
        related_name="families"
    )
    picture = models.ImageField("Картинка", upload_to="processor_families/", null=True, blank=True)

    class Meta:
        verbose_name = "Линейка процессора"
        verbose_name_plural = "Линейки процессоров"

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Laptop(models.Model):
    name = models.TextField("Модель ноутбука")
    description = models.TextField("Описание")
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Бренд"
    )
    processor_family = models.ForeignKey(
        ProcessorFamily,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Линейка процессора"
    )
    processor_model = models.CharField(
        "Модель процессора",
        max_length=50,
        blank=True,
        help_text="например, 12700K, 5600H"
    )
    price = models.DecimalField("Цена (руб)", max_digits=10, decimal_places=2, default=0)
    ram = models.CharField("ОЗУ", max_length=50, blank=True, help_text="например, 16GB")
    storage = models.CharField("SSD", max_length=50, blank=True, help_text="например, 512GB")
    picture = models.ImageField("Изображение", upload_to="laptops/", null=True, blank=True)
    user = models.ForeignKey(
        "auth.User",
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Ноутбук"
        verbose_name_plural = "Ноутбуки"

    def __str__(self):
        return self.name


class Review(models.Model):
    author_name = models.CharField("Имя автора", max_length=100)
    text = models.TextField("Текст отзыва")
    laptop = models.ForeignKey(
        Laptop,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Ноутбук"
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв от {self.author_name} на {self.laptop.name}"