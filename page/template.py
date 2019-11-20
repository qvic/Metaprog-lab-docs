import re
from abc import ABC


class TemplateRegistry:

    def __init__(self):
        # todo template path
        self.templates = {
            'root': FileTemplate('templates/template.html'),
            'method': FileTemplate('templates/method_template.html'),
            'property': FileTemplate('templates/property_template.html'),
            'class': FileTemplate('templates/class_template.html'),
            'interface': FileTemplate('templates/interface_template.html'),
            'enum': FileTemplate('templates/enum_template.html'),
            'list_package': FileTemplate('templates/list_package_template.html'),
            'list_item': FileTemplate('templates/list_item_template.html'),
        }

    def get(self, obj_name: str) -> 'FileTemplate':
        return self.templates[obj_name]


class TextTemplate:

    def __init__(self, text):
        self.text = text
        self.matches = list(re.finditer(r'{{\s*([^\d\W]\w*)\s*}}', text))

    def render(self, **kwargs) -> str:
        shift = 0
        text = self.text
        for match in self.matches:
            argument = str(kwargs.get(match.group(1), None))
            text = text[:match.start() + shift] + argument + text[match.end() + shift:]
            shift += len(argument) - match.end() + match.start()
        return text


class FileTemplate(TextTemplate):

    def __init__(self, template_path):
        with open(template_path, 'r') as file:
            text = file.read()
        super().__init__(text)
