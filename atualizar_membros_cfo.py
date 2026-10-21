#!/usr/bin/env python3
"""
Atualiza o app MEMBROS: acrescenta o campo "Curso CFO" (arquivo anexado) na secao
"5. DOCUMENTOS ANEXADOS" do cadastro e da ficha do membro.

Uso: na pasta do projeto (onde esta o manage.py), com o (venv) ativo:

    python atualizar_membros_cfo.py

O que faz:
  1. membros/models.py ................ novo campo doc_curso_cfo (FileField, opcional)
  2. membros/templates/membros/form_membro.html .... campo "Curso CFO" no formulario
  3. membros/templates/membros/detalhe_membro.html .. "Curso CFO" na ficha (com link para abrir)
  4. Roda makemigrations membros e migrate (cria a coluna no banco, sem apagar nada)
Antes de alterar cada arquivo, guarda uma copia .bak. Pode rodar mais de uma vez sem duplicar.
Para nao rodar as migracoes: python atualizar_membros_cfo.py --sem-migrar
"""
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

PASTA = Path.cwd()
CAMPO = "doc_curso_cfo"
ROTULO = "Curso CFO"
MODELS = PASTA / "membros" / "models.py"
FORM = PASTA / "membros" / "templates" / "membros" / "form_membro.html"
DETALHE = PASTA / "membros" / "templates" / "membros" / "detalhe_membro.html"

pendencias = []


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


def gravar(caminho, texto):
    backup(caminho)
    caminho.write_text(texto, encoding="utf-8")


def atualizar_models():
    print("1) membros/models.py")
    texto = ler(MODELS)
    if CAMPO in texto:
        print("   o campo ja existe")
        return
    m = re.search(r"^([ \t]*)doc_certidao_casamento\s*=.*$", texto, re.M)
    if not m or m.group(0).count("(") != m.group(0).count(")"):
        print("   AVISO: nao consegui inserir sozinho. Acrescente na classe Membro, junto dos outros doc_*:")
        pendencias.append(f'    {CAMPO} = models.FileField("{ROTULO}", upload_to=\'documentos/cfo/\', blank=True, null=True)')
        print(pendencias[-1])
        return
    recuo = m.group(1)
    nova = f'{recuo}{CAMPO} = models.FileField("{ROTULO}", upload_to=\'documentos/cfo/\', blank=True, null=True)'
    texto = texto[: m.end()] + "\n" + nova + texto[m.end():]
    gravar(MODELS, texto)
    print("   campo doc_curso_cfo acrescentado")


def atualizar_form():
    print("2) membros/templates/membros/form_membro.html")
    texto = ler(FORM)
    if CAMPO in texto:
        print("   o campo ja existe")
        return
    padrao = re.compile(
        r'^[ \t]*<div class="col-md-6">\s*<label class="form-label">[^<]*</label>\s*'
        r'\{\{\s*form\.doc_certidao_casamento\s*\}\}\s*</div>', re.M)
    m = padrao.search(texto)
    if not m:
        print("   AVISO: nao achei o bloco da Certidao de Casamento. Acrescente na secao 5 do formulario:")
        print('   <div class="col-md-6"><label class="form-label">Curso CFO</label>{{ form.doc_curso_cfo }}</div>')
        return
    bloco = m.group(0)
    novo = re.sub(r'(<label class="form-label">)[^<]*(</label>)', rf"\g<1>{ROTULO}\g<2>", bloco)
    novo = novo.replace("doc_certidao_casamento", CAMPO)
    texto = texto[: m.end()] + "\n" + novo + texto[m.end():]
    gravar(FORM, texto)
    print("   campo 'Curso CFO' acrescentado ao formulario")


def atualizar_detalhe():
    print("3) membros/templates/membros/detalhe_membro.html")
    texto = ler(DETALHE)
    if CAMPO in texto:
        print("   o campo ja existe")
        return
    padrao = re.compile(
        r'^([ \t]*)<div class="col-6">\s*<div class="data-label">[^<]*</div>\s*<div class="data-value">\s*'
        r'\{% if membro\.doc_certidao_casamento %\}.*?\{% endif %\}\s*</div>\s*</div>', re.M | re.S)
    m = padrao.search(texto)
    if not m:
        print("   AVISO: nao achei o bloco da Certidao de Casamento na ficha. Acrescente na secao 5:")
        print('   {% if membro.doc_curso_cfo %}<a href="{{ membro.doc_curso_cfo.url }}" target="_blank">Anexado (abrir)</a>{% else %}Não anexado{% endif %}')
        return
    i = m.group(1)
    novo = (
        f'{i}<div class="col-6">\n'
        f'{i}    <div class="data-label">{ROTULO}</div>\n'
        f'{i}    <div class="data-value">\n'
        f'{i}        {{% if membro.{CAMPO} %}}<a href="{{{{ membro.{CAMPO}.url }}}}" target="_blank">Anexado (abrir)</a>'
        f'{{% else %}}Não anexado{{% endif %}}\n'
        f'{i}    </div>\n'
        f'{i}</div>'
    )
    texto = texto[: m.end()] + "\n" + novo + texto[m.end():]
    gravar(DETALHE, texto)
    print("   'Curso CFO' acrescentado a ficha")


def migrar():
    print("4) Banco de dados")
    for comando in (["makemigrations", "membros"], ["migrate"]):
        print("   python manage.py", " ".join(comando))
        r = subprocess.run([sys.executable, "manage.py", *comando])
        if r.returncode != 0:
            sair("o comando acima falhou; leia a mensagem e me envie o texto completo.")


def main():
    if not (PASTA / "manage.py").exists() or not (PASTA / "membros").is_dir():
        sair("rode este script dentro da pasta do projeto (onde esta o manage.py e a pasta membros).")
    atualizar_models()
    atualizar_form()
    atualizar_detalhe()
    if pendencias:
        print("\nATENCAO: o models.py precisa do campo antes das migracoes. Faca o ajuste manual e rode:")
        print("   python manage.py makemigrations membros && python manage.py migrate")
        sys.exit(1)
    if "--sem-migrar" in sys.argv:
        print("4) migracoes puladas (--sem-migrar)")
    else:
        migrar()
    print("\nPronto! Rode: python manage.py runserver")
    print("Edite um membro: o campo 'Curso CFO' aparece na secao 5 (Documentos anexados).")


if __name__ == "__main__":
    main()
