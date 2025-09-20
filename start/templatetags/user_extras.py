from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    if user and hasattr(user, "groups"):
        return user.groups.filter(name=group_name).exists()
    return False
