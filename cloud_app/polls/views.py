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

# Create your views here.
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

@login_required
def home(request):
#     if request.user.is_authenticated:
#         user_files = File.objects.filter(user=request.user)
#     else:
#         user_files = None
#     return render(request, 'polls/home.html', {'user_files': user_files})

    base_path = os.path.join('uploads', request.user.username)
    current_path = request.GET.get('path', '')

    previous_path = request.GET.get('previous_path', '')

    full_path = os.path.join(base_path, current_path)
    
    folders = []
    files = []
    
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

    print(f"Current path: {current_path}")
    return render(request, 'polls/home.html', {
        'folders': folders,
        'files': files,
        'current_path': current_path,
        'previous_path': previous_path,
    })


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


def upload_file(request):
    # if request.method == 'POST':
    #     form = FileUploadForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         new_file_size = request.FILES['upload'].size
    #         max_file_size = 40 * 1024 * 1024  # 40 Mo limit per file
    #         max_user_storage = 100 * 1024 * 1024  # 100 Mo limit per user
            
    #         user_storage_usage = File.objects.filter(user=request.user).aggregate(total_size=Sum('size'))['total_size'] or 0
            
    #         if new_file_size > max_file_size:
    #             form.add_error('upload', "Le fichier dépasse la taille maximale de 40 Mo.")
    #         elif user_storage_usage + new_file_size > max_user_storage:
    #             form.add_error('upload', "La limite totale de stockage de 100 Mo est dépassée.")
    #         else:
    #             file_instance = form.save(commit=False)
    #             file_instance.user = request.user
    #             file_instance.name = request.FILES['upload'].name
    #             file_instance.size = new_file_size
    #             file_instance.save()
    #             return redirect('./../success')
    # else:
    #     form = FileUploadForm()

    # return render(request, 'polls/upload.html', {'form': form})

    current_path = request.GET.get('path', '')

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
                # Créer le chemin complet du dossier courant
                base_path = os.path.join('uploads', request.user.username, current_path)

                # Créer le dossier si nécessaire
                if current_path and not os.path.exists(base_path):
                    os.makedirs(base_path)

                # Sauvegarder le fichier dans le dossier courant
                file_instance = form.save(commit=False)
                file_instance.user = request.user
                file_instance.size = new_file_size

                # Définir le chemin d'enregistrement du fichier
                file_instance.upload.name = os.path.join(current_path, file_instance.upload.name)  # Associe le fichier au dossier courant

                file_instance.save()
                return redirect(f'/polls/?path={current_path}')
    else:
        form = FileUploadForm()

    return render(request, 'polls/', {'form': form})

def delete_file(request):
    # file_to_delete = get_object_or_404(File, id=file_id, user=request.user)
    
    # if file_to_delete.upload:
    #     file_to_delete.upload.delete(save=False)
    
    # file_to_delete.delete()
    
    # return redirect('./../../')
    current_path = request.GET.get('current_path', '')
    file_path = request.GET.get('path')
    
    if file_path:
        full_path = file_path

        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"Fichier supprimé : {full_path}")
        else:
            print(f"Aucun fichier trouvé à cet emplacement : {full_path}")
    
    return redirect(f'/polls/?path={current_path}')


def rename_file(request):
    # current_path = request.GET.get('current_path', '')
    # file_to_rename = get_object_or_404(File, id=file_id, user=request.user)

    # if request.method == 'POST':
    #     form = RenameFileForm(request.POST, instance=file_to_rename)
    #     if form.is_valid():
    #         new_name = form.cleaned_data['name']
    #         original_file_path = file_to_rename.upload.path
    #         new_file_path = os.path.join(settings.MEDIA_ROOT, f'uploads/{file_to_rename.user.username}/{new_name}')

    #         if original_file_path != new_file_path:
    #             os.rename(original_file_path, new_file_path)

    #         file_to_rename.name = new_name 
    #         file_to_rename.save()

    #         return redirect(f'/polls/?path={current_path}')
    # else:
    #     form = RenameFileForm(instance=file_to_rename)

    # return render(request, 'polls/rename_file.html', {'form': form, 'file': file_to_rename})

    file_path = request.GET.get('path')
    current_path = request.GET.get('current_path', '')  # Dossier actuel où se trouve le fichier
    
    if not file_path:
        return redirect(f'/polls/?path={current_path}')
    
    old_name = os.path.basename(file_path)

    # Si la requête est en POST, traiter le changement de nom
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        if new_name:
            old_file_path = file_path
            new_file_path = os.path.join('uploads', request.user.username, current_path, new_name)

            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)
                print(f"Fichier renommé de {old_file_path} à {new_file_path}")
            else:
                print(f"Le fichier n'existe pas : {old_file_path}")

            return redirect(f'/polls/?path={current_path}')
    
    return render(request, 'polls/rename_file.html', {
        'file_path': file_path,
        'current_path': current_path,
        'old_name': old_name
    })


def move_file(request):
    if request.method == "POST":
        file_path = request.POST.get('path')
        target_folder = request.POST.get('target_folder')
        print(target_folder)
        print(target_folder)
        print(target_folder)
        print(target_folder)
        
        # Validation des chemins
        if not file_path or target_folder==None:
            return HttpResponse("Paramètres manquants", status=400)

        current_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
        target_folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads', request.user.username, target_folder)

        # Vérifier les chemins
        if not os.path.exists(current_file_path):
            return HttpResponse("Fichier non trouvé", status=404)
        if not os.path.isdir(target_folder_path):
            return HttpResponse("Répertoire de destination introuvable", status=404)

        # Déplacement
        shutil.move(current_file_path, os.path.join(target_folder_path, os.path.basename(file_path)))
        return redirect(f'/polls/?path={target_folder}')
    else:
        return HttpResponse("Méthode non autorisée", status=405)



def statistics(request):
    # Dossier de stockage des fichiers (à adapter selon votre structure)
    storage_dir = os.path.join(settings.BASE_DIR, 'storage_root')
    
    # Initialisation des compteurs et données
    file_count_by_type = defaultdict(int)
    storage_usage_by_month = defaultdict(int)

    # Parcours des fichiers
    for root, _, files in os.walk(storage_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Comptage par type de fichier
            file_ext = os.path.splitext(file_name)[1].lower()  # Récupère l'extension en minuscule
            file_count_by_type[file_ext] += 1

            # Calcul de l'utilisation par mois
            file_size = os.path.getsize(file_path)
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            month_key = creation_time.strftime('%Y-%m')  # Format Année-Mois
            storage_usage_by_month[month_key] += file_size

    # Préparation des données pour le template
    file_count_by_type = dict(file_count_by_type)
    storage_usage_by_month = dict(sorted(storage_usage_by_month.items()))  # Trie par date

    return render(request, 'polls/statistics.html', {
        'file_count_by_type': file_count_by_type,
        'storage_usage_by_month': storage_usage_by_month,
    })


def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        if folder_name:
            base_path = 'uploads/'
            user_folder_path = os.path.join(base_path, request.user.username, folder_name)

            if not os.path.exists(user_folder_path):
                os.makedirs(user_folder_path)
            else:
                pass

        return redirect('home')

    return render(request, 'home.html')


def delete_folder(request):
    folder_path = request.GET.get('path')
    print(f"Chemin du dossier : {folder_path}")
    current_path = request.GET.get('current_path', '')
    base_path = os.path.join('uploads', request.user.username, folder_path)
    
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
        print(f"Dossier et tout son contenu supprimé : {base_path}")
    else:
        print(f"Aucun dossier trouvé à cet emplacement : {base_path}")

    return redirect(f'/polls/?path={current_path}')



def rename_folder(request):
    # Récupérer les paramètres 'path' (le chemin du dossier à renommer) et 'current_path' (dossier actuel)
    folder_path = request.GET.get('path')
    current_path = request.GET.get('current_path', '')  # Dossier actuel où se trouve le dossier
    
    if not folder_path:
        return redirect(f'/polls/?path={current_path}')
    
    old_name = os.path.basename(folder_path)

    # Si la requête est en POST, traiter le changement de nom
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        if new_name:
            old_folder_path = os.path.join('uploads', request.user.username, folder_path)
            new_folder_path = os.path.join('uploads', request.user.username, current_path, new_name)

            if os.path.exists(old_folder_path):
                os.rename(old_folder_path, new_folder_path)
                print(f"Dossier renommé de {old_folder_path} à {new_folder_path}")
            else:
                print(f"Le dossier n'existe pas : {old_folder_path}")

            return redirect(f'/polls/?path={current_path}')
    
    return render(request, 'polls/rename_folder.html', {
        'folder_path': folder_path,
        'current_path': current_path,
        'old_name': old_name
    })



def move_folder(request):
    if request.method == "POST":
        folder_path = request.POST.get('path')  # Le chemin du dossier à déplacer
        folder_path = os.path.join('uploads', request.user.username, folder_path)
        target_folder = request.POST.get('target_folder')  # Le répertoire de destination
        target_folder = os.path.join('uploads', request.user.username, target_folder)
        
        print(f"Chemin du fichier : {folder_path}")
        print(f"Répertoire de destination : {target_folder}")

        if not folder_path or target_folder==None:
            return HttpResponse("Paramètres manquants", status=400)

        # Obtenez le chemin absolu des dossiers
        current_folder_path = os.path.join(settings.MEDIA_ROOT, folder_path)
        print(f"Chemin du dossier actuel : {current_folder_path}")
        target_folder_path = os.path.join(settings.MEDIA_ROOT, target_folder)
        print(f"Chemin du répertoire de destination : {target_folder_path}")

        # Vérifier si le dossier source existe
        if not os.path.isdir(current_folder_path):
            return HttpResponse("Dossier source non trouvé", status=404)

        # Vérifier si le répertoire cible existe
        if not os.path.isdir(target_folder_path):
            return HttpResponse("Répertoire de destination introuvable", status=404)

        # Déplacer le dossier et son contenu
        try:
            shutil.move(current_folder_path, os.path.join(target_folder_path, os.path.basename(folder_path)))
            redirect_target = (target_folder.split('\\'))[len((target_folder.split('\\'))) - 1]
            return redirect(f'/polls/?path={redirect_target}')  # Rediriger vers le dossier cible après le déplacement
        except Exception as e:
            return HttpResponse(f"Erreur lors du déplacement du dossier: {str(e)}", status=500)
    
    else:
        return HttpResponse("Méthode non autorisée", status=405)
    

def choose_folder(request):
    move_type = request.GET.get('type')
    file_path = request.GET.get('file_path')
    folder_path = request.GET.get('folder_path')

    print(f"Chemin du fichier : {file_path}")
    print(f"Chemin du dossier : {folder_path}")

    if move_type == 'file' and file_path:
        parent_path = os.path.dirname(file_path).split('\\')
        parent_folder_name = parent_path[len(parent_path) - 1]
        print(f"Nom du dossier parent : {parent_folder_name}")
        file_name = os.path.basename(file_path)
        base_path = os.path.join('uploads', request.user.username)
        folders = []

        # Parcours des dossiers disponibles
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

    if move_type == 'folder' and folder_path:
        parent_path = os.path.dirname(folder_path).split('\\')
        parent_folder_name = parent_path[len(parent_path) - 1]
        print(f"Nom du dossier parent : {parent_folder_name}")
        folder_name = os.path.basename(folder_path)
        print(f"Nom du dossier : {folder_name}")
        print(f"Chemin du dossier : {folder_path}")
        base_path = os.path.join('uploads', request.user.username)
        folders = []

        # Parcours des dossiers disponibles
        for root, dirs, _ in os.walk(base_path):
            for d in dirs:
                print(f"1" + base_path)
                print(f"oui" + os.path.basename(folder_path))
                print(f"2" + os.path.join(base_path, os.path.basename(folder_path)))
                #is_child = target_folder_path.startswith(os.path.join(base_path, os.path.basename(folder_path)))
                #print(f"Chemin du dossier cible : {is_child}")
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