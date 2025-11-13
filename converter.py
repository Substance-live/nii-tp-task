"""
Модуль для конвертации данных в XML формат
"""

from typing import List
from xml.etree.ElementTree import Element, tostring
import xml.dom.minidom
import re


def create_xml_document(document_name: str, parameters: List[str]) -> str:
    """
    Создает XML документ из названия документа и списка параметров
    
    Args:
        document_name: Название документа
        parameters: Список нормализованных названий параметров
        
    Returns:
        XML строка в формате:
        <document>
            <param1></param1>
            <param2></param2>
            ...
        </document>
    """
    root = Element('document')
    
    for param in parameters:
        param_elem = Element(param)
        # Устанавливаем пустой текст, чтобы тег был закрыт правильно (не самозакрывающийся)
        param_elem.text = None
        root.append(param_elem)
    
    # Преобразуем в строку с красивым форматированием
    rough_string = tostring(root, encoding='unicode')
    reparsed = xml.dom.minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")
    
    # Убираем первую строку с XML декларацией для более чистого вывода
    lines = pretty_xml.split('\n')
    if lines and lines[0].startswith('<?xml'):
        lines = lines[1:]
    
    # Убираем пустые строки в начале и конце
    result = '\n'.join(lines).strip()
    
    # Заменяем самозакрывающиеся теги на закрывающиеся
    # <tag/> -> <tag></tag>
    # Поддерживаем имена тегов с подчеркиваниями и дефисами
    result = re.sub(r'<([a-zA-Z_][a-zA-Z0-9_-]*)\s*/>', r'<\1></\1>', result)
    
    return result

