from django.contrib import admin
from .models import CustomUser, Categories, Products, ProductMedia, \
    ProductVarientItems, MerchantUser, ProductVarientColor, \
    ProductVarientSize, ProductVarientItems, CustomerUser, CustomerOrder, \
    OrderProduct, AdminUser, StaffUser, ProductUserViewed


# # Register your models here.
class CustomerOrderInline(admin.TabularInline):
    model = CustomerOrder
    extra = 1
    readonly_fields = ('id',)
class CustomerUserAdmin(admin.ModelAdmin):
    model = CustomerUser
    list_display = ['id', 'name', 'phone', 'address', 'auth_user_id']
    inlines = [CustomerOrderInline]

class CustomerUserInline(admin.TabularInline):
    model = CustomerUser
    extra = 1

class AdminUserInline(admin.TabularInline):
    model = AdminUser
    extra = 1

class StaffUserInline(admin.TabularInline):
    model = StaffUser
    extra = 1

class MerchantUserInline(admin.TabularInline):
    model = MerchantUser
    extra = 1

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'is_staff']
    inlines = [AdminUserInline, StaffUserInline, MerchantUserInline, CustomerUserInline]
    # if CustomUser.user_type==1:
    #     inlines = [AdminUserInline]
    # if CustomUser.user_type==2:
    #     inlines = [StaffUserInline]
    # if CustomUser.user_type==3:
    #     inlines = [MerchantUserInline]
    # if CustomUser.user_type==4:
    #     inlines = [CustomerUserInline]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MerchantUser)
admin.site.register(CustomerUser, CustomerUserAdmin)
admin.site.register(Categories)

# product

class ProductMediaInline(admin.TabularInline):
     model=ProductMedia
     readonly_fields = ('id',)
     extra = 1
class ProductVarientItemInline(admin.TabularInline):
    model = ProductVarientItems
    readonly_fields = ('id', )
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name','category_id', 'is_active']
    list_filter = ['category_id']
    inlines = [ProductMediaInline, ProductVarientItemInline]

admin.site.register(Products, ProductAdmin)
admin.site.register(ProductVarientColor)
admin.site.register(ProductVarientSize)
admin.site.register(ProductMedia)
admin.site.register(ProductVarientItems)
admin.site.register(ProductUserViewed)

# order
class CustomerOrderAdmin(admin.ModelAdmin):
    model = CustomerOrder
    list_display = ['id', 'code', 'customer_id']
admin.site.register(CustomerOrder, CustomerOrderAdmin)
admin.site.register(OrderProduct)