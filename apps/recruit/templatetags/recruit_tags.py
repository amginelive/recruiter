from __future__ import (
    absolute_import,
)

from django.db.models import Q
from django.template import Library


register = Library()


@register.filter
def connections(connecter, connectee):
    return connecter.connections.through.objects.filter(
        (Q(connecter=connecter) & Q(connectee=connectee)) |
        (Q(connecter=connectee) & Q(connectee=connecter))
    ).first()
