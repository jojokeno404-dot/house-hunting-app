from django.contrib import admin
from .models import Apartment, ApartmentImage, TourRequest, Review, Favorite

admin.site.register(Apartment)
admin.site.register(ApartmentImage)
admin.site.register(TourRequest)
admin.site.register(Review)
admin.site.register(Favorite)