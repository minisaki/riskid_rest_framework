from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from io import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from decimal import *
# Create your models here.
class CustomUser(AbstractUser):
    user_type_choice = (
        ('1', 'Admin'),
        ('2', 'Staff'),
        ('3', 'Merchant'),
        ('4', 'Customer')
    )
    user_type=models.CharField(max_length=255, choices=user_type_choice,
                               default='4')

    class Meta:
        ordering = ('id',)
        verbose_name = ('Người Dùng')
        verbose_name_plural = ('Người Dùng')

class AdminUser(models.Model):
    profile_pic=models.FileField(default='', upload_to='uploads/user')
    auth_user_id=models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='adminuser')
    created_at=models.DateTimeField(auto_now_add=True)

class StaffUser(models.Model):
    profile_pic=models.FileField(default='', upload_to='uploads/user')
    auth_user_id = models.OneToOneField(CustomUser, on_delete=models.CASCADE,
                                     related_name='staffuser')
    created_at=models.DateTimeField(auto_now_add=True)

class MerchantUser(models.Model):
    profile_pic=models.FileField(default='', upload_to='uploads/user')
    auth_user_id = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='merchantuser')
    company_name=models.CharField(max_length=255)
    gst_details=models.CharField(max_length=255)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.auth_user_id.username

class CustomerUser(models.Model):
    profile_pic = models.FileField(default='', upload_to='uploads/user')
    auth_user_id = models.OneToOneField(CustomUser, on_delete=models.CASCADE,
                                     related_name='customeruser')
    created_at=models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=150, default='')
    phone = models.CharField(max_length=11, default='', blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Categories(models.Model):
    id=models.AutoField(primary_key=True)
    title=models.CharField(max_length=255)
    url_slug=models.CharField(max_length=255, blank=True, unique=True)
    thumbnail=models.FileField(blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


    def save(self, *args, **kwargs):
        if not  self.url_slug:
            self.url_slug = slugify(self.title)
        super(Categories, self).save(*args, **kwargs)

    class Meta:
        verbose_name = ('Danh mục sản phẩm')
        verbose_name_plural = ('Danh mục sản phẩm')
        # abstract = True

class Products(models.Model):
    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
        ('Color', 'Color'),
        ('Size-Color', 'Size-Color'),
    )

    id=models.AutoField(primary_key=True)
    product_name=models.CharField(max_length=255)
    category_id=models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='products')
    url_slug = models.CharField(max_length=255, unique=True, null=True,
                                blank=True)
    brand=models.CharField(max_length=255)
    image = models.ImageField(upload_to='uploads/images/', null=True)
    product_max_price=models.IntegerField(default=0)
    product_discount_price=models.IntegerField(default=0)
    product_description=models.TextField()
    product_long_description=models.TextField()
    added_by_merchant=models.ForeignKey(MerchantUser,
                                        on_delete=models.CASCADE,
                                        blank=True, null=True)
    is_stock_total=models.IntegerField(default=1)
    view_product = models.IntegerField(default=0, blank=True)
    variant = models.CharField(max_length=10, choices=VARIANTS, default='None')
    is_active=models.BooleanField(default=True)
    is_freeship=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        if not  self.url_slug:
            self.url_slug = slugify(self.product_name)
        super(Products, self).save(*args, **kwargs)

    class Meta:
        verbose_name = ('Sản phẩm')
        verbose_name_plural = ('Sản phẩm')

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.url_slug})


    def get_per_product_discount_price(self):
        result = round((self.product_discount_price/self.product_max_price
                        )*100)
        return 100 - result


class ProductMedia(models.Model):
    id = models.AutoField(primary_key=True)
    title=models.CharField(max_length=50, blank=True)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE,
                                   related_name='product_media')
    media_type_choice=(('1','Image'),('2','Video'))
    media_type=models.CharField(max_length=255, choices=media_type_choice)
    media_content = models.FileField(upload_to='uploads/media/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class ProductUserViewed(models.Model):
    customuser_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='productuserview')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE,
                                   related_name='product')
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_id.product_name

class ProductTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    transaction_type_choice=((1,'BUY'),(2,'SELL'))
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    transaction_product_count=models.IntegerField(default=1)
    transaction_type=models.CharField(choices=transaction_type_choice, max_length=255)
    transaction_description=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductDetails(models.CharField):
    id=models.AutoField(primary_key=True)
    product_id=models.ForeignKey(Products, on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    title_details=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class ProductAbout(models.CharField):
    id=models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class ProductTags(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class ProductQuestions(models.Model):
    id=models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    user_id = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    question=models.TextField()
    answer=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class ProductReviews(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    user_id = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    review_image=models.FileField()
    rating = models.CharField(default='5', max_length=10)
    review=models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class ProductReviewVoting(models.Model):
    id = models.AutoField(primary_key=True)
    product_review_id = models.ForeignKey(ProductReviews,
                                          on_delete=models.CASCADE)
    user_voting_id = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class ProductVarientColor(models.Model):
    id=models.AutoField(primary_key=True)
    title=models.CharField(max_length=255)
    code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProductVarientSize(models.Model):
    id=models.AutoField(primary_key=True)
    title=models.CharField(max_length=255)
    code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProductVarientItems(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    product_id=models.ForeignKey(Products, on_delete=models.CASCADE,
                                 related_name='product_varients')
    color = models.ForeignKey(ProductVarientColor, on_delete=models.CASCADE, blank=True,
                              null=True)
    size = models.ForeignKey(ProductVarientSize, on_delete=models.CASCADE, blank=True,
                             null=True)
    image_id = models.IntegerField(blank=True, null=True, default=0)

    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CustomerOrder(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(default='', max_length=50)
    customer_id=models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='customerorder')
    purchase_price=models.CharField(max_length=255)
    coupon_code=models.CharField(max_length=255)
    discount_amt=models.CharField(max_length=255)
    product_status=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_code_order()

    def get_total_cost(self):
        return sum(item.getAmount() for item in self.orderproduct.all())

    def get_discount(self):
        if self.coupon_code:
            discount = (int(self.discount_amt) / Decimal(100) * Decimal(
                self.get_total_cost()))
            return discount
        return Decimal(0)

    def get_ship(self):
        if self.get_total_cost() >= 0:
            return 0
        return Decimal(30)

    def get_total_price_after_discount(self):
        print(self.get_discount())
        return self.get_total_cost() + self.get_ship() - self.get_discount()

    def convert_number_to_word(self):
        pass

    def get_code_order(self):
        return f'{self.code}_00{self.id}'

class OrderProduct(models.Model):
    customorder_id=models.ForeignKey(CustomerOrder, on_delete=models.CASCADE,
                                     related_name='orderproduct')
    product_id=models.ForeignKey(Products, on_delete=models.DO_NOTHING)
    color=models.CharField(max_length=255)
    size=models.CharField(max_length=255)
    product_status=models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.FloatField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_id.product_name

    def getAmount(self):
        return self.price * self.quantity

class OrderDeliveryStatus(models.Model):
    id = models.AutoField(primary_key=True)
    order_id=models.ForeignKey(CustomerOrder, on_delete=models.CASCADE)
    status=models.CharField(max_length=255)
    status_message=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type==1:
            AdminUser.objects.create(auth_user_id=instance)
        if instance.user_type==2:
            StaffUser.objects.create(auth_user_id=instance)
        if instance.user_type==3:
            MerchantUser.objects.create(auth_user_id=instance,
                                        company_name="", gst_details="",
                                        address='')
        if instance.user_type==4:
            CustomerUser.objects.create(auth_user_id=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type==1:
        instance.adminuser.save()
    if instance.user_type==2:
        instance.staffuser.save()
    if instance.user_type==3:
        instance.merchantuser.save()
    if instance.user_type==4:
        instance.customeruser.save()