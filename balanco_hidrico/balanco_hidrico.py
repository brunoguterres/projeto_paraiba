import numpy as np
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
                    matriz[i][campo_vazao_montante] += float(matriz[j][campo_vazao_jusante])
                    contador_montante += 1
                    if contador_montante == 2:
                        break

        matriz[i][campo_vazao_jusante] = float(matriz[i][campo_vazao_montante]) + float(matriz[i][campo_disponibilidade])
               
    return matriz.tolist()

##### EXECUÇÃO #####
# Parâmetros de conexão com o banco de dados
nome_do_banco = 'teste_tabela'
usuario = 'postgres'
senha = 'tonico'
host = 'localhost'

conn = psycopg2.connect(
    dbname = nome_do_banco,
    user = usuario,
    password = senha,
    host = host,
    port = porta
)

campo_cotrecho = 0  # vai ser o cotrecho
campo_cobacia = 1 # vai ser a cobacia
campo_trechojus = 2  # vai ser o ntutrjusante
campo_disponibilidade = 3  # vai ser a disponibilidade no caso 1
campo_cabeceira = 4 # cabeceira
campo_vazao_montante = 5 # montante
campo_vazao_jusante = 6  # jusante
campo_deficit = 7   # vazio
campo_valor_deficit = 8  # vazio

print('Lendo:', time.time())
# Ler o arquivo do BD e transformar em matriz (usa o numpy)

cursor = conn.cursor()
cursor.execute("""
SELECT *
FROM parana50000
""")

# Converte os dados da tabela em uma lista de listas
dados = []
for row in cursor:
    dados.append(row)

# Transforma a lista de listas em uma matriz
matriz = np.array(dados)
print('Calculando:', time.time())

# Fazer o balanço ()

matriz = calculo_balanco(matriz)

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


print('Banco de dados atualizado !!!')