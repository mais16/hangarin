from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Hangarin Admin"
admin.site.site_title = "Hangarin"
admin.site.index_title = "To-Do Manager Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls')),
]
