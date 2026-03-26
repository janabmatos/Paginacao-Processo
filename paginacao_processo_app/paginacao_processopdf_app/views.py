from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os
import fitz  # PyMuPDF

def carimbar_pdf(request):
    if request.method == 'POST':
        # Captura o número do processo enviado pelo formulário
        numero_processo = request.POST.get('processo_numero')
        
        # Verifica se o arquivo foi enviado
        if 'pdf_file' in request.FILES:
            pdf_file = request.FILES['pdf_file']
            arquivo_entrada = os.path.join(settings.MEDIA_ROOT, pdf_file.name)
            
            # Salva o arquivo enviado no diretório de mídia
            with open(arquivo_entrada, 'wb') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            # Define o nome do arquivo de saída
            arquivo_saida = os.path.join(settings.MEDIA_ROOT, f"Carimbado_{pdf_file.name}")

            try:
                # Processa o PDF
                doc = fitz.open(arquivo_entrada)

                for i in range(len(doc)):
                    pagina = doc[i]
                    largura = pagina.rect.width

                    # Lógica de numeração:
                    numero_folha = (i // 2) + 1

                    # Verifica se a página do PDF é ímpar (índice par no Python: 0, 2, 4...)
                    if i % 2 == 0:
                        texto_folha = f"{numero_folha:02d}"
                        posicao_x = largura - 140  # Canto Superior Direito
                    else:
                        texto_folha = f"{numero_folha:02d} V"
                        posicao_x = 20  # Canto Superior Esquerdo

                    posicao_y = 30  # Margem superior

                    # Texto do carimbo com o número do processo
                    texto_carimbo = f"EMSERH\nFolha: {texto_folha}\nProcesso: {numero_processo}\nRubrica: Ismael"

                    # Inserindo o texto no PDF
                    pagina.insert_text((posicao_x, posicao_y), texto_carimbo, fontsize=10, color=(0, 0, 0))

                doc.save(arquivo_saida)
                doc.close()

                return HttpResponse(f"PDF carimbado com sucesso! Arquivo salvo em: {arquivo_saida}")

            except Exception as e:
                return HttpResponse(f"Erro ao processar o PDF: {e}")

    return render(request, 'carimbar_pdf.html')