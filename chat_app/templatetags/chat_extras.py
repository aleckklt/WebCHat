from django import template

register = template.Library()

@register.filter
def other_participants(conversation, current_user):
    others = conversation.participants.exclude(id=current_user.id)
    return ", ".join([user.username for user in others])
