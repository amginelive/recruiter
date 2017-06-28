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


@register.filter
def connection_requests(user, connection_type):
    return user.connectee_requests\
        .filter(connection_type=connection_type)\
        .values_list('connectee__pk', flat=True)
