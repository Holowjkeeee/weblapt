from rest_framework import serializers
from .models import Brand, ProcessorBrand, ProcessorFamily, Laptop, Review

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

class ProcessorBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessorBrand
        fields = "__all__"

class ProcessorFamilySerializer(serializers.ModelSerializer):
    brand_name = serializers.StringRelatedField(source='brand.name', read_only=True)

    class Meta:
        model = ProcessorFamily
        fields = "__all__"

class LaptopSerializer(serializers.ModelSerializer):
    processor_brand_name = serializers.StringRelatedField(
        source='processor_family.brand.name',
        read_only=True
    )
    processor_family_name = serializers.StringRelatedField(
        source='processor_family.name',
        read_only=True
    )

    def create(self, validated_data):
        if "request" in self.context:
            validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    class Meta:
        model = Laptop
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    laptop_name = serializers.StringRelatedField(source='laptop.name', read_only=True)

    class Meta:
        model = Review
        fields = "__all__"