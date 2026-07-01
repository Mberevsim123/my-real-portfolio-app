from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import re

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiply a value by an argument - usage: {{ value|multiply:arg }}"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError, AttributeError):
        return 0


@register.filter
def divide(value, arg):
    """Divide a value by an argument - usage: {{ value|divide:arg }}"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError, AttributeError):
        return 0


@register.filter
def percentage(value, total=100):
    """Calculate percentage - usage: {{ value|percentage:total }}"""
    try:
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError, AttributeError):
        return 0


@register.filter
def subtract(value, arg):
    """Subtract arg from value - usage: {{ value|subtract:arg }}"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError, AttributeError):
        return 0


@register.filter
def add_values(value, arg):
    """Add arg to value - usage: {{ value|add_values:arg }}"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError, AttributeError):
        return 0


@register.filter
def truncate_chars(value, max_length):
    """Truncate a string by characters - usage: {{ value|truncate_chars:50 }}"""
    if not value:
        return ''
    if len(value) <= max_length:
        return value
    return value[:max_length] + '...'


@register.filter
def markdown_to_html(value):
    """Convert markdown to HTML (with fallback) - usage: {{ value|markdown_to_html }}"""
    if not value:
        return ''
    try:
        import markdown
        return mark_safe(markdown.markdown(value, extensions=['extra', 'codehilite']))
    except ImportError:
        # Fallback: escape HTML and convert simple markdown
        escaped = escape(value)
        # Convert **bold** to <strong>
        escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
        # Convert *italic* to <em>
        escaped = re.sub(r'\*(.*?)\*', r'<em>\1</em>', escaped)
        # Convert `code` to <code>
        escaped = re.sub(r'`(.*?)`', r'<code>\1</code>', escaped)
        # Convert code blocks
        escaped = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', escaped, flags=re.DOTALL)
        # Convert headers
        escaped = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', escaped, flags=re.MULTILINE)
        escaped = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', escaped, flags=re.MULTILINE)
        escaped = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', escaped, flags=re.MULTILINE)
        return mark_safe(escaped)


@register.filter
def get_range(value):
    """Return a range of numbers - usage: {% for i in value|get_range %}"""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)


@register.simple_tag
def active_class(request, url_name):
    """Return 'active' class if current URL matches - usage: {% active_class request 'home' %}"""
    try:
        from django.urls import resolve
        if resolve(request.path).url_name == url_name:
            return 'active'
    except:
        pass
    return ''


@register.filter
def extract_tech_stack(technologies):
    """Extract technology stack from string - usage: {{ project.technologies|extract_tech_stack }}"""
    if not technologies:
        return []
    return [tech.strip() for tech in technologies.split(',')[:5]]


@register.filter
def reading_time(content):
    """Calculate estimated reading time in minutes - usage: {{ blog.content|reading_time }}"""
    if not content:
        return "1 min read"
    word_count = len(content.split())
    read_time = max(1, round(word_count / 200))
    return f"{read_time} min read"


@register.simple_tag
def get_gravatar_url(email, size=80):
    """Generate Gravatar URL - usage: {% get_gravatar_url user.email 80 %}"""
    import hashlib
    if not email:
        return ''
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=identicon"


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key - usage: {{ my_dict|get_item:key }}"""
    if not dictionary:
        return None
    return dictionary.get(key)


@register.filter
def get_attr(obj, attr):
    """Get attribute from object by name - usage: {{ obj|get_attr:'attribute_name' }}"""
    if not obj or not attr:
        return None
    return getattr(obj, attr, None)


@register.filter
def pluralize(value, arg):
    """Pluralize a word based on count - usage: {{ count|pluralize:'item,items' }}"""
    try:
        count = int(value)
        singular, plural = arg.split(',')
        return singular if count == 1 else plural
    except (ValueError, TypeError, AttributeError):
        return arg