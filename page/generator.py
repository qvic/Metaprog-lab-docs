import collections
import os
import re
import time
from distutils import dir_util
from pydoc import html
from typing import Optional, List

from page.template import FileTemplate, TemplateRegistry
from util.util import DocumentedFile, FileTreeNode, DocumentedClass, DocumentedInterface, \
    DocumentedEnum


class PageGenerator:
    DIR = 'html'

    templates = TemplateRegistry()

    @staticmethod
    def copy_resources():
        dir_util.copy_tree('templates/static', os.path.join(PageGenerator.DIR, 'static'))

    @staticmethod
    def create_file(tree: FileTreeNode, documented_file: DocumentedFile, file_list: List[DocumentedFile]):
        html_file_path = os.path.join(PageGenerator.DIR, documented_file.file_path + '.html')
        os.makedirs(os.path.dirname(html_file_path), exist_ok=True)

        with open(html_file_path, 'w') as file:
            rendered_classes_list = []
            for c in documented_file.classes:
                rendered_classes_list.append(PageGenerator._render_class_like_object(c, documented_file, file_list))

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
                    file_doc=PageGenerator.render_doc_string(documented_file.file_doc, documented_file, file_list),
                    package_name=documented_file.package or '',
                    index_page_path=os.path.relpath('index.html',
                                                    os.path.dirname(documented_file.file_path)),
                    classes=''.join(rendered_classes_list)))

    @staticmethod
    def _render_class_like_object(obj, documented_file: DocumentedFile, file_list: List[DocumentedFile]) -> str:
        if isinstance(obj, DocumentedClass):
            return PageGenerator._render_class(obj, documented_file, file_list)

        elif isinstance(obj, DocumentedEnum):
            return PageGenerator._render_enum(obj, documented_file, file_list)

        elif isinstance(obj, DocumentedInterface):
            return PageGenerator._render_interface(obj, documented_file, file_list)

    @staticmethod
    def _render_methods(methods, documented_file: DocumentedFile, file_list: List[DocumentedFile]) -> str:
        return ''.join(PageGenerator.templates.get('method').render(
            name=m.name,
            return_type=html.escape(m.return_type),
            args='<br>'.join(html.escape(' '.join(arg)) for arg in m.args),
            annotations=' '.join(m.annotations),
            access_modifier=m.access_modifier,
            modifiers=' '.join(html.escape(modifier) for modifier in m.modifiers),
            throws=', '.join(m.throws),
            docs=PageGenerator.render_doc_string(m.docs, documented_file, file_list)) for m in methods)

    @staticmethod
    def _render_properties(properties, documented_file: DocumentedFile, file_list: List[DocumentedFile]) -> str:
        return ''.join(PageGenerator.templates.get('property').render(
            name=p.name,
            type=html.escape(p.type),
            annotations=' '.join(p.annotations),
            access_modifier=p.access_modifier,
            modifiers=' '.join(html.escape(modifier) for modifier in p.modifiers),
            docs=PageGenerator.render_doc_string(p.docs, documented_file, file_list)) for p in properties)

    @staticmethod
    def _render_class(c: DocumentedClass, documented_file: DocumentedFile, file_list: List[DocumentedFile]) -> str:

        impl_list = []
        for class_name in c.implements_list:
            impl_list.append(PageGenerator._render_class_link(class_name, documented_file, file_list))
        rendered_impl_list = ', '.join(impl_list)

        rendered_methods = PageGenerator._render_methods(c.methods, documented_file, file_list)
        rendered_properties = PageGenerator._render_properties(c.properties, documented_file, file_list)

        rendered_extends = PageGenerator._render_class_link(c.extends, documented_file, file_list)

        return PageGenerator.templates.get('class').render(name=html.escape(c.name),
                                                           docs=PageGenerator.render_doc_string(c.docs, documented_file,
                                                                                                file_list),
                                                           extends=rendered_extends,
                                                           impl_list=rendered_impl_list,
                                                           inner_classes=''.join(
                                                               PageGenerator._render_class_like_object(ic,
                                                                                                       documented_file,
                                                                                                       file_list)
                                                               for ic in c.inner_classes),
                                                           methods=rendered_methods,
                                                           properties=rendered_properties)

    @staticmethod
    def _render_enum(c: DocumentedEnum, documented_file: DocumentedFile, file_list: List[DocumentedFile]) -> str:

        impl_list = []
        for class_name in c.implements_list:
            impl_list.append(PageGenerator._render_class_link(class_name, documented_file, file_list))
        rendered_impl_list = ', '.join(impl_list)

        rendered_methods = PageGenerator._render_methods(c.methods, documented_file, file_list)
        rendered_properties = PageGenerator._render_properties(c.properties, documented_file, file_list)

        return PageGenerator.templates.get('enum').render(name=html.escape(c.name),
                                                          docs=PageGenerator.render_doc_string(c.docs, documented_file,
                                                                                               file_list),
                                                          impl_list=rendered_impl_list,
                                                          inner_classes=''.join(
                                                              PageGenerator._render_class_like_object(ic,
                                                                                                      documented_file,
                                                                                                      file_list)
                                                              for ic in c.inner_classes),
                                                          methods=rendered_methods,
                                                          values=' '.join(c.values),
                                                          properties=rendered_properties)

    @staticmethod
    def _render_interface(c: DocumentedInterface, documented_file: DocumentedFile,
                          file_list: List[DocumentedFile]) -> str:

        extends_list = []
        for class_name in c.extends_list:
            extends_list.append(PageGenerator._render_class_link(class_name, documented_file, file_list))
        rendered_extends_list = ', '.join(extends_list)

        rendered_methods = PageGenerator._render_methods(c.methods, documented_file, file_list)

        return PageGenerator.templates.get('interface').render(name=html.escape(c.name),
                                                               docs=PageGenerator.render_doc_string(c.docs,
                                                                                                    documented_file,
                                                                                                    file_list),
                                                               extends_list=rendered_extends_list,
                                                               inner_classes=''.join(
                                                                   PageGenerator._render_class_like_object(ic,
                                                                                                           documented_file,
                                                                                                           file_list)
                                                                   for ic in c.inner_classes),
                                                               methods=rendered_methods)

    @staticmethod
    def _render_tree(tree: FileTreeNode, current_file: Optional[DocumentedFile], package_template: FileTemplate,
                     item_template: FileTemplate) -> str:
        result = ''

        for file in tree.files:
            node_class = 'text-secondary'

            if current_file is not None:
                if file is current_file:
                    node_class = 'text-primary'

                file_in_package_path = file.get_package_path()
                package_path = os.path.join(*current_file.package.split('.'))
                relative_path = os.path.relpath(file_in_package_path,
                                                package_path)
            else:
                relative_path = file.file_path

            result += item_template.render(node_class=node_class,
                                           name=file.get_file_name(),
                                           href=relative_path + '.html')

        for child in tree.children:
            result += PageGenerator._render_tree(child, current_file, package_template, item_template)

        return package_template.render(name=tree.directory, items=result)

    @staticmethod
    def _render_class_link(class_name, documented_file, file_list):
        if class_name is not None:
            class_name = class_name.split('.')[-1]
        path = documented_file.get_doc_import_path(class_name, file_list)
        return '<a class="{0}" href="{1}">{2}</a>'.format('disabled' if path is None else '',
                                                          path,
                                                          class_name or '')

    @staticmethod
    def create_index_page(tree: FileTreeNode, file_list: List[DocumentedFile], project_name, project_version):
        file_path = os.path.join(PageGenerator.DIR, 'index.html')

        rendered_package_structure = PageGenerator._render_tree(tree, None,
                                                                PageGenerator.templates.get('list_package'),
                                                                PageGenerator.templates.get('list_item'))

        rendered_alphabetical_index = PageGenerator.render_alphabetical_index(file_list)

        with open(file_path, 'w') as file:
            file.write(PageGenerator.templates.get('index').render(
                package_structure=rendered_package_structure,
                generation_date=time.strftime("%Y-%m-%d %H:%M:%S"),
                alphabetical_index=rendered_alphabetical_index,
                project_name=project_name,
                project_version=project_version or ''
            ))

    @staticmethod
    def render_alphabetical_index(file_list: List[DocumentedFile]) -> str:
        file_list.sort(key=lambda documented_file: documented_file.get_file_name())

        groups = collections.defaultdict(list)
        for file in file_list:
            group = file.get_file_name()[0].upper()
            groups[group].append(file)

        result = ''
        for group, files in groups.items():
            result += '<h3 class="mt-5">' + group + '</h3>'
            for file in files:
                result += PageGenerator.templates.get('list_item').render(node_class='text-secondary',
                                                                          href=file.file_path + '.html',
                                                                          name=file.get_file_name())

        return result

    @staticmethod
    def render_doc_string(doc: Optional[str], documented_file: DocumentedFile, file_list: List[DocumentedFile]):
        if doc is None:
            return ''

        lines = doc.split('\n')
        result = ''
        for line in lines:
            result += PageGenerator._process_doc_string_line(line, documented_file, file_list)

        return result

    @staticmethod
    def _process_doc_string_line(line: str, documented_file: DocumentedFile, file_list: List[DocumentedFile]):
        i = line.rfind('*')

        if i < 0:
            line = line + '\n'
        elif i + 1 < len(line) and line[i + 1] == '/':
            line = ''
        else:
            line = line[i + 1:].strip() + '\n'

        matches = re.finditer(r'{(?:@code) (.*?)}', line)
        shift = 0
        for match in matches:
            argument = html.escape(match.group(1))
            line = line[:match.start() + shift] + argument + line[match.end() + shift:]
            shift += len(argument) - match.end() + match.start()

        matches = re.finditer(r'{(?:@link) (\w+(:?.\w+)*)}', line)
        shift = 0
        for match in matches:
            argument = PageGenerator._render_class_link(match.group(1), documented_file, file_list)
            line = line[:match.start() + shift] + argument + line[match.end() + shift:]
            shift += len(argument) - match.end() + match.start()

        line = re.sub(r'(@[a-z]+)', r'<span class="text-primary">\1</span>', line)

        return line
