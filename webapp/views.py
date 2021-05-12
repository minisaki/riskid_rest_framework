from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from .serializers import CategorySerializer, CustomUserSerializer, \
    ProductSerializer, CustomerOrderSerializer, ProductUserViewedSerializer
from .models import Categories, CustomUser, Products, CustomerOrder, \
    ProductUserViewed
from rest_framework.response import Response
from django.db import Error
from rest_framework_simplejwt.authentication import JWTAuthentication, JWTTokenUserAuthentication
from rest_framework import permissions
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend, RangeFilter
import django_filters
# # Create your views here.
#
#
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['$title', '$url_slug', '$products__product_name', '$products__url_slug']
    ordering_fields = ['products__product_discount_price',]


class Filter(django_filters.FilterSet):
    # product_discount_price = RangeFilter()

    class Meta:
        model = Products
        fields = {
            'category_id': ['exact'],
            'is_freeship': ['exact'],
            'product_discount_price': ['lte', 'gte'],
        }

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['$product_name', '$product_description', '$url_slug']
    ordering_fields = ['product_discount_price','update_at', 'view_product']
    # filterset_fields = ['category_id', 'is_freeship', 'product_discount_price']
    filterset_class  = Filter

    def retrieve(self, request, pk=None, *args, **kwargs):
        print(pk)
        instance = Products.objects.get(url_slug=pk)
        instance.view_product += 1
        instance.save()
        serializer = ProductSerializer(instance)
        return Response(serializer.data)

    # def filter_queryset(self, queryset):
    #     if self.request.query_params.get('product_discount_price', None):
    #         queryset = super(ProductViewSet, self).filter_queryset(
    #             self.get_queryset())
    #         return queryset
    #
    #     else:
    #         queryset = self.get_queryset()
    #     return queryset

    # def get_queryset(self):
    #     queryset = Products.objects.all()
    #     category_id = self.request.query_params.get('category_id')
    #     is_freeship = self.request.query_params.get('is_freeship')
    #     if category_id is not None and is_freeship is not None:
    #         queryset = queryset.filter(category_id=category_id, is_freeship=is_freeship)
    #     if category_id is not None and is_freeship is None:
    #         queryset = queryset.filter(category_id=category_id)
    #     if category_id is None and is_freeship is not None:
    #         queryset = queryset.filter(is_freeship=is_freeship)
    #     return queryset

class ProductUserViewViewset(viewsets.ModelViewSet):
    queryset = ProductUserViewed.objects.all()
    serializer_class = ProductUserViewedSerializer

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = ProductUserViewed.objects.filter(customuser_id=user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        products = []
        for pu in queryset:
            product = Products.objects.get(id=pu.id)
            products.append(product)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class CustomUserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny,]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


    def create(self, request, *args, **kwargs):
        data = (request.data)

        try:
            userNew=CustomUser.objects.create_user(username=data[
                'username'], password=data['password'])
            if data['user_type'] is not None:
                userNew.user_type = data['user_type']
            else:
                userNew.user_type = '4'
            userNew.save()
            if userNew:
                serializer = CustomUserSerializer(userNew, many=False)
                response = {'message': 'tạo user thành công', 'data':
                    serializer.data}
                return Response(response, status=status.HTTP_201_CREATED)
        except ValueError as e:
            response = {'message': "username không đuwọc trống", 'data': []}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Error as d:
            print(d)
            response = {'message': 'username đã tồn tại', 'data': []}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class CustomerOrderViewset(viewsets.ModelViewSet):
    queryset = CustomerOrder.objects.all()
    serializer_class = CustomerOrderSerializer