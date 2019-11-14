import os
from collections import deque

from page.template import Template
from util.util import DocumentedFile, FileTreeNode, DocumentedMethod, DocumentedClass, DocumentedInterface


class PageGenerator:
    DIR = 'html'

    @staticmethod
    def create_file(tree: FileTreeNode, file_path: str, documented_file: DocumentedFile):
        html_file_path = os.path.join(PageGenerator.DIR, file_path + '.html')
        os.makedirs(os.path.dirname(html_file_path), exist_ok=True)

        with open(html_file_path, 'w') as file:
            main_template = Template('templates/template.html')
            templates = {
                'method': Template('templates/method_template.html'),
                'class': Template('templates/class_template.html'),
                'interface': Template('templates/interface_template.html')
            }

            rendered_classes_list = []
            for c in documented_file.classes:

                rendered_methods = ''.join(
                    templates.get('method').render(
                        name=m.name,
                        return_type=m.return_type,
                        args=m.args,
                        # todo other props
                        docs=m.docs)
                    for m in c.methods)

                if isinstance(c, DocumentedClass):
                    # todo separate template
                    rendered_impl_list = ''.join(
                        '<a href={0}>{1}</a>'.format(documented_file.get_doc_import_path(v), v) for v in
                        c.implements_list)

                    rendered_classes_list.append(
                        templates['class'].render(name=c.name,
                                                  docs=c.docs,
                                                  extends=c.extends,
                                                  extends_full=documented_file.get_doc_import_path(c.extends),
                                                  impl_list=rendered_impl_list,
                                                  methods=rendered_methods))
                elif isinstance(c, DocumentedInterface):
                    # todo separate template
                    rendered_extends_list = ''.join(
                        '<a href={0}>{1}</a>'.format(documented_file.get_doc_import_path(v), v) for v in c.extends_list)

                    rendered_classes_list.append(
                        templates['interface'].render(name=c.name,
                                                      docs=c.docs,
                                                      extends_list=rendered_extends_list,
                                                      methods=rendered_methods))

            rendered_package_structure = PageGenerator._render_tree(tree, documented_file,
                                                                    Template('templates/list_package_template.html'),
                                                                    Template('templates/list_item_template.html'))

            file.write(main_template.render(
                package_structure=rendered_package_structure,
                file_path=file_path,
                package_name=documented_file.package,
                classes=''.join(rendered_classes_list)))

    @staticmethod
    def _render_tree(tree, documented_file, package_template, item_template, id=0):
        result = ''

        for file in tree.files:
            result += item_template.render(name=file.file_path.split('/')[-1].split('.')[0],
                                           href=os.path.relpath(os.path.join(*file.file_path.split('/')[4:]),
                                                                os.path.join(*documented_file.package.split('.'))) + '.html')

        for child in tree.children:
            result += PageGenerator._render_tree(child, documented_file, package_template, item_template, id=id + 1)

        return package_template.render(name=tree.directory, items=result, id=id)
