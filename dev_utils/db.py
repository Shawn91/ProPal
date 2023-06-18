
from backend.tools.database import Prompt


class DBPopulator:
    def populate_prompts(self):
        for prompt,tags in [
            ('Please explain like I am a five year old', ['teacher']),
            ('请用一种简单的方式解释', ['教师', 'teacher']),
            ('The following questions are about {}', ['ask about']),
            ('下面的问题是关于{}', ['询问', 'ask about'])
        ]:
            Prompt(template=prompt, raw_tags=tags).save()


if __name__ == "__main__":
    DBPopulator().populate_prompts()