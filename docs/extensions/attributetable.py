# Credit to github.com/Rapptz (see: https://github.com/Rapptz/discord.py/blob/master/docs/extensions/attributetable.py)
# I simply couldn't find an alternative other than Rapptz's code. Sphinx's autosummary is broken for attributes.

from sphinx.util.docutils import SphinxDirective
from sphinx.locale import _
from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx

from collections import OrderedDict, namedtuple
import importlib
import inspect
import os
import re
import typing

class attributetable(nodes.General, nodes.Element):
    pass

class attributetablecolumn(nodes.General, nodes.Element):
    pass

class attributetabletitle(nodes.TextElement):
    pass

class attributetableplaceholder(nodes.General, nodes.Element):
    pass

class attributetablebadge(nodes.TextElement):
    pass

class attributetable_item(nodes.Part, nodes.Element):
    pass

class attributetable_attrref(nodes.General, nodes.Element):
    pass

class attributetable_methref(nodes.General, nodes.Element):
    pass

class attributetable_refspan(nodes.TextElement):
    pass

def visit_attributetable_node(self, node):
    class_ = node["python-class"]
    self.body.append(f'<div class="py-attribute-table" data-move-to-id="{class_}">')

def visit_attributetablecolumn_node(self, node):
    self.body.append(self.starttag(node, 'div', CLASS='py-attribute-table-column'))

def visit_attributetabletitle_node(self, node):
    self.body.append(self.starttag(node, 'span'))

def visit_attributetablebadge_node(self, node):
    attributes = {
        'class': 'py-attribute-table-badge',
        'title': node['badge-type'],
    }
    self.body.append(self.starttag(node, 'span', **attributes))

def visit_attributetable_item_node(self, node):
    self.body.append(self.starttag(node, 'li', CLASS='py-attribute-table-entry'))

def visit_attributetable_attrref_node(self, node):
    self.body.append(self.starttag(node, 'code', CLASS="py-attribute-table-ref xref py py-attr docutils literal notranslate"))

def visit_attributetable_methref_node(self, node):
    self.body.append(self.starttag(node, 'code', CLASS="py-attribute-table-ref xref py py-meth docutils literal notranslate"))

def visit_attributetable_refspan_node(self, node):
    self.body.append(self.starttag(node, 'span', CLASS="py-attribute-table-refspan pre"))

def depart_attributetable_node(self, node):
    self.body.append('</div>')

def depart_attributetablecolumn_node(self, node):
    self.body.append('</div>')

def depart_attributetabletitle_node(self, node):
    self.body.append('</span>')

def depart_attributetablebadge_node(self, node):
    self.body.append('</span>')

def depart_attributetable_item_node(self, node):
    self.body.append('</li>')


def depart_attributetable_attrref_node(self, node):
    self.body.append("</code>")


def depart_attributetable_methref_node(self, node):
    self.body.append("</code>")


def depart_attributetable_refspan_node(self, node):
    self.body.append("</span>")


_name_parser_regex = re.compile(r'(?P<module>[\w.]+\.)?(?P<name>\w+)')

class PyAttributeTable(SphinxDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def parse_name(self, content):
        path, name = _name_parser_regex.match(content).groups()
        if path:
            modulename = path.rstrip('.')
        else:
            modulename = self.env.temp_data.get('autodoc:module')
            if not modulename:
                modulename = self.env.ref_context.get('py:module')
        if modulename is None:
            raise RuntimeError('modulename somehow None for %s in %s.' % (content, self.env.docname))

        return modulename, name

    def run(self):
        """If you're curious on the HTML this is meant to generate:
        <div class="py-attribute-table">
            <div class="py-attribute-table-column">
                <span>_('Attributes')</span>
                <ul>
                    <li>
                        <a href="...">
                    </li>
                </ul>
            </div>
            <div class="py-attribute-table-column">
                <span>_('Methods')</span>
                <ul>
                    <li>
                        <a href="..."></a>
                        <span class="py-attribute-badge" title="decorator">D</span>
                    </li>
                </ul>
            </div>
        </div>
        However, since this requires the tree to be complete
        and parsed, it'll need to be done at a different stage and then
        replaced.
        """
        content = self.arguments[0].strip()
        node = attributetableplaceholder('')
        modulename, name = self.parse_name(content)
        node['python-doc'] = self.env.docname
        node['python-module'] = modulename
        node['python-class'] = name
        node['python-full-name'] = f'{modulename}.{name}'
        return [node]

def build_lookup_table(env):
    # Given an environment, load up a lookup table of
    # full-class-name: objects
    result = {}
    domain = env.domains['py']

    ignored = {
        'data', 'exception', 'module', 'class',
    }

    for (fullname, _, objtype, docname, _, _) in domain.get_objects():
        if objtype in ignored:
            continue

        classname, _, child = fullname.rpartition('.')
        try:
            result[classname].append(child)
        except KeyError:
            result[classname] = [child]

    return result


TableElement = namedtuple('TableElement', 'fullname label badge')

def process_attributetable(app, doctree, fromdocname):
    env = app.builder.env

    lookup = build_lookup_table(env)
    for node in doctree.traverse(attributetableplaceholder):
        modulename, classname, fullname = node['python-module'], node['python-class'], node['python-full-name']
        groups = get_class_results(lookup, modulename, classname, fullname)
        table = attributetable('')
        for label, subitems in groups.items():
            if not subitems:
                continue
            table.append(class_results_to_node(label, sorted(subitems, key=lambda c: c.label)))

        table['python-class'] = fullname

        if not table:
            node.replace_self([])
        else:
            node.replace_self([table])

def get_class_results(lookup, modulename, name, fullname):
    module = importlib.import_module(modulename)
    cls = getattr(module, name)

    groups = OrderedDict([
        (_('Attributes'), []),
        (_('Methods'), []),
    ])

    try:
        members = lookup[fullname]
    except KeyError:
        return groups

    for attr in members:
        attrlookup = f'{fullname}.{attr}'
        key = _('Attributes')
        badge = None
        label = attr
        value = None

        for base in cls.__mro__:
            value = base.__dict__.get(attr)
            if value is not None:
                break

        if value is not None:
            doc = value.__doc__ or ''
            if inspect.iscoroutinefunction(value) or doc.startswith('|coro|'):
                key = _('Methods')
                badge = attributetablebadge('async', 'async')
                badge['badge-type'] = _('coroutine')
            elif isinstance(value, classmethod):
                key = _('Methods')
                label = f'{name}.{attr}'
                badge = attributetablebadge('cls', 'cls')
                badge['badge-type'] = _('classmethod')
            elif inspect.isfunction(value):
                if doc.startswith(('A decorator', 'A shortcut decorator')):
                    # finicky but surprisingly consistent
                    badge = attributetablebadge('@', '@')
                    badge['badge-type'] = _('decorator')
                    key = _('Methods')
                else:
                    key = _('Methods')
                    badge = attributetablebadge('def', 'def')
                    badge['badge-type'] = _('method')

        groups[key].append(TableElement(fullname=attrlookup, label=label, badge=badge))

    return groups

def class_results_to_node(key, elements):
    title = attributetabletitle(key, key)
    ul = nodes.bullet_list('')
    for element in elements:
        if element.badge is None:  # attr
            refspan = attributetable_refspan(element.label.strip(), element.label.strip())
            customref = attributetable_attrref("", refspan)
        else:
            refspan = attributetable_refspan(element.label.strip() + "()", element.label.strip() + "()")
            customref = attributetable_methref("", refspan)
        ref = nodes.reference('', '', internal=True,
                                      refuri='#' + element.fullname,
                                      anchorname='',
                                      *[customref])
        # ref = addnodes.pending_xref("", refdomain="py", reftarget=element.fullname, *[nodes.Text(element.label)])
        para = addnodes.compact_paragraph('', '', ref)
        if element.badge is not None:
            ul.append(attributetable_item('', element.badge, para))
        else:
            ul.append(attributetable_item('', para))

    return attributetablecolumn('', title, ul)


def autodoc_docstring_hook(
    app: Sphinx, what: str, name: str, obj, options: typing.Dict[str, str], lines: typing.List[str]
):
    if app.config.attributetable_autodoc_hook:
        if what == "class":
            attr_table = f".. attributetable:: {name}"
            for i, line in enumerate(lines):
                if line.startswith(".. attribute:: ") or line.startswith(".. autoattribute:: "):
                    lines.insert(i, attr_table)
                    break  # add attributetable at the end of docstring; before attrs
            else:
                lines.append(attr_table)


def setup(app: Sphinx):
    # If True, an 'attributetable' is added to every autoclass.
    app.add_config_value("attributetable_autodoc_hook", False, True, "``[bool]``")
    app.connect("autodoc-process-docstring", autodoc_docstring_hook)
    app.add_directive('attributetable', PyAttributeTable)
    app.add_node(attributetable, html=(visit_attributetable_node, depart_attributetable_node))
    app.add_node(attributetablecolumn, html=(visit_attributetablecolumn_node, depart_attributetablecolumn_node))
    app.add_node(attributetabletitle, html=(visit_attributetabletitle_node, depart_attributetabletitle_node))
    app.add_node(attributetablebadge, html=(visit_attributetablebadge_node, depart_attributetablebadge_node))
    app.add_node(attributetable_item, html=(visit_attributetable_item_node, depart_attributetable_item_node))
    app.add_node(attributetable_attrref, html=(visit_attributetable_attrref_node, depart_attributetable_attrref_node))
    app.add_node(attributetable_methref, html=(visit_attributetable_methref_node, depart_attributetable_methref_node))
    app.add_node(attributetable_refspan, html=(visit_attributetable_refspan_node, depart_attributetable_refspan_node))
    app.add_node(attributetableplaceholder)
    app.connect('doctree-resolved', process_attributetable)
