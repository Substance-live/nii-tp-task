"""
Модуль для работы с базой данных
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Document, Parameter
from typing import Optional
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class DatabaseManager:
    """Класс для управления подключением к БД"""
    
    def __init__(self, database_url: str):
        """
        Args:
            database_url: URL подключения к БД (например, 
                         postgresql://user:password@localhost:5432/dbname)
        """
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Создает все таблицы в БД"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Возвращает новую сессию БД"""
        return self.SessionLocal()
    
    def get_or_create_parameter(self, session: Session, russian_name: str, 
                                 english_name: str) -> Parameter:
        """
        Получает существующий параметр или создает новый
        Поиск выполняется без учета регистра
        
        Args:
            session: Сессия БД
            russian_name: Русское название параметра
            english_name: Английское название параметра
            
        Returns:
            Объект Parameter
        """
        # Поиск без учета регистра (case-insensitive)
        parameter = session.query(Parameter).filter(
            func.lower(Parameter.russian_name) == func.lower(russian_name)
        ).first()
        
        if not parameter:
            parameter = Parameter(
                russian_name=russian_name,
                english_name=english_name
            )
            session.add(parameter)
            session.commit()
            session.refresh(parameter)
        
        return parameter
    
    def save_document(self, session: Session, original_filename: str,
                     document_name: str, xml_content: str) -> Document:
        """
        Сохраняет документ в БД
        
        Args:
            session: Сессия БД
            original_filename: Имя исходного .txt файла
            document_name: Название документа
            xml_content: XML содержимое документа
            
        Returns:
            Объект Document
        """
        document = Document(
            original_filename=original_filename,
            document_name=document_name,
            xml_content=xml_content
        )
        session.add(document)
        session.commit()
        session.refresh(document)
        return document


def get_database_url() -> str:
    """
    Получает URL подключения к БД из переменных окружения
    или использует значения по умолчанию
    """
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'documents_db')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

