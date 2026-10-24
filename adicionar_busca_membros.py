#!/usr/bin/env python3
"""
Atualiza o app MEMBROS: campo de busca por NOME ou CPF na lista de membros (tela /home/).

Uso: na pasta do projeto (onde esta o manage.py), com o (venv) ativo:

    python adicionar_busca_membros.py

O que faz:
  1. Cria membros/busca.py (a regra da busca: ignora acentos e maiusculas; aceita CPF parcial,
     com ou sem pontos e traco).
  2. membros/views.py ........................... a HomeView passa a filtrar pelo parametro ?q=
  3. membros/templates/membros/home.html ........ coloca o campo "Buscar por nome ou CPF" acima da lista
Antes de alterar cada arquivo, guarda uma copia .bak. Nao ha migracao. Pode rodar mais de uma vez.
"""
import base64
import re
import shutil
import sys
import time
from pathlib import Path

ARQUIVOS = {
    "membros/busca.py": """
IiIiQnVzY2EgZGUgbWVtYnJvcyBwb3Igbm9tZSBvdSBDUEYgKGlnbm9yYSBhY2VudG9zIGUgbWFpdXNjdWxhcykuIiIiCmltcG9y
dCByZQppbXBvcnQgdW5pY29kZWRhdGEKCgpkZWYgX3NlbV9hY2VudG8odGV4dG8pOgogICAgcmV0dXJuIHVuaWNvZGVkYXRhLm5v
cm1hbGl6ZSgiTkZLRCIsIHRleHRvIG9yICIiKS5lbmNvZGUoImFzY2lpIiwgImlnbm9yZSIpLmRlY29kZSgpLmNhc2Vmb2xkKCkK
CgpkZWYgZmlsdHJhcl9tZW1icm9zKHF1ZXJ5c2V0LCB0ZXJtbyk6CiAgICAiIiIKICAgIC0gU29tZW50ZSBudW1lcm9zIChjb20g
b3Ugc2VtIHBvbnRvcyBlIHRyYWNvKTogcHJvY3VyYSBkZW50cm8gZG8gQ1BGLCBpbmNsdXNpdmUgcGFydGUgZGVsZS4KICAgIC0g
VGV4dG86IHByb2N1cmEgbm8gbm9tZTsgY29tIHZhcmlhcyBwYWxhdnJhcywgdG9kYXMgcHJlY2lzYW0gYXBhcmVjZXIgKGVtIHF1
YWxxdWVyIG9yZGVtKS4KICAgIERldm9sdmUgdW0gcXVlcnlzZXQgKG1hbnRlbSBhIG9yZGVtIG9yaWdpbmFsIGRhIGxpc3RhKS4K
ICAgICIiIgogICAgdGVybW8gPSAodGVybW8gb3IgIiIpLnN0cmlwKCkKICAgIGlmIG5vdCB0ZXJtbzoKICAgICAgICByZXR1cm4g
cXVlcnlzZXQKCiAgICBpZiByZS5mdWxsbWF0Y2gociJbXGQuXC0vXHNdKyIsIHRlcm1vKToKICAgICAgICBudW1lcm9zID0gcmUu
c3ViKHIiXEQiLCAiIiwgdGVybW8pCiAgICAgICAgaWYgbm90IG51bWVyb3M6CiAgICAgICAgICAgIHJldHVybiBxdWVyeXNldC5u
b25lKCkKICAgICAgICBpZHMgPSBbcGsgZm9yIHBrLCBjcGYgaW4gcXVlcnlzZXQudmFsdWVzX2xpc3QoInBrIiwgImNwZiIpCiAg
ICAgICAgICAgICAgIGlmIG51bWVyb3MgaW4gcmUuc3ViKHIiXEQiLCAiIiwgY3BmIG9yICIiKV0KICAgIGVsc2U6CiAgICAgICAg
cGFsYXZyYXMgPSBfc2VtX2FjZW50byh0ZXJtbykuc3BsaXQoKQogICAgICAgIGlkcyA9IFtwayBmb3IgcGssIG5vbWUgaW4gcXVl
cnlzZXQudmFsdWVzX2xpc3QoInBrIiwgIm5vbWUiKQogICAgICAgICAgICAgICBpZiBhbGwocCBpbiBfc2VtX2FjZW50byhub21l
KSBmb3IgcCBpbiBwYWxhdnJhcyldCiAgICByZXR1cm4gcXVlcnlzZXQuZmlsdGVyKHBrX19pbj1pZHMpCg==
""",
}

PASTA = Path.cwd()
VIEWS = PASTA / "membros" / "views.py"
HOME = PASTA / "membros" / "templates" / "membros" / "home.html"

FORMULARIO = """<!-- Busca por nome ou CPF -->
<form method="get" class="row g-2 mb-3 align-items-center no-print">
    <div class="col-12 col-md-8 col-lg-6">
        <input type="text" name="q" value="{{ busca }}" class="form-control" placeholder="Buscar por nome ou CPF" autocomplete="off">
    </div>
    <div class="col-auto">
        <button type="submit" class="btn btn-dark">Buscar</button>
        {% if busca %}<a href="{% url 'home' %}" class="btn btn-outline-secondary">Limpar</a>{% endif %}
    </div>
    {% if busca %}
    <div class="col-12 small {% if total_busca %}text-muted{% else %}text-danger{% endif %}">
        {% if total_busca %}{{ total_busca }} membro{{ total_busca|pluralize }} encontrado{{ total_busca|pluralize }} para "{{ busca }}".{% else %}Nenhum membro encontrado para "{{ busca }}".{% endif %}
    </div>
    {% endif %}
</form>
"""

METODOS = (
    "def get_queryset(self):\n"
    "    return filtrar_membros(super().get_queryset(), self.request.GET.get('q', ''))\n"
    "\n"
    "def get_context_data(self, **kwargs):\n"
    "    contexto = super().get_context_data(**kwargs)\n"
    "    contexto['busca'] = self.request.GET.get('q', '').strip()\n"
    "    contexto['total_busca'] = self.object_list.count()\n"
    "    return contexto\n"
)


def sair(msg):
    print("ERRO:", msg)
    sys.exit(1)


def backup(caminho):
    destino = caminho.with_name(caminho.name + time.strftime(".%Y%m%d-%H%M%S.bak"))
    shutil.copy2(caminho, destino)
    print(f"   copia de seguranca: {destino.name}")


def ler(caminho):
    if not caminho.exists():
        sair(f"arquivo nao encontrado: {caminho.relative_to(PASTA)}")
    return caminho.read_text(encoding="utf-8")


def instalar_arquivos():
    print("1) membros/busca.py")
    for rel, b64 in ARQUIVOS.items():
        destino = PASTA / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(base64.b64decode("".join(b64.split())))
        print("   ok", rel)


def atualizar_views():
    print("2) membros/views.py")
    texto = ler(VIEWS)
    if "filtrar_membros" in texto:
        print("   ja esta atualizado")
        return True
    m_classe = re.search(r"^class HomeView\(ListView\):", texto, re.M)
    if not m_classe:
        print("   AVISO: nao achei a classe HomeView. Veja o passo manual no final.")
        return False
    fim = re.search(r"^class ", texto[m_classe.end():], re.M)
    limite = m_classe.end() + fim.start() if fim else len(texto)
    corpo = texto[m_classe.start():limite]
    if re.search(r"^[ \t]+def get_queryset\(", corpo, re.M):
        print("   AVISO: a HomeView ja tem get_queryset proprio. Veja o passo manual no final.")
        return False
    m_ctx = re.search(r"^([ \t]+)context_object_name\s*=.*$", corpo, re.M)
    if not m_ctx:
        print("   AVISO: nao achei context_object_name na HomeView. Veja o passo manual no final.")
        return False
    recuo = m_ctx.group(1)
    metodos = "\n".join((recuo + linha) if linha else "" for linha in METODOS.splitlines())
    novo_corpo = corpo[: m_ctx.end()] + "\n\n" + metodos + corpo[m_ctx.end():]
    texto = texto[: m_classe.start()] + novo_corpo + texto[limite:]
    m_import = re.search(r"^from \.models import .*$", texto, re.M)
    linha_import = "from .busca import filtrar_membros"
    if m_import:
        texto = texto[: m_import.end()] + "\n" + linha_import + texto[m_import.end():]
    else:
        texto = linha_import + "\n" + texto
    backup(VIEWS)
    VIEWS.write_text(texto, encoding="utf-8")
    print("   HomeView agora filtra pelo parametro ?q=")
    return True


def atualizar_home():
    print("3) membros/templates/membros/home.html")
    texto = ler(HOME)
    if 'name="q"' in texto:
        print("   o campo de busca ja existe")
        return True
    m = re.search(r"^([ \t]*)<table", texto, re.M)
    if not m:
        print("   AVISO: nao achei a tabela da lista. Veja o passo manual no final.")
        return False
    recuo = m.group(1)
    bloco = "\n".join((recuo + l) if l.strip() else "" for l in FORMULARIO.splitlines()) + "\n"
    texto = texto[: m.start()] + bloco + texto[m.start():]
    backup(HOME)
    HOME.write_text(texto, encoding="utf-8")
    print("   campo de busca colocado acima da lista")
    return True


def main():
    if not (PASTA / "manage.py").exists() or not (PASTA / "membros").is_dir():
        sair("rode este script dentro da pasta do projeto (onde esta o manage.py e a pasta membros).")
    instalar_arquivos()
    ok_views = atualizar_views()
    ok_home = atualizar_home()
    if not (ok_views and ok_home):
        print()
        print("PASSO MANUAL (so para o que deu AVISO acima):")
        if not ok_views:
            print("  views.py: na HomeView, acrescente os metodos abaixo e o import "
                  "'from .busca import filtrar_membros':")
            for linha in METODOS.splitlines():
                print("      " + linha)
        if not ok_home:
            print("  home.html: cole este bloco logo acima da lista de membros:")
            print(FORMULARIO)
        sys.exit(1)
    print()
    print("Pronto! Atualize a pagina /home/ (ou rode: python manage.py runserver).")
    print("Digite um nome ou CPF no campo 'Buscar' e tecle Enter.")


if __name__ == "__main__":
    main()
