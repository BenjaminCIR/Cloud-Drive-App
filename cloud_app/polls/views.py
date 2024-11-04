from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from .models import File
import json

# Create your views here.

@login_required
def home(request):
    files = []
    return render(request, 'polls/home.html', {'files': files})


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
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            return render(request, 'polls/success.html')
        else:
            error_message = "Aucun fichier n'a été sélectionné."
            return render(request, 'polls/upload.html', {'error_message': error_message})
    return render(request, 'polls/upload.html')


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