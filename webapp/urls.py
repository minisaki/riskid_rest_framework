
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CustomUserViewset, ProductViewSet, \
    CustomerOrderViewset, ProductUserViewViewset, MyTokenObtainPairView, \
    AnonymousUserViewset,OrderProductView, getUserView, CategoryMiniViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView
)
#
#
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'cate_mini', CategoryMiniViewSet)
router.register(r'products', ProductViewSet)
router.register(r'user', CustomUserViewset)
router.register(r'order', CustomerOrderViewset)
router.register(r'creatOrder', AnonymousUserViewset)
router.register(r'view', ProductUserViewViewset)
router.register(r'orderproduct', OrderProductView)
router.register(r'getuser', getUserView)


urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/custom/', MyTokenObtainPairView.as_view(),
         name='token_custom'),
    path('token/varify/', TokenVerifyView.as_view(), name='token_verify')
]