import xml.etree.ElementTree as ET
from django.db import transaction
import logging
logger = logging.getLogger(__name__)
from avito_parser.test_parser.xml_upload.models import info

def load_xml(file_path: str, batch_size: int = 500) -> None:
    """
    Загружает XML с объявлениями в БД с проверкой дубликатов.

    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()


        announc_to_create = []
        duplicates = 0
        
        for i, ad in enumerate(root.findall('ad')):
            # Проверка дубликатов по ссылке и названию
            if info.objects.filter(
                link=ad.find('link').text,
                title=ad.find('title').text
            ).exists():
                duplicates += 1
                continue
                
            announc_to_create.append(info(
                title=ad.find('title').text,
                link=ad.find('link').text,
                price=ad.find('price').text
            ))
            
            #Сохранение
            if len(announc_to_create) >= batch_size:
                with transaction.atomic():
                    info.objects.bulk_create(announc_to_create)
                announc_to_create = []
        
        
        if announc_to_create:
            with transaction.atomic():
                info.objects.bulk_create(announc_to_create)
        
        logger.info(f"Успешно загружено: {len(announc_to_create)}, дубликатов: {duplicates}")
    
    except ET.ParseError as e:
        logger.error(f"Ошибка парсинга XML: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")