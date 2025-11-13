"""
Модуль для транслитерации русских параметров в английские
"""

TRANSLIT_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
}


def transliterate(text: str) -> str:
    """
    Транслитерирует русский текст в английский
    
    Args:
        text: Текст на русском языке
        
    Returns:
        Транслитерированный текст на английском
    """
    result = []
    for char in text:
        if char in TRANSLIT_MAP:
            result.append(TRANSLIT_MAP[char])
        elif char.isalnum() or char in ['_', '-', ' ']:
            result.append(char)
        else:
            result.append('_')
    
    return ''.join(result)


def normalize_parameter_name(text: str) -> str:
    """
    Нормализует название параметра:
    - Транслитерирует русский текст
    - Убирает лишние символы
    - Приводит к нижнему регистру
    - Заменяет пробелы на подчеркивания
    - Убирает дефисы в конце (например, после точки с запятой)
    
    Args:
        text: Исходное название параметра (например, "ФИО;")
        
    Returns:
        Нормализованное имя параметра (например, "fio")
    """
    # Убираем точку с запятой и другие знаки препинания в конце
    text = text.rstrip(';.,!?')
    
    # Транслитерируем
    transliterated = transliterate(text.strip())
    
    # Приводим к нижнему регистру
    transliterated = transliterated.lower()
    
    # Заменяем пробелы и дефисы на подчеркивания
    transliterated = transliterated.replace(' ', '_').replace('-', '_')
    
    # Убираем множественные подчеркивания
    while '__' in transliterated:
        transliterated = transliterated.replace('__', '_')
    
    # Убираем подчеркивания в начале и конце
    transliterated = transliterated.strip('_')
    
    return transliterated


def translate_with_strategy(text: str, strategy: str = 'translit'):
    """
    Переводит параметр с использованием выбранной стратегии
    
    Args:
        text: Исходный текст параметра
        strategy: Стратегия перевода ('translit' или 'llm')
        
    Returns:
        Переведенное название параметра
    """
    if strategy == 'translit':
        return normalize_parameter_name(text)
    elif strategy == 'llm':
        # TODO: Реализовать использование LLM для перевода
        # Пока используем транслит как fallback
        return normalize_parameter_name(text)
    else:
        raise ValueError(f"Unknown translation strategy: {strategy}")


def split_parameter_with_strategy(text: str, strategy: str = 'none'):
    """
    Разделяет длинный параметр на несколько подпараметров
    
    Args:
        text: Исходный текст параметра
        strategy: Стратегия разделения ('none' или 'llm')
        
    Returns:
        Список подпараметров (пока возвращает один элемент)
    """
    if strategy == 'none':
        return [text]
    elif strategy == 'llm':
        # TODO: Реализовать использование LLM для разделения параметров
        # Например, "Дата и время: 01.01.2024 12:00" -> ["date", "time"]
        return [text]
    else:
        raise ValueError(f"Unknown splitting strategy: {strategy}")

