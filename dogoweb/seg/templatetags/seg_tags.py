# Basado en widget-tweaks https://pypi.python.org/pypi/django-widget-tweaks
import re
import types
from django.template import Library, Node, Context, TemplateSyntaxError
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.conf import settings

register = Library()


def silence_without_field(fn):
    def wrapped(field, attr):
        if not field:
            return ""
        return fn(field, attr)
    return wrapped


def _process_field_attributes(field, attr, process):

    # split attribute name and value from 'attr:value' string
    params = attr.split(':', 1)
    attribute = params[0]
    value = params[1] if len(params) == 2 else ''

    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        html = old_as_widget(widget, attrs, only_initial)
        self.as_widget = old_as_widget
        return html

    field.as_widget = types.MethodType(as_widget, field)
    return field


@register.filter("attr")
@silence_without_field
def set_attr(field, attr):

    def process(widget, attrs, attribute, value):
        attrs[attribute] = value

    return _process_field_attributes(field, attr, process)


@register.filter("add_error_attr")
@silence_without_field
def add_error_attr(field, attr):
    if hasattr(field, 'errors') and field.errors:
        return set_attr(field, attr)
    return field


@register.filter("append_attr")
@silence_without_field
def append_attr(field, attr):
    def process(widget, attrs, attribute, value):
        if attrs.get(attribute):
            attrs[attribute] += ' ' + value
        elif widget.attrs.get(attribute):
            attrs[attribute] = widget.attrs[attribute] + ' ' + value
        else:
            attrs[attribute] = value
    return _process_field_attributes(field, attr, process)


@register.filter("add_class")
@silence_without_field
def add_class(field, css_class):
    return append_attr(field, 'class:' + css_class)


@register.filter("add_error_class")
@silence_without_field
def add_error_class(field, css_class):
    if hasattr(field, 'errors') and field.errors:
        return add_class(field, css_class)
    return field


@register.filter("set_data")
@silence_without_field
def set_data(field, data):
    return set_attr(field, 'data-' + data)


@register.filter(name='field_type')
def field_type(field):
    """
    Template filter that returns field class name (in lower case).
    E.g. if field is CharField then {{ field|field_type }} will
    return 'charfield'.
    """
    if hasattr(field, 'field') and field.field:
        return field.field.__class__.__name__.lower()
    return ''


@register.filter(name='widget_type')
def widget_type(field):
    """
    Template filter that returns field widget class name (in lower case).
    E.g. if field's widget is TextInput then {{ field|widget_type }} will
    return 'textinput'.
    """
    if hasattr(field, 'field') and hasattr(field.field, 'widget') and field.field.widget:
        return field.field.widget.__class__.__name__.lower()
    return ''


# ======================== render_field tag ==============================

ATTRIBUTE_RE = re.compile(r"""
    (?P<attr>
        [\w_-]+
    )
    (?P<sign>
        \+?=
    )
    (?P<value>
    ['"]? # start quote
        [^"']*
    ['"]? # end quote
    )
""", re.VERBOSE | re.UNICODE)

def common_field_render(parser, token):
    """
    Render a form field using given attribute-value pairs

    Takes form field as first argument and list of attribute-value pairs for
    all other arguments.  Attribute-value pairs should be in the form of
    attribute=value or attribute="a value" for assignment and attribute+=value
    or attribute+="value" for appending.
    """
    error_msg = '%r tag requires a form field followed by a list of attributes and values in the form attr="value"' % token.split_contents()[0]
    try:
        bits = token.split_contents()
        tag_name = bits[0]
        form_field = bits[1]
        attr_list = bits[2:]
    except ValueError:
        raise TemplateSyntaxError(error_msg)

    form_field = parser.compile_filter(form_field)

    set_attrs = []
    append_attrs = []
    for pair in attr_list:
        match = ATTRIBUTE_RE.match(pair)
        if not match:
            raise TemplateSyntaxError(error_msg + ": %s" % pair)
        dct = match.groupdict()
        attr, sign, value = dct['attr'], dct['sign'], parser.compile_filter(dct['value'])
        if sign == "=":
            set_attrs.append((attr, value))
        else:
            append_attrs.append((attr, value))

    return form_field, set_attrs, append_attrs


@register.tag
def render_field(parser, token):
    form_field, set_attrs, append_attrs = common_field_render(parser, token)
    return FieldAttributeNode(form_field, set_attrs, append_attrs)

@register.tag
def render_field_full(parser, token):
    form_field, set_attrs, append_attrs = common_field_render(parser, token)
    return FieldAttributeNode(form_field, set_attrs, append_attrs, full=True)


@register.tag
def render_field_full_icon(parser, token):
    form_field, set_attrs, append_attrs = common_field_render(parser, token)
    return FieldAttributeNode(form_field, set_attrs, append_attrs, full=True, template='tags/field_full_icon.html')


@register.tag
def render_field_full_checkbox(parser, token):
    form_field, set_attrs, append_attrs = common_field_render(parser, token)
    return FieldAttributeNode(form_field, set_attrs, append_attrs, full=True, template='tags/field_full_checkbox.html')


@register.tag
def render_field_full_checkboxnull(parser, token):
    form_field, set_attrs, append_attrs = common_field_render(parser, token)
    return FieldAttributeNode(form_field, set_attrs, append_attrs, full=True, template='tags/field_full_checkboxnull.html')


@register.tag
def render_field_full_email(parser, token):
    form_field, set_attrs, append_attrs = common_field_render(parser, token)
    return FieldAttributeNode(form_field, set_attrs, append_attrs, full=True, template='tags/field_full_email.html')


@register.tag
def render_field_full_select2(parser, token):
    form_field, set_attrs, append_attrs = common_field_render(parser, token)
    return FieldAttributeNode(form_field, set_attrs, append_attrs, full=True, template='tags/field_full_select2.html')


@register.filter(name='set_focus', needs_autoscape=True)
def field_set_focus(field, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    focus = "<script>$('#%s').focus();</script>" % esc(field.id_for_label)
    return mark_safe(focus)


class FieldAttributeNode(Node):
    def __init__(self, field, set_attrs, append_attrs, full=False, template='tags/field_full.html'):
        self.field = field
        self.set_attrs = set_attrs
        self.append_attrs = append_attrs
        self.full = full
        self.Ntemplate = template

    def render(self, context):
        bounded_field = self.field.resolve(context)
        field = getattr(bounded_field, 'field', None)
        if 'WIDGET_BASE_CLASS' in context:
            bounded_field = add_class(bounded_field, context['WIDGET_BASE_CLASS'])
        if (getattr(bounded_field, 'errors', None) and 'WIDGET_ERROR_CLASS' in context):
            bounded_field = append_attr(bounded_field, 'class:%s' % context['WIDGET_ERROR_CLASS'])
        if field and field.required and 'WIDGET_REQUIRED_CLASS' in context:
            bounded_field = append_attr(bounded_field, 'class:%s' % context['WIDGET_REQUIRED_CLASS'])
        for k, v in self.set_attrs:
            if k == "dropdownParent":
                continue
            bounded_field = set_attr(bounded_field, '%s:%s' % (k, v.resolve(context)))
        for k, v in self.append_attrs:
            bounded_field = append_attr(bounded_field, '%s:%s' % (k, v.resolve(context)))
        # Si solo es el campo, retorno bounded_field formateado
        if not self.full:
            return bounded_field
        # En cambio si es full, hago un render del template
        datos = {'field': bounded_field }
        for k, v in self.set_attrs:
            if k == "dropdownParent":
                datos['dropdownParent'] = str(v).replace('"','').replace("'","")
        if 'WIDGET_BASE_CLASS' in context:
            datos['WIDGET_BASE_CLASS'] = context['WIDGET_BASE_CLASS']
        if 'WIDGET_REQUIRED_CLASS' in context:
            datos['WIDGET_REQUIRED_CLASS'] = context['WIDGET_REQUIRED_CLASS']
        if 'WIDGET_GROUP_CLASS' in context:
            datos['WIDGET_GROUP_CLASS'] = context['WIDGET_GROUP_CLASS']
        if 'WIDGET_ERROR_CLASS' in context:
            datos['WIDGET_ERROR_CLASS'] = context['WIDGET_ERROR_CLASS']
        if getattr(bounded_field, 'errors', None) and 'WIDGET_ERROR_LIST_CLASS' in context:
            datos['WIDGET_ERROR_LIST_CLASS'] = context['WIDGET_ERROR_LIST_CLASS']
        full_field = context.template.engine.get_template(self.Ntemplate)
        return full_field.render(Context(datos, autoescape=context.autoescape, use_l10n=context.use_l10n, use_tz=context.use_tz))


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")
