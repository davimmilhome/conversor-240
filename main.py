"""
CONTRIBUIDORES:

DAVI MILHOME

FUNÇÃO:

Esse módulo tem o objetivo de converter os lotes de TED do CNA240
ITAU para lotes PIX para

NOTAS:

Devido a sua construção, essse conversor só funciona com
arquivos de menos de 10 lotes. Caso o remessa tenha mais de 10
lotes, acarretará em problemas de contagem, então, nesse
cenário é necessário adaptar o arquivo.
"""
import os

directory_path = './input/'
extension = '.TXT'
modified_lines = []
contagem_blocos = 0
contagem_registros = 0

def get_files_with_ext(directory_path, extension):
    """
    Pega os arquivos dentro da pasta
    :param directory_path: define o path em que o arquivo está
    :param extension:  define a extensão do arquivo a ser captado
    :return: retorna o nome dos arquivos daquela extensão em uma lista
    """
    files_with_ext = []
    for file in os.listdir(directory_path):
        if file.endswith(extension):
            files_with_ext.append(file)
    return files_with_ext

txt_files = get_files_with_ext(directory_path, extension) # Instância a função

# Começo do tratamento
for file_name in txt_files:
    with open(os.path.join(directory_path, file_name)) as file:
        for idx, line in enumerate(file.readlines()):

            """
             - CAPTANDO HEADER DO ARQUIVO - sem mudancas
            """
            if line[7] == "0":
                modified_lines.append(line)

            """
             - CAPTANDO HEADERS DOS LOTES DE TED
            
            CLASSIFICACAO:
            2041 - ted para outro titular
            2045 - pix transferência
            
            MUDANCAS:
            se o tipo for igual a 1, header de lote
            e tipo de operação igual a 2041
                troca o 2041 por 2045
                block_type  = "TED"
                atualiza contagem de blocos (+=1)
            
            No caso, atribui-se block_type para evitar que algum outro
            tipo de bloco não TED seja utilizado no tratamento
            """
            if line[7] == "1" and line[9:13] == "2041":
                modified_line = line[:9] + "2045" + line[13:]

                block_type = "TED" # Classifica o bloco que está sendo tratado
                contagem_blocos += 1

                modified_line = line[:3] + f"000{contagem_blocos}" + line[7:]

                modified_lines.append(modified_line)

            # Impede que lotes de serviços não TED sejam tratados
            elif line[7] == "1" and  line[9:13] != "2041":
                block_type = "OUTROS"

            """
             - CAPTANDO DETALHES SEGMENTO A PARA BLOCOS TIPO TED
            
            MUDANCAS:
            TROCA CODIGO DO LOTE PARA CONTAGEM DE LOTE
                É sequencial, iniciando-se em 0001. Todos os pagamentos 
                de um lote devem ter o mesmo"Código de Lote".
                [03:07] > 000contagemlote
            TROCA DA CAMARA CENTRALIZADORA PARA SPI
                [17:20] > 009
            TROCA IDENTIFICACAO TIPO TRANSFERÊNCIA PARA C/C
                [112:114] > 001
            
            """
            if line[7] == "3" and block_type == "TED" and line[13] =="A" :
                modified_line = line[:3] + f"000{contagem_blocos}" + line[7:]

                modified_line = modified_line[:17] + "009" + modified_line[20:]

                modified_line = modified_line[:112] + "01" + modified_line[114:]

                modified_lines.append(modified_line)





            """
             - CAPTANDO TRAILLER DO LOTE
             
             MUDANCAS:
             TROCA CODIGO DO LOTE PARA CONTAGEM DE LOTE
                É seqüencial, iniciando-se em 0001. Todos os pagamentos 
                de um lote devem ter o mesmo"Código de Lote" e o codigo
                também deve estar no trailler
              [03:07] > 000contagemlote  
            """
            if line[7] == "5" and block_type == "TED":
                modified_line = line[:3] + f"000{contagem_blocos}" + line[7:]

                modified_lines.append(modified_line)
            """
             - CAPTANDO TRAILLER DO ARQUIVO
            
            CLASSIFICACAO:
            • Trailer de Arquivo:
            - Quantidade de lotes do arquivo = somatória dos registros 
            tipo 1;
            - Quantidade total de registros no arquivo = somatória 
            dos registros tipo 0, 1, 3, 5 e 9.

            MUDANCAS:
  
            """



            # # Compensação de preenchimento com zeros na contagem
            # while len(str(contagem_registros)) != 6:
            #     contagem_registros = "0" + str(contagem_registros)

            if line[7] == "9":
                #contagem de registros
                for i in modified_lines:
                    if i[7] in ["0","1","3","5"]:
                        contagem_registros += 1
                contagem_registros += 1  # Compensação contagem trailler-arquivo
                contagem_registros = str(contagem_registros)
                # Compensação de preenchimento com zeros na contagem
                while len(contagem_registros) != 6:
                    contagem_registros = "0" + contagem_registros

                modified_line = line[:17] + f"00000{contagem_blocos}" + line[23:]

                modified_line = line[:23] + contagem_registros + line[29:]

                modified_lines.append(modified_line)

    # Escreve o arquivo de saída
    output_file = open(f"./output/PIX{file_name}", 'w')
    for i in modified_lines:
        output_file.write(f"{i}")
    output_file.close()


