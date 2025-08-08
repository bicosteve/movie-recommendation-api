from django.contrib import admin
from .models import Movie


# Register your models here.
class MovieAdmin(admin.ModelAdmin):
    list_display = ["tmdb_id", "title", "release_date", "created"]
    search_fields = ["title", "tmdb_id"]
    list_filter = ["release_date"]
    ordering = ["-created"]
    list_per_page = 10


# Register the model along with its admin configuration
admin.site.register(Movie, MovieAdmin)
