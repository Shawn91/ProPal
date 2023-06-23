from string import Template
from typing import List, Tuple


class StringTemplate(Template):
    """
    When instantiating this class, the template string is checked for the presence of variables.
    Unlike the standard Template, this class only accepts variables in the form of ${name}. $name is not allowed.
    """

    def __init__(self, template: str) -> None:
        super().__init__(template=template)
        self.is_template = self._is_template()

    def get_identifiers(self) -> List[str]:
        """this is copied (with slight modification) from python 3.11 source code"""
        ids = []
        for mo in self.pattern.finditer(self.template):
            if mo.group("named") is not None:
                continue
            named = mo.group("braced")
            if named is not None and named not in ids:
                # add a named group only the first time it appears
                ids.append(named)
            elif named is None and mo.group("invalid") is None and mo.group("escaped") is None:
                # If all the groups are None, there must be
                # another group we're not expecting
                raise ValueError("Unrecognized named group in pattern", self.pattern)
        return ids

    def get_identifiers_with_positions(self) -> List[Tuple[str, int, int]]:
        ids = []
        for mo in self.pattern.finditer(self.template):
            if mo.group("named") is not None:
                continue
            named = mo.group("braced")
            if named is not None and named not in ids:
                # add a named group only the first time it appears
                ids.append((named, mo.start(), mo.end()))
            elif named is None and mo.group("invalid") is None and mo.group("escaped") is None:
                # If all the groups are None, there must be
                # another group we're not expecting
                raise ValueError("Unrecognized named group in pattern", self.pattern)
        return ids

    def _is_template(self) -> bool:
        return len(self.get_identifiers()) > 0


if __name__ == "__main__":
    t = StringTemplate("hello $name")
    print(t.get_identifiers_with_positions())
