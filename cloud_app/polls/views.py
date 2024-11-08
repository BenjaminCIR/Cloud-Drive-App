from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from .forms import FileUploadForm, RenameFileForm
from django.http import FileResponse, Http404, HttpResponse
from .models import File
import os
import shutil
from datetime import datetime
from collections import defaultdict


# View for the signup page
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'polls/signup.html', {'form': form})


# Forbid access to the home page if the user is not authenticated
@login_required


# View for the home page
def home(request):
    base_path = os.path.join('uploads', request.user.username)
    current_path = request.GET.get('path', '')

    previous_path = request.GET.get('previous_path', '')

    full_path = os.path.join(base_path, current_path)
    
    folders = []
    files = []
    
    # Folder and files navigation
    if os.path.exists(full_path):
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                folders.append({'name': item, 'path': os.path.join(current_path, item)})
            else:
                print(os.path.join(item_path, item))
                files.append({
                    'name': item,
                    'path': item_path,
                    'size': os.path.getsize(item_path),
                    'upload_date': datetime.fromtimestamp(os.path.getctime(item_path)).strftime('%Y-%m-%d %H:%M:%S'),
                })

    return render(request, 'polls/home.html', {
        'folders': folders,
        'files': files,
        'current_path': current_path,
        'previous_path': previous_path,
    })


# View to upload a file
def upload_file(request):
    current_path = request.GET.get('path', '')
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file_size = request.FILES['upload'].size
            max_file_size = 40 * 1024 * 1024  # 40 Mo limit per file
            max_user_storage = 100 * 1024 * 1024  # 100 Mo limit per user

            user_storage_usage = File.objects.filter(user=request.user).aggregate(total_size=Sum('size'))['total_size'] or 0

            # Limit the file size and the user storage
            if new_file_size > max_file_size:
                form.add_error('upload', "File size exceeds the max size of 40 Mo.")
            elif user_storage_usage + new_file_size > max_user_storage:
                form.add_error('upload', "The total storage limit of 100 Mo is exceeded.")
            else:
                # Create the complete path of the file
                base_path = os.path.join('uploads', request.user.username, current_path)

                # Create the folder if necessary
                if current_path and not os.path.exists(base_path):
                    os.makedirs(base_path)

                # Save the file in the current folder
                file_instance = form.save(commit=False)
                file_instance.user = request.user
                file_instance.size = new_file_size
                file_instance.upload.name = os.path.join(current_path, file_instance.upload.name)
                file_instance.save()
                return redirect(f'/polls/?path={current_path}')
    else:
        form = FileUploadForm()

    return render(request, 'polls/', {'form': form})


# View to delete a file
def delete_file(request):
    current_path = request.GET.get('current_path', '')
    file_path = request.GET.get('path')
    
    # Delete the file if it exists
    if file_path:
        full_path = file_path

        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"File deleted : {full_path}")
        else:
            print(f"No files found at this location : {full_path}")
    
    return redirect(f'/polls/?path={current_path}')


# View to rename a file
def rename_file(request):
    file_path = request.GET.get('path')
    current_path = request.GET.get('current_path', '')
    
    # Check if the file path exists
    if not file_path:
        return redirect(f'/polls/?path={current_path}')
    
    old_name = os.path.basename(file_path)

    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        # Rename the file if a new name is provided
        if new_name:
            old_file_path = file_path
            new_file_path = os.path.join('uploads', request.user.username, current_path, new_name)
            if os.path.exists(old_file_path):
                # Rename the file by replacing the file path name
                os.rename(old_file_path, new_file_path)
                print(f"File renamed from {old_file_path} to {new_file_path}")
            else:
                print(f"File does not exist : {old_file_path}")

            return redirect(f'/polls/?path={current_path}')
    
    return render(request, 'polls/rename_file.html', {
        'file_path': file_path,
        'current_path': current_path,
        'old_name': old_name
    })


# View to move a file
def move_file(request):
    if request.method == "POST":
        file_path = request.POST.get('path')
        target_folder = request.POST.get('target_folder')
        
        # Check the file path and the target folder (cannot be undefined)
        if not file_path or target_folder==None:
            return HttpResponse("Missing parameters", status=400)

        current_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
        target_folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads', request.user.username, target_folder)

        # Check if the source and destination files exist
        if not os.path.exists(current_file_path):
            return HttpResponse("File not found", status=404)
        if not os.path.isdir(target_folder_path):
            return HttpResponse("Destination directory not found", status=404)

        # Move the file to the target folder
        shutil.move(current_file_path, os.path.join(target_folder_path, os.path.basename(file_path)))
        return redirect(f'/polls/?path={target_folder}')
    else:
        return HttpResponse("Unauthorized method", status=405)


# View to show the statistics
def statistics(request):
    files_path = os.path.join(settings.MEDIA_ROOT, 'uploads', request.user.username)
    
    # Initialisation des compteurs et données
    file_count_by_type = defaultdict(int)
    storage_usage_by_month = defaultdict(int)

    # File path
    for root, _, files in os.walk(files_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Files count by type
            file_ext = os.path.splitext(file_name)[1].lower()
            file_count_by_type[file_ext] += 1

            # Storage usage by month
            file_size = os.path.getsize(file_path)
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            month_key = creation_time.strftime('%Y-%m')
            storage_usage_by_month[month_key] += file_size

    file_count_by_type = dict(file_count_by_type)
    storage_usage_by_month = dict(sorted(storage_usage_by_month.items()))

    return render(request, 'polls/statistics.html', {
        'file_count_by_type': file_count_by_type,
        'storage_usage_by_month': storage_usage_by_month,
    })


# View to create a folder
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        # Create the folder if the name is provided
        if folder_name:
            base_path = 'uploads/'
            user_folder_path = os.path.join(base_path, request.user.username, folder_name)
            # Create the folder if it does not exist
            if not os.path.exists(user_folder_path):
                os.makedirs(user_folder_path)
            else:
                pass

        return redirect('home')

    return render(request, 'home.html')


# View to delete a folder
def delete_folder(request):
    folder_path = request.GET.get('path')
    print(f"Folder path : {folder_path}")
    current_path = request.GET.get('current_path', '')
    base_path = os.path.join('uploads', request.user.username, folder_path)
    
    # Delete the folder if it exists
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
        print(f"Folder and all its contents deleted : {base_path}")
    else:
        print(f"Folder not found at this location : {base_path}")

    return redirect(f'/polls/?path={current_path}')


# View to rename a folder
def rename_folder(request):
    folder_path = request.GET.get('path')
    current_path = request.GET.get('current_path', '')
    
    # Check if the folder path exists
    if not folder_path:
        return redirect(f'/polls/?path={current_path}')
    
    old_name = os.path.basename(folder_path)

    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        # Rename the folder if a new name is provided
        if new_name:
            old_folder_path = os.path.join('uploads', request.user.username, folder_path)
            new_folder_path = os.path.join('uploads', request.user.username, current_path, new_name)
            # Rename the file by replacing the file path name
            if os.path.exists(old_folder_path):
                os.rename(old_folder_path, new_folder_path)
                print(f"Folder renamed from {old_folder_path} to {new_folder_path}")
            else:
                print(f"The folder does not exist : {old_folder_path}")

            return redirect(f'/polls/?path={current_path}')
    
    return render(request, 'polls/rename_folder.html', {
        'folder_path': folder_path,
        'current_path': current_path,
        'old_name': old_name
    })


# View to move a folder
def move_folder(request):
    if request.method == "POST":
        folder_path = request.POST.get('path')
        folder_path = os.path.join('uploads', request.user.username, folder_path)
        target_folder = request.POST.get('target_folder')
        target_folder = os.path.join('uploads', request.user.username, target_folder)

        # Check the file path and the target folder (cannot be undefined)
        if not folder_path or target_folder==None:
            return HttpResponse("Missing parameters", status=400)

        current_folder_path = os.path.join(settings.MEDIA_ROOT, folder_path)
        target_folder_path = os.path.join(settings.MEDIA_ROOT, target_folder)

        # Check if the source and destination files exist
        if not os.path.isdir(current_folder_path):
            return HttpResponse("Source folder not found ", status=404)
        
        if not os.path.isdir(target_folder_path):
            return HttpResponse("Destination directory not found", status=404)

        # Move the file to the target folder
        try:
            shutil.move(current_folder_path, os.path.join(target_folder_path, os.path.basename(folder_path)))
            # Redirect to target folder after move
            redirect_target = (target_folder.split('\\'))[len((target_folder.split('\\'))) - 1]
            return redirect(f'/polls/?path={redirect_target}')
        except Exception as e:
            return HttpResponse(f"Erreur lors du déplacement du dossier: {str(e)}", status=500)
    
    else:
        return HttpResponse("Unauthorized method", status=405)
    

# View to choose a folder
def choose_folder(request):
    move_type = request.GET.get('type')
    file_path = request.GET.get('file_path')
    folder_path = request.GET.get('folder_path')

    # Check the move type and the file path
    if move_type == 'file' and file_path:
        parent_path = os.path.dirname(file_path).split('\\')
        parent_folder_name = parent_path[len(parent_path) - 1]
        file_name = os.path.basename(file_path)
        base_path = os.path.join('uploads', request.user.username)
        folders = []

        # Browse available folders
        for root, dirs, _ in os.walk(base_path):
            for d in dirs:
                if(d != parent_folder_name):
                    target_folder_path = os.path.join(root, d)
                    relative_folder_path = os.path.relpath(target_folder_path, base_path)
                    folders.append({'name': d, 'path': relative_folder_path})

        return render(request, 'polls/choose_folder.html', {
            'path': file_path,
            'name': file_name,
            'folders': folders,
            'move_type': move_type,
            'url': 'move_file'
        })

    # Check the move type and the folder path
    if move_type == 'folder' and folder_path:
        parent_path = os.path.dirname(folder_path).split('\\')
        parent_folder_name = parent_path[len(parent_path) - 1]
        folder_name = os.path.basename(folder_path)
        base_path = os.path.join('uploads', request.user.username)
        folders = []

        # Browse available folders
        for root, dirs, _ in os.walk(base_path):
            for d in dirs:
                if(d != folder_name and d != parent_folder_name):
                    target_folder_path = os.path.join(root, d)
                    relative_folder_path = os.path.relpath(target_folder_path, base_path)
                    folders.append({'name': d, 'path': relative_folder_path})

        return render(request, 'polls/choose_folder.html', {
            'path': folder_path,
            'name': folder_name,
            'folders': folders,
            'move_type': move_type,
            'url': 'move_folder'
        })
    
    return HttpResponse("Paramètres incorrects", status=400)