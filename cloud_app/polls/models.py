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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

def validate_file_size(file):
    max_file_size = 40 * 1024 * 1024  # 40 MB en octets
    if file.size > max_file_size:
        raise ValidationError(f"File size must not exceed 40 MB.")
    
def user_directory_path(instance, filename):
    return f'uploads/{instance.user.username}/{filename}'

    
class File(models.Model):
    name = models.CharField(max_length=255)
    upload = models.FileField(upload_to=user_directory_path, validators=[validate_file_size])
    size = models.IntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='files')

    def __str__(self):
        return self.name
    

class FileStatistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_count = models.IntegerField(default=0)
    image_count = models.IntegerField(default=0)
    video_count = models.IntegerField(default=0)
    other_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)