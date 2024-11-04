from django.contrib import admin
from .models import UserProfile, Folder, File, FileStatistics

# Register your models here.

admin.site.register([UserProfile, Folder, File, FileStatistics])