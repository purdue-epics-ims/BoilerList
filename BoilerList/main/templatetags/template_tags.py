from django import template

register = template.Library()

#------------ Inclusion Tags --------------
# Can be used in templates to functionally render some html

# render notifications in a panel
@register.inclusion_tag('tags/notifications.html')
def dash_notifications(title, unread, read):
    context = {'unread':unread,
               'read':read,
               'title':title
               }
    return context
