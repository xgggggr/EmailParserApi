from pathlib import Path
import json
from app.logic.email import Email
import logging
logger = logging.getLogger(__name__)

class EmailParsing:
    HEAD_NORMALISER = {"subject":["subject", "tema", "тема"], "who_sent":["from", "ot kogo", "от кого"], "sent_to": ["komu", "to", "кому"]}
    def parse(self, filename:str, content:bytes) -> Email:
        try:
            file_format = Path(filename).suffix.lower().lstrip('.')
            if file_format in ["txt", ""]:
                return self._parse_txt(filename, content)
            elif file_format == "json":
                return self._parse_json(filename, content)
            elif file_format in ["jpeg", "jpg", "png", "gif"]:
                logger.warning(f"Файл '{filename}' является изображением и не может быть прочитан как письмо")
                return self._unreadable(filename, "image")
            elif file_format == "bin":
                logger.warning(f"Файл '{filename}' является бинарным и не может быть прочитан как письмо")
                return self._unreadable(filename, "binary")
            logger.warning(f"У файла '{filename}' неизвестный формат, не может быть прочитан как письмо")
            return self._unreadable(filename, "unknown")
        except Exception as e:
            logger.error(f"Не удалось прочитать файл '{filename}': {e}")
            return self._unreadable(filename, "unknown")
    def _parse_txt(self, filename:str, content:bytes) -> Email: #парсит текстовый файл
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning(f"файл '{filename}' не в кодировке UTF-8")
            return self._unreadable(filename, "txt")
        head, body = self._split_email(text)
        real_format = Path(filename).suffix.lower().lstrip('.') or "noext"
        return Email(filename, real_format, head.get('subject'), head.get('who_sent'), head.get('sent_to'), body,)
    def _split_email(self, content: str) -> tuple[dict[str, str], str]: #разделяет текстовый файл на заголовок и содержание. сам заголовок разделяется на тему, от кого пришло письмо и кому
        content_split = content.splitlines()
        head = []
        headers = {}
        body = []
        split_index = len(content_split)
        for index, i in enumerate(content_split):
            if i.strip() != "":
                head.append(i)
            else:
                split_index = index
                break
        for i in head:
            key, _, value = i.partition(':')
            normalised_key = self._normalize(key.strip().lower())
            if normalised_key:
                headers[normalised_key] = value.strip()
        if not headers:
            return headers, content.strip()
        body = content_split[split_index + 1:]
        return headers, "\n".join(body)
    def _normalize(self, key:str ) -> str | None: #нормализует части заголовков. Например, тема может в письмах помечаться как "tema", "тема", "subject". И метод в таком случае возвращает "subject".
        for true_key, value in self.HEAD_NORMALISER.items():
            if key in value:
                return true_key
        return None
    def _parse_json(self, filename: str, content:bytes) -> Email: #"парсит json файлы
        try:
            data = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Файл '{filename}' содержит некорректный JSON: {e}")
            return self._unreadable(filename, "json")
        return Email(filename, "json", subject=self._as_str(data.get("subject")), who_sent=self._as_str(data.get("from")), text=self._as_str(data.get("body")),)

    def _unreadable(self, filename:str, file_format:str) -> Email: #если файл нечитаем просто возвращает объект email с пометкой о нечитаемости, форматом и остальными пустыми атрибутами
        return Email(filename, file_format, is_readable=False)

    def _as_str(self, value) -> str | None:
        return value if isinstance(value, str) else None
