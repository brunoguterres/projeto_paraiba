import psycopg2
import time

def calculo_balanco(matriz): #esta função realiza o cálculo do balanço
    for i in range(len(matriz)):
        if matriz[i][campo_cabeceira] == '1':
            pass
        else:
            for j in range(i-1,-1,-1):
                contador_montante = 0
                if matriz[i][campo_cotrecho] == matriz[j][campo_trechojus] :
                    a = float(matriz[i][campo_vazao_montante])
                    a += float(matriz[j][campo_vazao_jusante])
                    contador_montante += 1
                    if contador_montante == 2:
                        break

        matriz[i][campo_vazao_jusante] = float(matriz[i][campo_vazao_montante]) + float(matriz[i][campo_disponibilidade])
               
    return matriz.tolist()

def calculo_balanco_novo(dados): #esta função realiza o cálculo do balanço
    for i in range(len(dados)):
        if dados[i][campo_cabeceira] == '1':
            dados[i][campo_vazao_montante] = 0
        elif dados[i][campo_cabeceira] == '0':
            for j in range(len(dados)): # colocar um teste para finalizar laço após encontrar 2 COBACIAJUS
                if dados[i][campo_cotrecho] == dados[j][campo_trechojus] :
                    dados[i][campo_vazao_montante] = dados[i][campo_vazao_montante]+dados[j][campo_vazao_jusante]
        dados[i][campo_vazao_jusante] = dados[i][campo_vazao_montante]+float(dados[i][campo_disponibilidade])-float(dados[i][campo_captacao])
        if dados[i][campo_vazao_jusante] < 0:
            dados[i][campo_vazao_jusante] = 0
            dados[i][campo_deficit] = dados[i][campo_vazao_jusante]*-1
    return dados

##### EXECUÇÃO #####
# Parâmetros de conexão com o banco de dados
nome_do_banco = 'banco_teste'
usuario = 'postgres'
senha = 'cobrape'
host = 'localhost'
porta = '5433'

conn = psycopg2.connect(
    dbname = nome_do_banco,
    user = usuario,
    password = senha,
    host = host,
    port = porta
)

campo_cotrecho = 0
campo_cobacia = 1
campo_trechojus = 2
campo_trecho = 3
campo_cabeceira = 4
campo_vazao_montante = 5
campo_vazao_jusante = 6
campo_captacao = 7
campo_disponibilidade = 8
campo_deficit = 9

print('Lendo:', time.time())
# Ler o arquivo do BD e transformar em matriz (usa o numpy)

cursor = conn.cursor()
cursor.execute("""
SELECT *
FROM parana50000b
ORDER BY cobacia DESC
LIMIT 1
""")

# Converte os dados da tabela em uma lista de listas
dados = []
print(dados)
for row in cursor:
    lista_row = list(row)
    dados.append(lista_row)

print(dados)

# Fazer o balanço ()

dados = calculo_balanco_novo(dados)
'''
#atualizar o BD
t1 = (time.time())
print('Escrevendo:', t1)

#valor=[(matriz[i, 6],) for i in len(matriz)]
#cursor.execute("UPDATE parana50000 SET jusante = (%s);",("3"))



for i in range(len(matriz)):
    valor = str(matriz[i][6])
    valor2 = matriz[i][1]
    cursor.execute("UPDATE parana50000 SET jusante = (%s) WHERE cobacia = (%s)", (valor, valor2))


conn.commit()
conn.close()

t2 = (time.time())
print('Escrevendo:', t2)
'''

print('Banco de dados atualizado !!!')