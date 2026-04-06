from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os
from pathlib import Path  # Adicione esta importação
import fitz  # PyMuPDF

def carimbar_pdf(request):
    if request.method == 'POST':
        try:
            # Captura os valores enviados pelo formulário
            numero_processo = request.POST.get('processo_numero')
            rubrica = request.POST.get('rubrica')
            paginas = request.POST.get('paginas')  # Captura as páginas
            posicao_y = int(request.POST.get('posicao_y'))
            tamanho_fonte = int(request.POST.get('tamanho_fonte'))
            
            # Verifica se o arquivo foi enviado
            if 'pdf_file' not in request.FILES:
                return HttpResponse("Erro: Nenhum arquivo PDF foi enviado.")
            
            pdf_file = request.FILES['pdf_file']
            arquivo_entrada = os.path.join(settings.MEDIA_ROOT, pdf_file.name)
            
            # Salva o arquivo enviado no diretório de mídia
            with open(arquivo_entrada, 'wb') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            # Obtém o caminho da pasta Downloads do usuário
            pasta_downloads = str(Path.home() / "Downloads")
            arquivo_saida = os.path.join(pasta_downloads, f"Carimbado_{pdf_file.name}")

            # Processa o PDF
            doc = fitz.open(arquivo_entrada)

            # Converte as páginas especificadas em uma lista de índices
            paginas_para_carimbar = []
            for parte in paginas.split(','):
                if '-' in parte:
                    inicio, fim = map(int, parte.split('-'))
                    paginas_para_carimbar.extend(range(inicio - 1, fim))  # Ajusta para índice 0
                else:
                    paginas_para_carimbar.append(int(parte) - 1)  # Ajusta para índice 0

            for i in paginas_para_carimbar:
                if i < 0 or i >= len(doc):
                    continue  # Ignora páginas fora do intervalo

                pagina = doc[i]
                largura = pagina.rect.width

                # Lógica de numeração:
                numero_folha = (i // 2) + 1

                # Alterna entre esquerda e direita
                if i % 2 == 0:  # Página ímpar (índice par no Python: 0, 2, 4...)
                    texto_folha = f"{numero_folha:02d}"
                    posicao_x = largura - 140 # Canto superior esquerdo
                else:  # Página par
                    texto_folha = f"{numero_folha:02d} V"
                    posicao_x = 20 # Canto superior direito

                # Adiciona o número da página ao texto do carimbo
                texto_carimbo = (
                    f"EMSERH\nProcesso: {numero_processo}\nRubrica: {rubrica}\nPágina: {texto_folha}"
                )

                # Inserindo o texto no PDF
                pagina.insert_text((posicao_x, posicao_y), texto_carimbo, fontsize=tamanho_fonte, color=(0, 0, 0))

            doc.save(arquivo_saida)
            doc.close()

            return HttpResponse(f"PDF carimbado com sucesso! Arquivo salvo em: {arquivo_saida}")

        except Exception as e:
            # Captura qualquer erro e retorna uma mensagem de erro
            return HttpResponse(f"Erro ao processar o PDF: {e}")

    return render(request, 'carimbar_pdf.html')