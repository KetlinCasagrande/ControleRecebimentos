from datetime import datetime, time

from PySide6.QtWidgets import (
QDialog,
QVBoxLayout,
QHBoxLayout,
QLabel,
QPushButton,
QComboBox,
QDateEdit,
QTableWidget,
QTableWidgetItem,
QMessageBox,
QFileDialog,
)

from PySide6.QtCore import QDate
from services.backup_service import criar_backup

from sqlalchemy.orm import joinedload

from database import SessionLocal
from models import Recebimento, Usuario

from services.excel_service import gerar_excel

class HistoricoWindow(QDialog):


    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Histórico - Meu Caixa")
        self.resize(900, 600)

        self.criar_interface()
        self.carregar_historico()

    def criar_interface(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        titulo = QLabel("Histórico de recebimentos")

        titulo.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        # FILTROS

        filtros = QHBoxLayout()

        filtros.addWidget(QLabel("De:"))

        self.data_inicial = QDateEdit()
        self.data_inicial.setCalendarPopup(True)
        self.data_inicial.setDate(QDate.currentDate())

        filtros.addWidget(self.data_inicial)

        filtros.addWidget(QLabel("Até:"))

        self.data_final = QDateEdit()
        self.data_final.setCalendarPopup(True)
        self.data_final.setDate(QDate.currentDate())

        filtros.addWidget(self.data_final)

        filtros.addWidget(QLabel("Recebedor:"))

        self.combo_recebedor = QComboBox()

        self.combo_recebedor.addItems([
            "Todos",
            "Fellipe",
            "Tuany",
        ])

        filtros.addWidget(self.combo_recebedor)

        filtros.addWidget(QLabel("Forma:"))

        self.combo_forma = QComboBox()

        self.combo_forma.addItems([
            "Todas",
            "PIX",
            "Cartão",
            "Dinheiro",
        ])

        filtros.addWidget(self.combo_forma)

        self.btn_filtrar = QPushButton("FILTRAR")

        filtros.addWidget(self.btn_filtrar)

        self.btn_exportar = QPushButton(
            "EXPORTAR EXCEL"
        )

        filtros.addWidget(self.btn_exportar)

        layout.addLayout(filtros)

        # TABELA

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(5)

        self.tabela.setHorizontalHeaderLabels([
            "Data",
            "Recebedor",
            "Forma",
            "Valor",
            "Observação",
        ])

        self.tabela.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabela.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabela.verticalHeader().setVisible(False)

        layout.addWidget(self.tabela)

        # TOTAL

        self.label_total = QLabel(
            "TOTAL: R$ 0,00"
        )

        self.label_total.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        layout.addWidget(self.label_total)

        # EVENTOS

        self.btn_filtrar.clicked.connect(
            self.carregar_historico
        )

        self.btn_exportar.clicked.connect(
            self.exportar_excel
        )

    def carregar_historico(self):

        data_inicio = (
            self.data_inicial
            .date()
            .toPython()
        )

        data_fim = (
            self.data_final
            .date()
            .toPython()
        )

        if data_inicio > data_fim:

            QMessageBox.warning(
                self,
                "Atenção",
                "A data inicial não pode ser maior que a data final."
            )

            return

        inicio = datetime.combine(
            data_inicio,
            time.min
        )

        fim = datetime.combine(
            data_fim,
            time.max
        )

        with SessionLocal() as session:

            query = (
                session.query(Recebimento)
                .options(
                    joinedload(
                        Recebimento.recebedor
                    )
                )
                .filter(
                    Recebimento.data_hora >= inicio,
                    Recebimento.data_hora <= fim
                )
            )

            recebedor = (
                self.combo_recebedor.currentText()
            )

            if recebedor != "Todos":

                query = (
                    query
                    .join(
                        Recebimento.recebedor
                    )
                    .filter(
                        Usuario.nome == recebedor
                    )
                )

            forma = (
                self.combo_forma.currentText()
            )

            if forma != "Todas":

                query = query.filter(
                    Recebimento.forma_pagamento
                    == forma
                )

            recebimentos = (
                query
                .order_by(
                    Recebimento.data_hora.desc()
                )
                .all()
            )

            self.tabela.setRowCount(
                len(recebimentos)
            )

            total = 0

            for linha, recebimento in enumerate(
                recebimentos
            ):

                data = (
                    recebimento.data_hora
                    .strftime("%d/%m/%Y %H:%M")
                )

                nome = (
                    recebimento.recebedor.nome
                )

                forma_pagamento = (
                    recebimento.forma_pagamento
                )

                valor = float(
                    recebimento.valor
                )

                total += valor

                observacao = (
                    recebimento.observacao or ""
                )

                self.tabela.setItem(
                    linha,
                    0,
                    QTableWidgetItem(data)
                )

                self.tabela.setItem(
                    linha,
                    1,
                    QTableWidgetItem(nome)
                )

                self.tabela.setItem(
                    linha,
                    2,
                    QTableWidgetItem(
                        forma_pagamento
                    )
                )

                self.tabela.setItem(
                    linha,
                    3,
                    QTableWidgetItem(
                        f"R$ {valor:.2f}".replace(
                            ".",
                            ","
                        )
                    )
                )

                self.tabela.setItem(
                    linha,
                    4,
                    QTableWidgetItem(
                        observacao
                    )
                )

        self.label_total.setText(
            f"TOTAL: R$ {total:.2f}".replace(
                ".",
                ","
            )
        )

        self.tabela.resizeColumnsToContents()

    def exportar_excel(self):

        data_inicio = (
            self.data_inicial
            .date()
            .toPython()
        )

        data_fim = (
            self.data_final
            .date()
            .toPython()
        )

        inicio = datetime.combine(
            data_inicio,
            time.min
        )

        fim = datetime.combine(
            data_fim,
            time.max
        )

        with SessionLocal() as session:

            query = (
                session.query(Recebimento)
                .options(
                    joinedload(
                        Recebimento.recebedor
                    )
                )
                .filter(
                    Recebimento.data_hora >= inicio,
                    Recebimento.data_hora <= fim
                )
            )

            recebedor = (
                self.combo_recebedor.currentText()
            )

            if recebedor != "Todos":

                query = (
                    query
                    .join(
                        Recebimento.recebedor
                    )
                    .filter(
                        Usuario.nome == recebedor
                    )
                )

            forma = (
                self.combo_forma.currentText()
            )

            if forma != "Todas":

                query = query.filter(
                    Recebimento.forma_pagamento
                    == forma
                )

            recebimentos = (
                query
                .order_by(
                    Recebimento.data_hora.asc()
                )
                .all()
            )

        if not recebimentos:

            QMessageBox.information(
                self,
                "Exportar Excel",
                "Não existem recebimentos para exportar com esses filtros."
            )

            return

        nome_padrao = (
            f"Meu_Caixa_"
            f"{data_inicio.strftime('%d-%m-%Y')}"
            f"_a_"
            f"{data_fim.strftime('%d-%m-%Y')}.xlsx"
        )

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatório",
            nome_padrao,
            "Excel (*.xlsx)"
        )

        if not caminho:
            return

        try:

            gerar_excel(
                recebimentos,
                caminho,
                data_inicio,
                data_fim
            )
            criar_backup()

            QMessageBox.information(
                self,
                "Sucesso",
                "Excel gerado com sucesso!"
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                f"Não foi possível gerar o Excel:\n{erro}"
            )
