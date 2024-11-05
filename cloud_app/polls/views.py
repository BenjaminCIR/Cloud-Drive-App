from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from .forms import FileUploadForm
from .models import File
import json

# Create your views here.

@login_required
def home(request):
    files = []
    return render(request, 'polls/home.html', {'files': files})

def success(request):
    return render(request, 'polls/success.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'polls/signup.html', {'form': form})


def upload(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file_size = request.FILES['upload'].size
            max_file_size = 40 * 1024 * 1024  # 40 Mo limit per file
            max_user_storage = 100 * 1024 * 1024  # 100 Mo limit per user
            
            user_storage_usage = File.objects.filter(user=request.user).aggregate(total_size=Sum('size'))['total_size'] or 0
            
            if new_file_size > max_file_size:
                form.add_error('upload', "Le fichier dépasse la taille maximale de 40 Mo.")
            elif user_storage_usage + new_file_size > max_user_storage:
                form.add_error('upload', "La limite totale de stockage de 100 Mo est dépassée.")
            else:
                file_instance = form.save(commit=False)
                file_instance.user = request.user
                file_instance.name = request.FILES['upload'].name
                file_instance.size = new_file_size
                file_instance.save()
                return redirect('./../success')
    else:
        form = FileUploadForm()

    return render(request, 'polls/upload.html', {'form': form})


def statistics(request):
    file_count_by_type = File.objects.values('file').annotate(count=Count('id'))
    file_count_by_type = list(file_count_by_type)

    storage_usage_by_month = (
        File.objects
        .annotate(month=TruncMonth('upload_date'))
        .values('month')
        .annotate(total_size=Sum('size'))
        .order_by('month')
    )
    storage_usage_by_month = list(storage_usage_by_month)

    total_storage_usage = File.objects.aggregate(total_size=Sum('size'))['total_size'] or 0

    context = {
        'file_count_by_type': json.dumps(file_count_by_type),
        'storage_usage_by_month': json.dumps(storage_usage_by_month),
        'total_storage_usage': total_storage_usage,
    }
    return render(request, 'polls/statistics.html', context)