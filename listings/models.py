from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self):
        return self.title

class ApartmentImage(models.Model):
        apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="images")
        image = models.ImageField(upload_to='apartments/')

class TourRequest(models.Model):
            STATUS_CHOICES = [
                ('pending', 'Pending'),
                ('approved', 'Approved'),
                ('rejected', 'Rejected')
            ]

            user = models.ForeignKey(User, on_delete=models.CASCADE)
            apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
            preferred_date = models.DateField()
            message = models.TextField(blank=True)
            status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
            created_at = models.DateTimeField(auto_now_add=True)
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)