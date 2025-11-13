#!/usr/bin/env python3
"""
CLI приложение для конвертации .txt файлов в XML и сохранения в БД
"""

import argparse
import os
import sys

from parser import parse_txt_file, find_txt_files
from transliteration import translate_with_strategy, split_parameter_with_strategy
from converter import create_xml_document
from database import DatabaseManager, get_database_url


def process_directory(directory: str, db_manager: DatabaseManager,
                     translation_strategy: str = 'translit',
                     splitting_strategy: str = 'none',
                     verbose: bool = False):
    """
    Обрабатывает все .txt файлы в директории
    
    Args:
        directory: Путь к директории с .txt файлами
        db_manager: Менеджер БД
        translation_strategy: Стратегия перевода ('translit' или 'llm')
        splitting_strategy: Стратегия разделения ('none' или 'llm')
        verbose: Выводить подробную информацию
    """
    # Создаем таблицы, если их еще нет
    db_manager.create_tables()
    
    # Находим все .txt файлы
    txt_files = find_txt_files(directory)
    
    if not txt_files:
        print(f"В директории {directory} не найдено .txt файлов")
        return
    
    print(f"Найдено {len(txt_files)} .txt файл(ов)")
    
    session = db_manager.get_session()
    
    try:
        processed = 0
        errors = 0
        
        for txt_file in txt_files:
            try:
                if verbose:
                    print(f"\nОбработка файла: {txt_file}")
                
                # Парсим файл
                document_name, parameters = parse_txt_file(txt_file)
                
                if verbose:
                    print(f"  Название документа: {document_name}")
                    print(f"  Параметров: {len(parameters)}")
                
                # Переводим параметры
                english_params = []
                for param in parameters:
                    # Разделяем параметр при необходимости
                    split_params = split_parameter_with_strategy(param, splitting_strategy)
                    
                    # Для каждого подпараметра переводим и получаем или создаем запись в БД
                    for sub_param in split_params:
                        sub_translated = translate_with_strategy(sub_param, translation_strategy)
                        # Сохраняем русское и английское название параметра в БД
                        db_manager.get_or_create_parameter(
                            session, sub_param, sub_translated
                        )
                        english_params.append(sub_translated)
                
                # Создаем XML
                xml_content = create_xml_document(document_name, english_params)
                
                # Сохраняем в БД
                filename = os.path.basename(txt_file)
                db_manager.save_document(session, filename, document_name, xml_content)
                
                processed += 1
                
                if verbose:
                    print(f"  ✓ Успешно обработан и сохранен в БД")
                
            except Exception as e:
                errors += 1
                print(f"  ✗ Ошибка при обработке {txt_file}: {e}", file=sys.stderr)
                if verbose:
                    import traceback
                    traceback.print_exc()
        
        print(f"\nОбработано: {processed}, Ошибок: {errors}")
        
    finally:
        session.close()


def main():
    """Главная функция CLI приложения"""
    parser = argparse.ArgumentParser(
        description='Конвертация .txt файлов в XML и сохранение в PostgreSQL БД',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s /path/to/documents
  %(prog)s /path/to/documents --translation-strategy llm
  %(prog)s /path/to/documents --translation-strategy translit --splitting-strategy llm
  %(prog)s /path/to/documents --verbose
        """
    )
    
    parser.add_argument(
        'directory',
        type=str,
        help='Путь к директории с .txt файлами'
    )
    
    parser.add_argument(
        '--translation-strategy',
        type=str,
        choices=['translit', 'llm'],
        default='translit',
        help='Стратегия перевода параметров (по умолчанию: translit)'
    )
    
    parser.add_argument(
        '--splitting-strategy',
        type=str,
        choices=['none', 'llm'],
        default='none',
        help='Стратегия разделения длинных параметров (по умолчанию: none)'
    )
    
    parser.add_argument(
        '--db-url',
        type=str,
        default=None,
        help='URL подключения к БД (по умолчанию: из переменных окружения)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Выводить подробную информацию о процессе'
    )
    
    args = parser.parse_args()
    
    # Проверяем существование директории
    if not os.path.isdir(args.directory):
        print(f"Ошибка: директория '{args.directory}' не существует", file=sys.stderr)
        sys.exit(1)
    
    # Получаем URL БД
    db_url = args.db_url or get_database_url()
    
    if args.verbose:
        print(f"Подключение к БД: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        print(f"Стратегия перевода: {args.translation_strategy}")
        print(f"Стратегия разделения: {args.splitting_strategy}")
    
    # Создаем менеджер БД
    try:
        db_manager = DatabaseManager(db_url)
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Обрабатываем директорию
    try:
        process_directory(
            args.directory,
            db_manager,
            args.translation_strategy,
            args.splitting_strategy,
            args.verbose
        )
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Критическая ошибка: {e}", file=sys.stderr)
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

