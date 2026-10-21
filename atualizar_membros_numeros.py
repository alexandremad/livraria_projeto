#!/usr/bin/env python3
"""
Atualiza o app MEMBROS: CPF, RG e telefones passam a aceitar SOMENTE NUMEROS.

Uso: na pasta do projeto (onde esta o manage.py), com o (venv) ativo:

    python atualizar_membros_numeros.py

O que faz:
  1. Cria os arquivos novos (validacao, mascara em JavaScript, filtros para exibir CPF/telefone formatados
     e o comando que limpa os cadastros antigos).
  2. membros/forms.py ............................ passa a validar CPF, RG e telefones (so numeros).
  3. membros/templates/membros/form_membro.html .. ativa a mascara e bloqueia letras ao digitar.
  4. membros/templates/membros/detalhe_membro.html  mostra CPF e telefones formatados na ficha.
  5. Faz copia do db.sqlite3 e remove pontos, tracos, parenteses e espacos dos membros ja cadastrados.
Antes de alterar cada arquivo, guarda uma copia .bak. Nao ha migracao (a estrutura do banco nao muda).

Opcoes:
  --simular          so mostra o que a limpeza dos cadastros antigos faria (nao grava nada)
  --sem-normalizar   nao mexe nos cadastros antigos
"""
import base64
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ARQUIVOS = {
    "membros/validadores.py": """
IiIiClRyYXRhbWVudG8gZGUgbnVtZXJvcyBubyBjYWRhc3RybyBkZSBtZW1icm9zOiBDUEYsIFJHIGUgdGVsZWZvbmVzLgoKLSBP
IHF1ZSBvIHVzdWFyaW8gZGlnaXRhIGUgbGltcG86IHNvIGZpY2FtIG9zIG51bWVyb3MgKG8gYmFuY28gZ3VhcmRhIFNPTUVOVEUg
bnVtZXJvcykuCi0gTmEgdGVsYSwgbyBKYXZhU2NyaXB0IChzdGF0aWMvbWVtYnJvcy9qcy9tYXNjYXJhcy5qcykgYmxvcXVlaWEg
bGV0cmFzIGUgY29sb2NhIGEgbWFzY2FyYQogIChDUEYgMDAwLjAwMC4wMDAtMDAgZSB0ZWxlZm9uZSAoMDApIDAwMDAwLTAwMDAp
IHNlbSBvIHVzdWFyaW8gZGlnaXRhciBwb250b3Mgb3UgdHJhY29zLgoiIiIKaW1wb3J0IHJlCgpmcm9tIGRqYW5nby5jb3JlLmV4
Y2VwdGlvbnMgaW1wb3J0IFZhbGlkYXRpb25FcnJvcgoKIyAtLS0gQWp1c3RlcyAobXVkZSBhcXVpIHNlIHByZWNpc2FyKSAtLS0t
LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tClZBTElEQVJfRElHSVRPU19DUEYgPSBGYWxzZSAg
ICAgICMgVHJ1ZSA9IHJlY3VzYSBDUEYgY29tIGRpZ2l0b3MgdmVyaWZpY2Fkb3JlcyBpbnZhbGlkb3MKVEVMRUZPTkVfVEFNQU5I
T1MgPSAoMTAsIDExKSAgICAgIyBEREQgKyBudW1lcm86IDEwIChmaXhvKSBvdSAxMSAoY2VsdWxhcikKUkdfTUlOLCBSR19NQVgg
PSA1LCAxNSAgICAgICAgICAgIyBxdWFudGlkYWRlIGRlIG51bWVyb3MgYWNlaXRhIG5vIFJHCiMgLS0tLS0tLS0tLS0tLS0tLS0t
LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCgoKZGVm
IHNvX2RpZ2l0b3ModmFsb3IpOgogICAgcmV0dXJuIHJlLnN1YihyIlxEIiwgIiIsIHZhbG9yIG9yICIiKQoKCmRlZiBjcGZfdmFs
aWRvKGNwZik6CiAgICAiIiJDb25mZXJlIG9zIGRvaXMgZGlnaXRvcyB2ZXJpZmljYWRvcmVzIGRvIENQRiAoc29tZW50ZSBudW1l
cm9zLCAxMSBwb3NpY29lcykuIiIiCiAgICBpZiBsZW4oY3BmKSAhPSAxMSBvciBjcGYgPT0gY3BmWzBdICogMTE6CiAgICAgICAg
cmV0dXJuIEZhbHNlCiAgICBmb3IgaSBpbiAoOSwgMTApOgogICAgICAgIHNvbWEgPSBzdW0oaW50KGNwZltuXSkgKiAoaSArIDEg
LSBuKSBmb3IgbiBpbiByYW5nZShpKSkKICAgICAgICBpZiAoc29tYSAqIDEwKSAlIDExICUgMTAgIT0gaW50KGNwZltpXSk6CiAg
ICAgICAgICAgIHJldHVybiBGYWxzZQogICAgcmV0dXJuIFRydWUKCgojIGF0cmlidXRvcyBIVE1MIHF1ZSBvIEphdmFTY3JpcHQg
dXNhIHBhcmEgY29sb2NhciBhIG1hc2NhcmEKX0FUUklCVVRPUyA9IHsKICAgICJjcGYiOiB7ImRhdGEtbWFzY2FyYSI6ICJjcGYi
LCAibWF4bGVuZ3RoIjogMTQsICJwbGFjZWhvbGRlciI6ICIwMDAuMDAwLjAwMC0wMCJ9LAogICAgInJnIjogeyJkYXRhLW1hc2Nh
cmEiOiAibnVtZXJvcyIsICJtYXhsZW5ndGgiOiBSR19NQVgsICJwbGFjZWhvbGRlciI6ICJTb21lbnRlIG7Dum1lcm9zIn0sCiAg
ICAiY2VsdWxhciI6IHsiZGF0YS1tYXNjYXJhIjogInRlbCIsICJtYXhsZW5ndGgiOiAxNSwgInBsYWNlaG9sZGVyIjogIigwMCkg
MDAwMDAtMDAwMCJ9LAogICAgImNlbHVsYXJfY29udGF0byI6IHsiZGF0YS1tYXNjYXJhIjogInRlbCIsICJtYXhsZW5ndGgiOiAx
NSwgInBsYWNlaG9sZGVyIjogIigwMCkgMDAwMDAtMDAwMCJ9LAogICAgImNlbHVsYXJfZmlsaG8iOiB7ImRhdGEtbWFzY2FyYSI6
ICJ0ZWwiLCAibWF4bGVuZ3RoIjogMTUsICJwbGFjZWhvbGRlciI6ICIoMDApIDAwMDAwLTAwMDAifSwKfQoKCmNsYXNzIFNvbWVu
dGVOdW1lcm9zTWl4aW46CiAgICAiIiJVc2UgYW50ZXMgZGUgZm9ybXMuTW9kZWxGb3JtOiBjbGFzcyBNZW1icm9Gb3JtKFNvbWVu
dGVOdW1lcm9zTWl4aW4sIGZvcm1zLk1vZGVsRm9ybSkuIiIiCgogICAgZGVmIF9faW5pdF9fKHNlbGYsICphcmdzLCAqKmt3YXJn
cyk6CiAgICAgICAgc3VwZXIoKS5fX2luaXRfXygqYXJncywgKiprd2FyZ3MpCiAgICAgICAgZm9yIG5vbWUsIGF0cmlidXRvcyBp
biBfQVRSSUJVVE9TLml0ZW1zKCk6CiAgICAgICAgICAgIGlmIG5vbWUgaW4gc2VsZi5maWVsZHM6CiAgICAgICAgICAgICAgICBz
ZWxmLmZpZWxkc1tub21lXS53aWRnZXQuYXR0cnMudXBkYXRlKAogICAgICAgICAgICAgICAgICAgIHsiaW5wdXRtb2RlIjogIm51
bWVyaWMiLCAiYXV0b2NvbXBsZXRlIjogIm9mZiIsICoqYXRyaWJ1dG9zfSkKCiAgICBkZWYgY2xlYW5fY3BmKHNlbGYpOgogICAg
ICAgIGNwZiA9IHNvX2RpZ2l0b3Moc2VsZi5jbGVhbmVkX2RhdGEuZ2V0KCJjcGYiKSkKICAgICAgICBpZiBsZW4oY3BmKSAhPSAx
MToKICAgICAgICAgICAgcmFpc2UgVmFsaWRhdGlvbkVycm9yKCJPIENQRiBkZXZlIHRlciAxMSBuw7ptZXJvcy4iKQogICAgICAg
IGlmIFZBTElEQVJfRElHSVRPU19DUEYgYW5kIG5vdCBjcGZfdmFsaWRvKGNwZik6CiAgICAgICAgICAgIHJhaXNlIFZhbGlkYXRp
b25FcnJvcigiQ1BGIGludsOhbGlkby4gQ29uZmlyYSBvcyBuw7ptZXJvcyBkaWdpdGFkb3MuIikKICAgICAgICByZXR1cm4gY3Bm
CgogICAgZGVmIGNsZWFuX3JnKHNlbGYpOgogICAgICAgIHJnID0gc29fZGlnaXRvcyhzZWxmLmNsZWFuZWRfZGF0YS5nZXQoInJn
IikpCiAgICAgICAgaWYgbm90IChSR19NSU4gPD0gbGVuKHJnKSA8PSBSR19NQVgpOgogICAgICAgICAgICByYWlzZSBWYWxpZGF0
aW9uRXJyb3IoZiJPIFJHIGRldmUgdGVyIHNvbWVudGUgbsO6bWVyb3MgKHtSR19NSU59IGEge1JHX01BWH0gZMOtZ2l0b3MpLiIp
CiAgICAgICAgcmV0dXJuIHJnCgogICAgZGVmIF90ZWxlZm9uZShzZWxmLCBub21lKToKICAgICAgICBvcmlnaW5hbCA9IHNlbGYu
Y2xlYW5lZF9kYXRhLmdldChub21lKQogICAgICAgIG51bWVybyA9IHNvX2RpZ2l0b3Mob3JpZ2luYWwpCiAgICAgICAgaWYgbm90
IG51bWVybzoKICAgICAgICAgICAgcmV0dXJuIG9yaWdpbmFsICAjIHZhemlvOiBhIG9icmlnYXRvcmllZGFkZSBqYSBlIHRyYXRh
ZGEgcGVsbyBwcm9wcmlvIGNhbXBvCiAgICAgICAgaWYgbGVuKG51bWVybykgbm90IGluIFRFTEVGT05FX1RBTUFOSE9TOgogICAg
ICAgICAgICByYWlzZSBWYWxpZGF0aW9uRXJyb3IoIkluZm9ybWUgbyBEREQgZSBvIG7Dum1lcm8gZG8gdGVsZWZvbmUgKDEwIG91
IDExIG7Dum1lcm9zKS4iKQogICAgICAgIHJldHVybiBudW1lcm8KCiAgICBkZWYgY2xlYW5fY2VsdWxhcihzZWxmKToKICAgICAg
ICByZXR1cm4gc2VsZi5fdGVsZWZvbmUoImNlbHVsYXIiKQoKICAgIGRlZiBjbGVhbl9jZWx1bGFyX2NvbnRhdG8oc2VsZik6CiAg
ICAgICAgcmV0dXJuIHNlbGYuX3RlbGVmb25lKCJjZWx1bGFyX2NvbnRhdG8iKQoKICAgIGRlZiBjbGVhbl9jZWx1bGFyX2ZpbGhv
KHNlbGYpOgogICAgICAgIHJldHVybiBzZWxmLl90ZWxlZm9uZSgiY2VsdWxhcl9maWxobyIpCg==
""",
    "membros/templatetags/__init__.py": """

""",
    "membros/templatetags/formatos.py": """
aW1wb3J0IHJlCgpmcm9tIGRqYW5nbyBpbXBvcnQgdGVtcGxhdGUKCnJlZ2lzdGVyID0gdGVtcGxhdGUuTGlicmFyeSgpCgoKZGVm
IF9kaWdpdG9zKHZhbG9yKToKICAgIHJldHVybiByZS5zdWIociJcRCIsICIiLCBzdHIodmFsb3Igb3IgIiIpKQoKCkByZWdpc3Rl
ci5maWx0ZXIKZGVmIGNwZih2YWxvcik6CiAgICAiIiIxMjM0NTY3ODkwOSAtPiAxMjMuNDU2Ljc4OS0wOSIiIgogICAgZCA9IF9k
aWdpdG9zKHZhbG9yKQogICAgaWYgbGVuKGQpID09IDExOgogICAgICAgIHJldHVybiBmIntkWzozXX0ue2RbMzo2XX0ue2RbNjo5
XX0te2RbOTpdfSIKICAgIHJldHVybiB2YWxvciBvciAiIgoKCkByZWdpc3Rlci5maWx0ZXIKZGVmIHRlbGVmb25lKHZhbG9yKToK
ICAgICIiIjYxOTk5OTk4ODg4IC0+ICg2MSkgOTk5OTktODg4OCA7IDYxMzMzMzQ0NDQgLT4gKDYxKSAzMzMzLTQ0NDQiIiIKICAg
IGQgPSBfZGlnaXRvcyh2YWxvcikKICAgIGlmIGxlbihkKSA9PSAxMToKICAgICAgICByZXR1cm4gZiIoe2RbOjJdfSkge2RbMjo3
XX0te2RbNzpdfSIKICAgIGlmIGxlbihkKSA9PSAxMDoKICAgICAgICByZXR1cm4gZiIoe2RbOjJdfSkge2RbMjo2XX0te2RbNjpd
fSIKICAgIHJldHVybiB2YWxvciBvciAiIgo=
""",
    "membros/static/membros/js/mascaras.js": """
LyogQ2FkYXN0cm8gZGUgbWVtYnJvczogc28gbnVtZXJvcyBlbSBDUEYsIFJHIGUgdGVsZWZvbmVzLCBjb20gbWFzY2FyYSBhdXRv
bWF0aWNhLiAqLwooZnVuY3Rpb24gKCkgewogIGNvbnN0IGRpZ2l0b3MgPSAocykgPT4gKHMgfHwgIiIpLnJlcGxhY2UoL1xEL2cs
ICIiKTsKCiAgY29uc3QgbWFzY2FyYXMgPSB7CiAgICBjcGY6IChkKSA9PiB7CiAgICAgIGQgPSBkLnNsaWNlKDAsIDExKTsKICAg
ICAgaWYgKGQubGVuZ3RoID4gOSkgcmV0dXJuIGQuc2xpY2UoMCwgMykgKyAiLiIgKyBkLnNsaWNlKDMsIDYpICsgIi4iICsgZC5z
bGljZSg2LCA5KSArICItIiArIGQuc2xpY2UoOSk7CiAgICAgIGlmIChkLmxlbmd0aCA+IDYpIHJldHVybiBkLnNsaWNlKDAsIDMp
ICsgIi4iICsgZC5zbGljZSgzLCA2KSArICIuIiArIGQuc2xpY2UoNik7CiAgICAgIGlmIChkLmxlbmd0aCA+IDMpIHJldHVybiBk
LnNsaWNlKDAsIDMpICsgIi4iICsgZC5zbGljZSgzKTsKICAgICAgcmV0dXJuIGQ7CiAgICB9LAogICAgdGVsOiAoZCkgPT4gewog
ICAgICBkID0gZC5zbGljZSgwLCAxMSk7CiAgICAgIGlmIChkLmxlbmd0aCA+IDEwKSByZXR1cm4gIigiICsgZC5zbGljZSgwLCAy
KSArICIpICIgKyBkLnNsaWNlKDIsIDcpICsgIi0iICsgZC5zbGljZSg3KTsKICAgICAgaWYgKGQubGVuZ3RoID4gNikgcmV0dXJu
ICIoIiArIGQuc2xpY2UoMCwgMikgKyAiKSAiICsgZC5zbGljZSgyLCA2KSArICItIiArIGQuc2xpY2UoNik7CiAgICAgIGlmIChk
Lmxlbmd0aCA+IDIpIHJldHVybiAiKCIgKyBkLnNsaWNlKDAsIDIpICsgIikgIiArIGQuc2xpY2UoMik7CiAgICAgIGlmIChkLmxl
bmd0aCA+IDApIHJldHVybiAiKCIgKyBkOwogICAgICByZXR1cm4gIiI7CiAgICB9LAogICAgbnVtZXJvczogKGQpID0+IGQuc2xp
Y2UoMCwgMTUpLAogIH07CgogIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoImlucHV0W2RhdGEtbWFzY2FyYV0iKS5mb3JFYWNo
KChlbCkgPT4gewogICAgY29uc3QgbWFzY2FyYSA9IG1hc2NhcmFzW2VsLmRhdGFzZXQubWFzY2FyYV07CiAgICBpZiAoIW1hc2Nh
cmEpIHJldHVybjsKICAgIGNvbnN0IGFwbGljYXIgPSAoKSA9PiB7CiAgICAgIGNvbnN0IG5vdm8gPSBtYXNjYXJhKGRpZ2l0b3Mo
ZWwudmFsdWUpKTsKICAgICAgaWYgKG5vdm8gIT09IGVsLnZhbHVlKSBlbC52YWx1ZSA9IG5vdm87CiAgICB9OwogICAgYXBsaWNh
cigpOyAvLyBmb3JtYXRhIG8gdmFsb3IgcXVlIGphIHZlbSBkbyBiYW5jbyAoYW8gZWRpdGFyKQogICAgZWwuYWRkRXZlbnRMaXN0
ZW5lcigiaW5wdXQiLCBhcGxpY2FyKTsKICAgIC8vIGJsb3F1ZWlhIGxldHJhcyBlIHNpbWJvbG9zIG5hIGhvcmEgZGUgZGlnaXRh
cgogICAgZWwuYWRkRXZlbnRMaXN0ZW5lcigia2V5cHJlc3MiLCAoZSkgPT4gewogICAgICBpZiAoZS5rZXkubGVuZ3RoID09PSAx
ICYmICEvXGQvLnRlc3QoZS5rZXkpICYmICFlLmN0cmxLZXkgJiYgIWUubWV0YUtleSkgZS5wcmV2ZW50RGVmYXVsdCgpOwogICAg
fSk7CiAgfSk7Cn0pKCk7Cg==
""",
    "membros/management/__init__.py": """

""",
    "membros/management/commands/__init__.py": """

""",
    "membros/management/commands/normalizar_documentos.py": """
aW1wb3J0IHJlCgpmcm9tIGRqYW5nby5jb3JlLm1hbmFnZW1lbnQuYmFzZSBpbXBvcnQgQmFzZUNvbW1hbmQKZnJvbSBkamFuZ28u
ZGIgaW1wb3J0IHRyYW5zYWN0aW9uCgpmcm9tIG1lbWJyb3MubW9kZWxzIGltcG9ydCBNZW1icm8KCkNBTVBPUyA9IFsiY3BmIiwg
InJnIiwgImNlbHVsYXIiLCAiY2VsdWxhcl9jb250YXRvIiwgImNlbHVsYXJfZmlsaG8iXQoKCmRlZiBfZGlnaXRvcyh2YWxvcik6
CiAgICByZXR1cm4gcmUuc3ViKHIiXEQiLCAiIiwgdmFsb3Igb3IgIiIpCgoKY2xhc3MgQ29tbWFuZChCYXNlQ29tbWFuZCk6CiAg
ICBoZWxwID0gKCJEZWl4YSBzb21lbnRlIG51bWVyb3MgZW0gQ1BGLCBSRyBlIHRlbGVmb25lcyBkb3MgbWVtYnJvcyBqYSBjYWRh
c3RyYWRvcy4gIgogICAgICAgICAgICAiVXNlIC0tc2ltdWxhciBwYXJhIGFwZW5hcyB2ZXIgbyBxdWUgc2VyaWEgZmVpdG8uIikK
CiAgICBkZWYgYWRkX2FyZ3VtZW50cyhzZWxmLCBwYXJzZXIpOgogICAgICAgIHBhcnNlci5hZGRfYXJndW1lbnQoIi0tc2ltdWxh
ciIsIGFjdGlvbj0ic3RvcmVfdHJ1ZSIsIGhlbHA9Im5hbyBncmF2YSBuYWRhIikKCiAgICBAdHJhbnNhY3Rpb24uYXRvbWljCiAg
ICBkZWYgaGFuZGxlKHNlbGYsICphcmdzLCAqKm9wdHMpOgogICAgICAgIG1lbWJyb3MgPSBsaXN0KE1lbWJyby5vYmplY3RzLmFs
bCgpKQoKICAgICAgICAjIENQRnMgcXVlIGZpY2FyaWFtIHJlcGV0aWRvcyBkZXBvaXMgZGUgdGlyYXIgcG9udG9zIGUgdHJhY29z
CiAgICAgICAgcG9yX2NwZiA9IHt9CiAgICAgICAgZm9yIG0gaW4gbWVtYnJvczoKICAgICAgICAgICAgcG9yX2NwZi5zZXRkZWZh
dWx0KF9kaWdpdG9zKG0uY3BmKSwgW10pLmFwcGVuZChtLnBrKQogICAgICAgIHJlcGV0aWRvcyA9IHtrOiB2IGZvciBrLCB2IGlu
IHBvcl9jcGYuaXRlbXMoKSBpZiBsZW4odikgPiAxfQogICAgICAgIGlkc19jb25mbGl0byA9IHtwayBmb3IgaWRzIGluIHJlcGV0
aWRvcy52YWx1ZXMoKSBmb3IgcGsgaW4gaWRzfQoKICAgICAgICBhanVzdGFkb3MsIHRhbWFuaG9fY3BmID0gMCwgW10KICAgICAg
ICBmb3IgbSBpbiBtZW1icm9zOgogICAgICAgICAgICBub3ZvcyA9IHt9CiAgICAgICAgICAgIGZvciBjYW1wbyBpbiBDQU1QT1M6
CiAgICAgICAgICAgICAgICBhbnRpZ28gPSBnZXRhdHRyKG0sIGNhbXBvKQogICAgICAgICAgICAgICAgaWYgYW50aWdvIGlzIE5v
bmU6CiAgICAgICAgICAgICAgICAgICAgY29udGludWUKICAgICAgICAgICAgICAgIGlmIGNhbXBvID09ICJjcGYiIGFuZCBtLnBr
IGluIGlkc19jb25mbGl0bzoKICAgICAgICAgICAgICAgICAgICBjb250aW51ZQogICAgICAgICAgICAgICAgbnVtZXJvID0gX2Rp
Z2l0b3MoYW50aWdvKQogICAgICAgICAgICAgICAgaWYgbnVtZXJvICE9IGFudGlnbzoKICAgICAgICAgICAgICAgICAgICBub3Zv
c1tjYW1wb10gPSBudW1lcm8KICAgICAgICAgICAgaWYgbGVuKF9kaWdpdG9zKG0uY3BmKSkgIT0gMTE6CiAgICAgICAgICAgICAg
ICB0YW1hbmhvX2NwZi5hcHBlbmQobS5waykKICAgICAgICAgICAgaWYgbm92b3M6CiAgICAgICAgICAgICAgICBhanVzdGFkb3Mg
Kz0gMQogICAgICAgICAgICAgICAgaWYgbm90IG9wdHNbInNpbXVsYXIiXToKICAgICAgICAgICAgICAgICAgICBNZW1icm8ub2Jq
ZWN0cy5maWx0ZXIocGs9bS5waykudXBkYXRlKCoqbm92b3MpCgogICAgICAgIGFjYW8gPSAic2VyaWFtIGFqdXN0YWRvcyIgaWYg
b3B0c1sic2ltdWxhciJdIGVsc2UgImFqdXN0YWRvcyIKICAgICAgICBzZWxmLnN0ZG91dC53cml0ZShzZWxmLnN0eWxlLlNVQ0NF
U1MoZiJ7YWp1c3RhZG9zfSBtZW1icm8ocykge2FjYW99LiIpKQogICAgICAgIGlmIHJlcGV0aWRvczoKICAgICAgICAgICAgaWRz
ID0gc29ydGVkKGlkc19jb25mbGl0bykKICAgICAgICAgICAgc2VsZi5zdGRvdXQud3JpdGUoc2VsZi5zdHlsZS5XQVJOSU5HKAog
ICAgICAgICAgICAgICAgZiJDUEYgcmVwZXRpZG8gZGVwb2lzIGRhIGxpbXBlemEgbm9zIG1lbWJyb3MgZGUgaWQge2lkc30uICIK
ICAgICAgICAgICAgICAgICJPIENQRiBkZXNzZXMgbWVtYnJvcyBOQU8gZm9pIGFsdGVyYWRvOiBjb3JyaWphIHBlbG8gL2FkbWlu
Ly4iKSkKICAgICAgICBpZiB0YW1hbmhvX2NwZjoKICAgICAgICAgICAgc2VsZi5zdGRvdXQud3JpdGUoc2VsZi5zdHlsZS5XQVJO
SU5HKAogICAgICAgICAgICAgICAgZiJDUEYgY29tIHF1YW50aWRhZGUgZGUgbnVtZXJvcyBkaWZlcmVudGUgZGUgMTEgbm9zIG1l
bWJyb3MgZGUgaWQge3NvcnRlZCh0YW1hbmhvX2NwZil9LiAiCiAgICAgICAgICAgICAgICAiQ29ycmlqYSBhbyBlZGl0YXIgbyBj
YWRhc3Ryby4iKSkK
""",
}

PASTA = Path.cwd()
FORMS = PASTA / "membros" / "forms.py"
FORM_HTML = PASTA / "membros" / "templates" / "membros" / "form_membro.html"
DETALHE = PASTA / "membros" / "templates" / "membros" / "detalhe_membro.html"
pendencias = []


def sair(msg):
    print("ERRO:", msg)
    sys.exit(1)


def carimbo():
    return time.strftime(".%Y%m%d-%H%M%S.bak")


def backup(caminho):
    destino = caminho.with_name(caminho.name + carimbo())
    shutil.copy2(caminho, destino)
    print(f"   copia de seguranca: {destino.name}")


def ler(caminho):
    if not caminho.exists():
        sair(f"arquivo nao encontrado: {caminho.relative_to(PASTA)}")
    return caminho.read_text(encoding="utf-8")


def gravar(caminho, texto):
    backup(caminho)
    caminho.write_text(texto, encoding="utf-8")


def instalar_arquivos():
    print("1) Arquivos novos")
    for rel, b64 in ARQUIVOS.items():
        destino = PASTA / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith("__init__.py") and destino.exists():
            continue  # nao mexe em pacotes que ja existem
        destino.write_bytes(base64.b64decode("".join(b64.split())))
        print("   ok", rel)


def atualizar_forms():
    print("2) membros/forms.py")
    texto = ler(FORMS)
    if "SomenteNumerosMixin" in texto:
        print("   ja esta atualizado")
        return
    m_import = re.search(r"^from \.models import .*$", texto, re.M)
    m_classe = re.search(r"^class MembroForm\(forms\.ModelForm\):", texto, re.M)
    if not m_import or not m_classe:
        print("   AVISO: nao consegui alterar sozinho. Faca duas mudancas em membros/forms.py:")
        print("     a) junto dos imports:  from .validadores import SomenteNumerosMixin")
        print("     b) troque a linha da classe por:  class MembroForm(SomenteNumerosMixin, forms.ModelForm):")
        pendencias.append("forms.py")
        return
    texto = texto.replace(
        m_classe.group(0), "class MembroForm(SomenteNumerosMixin, forms.ModelForm):", 1)
    texto = texto[: m_import.end()] + "\nfrom .validadores import SomenteNumerosMixin" + texto[m_import.end():]
    gravar(FORMS, texto)
    print("   validacao de CPF, RG e telefones ativada")


def atualizar_form_html():
    print("3) membros/templates/membros/form_membro.html")
    texto = ler(FORM_HTML)
    if "mascaras.js" in texto:
        print("   a mascara ja esta ativa")
        return
    pos = texto.rfind("</body>")
    if pos == -1:
        print("   AVISO: nao achei </body>. Acrescente antes do fim da pagina:")
        print("     <script src=\"{% static 'membros/js/mascaras.js' %}\"></script>")
        return
    if "{% load static" not in texto:
        texto = "{% load static %}\n" + texto
        pos = texto.rfind("</body>")
    tag = "<script src=\"{% static 'membros/js/mascaras.js' %}\"></script>\n"
    texto = texto[:pos] + tag + texto[pos:]
    gravar(FORM_HTML, texto)
    print("   mascara ativada no formulario")


def atualizar_detalhe():
    print("4) membros/templates/membros/detalhe_membro.html")
    texto = ler(DETALHE)
    if "|cpf" in texto:
        print("   ja esta atualizado")
        return
    trocas = [
        ("{% load static %}", "{% load static formatos %}"),
        ("{{ membro.cpf }}", "{{ membro.cpf|cpf }}"),
        ("{{ membro.celular }}", "{{ membro.celular|telefone }}"),
        ('{{ membro.celular_contato|default:"-" }}', '{{ membro.celular_contato|telefone|default:"-" }}'),
        ('{{ membro.celular_filho|default:"-" }}', '{{ membro.celular_filho|telefone|default:"-" }}'),
    ]
    mudou = False
    for antigo, novo in trocas:
        if antigo in texto:
            texto = texto.replace(antigo, novo, 1)
            mudou = True
        else:
            print(f"   AVISO: nao achei {antigo} (ajuste na mao, se quiser formatar esse campo)")
    if mudou:
        gravar(DETALHE, texto)
        print("   CPF e telefones formatados na ficha")


def normalizar():
    print("5) Cadastros ja existentes")
    simular = "--simular" in sys.argv
    if not simular:
        banco = PASTA / "db.sqlite3"
        if banco.exists():
            destino = banco.with_name(banco.name + carimbo())
            shutil.copy2(banco, destino)
            print(f"   copia de seguranca do banco: {destino.name}")
        else:
            print("   AVISO: db.sqlite3 nao encontrado na pasta; faca uma copia do seu banco antes de continuar.")
    comando = [sys.executable, "manage.py", "normalizar_documentos"] + (["--simular"] if simular else [])
    r = subprocess.run(comando)
    if r.returncode != 0:
        sair("a limpeza dos cadastros falhou; leia a mensagem acima e me envie o texto completo.")


def main():
    if not (PASTA / "manage.py").exists() or not (PASTA / "membros").is_dir():
        sair("rode este script dentro da pasta do projeto (onde esta o manage.py e a pasta membros).")
    instalar_arquivos()
    atualizar_forms()
    atualizar_form_html()
    atualizar_detalhe()
    if pendencias:
        print("\nATENCAO: termine o ajuste manual do forms.py e rode de novo este script.")
        sys.exit(1)
    if "--sem-normalizar" in sys.argv:
        print("5) limpeza dos cadastros antigos pulada (--sem-normalizar)")
    else:
        normalizar()
    print()
    print("Pronto! PARE o servidor (Ctrl + C) e rode de novo: python manage.py runserver")
    print("(e obrigatorio reiniciar: os filtros novos so sao carregados na partida)")


if __name__ == "__main__":
    main()
