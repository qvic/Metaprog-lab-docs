import os
from collections import deque
from pydoc import html

from page.template import FileTemplate, TemplateRegistry
from util.util import DocumentedFile, FileTreeNode, DocumentedMethod, DocumentedClass, DocumentedInterface, \
    DocumentedEnum
from distutils import dir_util


class PageGenerator:
    DIR = 'html'

    templates = TemplateRegistry()

    @staticmethod
    def copy_resources():
        dir_util.copy_tree('templates/static', os.path.join(PageGenerator.DIR, 'static'))

    @staticmethod
    def create_file(tree: FileTreeNode, documented_file: DocumentedFile):
        html_file_path = os.path.join(PageGenerator.DIR, documented_file.file_path + '.html')
        os.makedirs(os.path.dirname(html_file_path), exist_ok=True)

        with open(html_file_path, 'w') as file:
            rendered_classes_list = []
            for c in documented_file.classes:
                rendered_classes_list.append(PageGenerator._render_class_like_object(c, documented_file))

            rendered_package_structure = PageGenerator._render_tree(tree, documented_file,
                                                                    PageGenerator.templates.get('list_package'),
                                                                    PageGenerator.templates.get('list_item'))

            file.write(
                PageGenerator.templates.get('root').render(
                    rel_path_bootstrap=os.path.relpath('static/css/bootstrap.css',
                                                       os.path.dirname(documented_file.file_path)),
                    rel_path_stylesheet=os.path.relpath('static/css/styles.css',
                                                        os.path.dirname(documented_file.file_path)),
                    package_structure=rendered_package_structure,
                    file_path=documented_file.file_path,
                    package_name=documented_file.package,
                    classes=''.join(rendered_classes_list)))

    @staticmethod
    def _render_class_like_object(obj, documented_file) -> str:
        if isinstance(obj, DocumentedClass):
            return PageGenerator._render_class(obj, documented_file)

        elif isinstance(obj, DocumentedEnum):
            return PageGenerator._render_enum(obj, documented_file)

        elif isinstance(obj, DocumentedInterface):
            return PageGenerator._render_interface(obj, documented_file)

    @staticmethod
    def _render_methods(methods) -> str:
        return ''.join(PageGenerator.templates.get('method').render(
            name=m.name,
            return_type=html.escape(m.return_type),
            args='<br>'.join(html.escape(' '.join(arg)) for arg in m.args),
            annotations=' '.join(m.annotations),
            access_modifier=m.access_modifier,
            modifiers=' '.join(html.escape(modifier) for modifier in m.modifiers),
            throws=', '.join(m.throws),
            post_args=m.post_args,
            docs=m.docs) for m in methods)

    @staticmethod
    def _render_properties(properties) -> str:
        return ''.join(PageGenerator.templates.get('property').render(
            name=p.name,
            type=html.escape(p.type),
            annotations=' '.join(p.annotations),
            access_modifier=p.access_modifier,
            modifiers=' '.join(html.escape(modifier) for modifier in p.modifiers),
            docs=p.docs) for p in properties)

    @staticmethod
    def _render_class(c: DocumentedClass, documented_file: DocumentedFile) -> str:

        # todo extract this
        impl_list = []
        for v in c.implements_list:
            import_path = documented_file.get_doc_import_path(v)
            a_class = 'disabled' if import_path is None else ''
            if import_path is None:
                import_path = ''
            impl_list.append('<a class="{0}" href="{1}">{2}</a>'.format(a_class, import_path, v))
        rendered_impl_list = ', '.join(impl_list)

        path = documented_file.get_doc_import_path(c.extends)

        rendered_methods = PageGenerator._render_methods(c.methods)
        rendered_properties = PageGenerator._render_properties(c.properties)

        return PageGenerator.templates.get('class').render(name=html.escape(c.name),
                                                           docs=c.docs,
                                                           extends='<a class="{0}" href="{1}">{2}</a>'.format(
                                                               'disabled' if path is None else '', path, c.extends),
                                                           impl_list=rendered_impl_list,
                                                           inner_classes=''.join(
                                                               PageGenerator._render_class_like_object(ic,
                                                                                                       documented_file)
                                                               for ic in c.inner_classes),
                                                           methods=rendered_methods,
                                                           properties=rendered_properties)

    @staticmethod
    def _render_enum(c: DocumentedEnum, documented_file: DocumentedFile) -> str:

        impl_list = []
        for v in c.implements_list:
            import_path = documented_file.get_doc_import_path(v)
            a_class = 'disabled' if import_path is None else ''
            if import_path is None:
                import_path = ''
            impl_list.append('<a class="{0}" href="{1}">{2}</a>'.format(a_class, import_path, v))
        rendered_impl_list = ', '.join(impl_list)

        rendered_methods = PageGenerator._render_methods(c.methods)
        rendered_properties = PageGenerator._render_properties(c.properties)

        return PageGenerator.templates.get('enum').render(name=html.escape(c.name),
                                                          docs=c.docs,
                                                          impl_list=rendered_impl_list,
                                                          inner_classes=''.join(
                                                              PageGenerator._render_class_like_object(ic,
                                                                                                      documented_file)
                                                              for ic in c.inner_classes),
                                                          methods=rendered_methods,
                                                          values=' '.join(c.values),
                                                          properties=rendered_properties)

    @staticmethod
    def _render_interface(c: DocumentedInterface, documented_file: DocumentedFile) -> str:

        extends_list = []
        for v in c.extends_list:
            import_path = documented_file.get_doc_import_path(v)
            a_class = 'disabled' if import_path is None else ''
            if import_path is None:
                import_path = ''
            extends_list.append('<a class="{0}" href="{1}">{2}</a>'.format(a_class, import_path, v))
        rendered_extends_list = ', '.join(extends_list)

        rendered_methods = PageGenerator._render_methods(c.methods)

        return PageGenerator.templates.get('interface').render(name=html.escape(c.name),
                                                               docs=c.docs,
                                                               extends_list=rendered_extends_list,
                                                               inner_classes=''.join(
                                                                   PageGenerator._render_class_like_object(ic,
                                                                                                           documented_file)
                                                                   for ic in c.inner_classes),
                                                               methods=rendered_methods)

    @staticmethod
    def _render_tree(tree: FileTreeNode, current_file: DocumentedFile, package_template: FileTemplate,
                     item_template: FileTemplate) -> str:
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
