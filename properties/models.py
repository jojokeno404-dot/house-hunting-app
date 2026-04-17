from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Apartment(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    description = models.TextField()
    available = models.BooleanField(default=True)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)

    # NEW AGENT FIELDS
    agent_name = models.CharField(max_length=100, blank=True, null=True)
    agent_phone = models.CharField(max_length=15, blank=True, null=True)
    agent_email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='apartments/')


class TourRequest(models.Model):
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.apartment.title}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)

    # M-Pesa fields
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=100, null=True, blank=True)

    status = models.CharField(max_length=20, default="Pending")  # Pending, Completed, Failed

    paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'apartment')  # One payment per user per apartment

    def __str__(self):
        return f"{self.user} - {self.apartment} - {'Paid' if self.paid else 'Pending'}"
from django.db import models

# Create your models here.
class MpesaPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)

    phone_number = models.CharField(max_length=15)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)

    # These two fields were missing
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending")  # Pending, Completed, Failed

    transaction_date = models.DateTimeField(blank=True, null=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'apartment')

    def __str__(self):
        return f"{self.user} - {self.apartment.title} - {'Paid' if self.paid else 'Pending'}"
