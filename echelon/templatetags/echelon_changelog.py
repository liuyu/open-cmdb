from django.template import Library
register = Library()

@register.inclusion_tag('echelon/changelog_detail.html')
def changelog_detail(changes):
    changes = changes.items()
    return {'changes': changes}
