from openpyxl import Workbook


def gerar_excel(recebimentos, caminho, data_inicio, data_fim):

    wb = Workbook()

    ws = wb.active
    ws.title = "Recebimentos"

    ws.append([
        "Data",
        "Recebedor",
        "Forma de pagamento",
        "Valor",
        "Observação",
    ])

    total = 0

    for recebimento in recebimentos:

        valor = float(recebimento.valor)

        total += valor

        ws.append([
            recebimento.data_hora.strftime(
                "%d/%m/%Y %H:%M"
            ),
            recebimento.recebedor.nome,
            recebimento.forma_pagamento,
            valor,
            recebimento.observacao or "",
        ])

    ws.append([])

    ws.append([
        "TOTAL",
        "",
        "",
        total,
        "",
    ])

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 22
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 40

    for celula in ws["D"]:
        celula.number_format = 'R$ #,##0.00'

    wb.save(caminho)