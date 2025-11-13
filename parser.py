"""
Модуль для парсинга .txt файлов
"""

import os
import re
from typing import List, Tuple, Optional


def parse_txt_file(file_path: str) -> Tuple[str, List[str]]:
    """
    Парсит .txt файл и извлекает название документа и список параметров
    Использует регулярные выражения для гибкого парсинга различных форматов
    
    Args:
        file_path: Путь к .txt файлу
        
    Returns:
        Кортеж (название документа, список параметров)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        raise ValueError(f"File {file_path} is empty")
    
    lines = content.split('\n')
    
    # Первая непустая строка - название документа
    document_name = None
    for line in lines:
        line = line.strip()
        if line and not re.match(r'^[-•]\s+', line):
            document_name = line
            break
    
    if not document_name:
        raise ValueError(f"Document name not found in {file_path}")
    
    # Ищем параметры с помощью регулярного выражения
    # Поддерживаем различные форматы:
    # - Параметр;
    # - Параметр.
    # • Параметр;
    # • Параметр.
    # и другие варианты
    parameters = []
    # Регулярное выражение для поиска параметров:
    # Начинается с дефиса или маркера списка, затем пробелы, затем текст параметра,
    # который может заканчиваться на точку с запятой или точку
    param_pattern = re.compile(r'^[-•]\s+(.+?)(?:[;.]\s*)?$', re.MULTILINE)
    
    matches = param_pattern.findall(content)
    for match in matches:
        param = match.strip()
        # Убираем точку с запятой и точку в конце, если они остались
        param = re.sub(r'[;.]\s*$', '', param).strip()
        if param:
            parameters.append(param)
    
    # Если регулярное выражение не нашло параметры, пробуем старый способ
    if not parameters:
        for line in lines[1:]:
            line = line.strip()
            # Проверяем, начинается ли строка с дефиса или маркера списка
            if re.match(r'^[-•]\s+', line):
                # Убираем маркер в начале и знаки препинания в конце
                param = re.sub(r'^[-•]\s+', '', line)
                param = re.sub(r'[;.]\s*$', '', param).strip()
                if param:
                    parameters.append(param)
    
    return document_name, parameters


def find_txt_files(directory: str) -> List[str]:
    """
    Находит все .txt файлы в указанной директории
    
    Args:
        directory: Путь к директории
        
    Returns:
        Список путей к .txt файлам
    """
    txt_files = []
    
    if not os.path.isdir(directory):
        raise ValueError(f"Directory {directory} does not exist")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    
    return txt_files

