"""
CONTRIBUIDORES:

DAVI MILHOME

FUNÇÃO:

A função implementada neste módulo tem objetivo de realizar aconversão
de lotes de TED do arquivo CNA240 Itaú para lotes PIX.
A função get_files_with_ext é utilizada para coletar todos os arquivos
com a extensão ".TXT" que se encontram na pasta "input/".
Em seguida, a função lê cada linha do arquivo em questão e realiza
as seguintes operações:

Captura o header do arquivo sem modificá-lo.

Captura os headers dos lotes de TED e, se o tipo for igual a 1 e o
tipo de operação for igual a 2041, realiza as seguintes modificações:
Troca o tipo de operação de 2041 para 2045. Define a variável
block_type como "TED" para evitar que outros tipos de bloco não TED
sejam tratados. Atualiza a contagem de blocos no arquivo de
saída e a contagem total de blocos no arquivo de entrada.
Zera a contagem de registros no lote. Impede que lotes de serviços
não TED sejam tratados.

Captura os detalhes do segmento A para blocos tipo TED e, se block_type
for igual a "TED" e a linha se referir ao segmento A, realiza as
seguintes modificações:

Troca o código do lote para a contagem de lote de saída sequencial,
iniciando-se em 0001.
Troca a câmara centralizadora para "SPI".
Troca a identificação de tipo de transferência para "C/C".

NOTAS:


"""
import os
import itertools

directory_path = './input/'
output_path = "./output/P"
extension = '.TXT'



# Variaveis do arquivo de entrada
contagem_lotes_input = 0

# Variaveis do arquivo de saida
modified_lines_TED = []
next_line = "" # Ferramenta de iteração

contagem_lotes_output = 0
contagem_lotes_output_str = ""

contagem_registros_lote = 0
contagem_registros_lote_str = ""
contagem_registros_output = 0
contagem_registros_output_str = ""

# Variáveis de troca
cod_camara = "009" #SPI
tipo_tranferencia_cc = "01"

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

txt_files = get_files_with_ext(directory_path, extension) # Instancia a função

# Começo do tratamento
for file_name in txt_files:
    # Zerando contagens para cada novo arquivo processado
    contagem_lotes_input = 0
    contagem_registros_output = 0
    contagem_lotes_output = 0
    modified_lines_TED = []
    next_line = ""
    block_type = ""

    # Lê cada linha do arquivo na fila e aplica a lógica
    with open(os.path.join(directory_path, file_name)) as file:
        lines = file.readlines()
        for idx, line in enumerate(lines):
            """* CAPTANDO HEADER DO ARQUIVO - sem mudancas"""
            if line[7] == "0":
                modified_lines_TED.append(line)

            """
             * CAPTANDO HEADERS DOS LOTES DE TED
            
            CLASSIFICACAO:
            2041 - ted para outro titular
            2045 - pix transferência
            
            MUDANCAS:
            se o tipo for igual a 1, header de lote
            e tipo de operação igual a 2041
                troca o 2041 por 2045
                block_type  = "TED"
                No caso, atribui-se block_type para evitar que algum outro
                tipo de bloco não TED seja utilizado no tratamento
                att contagem de blocos do output (+=1)
                att contagem blocos total do input em questao  (+=1)
                att contagem de registros no lote  (=0)
            """
            if line[7] == "1" and line[9:13] == "2041":
                block_type = "TED" # Classifica o lote que está sendo tratado
                contagem_lotes_input  += 1
                contagem_registros_lote = 0 # Zera a contagem de registros
                contagem_lotes_output += 1
                contagem_lotes_output_str = str(contagem_lotes_output)
                while len(contagem_lotes_output_str) != 4:
                    contagem_lotes_output_str = '0' +  contagem_lotes_output_str

                modified_line = (
                        line[:3] +
                        contagem_lotes_output_str
                        + line[7:]
                )
                modified_line = (
                        modified_line[:9]
                        + "2045" +
                        modified_line[13:]
                )

                modified_lines_TED.append(modified_line)

            # Impede que lotes de serviços não TED sejam tratados
            elif line[7] == "1" and  line[9:13] != "2041":
                block_type = "OUTROS"
                contagem_lotes_input += 1
                contagem_registros_lote = 0

            """
              * CAPTANDO DETALHES SEGMENTO A PARA BLOCOS TIPO TED
            
            MUDANCAS:
            Troca código do lote para contagem de lote output
                É sequencial, iniciando-se em 0001. Todos os pagamentos 
                de um lote devem ter o mesmo"Código de Lote".
                
            [03:07] = contagem_lotes_output_str
                
            TROCA DA CAMARA CENTRALIZADORA PARA SPI
            [17:20] = 009
                
            TROCA IDENTIFICACAO TIPO TRANSFERÊNCIA PARA C/C 
            [112:114] = 001
            
            """
            if line[7] == "3" and block_type == "TED" and line[13] =="A":
                contagem_registros_lote += 1
                contagem_registros_lote_str = str(contagem_registros_lote)
                while len(contagem_registros_lote_str) != 5:
                    contagem_registros_lote_str = '0' + contagem_registros_lote_str

                modified_line = line[:3] + contagem_lotes_output_str + line[7:]
                modified_line = (
                        modified_line[:8]
                         + contagem_registros_lote_str
                         + modified_line[13:]
                )
                modified_line = (
                        modified_line[:17]
                        + cod_camara
                        + modified_line[20:]
                )
                modified_line = (
                        modified_line[:112]
                        + tipo_tranferencia_cc
                        + modified_line[114:]
                )

                # Auste referente ao erro do sypag
                """
                Observe, precisamos do código abaixo pois o arquivo do 
                syspag, nos registros detalhe do tipo A traz o CNPJ de 
                maneira errônea (sim, têm um erro na formação do file
                do syspag). Sendo assim, pegamos a informação de CNPJ 
                que está correta no registro B, abaixo A e insere no
                registro A que será salvo.
                """
                if idx < len(lines) - 1:
                    next_line = next(itertools.islice(lines, idx + 1, None))

                modified_line = (
                        modified_line[:203]
                        + next_line[18:32] # Pegando CNPJ da próxima linha
                        + modified_line[217:]
                )

                modified_lines_TED.append(modified_line)

            """
            * CAPTANDO TRAILLER DO LOTE
             
             MUDANCAS:
             Troca código do lote para contagem de lote output
                É sequencial, iniciando-se em 0001. Todos os pagamentos 
                de um lote devem ter o mesmo"Código de Lote".
                
            [03:07] = contagem_lotes_output_str  
            
            Troca contagem de registros do lote
            Nessa contagem, é necesário adicionar 2 para levar
            em consideração o header e o trailer
            """
            if line[7] == "5" and block_type == "TED":
                # Desconto do trailer e header lote
                contagem_registros_lote = contagem_registros_lote + 2
                contagem_registros_lote_str = str(contagem_registros_lote)
                while len(contagem_registros_lote_str) != 6:
                    contagem_registros_lote_str = '0' + contagem_registros_lote_str

                modified_line = (
                        line[:3]
                        + contagem_lotes_output_str
                        + line[7:]
                )
                modified_line = (
                        modified_line[:17]
                        + contagem_registros_lote_str
                        + modified_line[23:]
                )


                modified_lines_TED.append(modified_line)
            """
             - CAPTANDO TRAILLER DO ARQUIVO
            
            CLASSIFICACAO:
            • Trailer de Arquivo:
            - Quantidade de lotes do arquivo = somatória dos registros 
            tipo 1;
            
            - Quantidade total de registros no arquivo = somatória 
            dos registros tipo 0, 1, 3, 5 e 9. Necessario adicionar
            1 para levar em consideração o registro 9 trailler arquivo

            MUDANCAS:
            Conta a quantidade de registros presentes em modified_lines
            e preenche no trailler do arquivo
            
            além disso, muda o len contagem de lotes e preenche no trailler
            do arquivo
            """
            if line[7] == "9":
                #contagem de registros
                for i in modified_lines_TED:
                    if i[7] in ["0","1","3","5"]:
                        contagem_registros_output += 1
                contagem_registros_output += 1  # Compensação contagem trailler
                contagem_registros_output_str = str(contagem_registros_output)
                while len(contagem_registros_output_str) != 6:
                    contagem_registros_output_str = "0" + contagem_registros_output_str

                while len(contagem_lotes_output_str) != 6:
                    contagem_lotes_output_str = '0' + contagem_lotes_output_str


                modified_line = (
                        line[:17]
                        + contagem_lotes_output_str
                        + line[23:]
                )

                modified_line = (
                        modified_line[:23]
                        + contagem_registros_output_str
                        + modified_line[29:]
                )

                modified_lines_TED.append(modified_line)

    print(
        f"""
        Programa executado.
        nome do arquivo: {file_name}
        Contagem de blocos total: {contagem_lotes_input}
        Contagem de blocos output: {contagem_lotes_output}
        """
    )

    # Escreve o arquivo de saída
    output_file = open(output_path + file_name[4:], 'w')
    for i in modified_lines_TED:
        output_file.write(f"{i}")
    output_file.close()




