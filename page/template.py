import re


class TemplateRegistry:
    pass


class Template:

    def __init__(self, template_path):
        self._template_path = template_path
        with open(template_path, 'r') as file:
            self.text = file.read()
            self.matches = list(re.finditer(r'{{\s*([^\d\W]\w*)\s*}}', self.text))

    def render(self, **kwargs) -> str:
        shift = 0
        text = self.text
        for match in self.matches:
            argument = str(kwargs.get(match.group(1), None))
            text = text[:match.start() + shift] + argument + text[match.end() + shift:]
            shift += len(argument) - match.end() + match.start()
        return text
