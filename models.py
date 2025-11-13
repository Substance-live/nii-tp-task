from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Parameter(Base):
    """Таблица для хранения встреченных параметров"""
    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True)
    russian_name = Column(String(255), unique=True, nullable=False, index=True)
    english_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    """Таблица для хранения документов"""
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    original_filename = Column(String(255), nullable=False)
    document_name = Column(String(255), nullable=False)
    xml_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

