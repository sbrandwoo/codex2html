import argparse
import markdown
from operator import attrgetter
import os

"""
    Create a static HTML site from a directory of text files, annotated
    with Markdown.

    Usage:
        build_codex.py source_directory target_directory
"""

class Page:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def get_file_path(self, root_path=""):
        return os.path.join(root_path, self.get_dir_path(), self.name)

    def get_dir_path(self):
        return apply(os.path.join, self.path)

    def get_relative_path(self, target):
        """Return a file path from the current page to the target path"""
        sp = self.path
        tp = target.path
        i = len(sp) - 1
        o = ""
        # Traverse down
        while i >= 0 and not (len(tp) > i and tp[i] == sp[i]):
            o = os.path.join("..", o)
            i -= 1
        i += 1
        # Traverse up
        while i < len(tp):
            o = os.path.join(o, tp[i])
            i += 1
        return os.path.join(o, target.name)


def load_html(page, root_path):
    """Load the page text and convert the markdown to HTML"""
    with open(page.get_file_path(root_path), "rb") as f:
        return markdown.markdown(f.read(), ['def_list'])

def create_html_file(page, content_html, template, target_root):
    """Create an output HTML file for this page"""
    html = template.replace("{{CONTENT}}", content_html) \
            .replace("{{TITLE}}", page.name)

    output_dir = os.path.join(target_root, page.get_dir_path())
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(target_root, page.get_file_path()) + ".htm"
    with open(output_path, "wb") as f:
        f.write(html)

def build_nav(page_map, current_page):
    """Build navigation from the current page to all pages in the page map"""
    o = "<ul>"
    for dir, pages in sorted(page_map.items()):
        o += '<li>%s</a><ul>\n' % dir
        for page in pages:
            link = current_page.get_relative_path(page) + ".htm"
            o += '<li><a href="%s">%s</a></li>\n' % (link, page.name)
        o += '    </ul>\n'
        o += '</li>\n'
    return o + "</ul>"

def parse_args():
    parser = argparse.ArgumentParser(description='Create a codex site')
    parser.add_argument('source', help='location of source text files')
    parser.add_argument('target', help='destination of generated html files')
    args = parser.parse_args()
    return args

def create_site(source_root, target_root):
    page_map = {}

    # Find pages in the source_root
    top_dirs = os.listdir(source_root)
    top_dirs.sort()
    for f in top_dirs:
        path = os.path.join(source_root, f)
        if os.path.isdir(path):
            page_map[f] = []
            for g in os.listdir(path):
                if os.path.isfile(os.path.join(path, g)):
                    page_map[f].append(Page(g, [f]))
            page_map[f] = sorted(page_map[f], key=attrgetter('name'))

    template = open("template.htm").read()

    # Product output files
    for dir, pages in page_map.items():
        for page in pages:
            nav = build_nav(page_map, page)
            page_template = template.replace("{{NAV}}", nav)
            content_html = load_html(page, source_root)
            create_html_file(page, content_html, page_template, target_root)


if __name__ == "__main__":
    args = parse_args()
    create_site(args.source, args.target)
