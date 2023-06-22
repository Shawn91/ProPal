from collections.abc import Sequence
from datetime import datetime
from typing import Optional, Dict, List
import uuid

import peewee as pw

from setting.setting_reader import setting


def create_db_connection():
    return pw.SqliteDatabase(setting.root_path / "data/data.db")


db = create_db_connection()


class ModelWithTags:
    def _preprocess_tags(self, tags):
        if isinstance(tags, Sequence) and not isinstance(tags, str):
            tags = ",".join(tags)
        if not isinstance(tags, str):
            raise TypeError(f"tags must be a string or a sequence of strings, not {type(tags)}")
        return tags

    @property
    def tag_list(self):
        return self.tags.split(",")


class Prompt(pw.Model, ModelWithTags):
    content = pw.TextField(index=True)
    tags = pw.TextField(index=True, null=True)  # comma separated

    id = pw.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = pw.DateTimeField(default=datetime.now)
    updated_at = pw.DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def __init__(self, **kwargs):
        tags = self._preprocess_tags(kwargs.pop("tags", []))
        super().__init__(tags=tags, **kwargs)

    def create(self, **kwargs):
        tags = self._preprocess_tags(kwargs.pop("tags", []))
        super().save(tags=tags, **kwargs)

    @classmethod
    def search_by_string(cls, search_str: str) -> List[Dict]:
        content_matches: List["Prompt"] = list(cls.select().where(cls.content.contains(search_str)))
        tag_matches: List["Prompt"] = list(cls.select().where(cls.tags.contains(search_str)))
        matches = []
        for content_match in content_matches:
            match_info = {"match_fields": ["content"], "data": content_match}
            if content_match in tag_matches:
                match_info["match_fields"].append("tag")
                tag_matches.remove(content_match)
            matches.append(match_info)
        for tag_match in tag_matches:
            match_info = {"match_fields": ["tag"], "data": tag_match}
            matches.append(match_info)
        return matches

    def to_dict(self):
        return {
            "content": self.content,
            "tags": self.tag_list,
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ChatMessage(pw.Model):
    ...


class DBManager:
    MODELS = {"prompt": Prompt}

    def __init__(self):
        self._create_tables()

    def _create_tables(self):
        """only create tables once"""
        db.create_tables([Prompt])

    def search_by_string(self, search_str, in_models: Optional[List[str]] = None) -> List[Dict]:
        if in_models is None:
            in_models = []

        result = []
        for model_name, model_class in self.MODELS.items():
            if in_models and model_class not in in_models:
                continue
            result.extend(({"type": model_name, **x} for x in model_class.search_by_string(search_str)))
        return result


db_manager = DBManager()
