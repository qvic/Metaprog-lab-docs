import os
from collections import deque
from pydoc import html

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
                        annotations=m.annotations,
                        access_modifier=m.access_modifier,
                        modifiers=m.modifiers,
                        docs=m.docs)
                    for m in c.methods)

                if isinstance(c, DocumentedClass):
                    # todo separate template

                    impl_list = []
                    for v in c.implements_list:
                        import_path = documented_file.get_doc_import_path(v)
                        a_class = 'disabled' if import_path is None else ''
                        if import_path is None:
                            import_path = ''
                        impl_list.append('<a class="{0}" href="{1}">{2}</a>'.format(a_class, import_path, v))
                    rendered_impl_list = ', '.join(impl_list)

                    path = documented_file.get_doc_import_path(c.extends)
                    rendered_classes_list.append(
                        templates['class'].render(name=html.escape(c.name),
                                                  docs=c.docs,
                                                  extends='<a class="{0}" href="{1}">{2}</a>'.format(
                                                      'disabled' if path is None else '', path, c.extends),
                                                  impl_list=rendered_impl_list,
                                                  methods=rendered_methods))
                elif isinstance(c, DocumentedInterface):
                    extends_list = []
                    for v in c.extends_list:
                        import_path = documented_file.get_doc_import_path(v)
                        a_class = 'disabled' if import_path is None else ''
                        if import_path is None:
                            import_path = ''
                        extends_list.append('<a class="{0}" href="{1}">{2}</a>'.format(a_class, import_path, v))
                    rendered_extends_list = ', '.join(extends_list)

                    rendered_classes_list.append(
                        templates['interface'].render(name=html.escape(c.name),
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
                                                                os.path.join(
                                                                    *documented_file.package.split('.'))) + '.html')

        for child in tree.children:
            result += PageGenerator._render_tree(child, documented_file, package_template, item_template, id=id + 1)

        return package_template.render(name=tree.directory, items=result, id=id)
