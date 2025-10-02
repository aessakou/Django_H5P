from django import template


register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name):
    """Return True if the given user belongs to the given group name.

    Safe to use in templates; returns False on any error or when user is anonymous.
    """
    try:
        if not getattr(user, "is_authenticated", False):
            return False
        return user.groups.filter(name=group_name).exists()
    except Exception:
        return False


