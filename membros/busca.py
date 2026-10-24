"""Busca de membros por nome ou CPF (ignora acentos e maiusculas)."""
import re
import unicodedata


def _sem_acento(texto):
    return unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().casefold()


def filtrar_membros(queryset, termo):
    """
    - Somente numeros (com ou sem pontos e traco): procura dentro do CPF, inclusive parte dele.
    - Texto: procura no nome; com varias palavras, todas precisam aparecer (em qualquer ordem).
    Devolve um queryset (mantem a ordem original da lista).
    """
    termo = (termo or "").strip()
    if not termo:
        return queryset

    if re.fullmatch(r"[\d.\-/\s]+", termo):
        numeros = re.sub(r"\D", "", termo)
        if not numeros:
            return queryset.none()
        ids = [pk for pk, cpf in queryset.values_list("pk", "cpf")
               if numeros in re.sub(r"\D", "", cpf or "")]
    else:
        palavras = _sem_acento(termo).split()
        ids = [pk for pk, nome in queryset.values_list("pk", "nome")
               if all(p in _sem_acento(nome) for p in palavras)]
    return queryset.filter(pk__in=ids)
