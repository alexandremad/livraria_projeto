# Linhas em branco do modelo físico (onde o usuário escreve itens novos)
# chave: (página, coluna) -> quantidade de linhas e se tem o título "ESPAÇO PARA NOVOS ITENS"
LINHAS_LIVRES = {
    (1, 1): {"qtd": 5, "cabecalho": False},   # linhas em branco no fim da coluna 1 da pág. 1
    (2, 2): {"qtd": 11, "cabecalho": True},   # "ESPAÇO PARA NOVOS ITENS" pág. 2
    (3, 2): {"qtd": 4, "cabecalho": True},    # "ESPAÇO PARA NOVOS ITENS" pág. 3
}

# Texto fixo do cabeçalho (igual ao papel)
CABECALHO_FIXO = {
    "igreja": "DEUS É AMOR",
    "subtitulo": "IGREJA PENTECOSTAL",
    "endereco": "RUA ALEXANDRE LEVI, 50 - CAMBUCI - SÃO PAULO/SP",
    "cep": "CEP:01520-000",
    "conferencia": "CONFERÊNCIA DE LIVRARIA: (11) 3348-0828 / RAMAIS: 132 / 849",
    "email": "conferencia.livraria@ipda.com.br",
    "titulo": "RELATÓRIO MENSAL DE MATERIAL EVANGELISTICO",
    "aviso": "ESTE RELATÓRIO DEVE SER LANÇADO NA PLATAFORMA DE RELATÓRIO ON-LINE PELO VOL. FINANCEIRO(A).",
}
