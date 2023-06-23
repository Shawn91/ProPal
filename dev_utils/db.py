from backend.tools.database import Prompt


class DBPopulator:
    def populate_prompts(self):
        for role, prompt, tags in [
            ("system", "Please explain like I am a five year old", ["teacher"]),
            ("system", "请用一种简单的方式解释", ["教师", "teacher"]),
            ("user", "The following questions are about ${var}", ["ask about"]),
            ("user", "下面的问题是关于${about}", ["询问", "ask about"]),
        ]:
            Prompt(role=role, content=prompt, tags=tags).save(force_insert=True)


if __name__ == "__main__":
    DBPopulator().populate_prompts()
    # p = Prompt.get(Prompt.content == "下面的问题是关于${about}")
    # p.content = "下面的问题是关于${var}"
    # p.save()
    # Prompt.update(content="下面的问题是关于${about}").where(Prompt.content == "下面的问题是关于${var}").execute()
