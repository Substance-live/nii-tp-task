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


def process_directory(directory: str, db_manager: DatabaseManager = None,
                     translation_strategy: str = 'translit',
                     splitting_strategy: str = 'none',
                     verbose: bool = False,
                     output_xml: bool = False,
                     xml_dir: str = None):
    """
    Обрабатывает все .txt файлы в директории
    
    Args:
        directory: Путь к директории с .txt файлами
        db_manager: Менеджер БД (опционально)
        translation_strategy: Стратегия перевода ('translit' или 'llm')
        splitting_strategy: Стратегия разделения ('none' или 'llm')
        verbose: Выводить подробную информацию
        output_xml: Сохранять XML в файлы
        xml_dir: Директория для сохранения XML файлов (если None, сохранять рядом с исходными файлами)
    """
    # Создаем таблицы, если БД используется
    if db_manager:
        db_manager.create_tables()
    
    # Находим все .txt файлы
    txt_files = find_txt_files(directory)
    
    if not txt_files:
        print(f"В директории {directory} не найдено .txt файлов")
        return
    
    print(f"Найдено {len(txt_files)} .txt файл(ов)")
    
    # Подключаемся к БД только если она используется
    session = None
    if db_manager:
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
                        # Сохраняем русское и английское название параметра в БД (если БД используется)
                        if db_manager and session:
                            db_manager.get_or_create_parameter(
                                session, sub_param, sub_translated
                            )
                        english_params.append(sub_translated)
                
                # Создаем XML
                xml_content = create_xml_document(document_name, english_params)
                
                # Сохраняем в БД (если используется)
                if db_manager and session:
                    filename = os.path.basename(txt_file)
                    db_manager.save_document(session, filename, document_name, xml_content)
                    if verbose:
                        print(f"  ✓ Сохранено в БД")
                
                # Сохраняем в XML файл (если указан флаг)
                if output_xml:
                    save_xml_to_file(txt_file, xml_content, xml_dir, verbose)
                
                processed += 1
                
                if verbose and not output_xml and not db_manager:
                    print(f"  ✓ Успешно обработан")
                elif verbose and (output_xml or db_manager):
                    if output_xml and db_manager:
                        print(f"  ✓ Сохранено в БД и в XML файл")
                    elif output_xml:
                        print(f"  ✓ Сохранено в XML файл")
                
            except Exception as e:
                errors += 1
                print(f"  ✗ Ошибка при обработке {txt_file}: {e}", file=sys.stderr)
                if verbose:
                    import traceback
                    traceback.print_exc()
        
        print(f"\nОбработано: {processed}, Ошибок: {errors}")
        
    finally:
        if session:
            session.close()


def save_xml_to_file(txt_file: str, xml_content: str, xml_dir: str = None, verbose: bool = False):
    """
    Сохраняет XML содержимое в файл
    
    Args:
        txt_file: Путь к исходному .txt файлу
        xml_content: XML содержимое для сохранения
        xml_dir: Директория для сохранения XML (если None, рядом с исходным файлом)
        verbose: Выводить подробную информацию
    """
    # Определяем имя выходного XML файла
    txt_basename = os.path.basename(txt_file)
    xml_basename = os.path.splitext(txt_basename)[0] + '.xml'
    
    # Определяем директорию для сохранения
    if xml_dir:
        # Используем указанную директорию
        if not os.path.exists(xml_dir):
            os.makedirs(xml_dir, exist_ok=True)
            if verbose:
                print(f"  Создана директория: {xml_dir}")
        xml_file_path = os.path.join(xml_dir, xml_basename)
    else:
        # Сохраняем рядом с исходным файлом
        txt_dir = os.path.dirname(txt_file)
        xml_file_path = os.path.join(txt_dir, xml_basename)
    
    # Сохраняем XML в файл
    try:
        with open(xml_file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        if verbose:
            print(f"  Сохранен XML файл: {xml_file_path}")
    except Exception as e:
        print(f"  ✗ Ошибка при сохранении XML файла {xml_file_path}: {e}", file=sys.stderr)
        raise


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
  %(prog)s /path/to/documents --output-xml
  %(prog)s /path/to/documents --output-xml --xml-dir /path/to/output
  %(prog)s /path/to/documents --output-xml --no-db
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
    
    parser.add_argument(
        '--output-xml',
        action='store_true',
        help='Сохранять XML в файлы (работает без БД)'
    )
    
    parser.add_argument(
        '--xml-dir',
        type=str,
        default=None,
        help='Директория для сохранения XML файлов (по умолчанию: рядом с исходными .txt файлами)'
    )
    
    parser.add_argument(
        '--no-db',
        action='store_true',
        help='Не использовать БД (только сохранять в XML файлы)'
    )
    
    args = parser.parse_args()
    
    # Проверяем существование директории
    if not os.path.isdir(args.directory):
        print(f"Ошибка: директория '{args.directory}' не существует", file=sys.stderr)
        sys.exit(1)
    
    # Проверяем, нужно ли использовать БД
    # По умолчанию используем БД, если не указан --no-db
    use_db = not args.no_db
    
    db_manager = None
    if use_db:
        # Получаем URL БД
        db_url = args.db_url or get_database_url()
        
        if args.verbose:
            print(f"Подключение к БД: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        
        # Создаем менеджер БД
        try:
            db_manager = DatabaseManager(db_url)
        except Exception as e:
            if args.output_xml:
                # Если БД недоступна, но указан --output-xml, продолжаем работу без БД
                print(f"Предупреждение: не удалось подключиться к БД: {e}", file=sys.stderr)
                print(f"Продолжаем работу только с сохранением в XML файлы", file=sys.stderr)
                db_manager = None
            else:
                print(f"Ошибка подключения к БД: {e}", file=sys.stderr)
                sys.exit(1)
    
    if args.verbose:
        print(f"Стратегия перевода: {args.translation_strategy}")
        print(f"Стратегия разделения: {args.splitting_strategy}")
        if args.output_xml:
            if xml_dir := args.xml_dir:
                print(f"Директория для XML: {xml_dir}")
            else:
                print(f"XML файлы будут сохранены рядом с исходными .txt файлами")
        if db_manager:
            print(f"Использование БД: Да")
        else:
            print(f"Использование БД: Нет")
    
    # Обрабатываем директорию
    try:
        process_directory(
            args.directory,
            db_manager,
            args.translation_strategy,
            args.splitting_strategy,
            args.verbose,
            args.output_xml,
            args.xml_dir
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

