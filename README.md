# Gestão de Membros, Estoque de Livraria e Reuniões

Sistema web em Django para a Igreja Pentecostal Deus é Amor, que reúne em um só lugar:

- **Estoque da Livraria**: o *Relatório Mensal de Material Evangelístico*, igual ao modelo físico de papel, com cadastro de livrarias principais e auxiliares e impressão em 3 folhas A4.
- **Cadastro de Membros**: ficha completa do membro, com foto 3x4, documentos anexados e impressão da ficha.
- **Lista de Presença de Reunião**: cadastro de participantes por região e lista de impressão por data.

Roda no navegador, então funciona em qualquer sistema operacional (Mac, Windows, Linux, Android e iOS) dentro da mesma rede.

---

## Sumário

1. [Funcionalidades](#funcionalidades)
2. [Tecnologias](#tecnologias)
3. [Estrutura do projeto](#estrutura-do-projeto)
4. [Instalação](#instalação)
5. [Primeiro uso](#primeiro-uso)
6. [Impressão](#impressão)
7. [Acesso por outros aparelhos](#acesso-por-outros-aparelhos-na-rede)
8. [Fotos e documentos](#fotos-e-documentos-dos-membros)
9. [Importar e juntar dados](#importar-e-juntar-dados)
10. [Backup](#backup)
11. [Segurança e uso em produção](#segurança-e-uso-em-produção)
12. [Personalização](#personalização)
13. [Solução de problemas](#solução-de-problemas)

---

## Funcionalidades

### Estoque da Livraria (`/livraria/`)

- Relatório mensal fiel ao modelo físico: 3 páginas A4, 2 colunas por página, com as seções, códigos, nomes e valores já preenchidos (221 produtos).
- Campos de preenchimento: **Estoque Inicial, Entrada, Transferência, Qtd. de Vendas**.
- **Custo Total** (Qtd. de Vendas × Valor Unit.) e **TOTAL** de cada coluna calculados na hora.
- Linhas em branco para **novos itens** (código, nome e valor digitados à mão).
- Cabeçalho do relatório (porte, endereço, dirigente, vol. estoque, vol. financeira) copiado do cadastro da livraria e editável na folha.
- Cadastro de **livrarias principais e auxiliares** (a auxiliar é ligada a uma principal).
- Impressão fiel ao papel e opção de **imprimir em branco**, para preencher à mão.
- O valor de cada produto fica guardado no relatório, então mudar um preço depois não altera os relatórios antigos.
- Atalho no preenchimento: a tecla **Enter** desce para a linha de baixo.

### Cadastro de Membros (tela inicial → *Lista de Membros*)

- Ficha em 5 seções: dados pessoais, endereço e contato, dados familiares e saúde, vida ministerial e documentos.
- **Foto 3x4** com conversão automática para JPEG (aceita fotos de iPhone em HEIC, Android, PNG e WebP).
- Anexo de documentos: CPF e RG, comprovante de endereço, certidões de nascimento e de casamento.
- Visualização da ficha com os documentos em links e **impressão em A4**.
- Editar, apagar e listar membros.

### Lista de Presença (`/reuniao/`)

- Cadastro de participantes com **nome e região** (74 regiões em lista).
- Lista de impressão em 4 colunas, **por data**, com o total de participantes do dia.
- Importação dos participantes antigos do MySQL, mantendo a data original.

---

## Tecnologias

| Item | Detalhe |
| --- | --- |
| Linguagem | Python 3.12 ou mais novo |
| Framework | Django 5.x |
| Banco de dados | SQLite (`db.sqlite3`, um só arquivo para todos os módulos) |
| Imagens | Pillow e pillow-heif |
| Interface | HTML, CSS e JavaScript simples; Bootstrap 5 nas telas de membros |
| Fuso e idioma | `America/Sao_Paulo`, `pt-br` |

---

## Estrutura do projeto

```
livraria_projeto/
├── manage.py
├── requirements.txt
├── db.sqlite3                  # banco de dados único
├── media/                      # fotos e documentos enviados (criada ao enviar o primeiro arquivo)
├── config/                     # configurações do projeto
│   ├── settings.py
│   └── urls.py
├── estoque/                    # livraria: relatório mensal, livrarias, tela inicial
├── membros/                    # cadastro de membros
├── reuniao/                    # lista de presença
│   └── static/reuniao/img/     # logo.png e horizontal_portugues.png
├── juntar_bancos.py            # utilitário para juntar dois bancos SQLite
└── venv/                       # ambiente virtual (não vai para o Git)
```

A pasta `cadastro/`, se existir, é a configuração antiga do projeto de membros e não é usada por este projeto.

---

## Instalação

Requisitos: **Python 3.12+** (python.org). No Windows, marque *Add Python to PATH* na instalação.

1. Entre na pasta do projeto:

   ```bash
   cd livraria_projeto
   ```

2. Crie e ative o ambiente virtual (sem ponto no final do nome):

   ```bash
   python3 -m venv venv
   source venv/bin/activate          # Mac e Linux
   venv\Scripts\activate             # Windows
   ```

   Com o ambiente ativo, o terminal mostra `(venv)` no começo da linha.

3. Instale as dependências. O `requirements.txt` deve conter:

   ```
   Django>=5.0,<6.0
   pillow
   pillow-heif
   ```

   ```bash
   pip install -r requirements.txt
   ```

4. Crie as tabelas do banco:

   ```bash
   python manage.py makemigrations estoque membros reuniao
   python manage.py migrate
   ```

5. Carregue os produtos do modelo físico (221 itens com códigos, nomes e valores):

   ```bash
   python manage.py carregar_produtos
   ```

6. Crie o usuário administrador:

   ```bash
   python manage.py createsuperuser
   ```

7. Rode o sistema:

   ```bash
   python manage.py runserver
   ```

   Abra http://127.0.0.1:8000/ no navegador e entre com o usuário criado.

---

## Primeiro uso

| Endereço | O que abre |
| --- | --- |
| `/` | Tela inicial, com os atalhos dos módulos |
| `/livraria/` | Relatórios mensais e livrarias |
| `/home/` | Lista de membros |
| `/reuniao/` | Cadastro de participantes da reunião |
| `/reuniao/impressao/` | Lista de presença de hoje (ou `?data_reuniao=AAAA-MM-DD`) |
| `/admin/` | Painel administrativo (usuários, produtos, preços) |

**Livraria:**

1. Em **Livrarias**, clique em **+ Nova livraria**. Para uma auxiliar, escolha a livraria principal no campo correspondente. Cadastre a principal antes.
2. Em **Relatórios**, clique em **+ Novo relatório**, escolha a livraria e o mês (formato `2026-09`).
3. Preencha a folha e clique em **Salvar**. Depois use **Imprimir**.

**Usuários:** crie os operadores em `/admin/` → *Usuários*. Quem só precisa usar o sistema não precisa ser administrador.

---

## Impressão

Todas as impressões usam o diálogo do navegador. Para a livraria e a ficha de membros:

- Papel **A4**, orientação **retrato**.
- Margens: **Nenhuma** (livraria) ou a padrão (ficha e lista de presença).
- Escala **100%**.
- Marque **Gráficos de segundo plano** (Chrome) ou **Imprimir fundos** (Firefox e Safari), para as faixas escuras aparecerem.

O relatório da livraria sai em **3 folhas**. Para imprimir o modelo sem números, use **Imprimir em branco** na lista de relatórios.

---

## Acesso por outros aparelhos na rede

1. Descubra o IP do computador:
   - Mac: `ipconfig getifaddr en0`
   - Windows: `ipconfig`
   - Linux: `hostname -I`
2. Suba o servidor aceitando conexões externas:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. No outro aparelho, na **mesma rede Wi-Fi**, abra `http://IP-DO-COMPUTADOR:8000/`.

O computador precisa ficar ligado, com o servidor rodando. O IP pode mudar quando a rede muda. Se o sistema operacional perguntar sobre conexões de entrada, permita.

---

## Fotos e documentos dos membros

- Os arquivos ficam na pasta `media/` (`MEDIA_ROOT`), servida em `/media/`.
- Toda foto enviada é convertida para JPEG (HEIC do iPhone, PNG e WebP incluídos), com a orientação corrigida e o tamanho reduzido.
- Ao mover o projeto para outro computador, **leve a pasta `media/` junto** com o `db.sqlite3`. O banco guarda só o caminho dos arquivos.

---

## Importar e juntar dados

**Participantes antigos do MySQL (reunião):**

1. No phpMyAdmin, exporte a tabela `participantes` em **CSV**, com a primeira linha de títulos (`nome`, `setor` e `data_cadastro`).
2. Rode:

   ```bash
   python manage.py importar_participantes caminho/do/arquivo.csv
   ```

   A data original é mantida, e rodar de novo não duplica registros.

**Juntar dois bancos SQLite (por exemplo, o de membros com o da livraria):**

```bash
python juntar_bancos.py banco_destino.sqlite3 banco_origem.sqlite3
python manage.py migrate
```

O script cria uma cópia de segurança do banco de destino antes de alterar, e o de origem só é lido.

---

## Backup

Tudo o que importa está em dois lugares:

- **`db.sqlite3`**: todos os dados.
- **`media/`**: fotos e documentos.

Copie os dois para um pente USB ou nuvem de forma regular, com o servidor parado (ou em horário sem uso). Para restaurar, coloque os dois de volta na pasta do projeto.

---

## Segurança e uso em produção

O projeto vem configurado para **uso local e de teste**. Antes de usar com dados reais em rede aberta ou na internet:

- Troque a `SECRET_KEY` em `config/settings.py` por uma chave longa e secreta, fora do repositório.
- Defina `DEBUG = False` e liste os endereços em `ALLOWED_HOSTS` (hoje está `["*"]`).
- Não use o `runserver` em produção: use um servidor adequado (por exemplo Gunicorn com Nginx) e HTTPS.
- A pasta `media/` é servida **sem exigir login**. Ela guarda fotos, CPF, RG e certidões. Em produção, proteja o acesso a esses arquivos.
- Os membros têm **dados pessoais e de saúde**. Restrinja o acesso a pessoas autorizadas, mantenha cópias de segurança protegidas e trate os dados conforme a LGPD.
- Se usar Git, **não envie** `db.sqlite3`, `media/` nem `venv/`. Coloque-os no `.gitignore`.

---

## Personalização

| O que mudar | Onde |
| --- | --- |
| Preço ou nome de um produto | `/admin/` → *Produtos* (vale para os relatórios novos) |
| Produtos e seções do modelo físico | `estoque/dados_modelo.py` e depois `python manage.py carregar_produtos` |
| Linhas em branco e textos fixos do cabeçalho do relatório | `estoque/constantes.py` |
| Visual e impressão da folha da livraria | `estoque/static/estoque/folha.css` |
| Regiões da lista de presença | `reuniao/regioes.py` |
| Logos da lista de presença | `reuniao/static/reuniao/img/` |
| Fuso horário e idioma | `config/settings.py` (`TIME_ZONE`, `LANGUAGE_CODE`) |

Regras de cálculo: **Custo Total = Qtd. de Vendas × Valor Unit.** Se o seu controle usar outra conta, altere `custo_total` em `estoque/models.py` e a função `recalcLinha` em `estoque/static/estoque/folha.js`.

---

## Solução de problemas

| Mensagem ou sintoma | Causa e solução |
| --- | --- |
| `source: no such file or directory: venv/bin/activate` | O ambiente virtual não foi criado ou o nome tem um ponto no final. Rode `python3 -m venv venv`. |
| `No installed app with label 'reuniao'` | Falta `"reuniao"` no `INSTALLED_APPS` de `config/settings.py` (confira se é o arquivo da pasta `config`). |
| `ModuleNotFoundError: No module named 'inicio'` | O `INSTALLED_APPS` lista um app que não existe na pasta. Apague a linha. |
| `NoReverseMatch ... 'reuniao' not found` | Um link usa o nome errado. Use `{% url 'reuniao_cadastro' %}`. |
| `TooManyFieldsSent` ao salvar a folha da livraria | Falta `DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000` no `config/settings.py`. |
| `no such table: ...` | Faltou rodar `python manage.py migrate` (e `makemigrations` do app). |
| Página 404 em `/reuniao/` | Falta a rota `path("reuniao/", include("reuniao.urls"))` em `config/urls.py`. |
| "Envie uma imagem válida" ao anexar foto | A foto está em formato que o Pillow não abre (HEIC). Confirme que o `pillow-heif` está instalado e que `clean_foto` está no `membros/forms.py`. |
| A foto ou o documento não aparece na ficha | Confira `MEDIA_URL`, `MEDIA_ROOT` e a linha `static(...)` no `config/urls.py`, e se o campo `foto` existe no modelo. |
| Não abre de outro aparelho | Use `runserver 0.0.0.0:8000`, o IP do computador e a mesma rede Wi-Fi. Algumas redes e hotspots bloqueiam a comunicação entre aparelhos. |
| Faixas escuras não saem na impressão | Ative *Gráficos de segundo plano* ou *Imprimir fundos* no diálogo de impressão. |
| `Port is already in use` | Há outro servidor rodando. Pare-o com `Ctrl + C` ou use outra porta: `python manage.py runserver 8001`. |

Para ver a causa de qualquer falha de configuração, rode `python manage.py check`.