
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CustomUserViewset, ProductViewSet, \
    CustomerOrderViewset, ProductUserViewViewset
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
#
#
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'user', CustomUserViewset)
router.register(r'order', CustomerOrderViewset)
router.register(r'view', ProductUserViewViewset)
urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]