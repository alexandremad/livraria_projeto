# Controle de Estoque da Livraria – Relatório Mensal de Material Evangelístico

Aplicação Django que reproduz o modelo físico (3 folhas A4), com cadastro de livrarias
(principais e auxiliares) e impressão fiel ao papel.

## Passo a passo

1. Instale o Python 3.10+ (python.org). No Windows, marque "Add Python to PATH".
2. Abra o terminal na pasta do projeto (onde está o `manage.py`).
3. Crie e ative o ambiente virtual:
   - Windows: `python -m venv venv` e `venv\Scripts\activate`
   - Linux/Mac: `python3 -m venv venv` e `source venv/bin/activate`
4. Instale o Django: `pip install -r requirements.txt`
5. Crie as tabelas:
   `python manage.py makemigrations estoque`
   `python manage.py migrate`
6. Carregue os 221 produtos do modelo (códigos, nomes e valores):
   `python manage.py carregar_produtos`
7. Crie seu usuário: `python manage.py createsuperuser`
8. Rode: `python manage.py runserver` e abra http://127.0.0.1:8000
9. Use:
   - **Livrarias** > Nova livraria (para auxiliar, escolha a livraria principal).
   - **Relatórios** > Novo relatório (livraria + mês). A folha abre igual ao papel: preencha
     Estoque Inicial, Entrada, Transferência e Qtd. de Vendas (Enter desce para a linha de baixo).
   - **Salvar** e depois **Imprimir**. Na janela de impressão: A4, retrato, margens "Nenhuma",
     escala 100%, e marque "Gráficos de segundo plano" (para as faixas escuras).
   - "Imprimir em branco" gera o modelo sem números, para preencher à mão.

## Onde ajustar
- Preços/produtos: `/admin/` > Produtos (vale para relatórios novos; os antigos guardam o valor da época).
- Nº de linhas em branco ("novos itens"): `estoque/constantes.py`.
- Textos fixos do cabeçalho: `estoque/constantes.py`.
- Visual da folha: `estoque/static/estoque/folha.css`.
- Logotipo: hoje é texto estilizado; para usar imagem, troque o bloco `.logo` em `_cabecalho.html`.
- Produtos novos no modelo físico: edite `estoque/dados_modelo.py` e rode `carregar_produtos` de novo
  (ou cadastre pelo admin escolhendo a Seção e a Ordem).

## Observação
Custo total = Qtd. de vendas x Valor unit. (calculado automaticamente). Se no seu controle o
custo for outra conta, altere `custo_total` em `estoque/models.py` e a função `recalcLinha` em `folha.js`.
