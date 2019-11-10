import re


class Template:

    def __init__(self, template_path):
        self.template_path = template_path

    def render(self, **kwargs) -> str:
        with open(self.template_path, 'r') as file:
            text = file.read()
            matches = re.finditer(r'{{\s*([^\d\W]\w*)\s*}}', text)

            shift = 0
            for match in matches:
                argument = str(kwargs.get(match.group(1), None))
                text = text[:match.start() + shift] + argument + text[match.end() + shift:]
                shift += len(argument) - match.end() + match.start()
            return text
