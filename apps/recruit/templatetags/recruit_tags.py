from __future__ import (
    absolute_import,
)

from django.db.models import Q
from django.template import Library

from recruit.models import Connection

register = Library()


@register.filter
def connections(connecter, connectee):
    return Connection.objects.filter(
        (Q(connecter=connecter) & Q(connectee=connectee)) |
        (Q(connecter=connectee) & Q(connectee=connecter))
    ).first()
