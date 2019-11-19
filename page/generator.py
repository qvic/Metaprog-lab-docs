import os
from collections import deque
from pydoc import html

from page.template import Template
from util.util import DocumentedFile, FileTreeNode, DocumentedMethod, DocumentedClass, DocumentedInterface, \
    DocumentedEnum
from distutils import dir_util


class PageGenerator:
    DIR = 'html'

    @staticmethod
    def copy_resources():
        dir_util.copy_tree('templates/static', os.path.join(PageGenerator.DIR, 'static'))

    @staticmethod
    def create_file(tree: FileTreeNode, documented_file: DocumentedFile):
        html_file_path = os.path.join(PageGenerator.DIR, documented_file.file_path + '.html')
        os.makedirs(os.path.dirname(html_file_path), exist_ok=True)

        with open(html_file_path, 'w') as file:
            main_template = Template('templates/template.html')
            templates = {
                'method': Template('templates/method_template.html'),
                'property': Template('templates/property_template.html'),
                'class': Template('templates/class_template.html'),
                'interface': Template('templates/interface_template.html'),
                'enum': Template('templates/enum_template.html'),
            }

            rendered_classes_list = []
            for c in documented_file.classes:

                if isinstance(c, DocumentedClass):
                    # todo separate template
                    rendered_classes_list.append(
                        PageGenerator._render_class(c, documented_file,
                                                    PageGenerator._render_methods(c, templates['method']),
                                                    PageGenerator._render_properties(c, templates['property']),
                                                    templates['class'], templates['method'], templates['property']))

                elif isinstance(c, DocumentedEnum):

                    rendered_classes_list.append(
                        PageGenerator._render_enum(c, documented_file,
                                                   PageGenerator._render_methods(c, templates['method']),
                                                   PageGenerator._render_properties(c, templates['property']),
                                                   templates['enum'], templates['method'], templates['property']))

                elif isinstance(c, DocumentedInterface):
                    rendered_classes_list.append(
                        PageGenerator._render_interface(c, documented_file,
                                                        PageGenerator._render_methods(c, templates['method']),
                                                        templates['class'], templates['method']))

            rendered_package_structure = PageGenerator._render_tree(tree, documented_file,
                                                                    Template('templates/list_package_template.html'),
                                                                    Template('templates/list_item_template.html'))

            file.write(
                main_template.render(
                    rel_path_bootstrap=os.path.relpath('static/css/bootstrap.css',
                                                       os.path.dirname(documented_file.file_path)),
                    rel_path_stylesheet=os.path.relpath('static/css/styles.css',
                                                        os.path.dirname(documented_file.file_path)),
                    package_structure=rendered_package_structure,
                    file_path=documented_file.file_path,
                    package_name=documented_file.package,
                    classes=''.join(rendered_classes_list)))

    @staticmethod
    def _render_methods(c, template: Template) -> str:
        return ''.join(template.render(
            name=m.name,
            return_type=html.escape(m.return_type),
            args='<br>'.join(html.escape(' '.join(arg)) for arg in m.args),
            annotations=' '.join(m.annotations),
            access_modifier=m.access_modifier,
            modifiers=' '.join(html.escape(modifier) for modifier in m.modifiers),
            docs=m.docs) for m in c.methods)

    @staticmethod
    def _render_properties(c, template: Template) -> str:
        return ''.join(template.render(
            name=m.name,
            type=html.escape(m.type),
            annotations=' '.join(m.annotations),
            access_modifier=m.access_modifier,
            modifiers=' '.join(html.escape(modifier) for modifier in m.modifiers),
            docs=m.docs) for m in c.properties)

    @staticmethod
    def _render_class(c: DocumentedClass, documented_file: DocumentedFile,
                      rendered_methods: str,
                      rendered_properties: str,
                      template: Template, method_template: Template, property_template: Template) -> str:
        impl_list = []
        for v in c.implements_list:
            import_path = documented_file.get_doc_import_path(v)
            a_class = 'disabled' if import_path is None else ''
            if import_path is None:
                import_path = ''
            impl_list.append('<a class="{0}" href="{1}">{2}</a>'.format(a_class, import_path, v))
        rendered_impl_list = ', '.join(impl_list)

        path = documented_file.get_doc_import_path(c.extends)
        return template.render(name=html.escape(c.name),
                               docs=c.docs,
                               extends='<a class="{0}" href="{1}">{2}</a>'.format(
                                   'disabled' if path is None else '', path, c.extends),
                               impl_list=rendered_impl_list,
                               # todo can be inner interface in class
                               inner_classes=''.join(PageGenerator._render_class(ic,
                                                                                 documented_file,
                                                                                 PageGenerator._render_methods(ic,
                                                                                                               method_template),
                                                                                 PageGenerator._render_properties(ic,
                                                                                                                  property_template),
                                                                                 template, method_template,
                                                                                 property_template)
                                                     for ic in c.inner_classes),
                               methods=rendered_methods,
                               properties=rendered_properties)

    @staticmethod
    def _render_enum(c: DocumentedEnum, documented_file: DocumentedFile,
                     rendered_methods: str,
                     rendered_properties: str,
                     template: Template, method_template: Template, property_template: Template) -> str:

        impl_list = []
        for v in c.implements_list:
            import_path = documented_file.get_doc_import_path(v)
            a_class = 'disabled' if import_path is None else ''
            if import_path is None:
                import_path = ''
            impl_list.append('<a class="{0}" href="{1}">{2}</a>'.format(a_class, import_path, v))
        rendered_impl_list = ', '.join(impl_list)

        path = documented_file.get_doc_import_path(c.extends)
        return template.render(name=html.escape(c.name),
                               docs=c.docs,
                               impl_list=rendered_impl_list,
                               inner_classes=None,
                               methods=rendered_methods,
                               values=' '.join(c.values),
                               properties=rendered_properties)

    @staticmethod
    def _render_interface(c: DocumentedInterface, documented_file: DocumentedFile, rendered_methods: str,
                          template: Template, method_template: Template) -> str:
        extends_list = []
        for v in c.extends_list:
            import_path = documented_file.get_doc_import_path(v)
            a_class = 'disabled' if import_path is None else ''
            if import_path is None:
                import_path = ''
            extends_list.append('<a class="{0}" href="{1}">{2}</a>'.format(a_class, import_path, v))
        rendered_extends_list = ', '.join(extends_list)

        return template.render(name=html.escape(c.name),
                               docs=c.docs,
                               extends_list=rendered_extends_list,
                               methods=rendered_methods)

    @staticmethod
    def _render_tree(tree: FileTreeNode, current_file: DocumentedFile, package_template: Template,
                     item_template: Template) -> str:
        result = ''

        for file in tree.files:
            node_class = 'text-secondary'
            if file is current_file:
                node_class = 'text-primary'

            result += item_template.render(node_class=node_class,
                                           name=file.get_file_name(),
                                           href=os.path.relpath(
                                               os.path.join(*file.file_path.split('/')[4:]),
                                               os.path.join(*current_file.package.split('.'))) + '.html')

        for child in tree.children:
            result += PageGenerator._render_tree(child, current_file, package_template, item_template)

        return package_template.render(name=tree.directory, items=result)
