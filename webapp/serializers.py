from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Categories, Products, ProductMedia, ProductVarientColor, \
    ProductVarientSize, ProductVarientItems, CustomUser, CustomerUser, \
    CustomerOrder, OrderProduct, ProductUserViewed


class ProductVarientColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVarientColor
        fields = ('id', 'title', 'code')

class ProductVarientSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVarientSize
        fields = ('id', 'title', 'code')

class ProductVarientItemsSerializer(serializers.ModelSerializer):
    color = ProductVarientColorSerializer(many=False)
    size = ProductVarientSizeSerializer (many=False)
    class Meta:
        model = ProductVarientItems
        fields = ('id', 'title', 'product_id', 'color', 'size', 'image_id', 'quantity')


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = ('id', 'media_type', 'media_content')


class ProductSerializer(serializers.ModelSerializer):
    product_varients = ProductVarientItemsSerializer(many=True)
    product_media = ProductMediaSerializer(many=True)
    class Meta:
        model = Products
        fields = ['id', 'url_slug', 'product_name', 'view_product',
                  'product_discount_price', 'product_max_price',
                  'is_stock_total', 'is_freeship', 'category_id',
                  'image' , 'get_per_product_discount_price',
                  'product_media', 'product_varients',
                  'get_per_product_discount_price', 'product_description', 'product_long_description']

class ProductMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'url_slug', 'product_name', 'view_product',
                  'product_discount_price', 'product_max_price',
                  'image' , 'get_per_product_discount_price',]

class CategorySerializer(serializers.ModelSerializer):
    products = ProductMiniSerializer(many=True)
    class Meta:
        model = Categories
        fields = ['id', 'url_slug', 'title', 'products']

class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'url_slug', 'title']

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['customorder_id', 'product_id', 'quantity', 'price',
                  'color', 'size']

class CustomerOrderSerializer(serializers.ModelSerializer):
    orderproduct = OrderProductSerializer(many=True)
    class Meta:
        model = CustomerOrder
        fields = ['code', 'customer_id', 'orderproduct', 'get_total_cost']


class CustomerUserSerializer(serializers.ModelSerializer):
    customerorder = CustomerOrderSerializer(many=True)
    class Meta:
        model = CustomerUser
        fields = ['auth_user_id', 'name', 'phone', 'address', 'customerorder']


class ProductUserViewedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUserViewed
        fields = ['product_id', 'customuser_id']

class CustomUserSerializer(serializers.ModelSerializer):
    # customeruser = CustomerUserSerializer(many=False)
    # productuserview = ProductUserViewedSerializer(many=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'user_type', 'first_name']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data