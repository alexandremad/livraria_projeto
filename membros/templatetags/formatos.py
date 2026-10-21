import re

from django import template

register = template.Library()


def _digitos(valor):
    return re.sub(r"\D", "", str(valor or ""))


@register.filter
def cpf(valor):
    """12345678909 -> 123.456.789-09"""
    d = _digitos(valor)
    if len(d) == 11:
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    return valor or ""


@register.filter
def telefone(valor):
    """61999998888 -> (61) 99999-8888 ; 6133334444 -> (61) 3333-4444"""
    d = _digitos(valor)
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return valor or ""
