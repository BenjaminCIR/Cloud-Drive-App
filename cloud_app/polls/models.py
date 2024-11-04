from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    storage_used = models.BigIntegerField(default=0)

    def __str__(self):
        return self.user.username
    

class Folder(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

def validate_file_size(file):
    max_file_size = 40 * 1024 * 1024  # 40 MB en octets
    if file.size > max_file_size:
        raise ValidationError(f"File size must not exceed 40 MB.")
    
class File(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/', validators=[validate_file_size])
    size = models.PositiveIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class FileStatistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_count = models.IntegerField(default=0)
    image_count = models.IntegerField(default=0)
    video_count = models.IntegerField(default=0)
    other_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)