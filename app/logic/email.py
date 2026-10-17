from dataclasses import dataclass
from pathlib import Path
@dataclass
class Email:
    filename: str #имя файла
    format: str #формат(.txt, .jpeg, .json и т.д.)
    subject: str | None = None #тема письма
    who_sent: str | None = None #отправитель
    sent_to: str | None = None #кому отправлен эмейл
    text: str | None = None #содержание эмейла
    is_readable: bool = True
