import os

from page.template_engine import Template
from util.util import DocumentedFile


class PageGenerator:
    DIR = 'html'

    @staticmethod
    def create_file(file_path: str, documented_file: DocumentedFile):
        html_file_path = os.path.join(PageGenerator.DIR, file_path + '.html')
        os.makedirs(os.path.dirname(html_file_path), exist_ok=True)

        with open(html_file_path, 'w') as file:
            main_template = Template('templates/template.html')
            class_template = Template('templates/class_template.html')
            method_template = Template('templates/method_template.html')

            rendered_classes = ''.join(class_template.render(name=c.name, docs=c.docs, methods=''.join(
                method_template.render(name=m.name, return_type=m.return_type, args=m.args, docs=m.docs)
                for m in c.methods)) for c in documented_file.classes)
            file.write(main_template.render(file_path=file_path, package_name=documented_file.package,
                                            classes=rendered_classes))
