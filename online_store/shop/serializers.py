from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
   class Meta:
      model = UserProfile
      fields = ('username', 'email', 'password', 'first_name', 'last_name', 'age', 'phone_number')
      extra_kwargs = {'password': {'write_only': True}}

   def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user

   def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Неверные учетные данные')

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),

        }
class UserProfileSimpleSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']


class UserProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']


class RatingSerializers(serializers.ModelSerializer):
    user = UserProfileSimpleSerializers()

    class Meta:
        model = Rating
        fields = ['user', 'stars']


class ReviewSerializers(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%d-%m-%Y')
    author = UserProfileSimpleSerializers()

    class Meta:
        model = Review
        fields = ['author', 'parent_reviews', 'text', 'created_date']


class ProductPhotoSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductPhotos
        fields = ['image']


class ProductListSerializers(serializers.ModelSerializer):
    product_photo = ProductPhotoSerializers(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['product_name', 'product_photo', 'price', 'average_rating']

    def get_average_rating(self, obj):
        return obj.get_average_rating()


class ProductDetailSerializers(serializers.ModelSerializer):
    category = CategorySerializers()
    product_photo = ProductPhotoSerializers(many=True, read_only=True)
    date = serializers.DateField(format='%d-%m-%Y %H:%M')
    ratings = RatingSerializers(many=True, read_only=True)
    reviews = ReviewSerializers(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['product_name', 'category', 'date', 'product_photo', 'price', 'description',
                  'average_rating', 'ratings', 'Product_video', 'owner', 'reviews']

    def get_average_rating(self, obj):
        return obj.get_average_rating()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializers(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'get_total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()
