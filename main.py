"""

Esse módulo tem o objetivo de converter os lotes de TED do CNA240
ITAU para lotes PIX para
"""
import os

directory_path = './input/'
extension = '.TXT'
modified_lines = []
contagem_blocos = 0

def get_files_with_ext(directory_path, extension):
    """
    Pega os
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



for file_name in txt_files:
    with open(os.path.join(directory_path, file_name)) as file:
        for idx, line in enumerate(file.readlines()):

            """CAPTANDO HEADER DO ARQUIVO - sem mudancas"""
            if line[7] == "0":
                modified_lines.append(line)

            """
            CAPTANDO HEADERS DOS LOTES DE TED
            
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
                modified_lines.append(modified_line)

                block_type = "TED" # Classifica o bloco que está sendo tratado
                contagem_blocos += 1

            # Impede que lotes de serviços não TED sejam tratados
            elif line[7] == "1" and  line[9:13] != "2041":
                block_type = "OUTROS"

            """
            CAPTANDO DETALHES SEGMENTO A PARA BLOCOS TIPO TED
            
            MUDANCAS:
            TROCA CODIGO DO LOTE PARA CONTAGEM DE LOTE
                É seqüencial, iniciando-se em 0001. Todos os pagamentos 
                de um lote devem ter o mesmo"Código de Lote".
            TROCA DA CAMARA CENTRALIZADORA PARA SPI
                [17:20] > 009
            TROCA IDENTIFICACAO TIPO TRANSFERÊNCIA PARA C/C
                [112:114] > 001
            
            """
            # ATUA NO DETALHE SEGMENTO A
            if line[7] == "3" and block_type == "TED" and line[13] =="A" :
                modified_line = line[:3] + f"000{contagem_blocos}" + line[7:]

                modified_line = modified_line[:17] + "009" + modified_line[20:]

                modified_line = modified_line[:112] + "01" + modified_line[114:]

                modified_lines.append(modified_line)

    output_file = open(f"./output/PIX{file_name}", 'w')

    for i in modified_lines:
        output_file.write(f"{i}")
    output_file.close()


