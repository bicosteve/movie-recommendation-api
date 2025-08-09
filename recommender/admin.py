from django.contrib import admin
from .models import Rating


# Register your models here.
class RatingAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "rating"]
    search_fields = ["movie", "rating"]
    list_filter = ["rating"]
    list_per_page = 10


admin.site.register(Rating, RatingAdmin)
