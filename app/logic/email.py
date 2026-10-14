from dataclasses import dataclass
from pathlib import Path
@dataclass
class Email:
    filename: str #имя файла
    format: str #формат(.txt, .jpeg, .json и т.д.)
    subject: str = "" #тема письма
    who_sent: str = "" #отправитель
    sent_to: str = "" #кому отправлен эмейл
    text: str = "" #содержание эмейла
    is_readable: bool = True
