import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Optional, Dict, List

import peewee as pw
from playhouse.shortcuts import model_to_dict

from backend.tools.string_template import StringTemplate
from backend.tools.utils import get_subsequences
from setting.setting_reader import setting


def create_db_connection():
    return pw.SqliteDatabase(setting.root_path / "data/data.db")


db = create_db_connection()


class ArrayField(pw.TextField):
    """A field that stores a list as a semi-colon separated string in the database."""

    def __init__(self, seperator=";", element_type_converter=str, **kwargs):
        self.seperator = seperator
        self.element_type_converter = element_type_converter
        super().__init__(**kwargs)

    def db_value(self, value):
        if isinstance(value, Sequence) and not isinstance(value, str):
            value = self.seperator.join((str(x) for x in value))
        if not isinstance(value, str):
            raise TypeError(f"value must be a string or a sequence of strings, not {type(value)}")
        return value

    def python_value(self, value):
        if isinstance(value, str):
            return [self.element_type_converter(x) for x in value.split(self.seperator)]
        return value


class ModelWithTags:
    def _preprocess_tags(self, tags):
        if isinstance(tags, Sequence) and not isinstance(tags, str):
            tags = ",".join(tags)
        if not isinstance(tags, str):
            raise TypeError(f"tags must be a string or a sequence of strings, not {type(tags)}")
        return tags


class Prompt(pw.Model, ModelWithTags):
    """
    Note: when we update the content of a prompt instance and call prompt.save(), the identifier_positions field is updated.
        However, when we use Prompt.update(xxx).where(xxx).execute(), the identifier_positions field is not updated.
    """

    role = pw.TextField(choices=[("user", "user"), ("system", "system")], default="user")
    content = pw.TextField(index=True)
    tags = ArrayField(index=True, null=True)  # semi-colon separated string in the database, but list in python
    identifier_positions = pw.TextField(null=True)  # start1,end1;start2,end2;...;startN,endN

    id = pw.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = pw.DateTimeField(default=datetime.now)
    updated_at = pw.DateTimeField(default=datetime.now)

    class Meta:
        database = db

    @property
    def identifier_positions_list(self):
        return [[int(p) for p in pos.split(",")] for pos in self.identifier_positions.split(";")]

    @property
    def content_template(self) -> StringTemplate:
        return StringTemplate(self.content)

    def save(self, **kwargs):
        self.identifier_positions = self.calculate_identifier_positions_string()
        return super().save(**kwargs)

    @staticmethod
    def _filter_out_matches_in_identifieres(matches: List["Prompt"], search_str: str) -> List["Prompt"]:
        result = []
        for match in matches:
            if not match.identifier_positions:
                result.append(match)
                continue
            for subcontent in get_subsequences(seq=match.content, exclude_indices=match.identifier_positions_list):
                if search_str in subcontent:
                    result.append(match)
                    break
        return result

    @classmethod
    def search_by_string(cls, search_str: str) -> List[Dict]:
        content_matches: List["Prompt"] = list(cls.select().where(cls.content.contains(search_str)))
        content_matches = cls._filter_out_matches_in_identifieres(content_matches, search_str)
        tag_matches: List["Prompt"] = list(cls.select().where(cls.tags.contains(search_str)))
        tag_matches = cls._filter_out_matches_in_identifieres(tag_matches, search_str)
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

    def calculate_identifier_positions_string(self):
        """Identifiers in the content should not be matched against the search query.
        Therefore, identifier positions, including ${}, are stored in the database and used to filter out.

        identifier_positions is a string of the form "start1,end1;start2,end2;...;startN,endN"
        """
        template = StringTemplate(self.content)
        if not template.is_template:
            return ""
        id_positions = template.get_identifiers_with_positions()
        return ";".join(f"{id_pos[1]},{id_pos[2]}" for id_pos in id_positions)

    def to_dict(self):
        return model_to_dict(self)


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
