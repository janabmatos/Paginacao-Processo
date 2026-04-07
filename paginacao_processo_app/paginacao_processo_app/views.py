from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from io import BytesIO
import fitz  # PyMuPDF

def carimbar_pdf(request):
    if request.method == 'POST':
        try:
            # Captura os valores enviados pelo formulário
            numero_processo = request.POST.get('processo_numero')
            rubrica = request.POST.get('rubrica')
            paginas = request.POST.get('paginas')  # Captura o intervalo da numeração (ex: 5-15)
            posicao_y = int(request.POST.get('posicao_y'))
            tamanho_fonte = int(request.POST.get('tamanho_fonte'))
            
            # Verifica se o arquivo foi enviado
            if 'pdf_file' not in request.FILES:
                return HttpResponse("Erro: Nenhum arquivo PDF foi enviado.")
            
            pdf_file = request.FILES['pdf_file']

            # Processa o PDF
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")

            if '-' not in paginas:
                return HttpResponse("Erro: informe o intervalo no formato início-fim. Ex: 5-15.")

            inicio_str, fim_str = paginas.split('-', 1)
            inicio_num = int(inicio_str.strip())
            fim_num = int(fim_str.strip())

            if inicio_num <= 0 or fim_num < inicio_num:
                return HttpResponse("Erro: intervalo inválido. Exemplo válido: 5-15.")

            total_folhas = fim_num - inicio_num + 1
            total_paginas_para_carimbar = min(len(doc), total_folhas * 2)

            for i in range(total_paginas_para_carimbar):
                pagina = doc[i]
                largura = pagina.rect.width

                # Lógica de numeração:
                numero_folha = inicio_num + (i // 2)

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

            pdf_saida = doc.tobytes()
            doc.close()

            nome_saida = f"Carimbado_{pdf_file.name}"
            return FileResponse(
                BytesIO(pdf_saida),
                as_attachment=True,
                filename=nome_saida,
                content_type='application/pdf',
            )

        except Exception as e:
            # Captura qualquer erro e retorna uma mensagem de erro
            return HttpResponse(f"Erro ao processar o PDF: {e}")

    return render(request, 'carimbar_pdf.html')