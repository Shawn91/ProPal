from collections.abc import Sequence

import peewee as pw

from setting.setting_reader import setting


db = pw.SqliteDatabase(setting.root_path / 'data/data.db')


class Prompt(pw.Model):
    class Meta:
        database = db

    def __init__(self, **kwargs):
        tags = kwargs.pop('tags', [])
        if isinstance(tags, Sequence) and not isinstance(tags, str):
            tags = ','.join(tags)
        super().__init__(tags=tags, **kwargs)    

    template = pw.TextField(index=True)
    tags = pw.TextField(index=True)  # comma separated

    @property
    def 



class DBManager:
    def __init__(self):
        self._create_tables()
    
    def _create_tables(self):
        db.create_tables([Prompt])


db_manager = DBManager()