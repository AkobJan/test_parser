from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .forms import XMLUploadForm
from .models import info
import xml.etree.ElementTree as ET
import os
from django.conf import settings
from django.shortcuts import render

def home(request):
    if request.method == 'POST':
        form = XMLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            return uploaded_file(request.FILES['xml_file'])
    else:
        form = XMLUploadForm()
        
    return render(request, 'upload.html', {'form': form})

def uploaded_file(_):
    try:
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp.xml')
        with open(temp_path, 'wb+') as destination:
            for chunk in _.chunks():
                destination.write(chunk)
        
        # Парсинг XML
        tree = ET.parse(temp_path)
        root = tree.getroot() 
        
        added = 0 
        duplicates = 0  
        
        # Обработка каждого объявления
        for item in root.findall('ad'): 
            data = {
                'title': item.find('title').text,
                'price': item.find('price').text,
                'address': item.find('address').text, 
                'square': item.find('square').text,
                'link': item.find('link').text,
                'date': item.find('date').text,
            }
            
            # Проверка дубликатов
            if not info.objects.filter(link=data['link']).exists() and \
               not info.objects.filter(title=data['title'], address=data['address']).exists():
                info.objects.create(**data)
                added += 1
            else:
                duplicates += 1
        
        os.remove(temp_path)
        
        return JsonResponse({
            'status': 'success',
            'added': added,
            'duplicates': duplicates
        })
    # Обработка ошибок
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)