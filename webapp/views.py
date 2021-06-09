from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import logout, login
from rest_framework_simplejwt.models import TokenUser
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CategorySerializer, CustomUserSerializer, \
    ProductSerializer, CustomerOrderSerializer, ProductUserViewedSerializer, \
    MyTokenObtainPairSerializer, OrderProductSerializer, \
    CustomerUserSerializer,CategoryMiniSerializer
from .models import Categories, CustomUser, Products, CustomerOrder, \
    ProductUserViewed, CustomerUser, OrderProduct
from rest_framework.response import Response
from django.db import Error
from django.shortcuts import get_object_or_404
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

class CategoryMiniViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoryMiniSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


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
    pagination_class.page_size = 20
    # paginator = PageNumberPagination(PageNumberPagination, 20)

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
        if self.action == 'create' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny,]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


    def create(self, request, *args, **kwargs):
        data = (request.data)
        try:
            userNew=CustomUser.objects.create_user(username=data[
                'username'], password=data['password'], first_name=data[
                'username'])
            if data.get('user_type') is not None:
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


    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = CustomUser.objects.get(username=pk)
        instance.save()
        serializer = CustomUserSerializer(instance)
        response = {'message': 'đăng nhập thành công', 'data':
            serializer.data}
        return Response(response, status=status.HTTP_200_OK)

class AnonymousUserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'list':
            permission_classes = [permissions.AllowAny,]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


    def create(self, request, *args, **kwargs):
        data = (request.data)
        user = request.user
        if (user.is_authenticated):
            userNew = CustomUser.objects.get(id=user.id)
            print(userNew.id)
            try:
                try:
                    CustomerUserNew = get_object_or_404(CustomerUser,
                                        auth_user_id=userNew,
                                        name=data['customeruser']['name'],
                                        phone=data['customeruser']['phone'])
                    print(CustomerUserNew)
                except:
                    CustomerUserNew = CustomerUser.objects.create(
                        auth_user_id=userNew)
                    if data.get('customeruser') is not None:
                        CustomerUserNew.phone = data['customeruser']['phone']
                        CustomerUserNew.address = data['customeruser']['address']
                        CustomerUserNew.name = data['customeruser']['name']
                    else:
                        CustomerUserNew.phone = ''
                        CustomerUserNew.address = ''
                    CustomerUserNew.save()
            except:
                response = {'message': 'chưa tạo được customer', 'data': []}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                userNew=CustomUser.objects.create_user(username=data[
                    'username'], password=data['password'], first_name='Anonymous')
                if data.get('user_type') is not None:
                    userNew.user_type = data['user_type']
                else:
                    userNew.user_type = '4'
                userNew.save()
            except:
                response = {'message': 'chưa tạo được user', 'data': []}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            try:
                CustomerUserNew = CustomerUser.objects.create(auth_user_id=userNew)
                if data.get('customeruser') is not None:
                    CustomerUserNew.phone = data['customeruser']['phone']
                    CustomerUserNew.address = data['customeruser']['address']
                    CustomerUserNew.name = data['customeruser']['name']
                else:
                    CustomerUserNew.phone = ''
                    CustomerUserNew.address = ''
                CustomerUserNew.save()
            except:
                response = {'message': 'chưa tạo được customer', 'data': []}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        try:
            CustomerOrderNew = CustomerOrder.objects.create(
                customer_id=CustomerUserNew, code=data['codeOrder'])
            CustomerOrderNew.save()
        except:
            response = {'message': 'chưa tạo được customer order', 'data': []}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        try:
            carts = data['carts']
            for cart in carts:
                product = Products.objects.get(id=cart['product']['id'])
                OrderProduct.objects.create(
                    customorder_id=CustomerOrderNew, product_id=product,
                    quantity = cart['quantity'],
                    price = cart['product']['price'],
                    color = cart['color'],
                    size = cart['size'])
            if CustomerOrderNew:
                serializer = CustomerOrderSerializer(CustomerOrderNew, many=False)
                response = {'message': 'tạo đơn hàng thành công', 'data':
                    serializer.data}
                return Response(response, status=status.HTTP_201_CREATED)

        except :
            response = {'message': 'chưa tạo được đơn hàng', 'data': []}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, pk=None, *args, **kwargs):
        user = request.user
        try:
            instance = CustomUser.objects.get(id=user.id)

            CustomerUserNew = CustomerUser.objects.filter(
                auth_user_id=instance).latest('id')
            print(CustomerUserNew)
            CustomerUserNew.save()
            serializer = CustomerUserSerializer(CustomerUserNew)
            response = {'message': 'lấy thông tin customer', 'data':
                serializer.data}
            return Response(response, status=status.HTTP_200_OK)
        except :
            response = {'message': 'chưa có tài khoản', 'data': []}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class CustomerOrderViewset(viewsets.ModelViewSet):
    queryset = CustomerOrder.objects.all()
    serializer_class = CustomerOrderSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class OrderProductView(viewsets.ModelViewSet):
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductSerializer

class getUserView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def list(self, request, *args, **kwargs):
        header = request.headers
        user = getattr(request, 'user', None)
        bool = hasattr(request, 'user')
        user1 = getattr(user, 'is_authenticated', True)
        print(f'user {user.id} - bool {bool} -header {header}' )
        if not user1:
            print(user)
        else:
            print('k có user')
        # auth = JWTAuthentication()
        # auth.authenticate(request)


        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)
