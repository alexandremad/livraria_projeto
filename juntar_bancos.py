"""
Junta o banco do app MEMBROS dentro do banco da LIVRARIA (um único db.sqlite3).

Uso (com o servidor parado):
    python juntar_bancos.py  CAMINHO/livraria/db.sqlite3  CAMINHO/membros/db.sqlite3

- O banco de destino (livraria) é copiado para um .bak antes de qualquer alteração.
- O banco de origem (membros) só é lido, nunca alterado.
- Copia a tabela membros_membro (com seus dados) e registra as migrações do app membros.
- Usuários, permissões e tipos de conteúdo NÃO são copiados: o próprio Django recria
  as permissões no próximo `python manage.py migrate`.
"""
import shutil
import time
import sqlite3
import sys
from pathlib import Path

TABELAS = ["membros_membro"]
APPS_MIGRACOES = ["membros"]


def main(destino, origem):
    destino, origem = Path(destino), Path(origem)
    for p in (destino, origem):
        if not p.exists():
            sys.exit(f"Arquivo não encontrado: {p}")

    backup = destino.with_name(destino.name + time.strftime(".%Y%m%d-%H%M%S.bak"))
    shutil.copy2(destino, backup)
    print(f"Backup criado: {backup}")

    con = sqlite3.connect(destino, isolation_level=None)  # transação controlada à mão
    con.execute(f"ATTACH DATABASE '{origem.as_posix()}' AS o")

    try:
        con.execute("BEGIN")
        for t in TABELAS:
            existe = con.execute("SELECT 1 FROM main.sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()
            if existe:
                raise RuntimeError(f"A tabela {t} já existe no banco de destino; nada foi alterado.")
            sql = con.execute("SELECT sql FROM o.sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()
            if not sql:
                raise RuntimeError(f"A tabela {t} não existe no banco de origem.")
            con.execute(sql[0])
            con.execute(f'INSERT INTO main."{t}" SELECT * FROM o."{t}"')
            for (isql,) in con.execute(
                "SELECT sql FROM o.sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL", (t,)
            ).fetchall():
                con.execute(isql)
            seq = con.execute("SELECT seq FROM o.sqlite_sequence WHERE name=?", (t,)).fetchone()
            if seq:
                con.execute("DELETE FROM main.sqlite_sequence WHERE name=?", (t,))
                con.execute("INSERT INTO main.sqlite_sequence(name, seq) VALUES (?, ?)", (t, seq[0]))
            n = con.execute(f'SELECT COUNT(*) FROM main."{t}"').fetchone()[0]
            print(f"{t}: {n} registro(s) copiado(s)")

        for app in APPS_MIGRACOES:
            con.execute(
                "INSERT INTO main.django_migrations(app, name, applied) "
                "SELECT app, name, applied FROM o.django_migrations "
                "WHERE app=? AND name NOT IN (SELECT name FROM main.django_migrations WHERE app=?)",
                (app, app),
            )
        con.execute("COMMIT")
    except Exception as e:
        con.execute("ROLLBACK")
        con.close()
        shutil.copy2(backup, destino)
        sys.exit(f"ERRO: {e}\nO banco de destino foi mantido como estava.")

    ok = con.execute("PRAGMA integrity_check").fetchone()[0]
    print("Verificação de integridade:", ok)
    con.close()
    print("Pronto. Agora rode: python manage.py migrate")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])