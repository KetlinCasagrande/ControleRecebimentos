from PySide6.QtWidgets import (
    QMainWindow,
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QComboBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QScrollArea,
    QSizePolicy,
    QHeaderView,
)

from services.recebimento_service import criar_recebimento
from services.dashboard_service import buscar_resumo
from services.ultimos_recebimentos import buscar_ultimos_recebimentos
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from services.gerenciar_recebimento import (
    buscar_recebimento,
    editar_recebimento,
    excluir_recebimento,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.recebedor_selecionado = None
        self.forma_selecionada = None

        self.setWindowTitle("Meu Caixa")
        self.resize(1000, 700)

        self.criar_interface()
        self.configurar_eventos()
        self.atualizar_dashboard()
        self.atualizar_lancamentos()

    # ==========================================================
    # INTERFACE
    # ==========================================================



    # ==========================================================
    # EDITAR LANÇAMENTO
    # ==========================================================

    def editar_lancamento(self):

        itens = (
            self.tabela_lancamentos
            .selectedItems()
        )

        if not itens:
            return

        linha = (
            self.tabela_lancamentos
            .currentRow()
        )

        item_data = (
            self.tabela_lancamentos
            .item(linha, 0)
        )

        recebimento_id = (
            item_data.data(32)
        )

        if not recebimento_id:

            QMessageBox.warning(
                self,
                "Erro",
                "Não foi possível identificar o lançamento."
            )

            return

        dados = buscar_recebimento(
            recebimento_id
        )

        if not dados:

            QMessageBox.warning(
                self,
                "Erro",
                "Lançamento não encontrado."
            )

            return

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Editar lançamento"
        )

        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        formulario = QFormLayout()

        valor = QLineEdit()

        valor.setText(
            f"{dados['valor']:.2f}".replace(
                ".",
                ","
            )
        )

        recebedor = QComboBox()

        recebedor.addItems([
            "Fellipe",
            "Tuany",
        ])

        recebedor.setCurrentText(
            dados["recebedor"]
        )

        forma = QComboBox()

        forma.addItems([
            "PIX",
            "Cartão",
            "Dinheiro",
        ])

        forma.setCurrentText(
            dados["forma_pagamento"]
        )

        observacao = QLineEdit()

        observacao.setText(
            dados["observacao"]
        )

        formulario.addRow(
            "Valor:",
            valor
        )

        formulario.addRow(
            "Recebedor:",
            recebedor
        )

        formulario.addRow(
            "Forma:",
            forma
        )

        formulario.addRow(
            "Observação:",
            observacao
        )

        layout.addLayout(
            formulario
        )

        botoes = QHBoxLayout()

        cancelar = QPushButton(
            "Cancelar"
        )

        salvar = QPushButton(
            "Salvar alterações"
        )

        botoes.addWidget(
            cancelar
        )

        botoes.addWidget(
            salvar
        )

        layout.addLayout(
            botoes
        )

        cancelar.clicked.connect(
            dialog.reject
        )

        def salvar_edicao():

            try:

                editar_recebimento(
                    recebimento_id=recebimento_id,
                    valor=valor.text(),
                    recebedor=recebedor.currentText(),
                    forma_pagamento=forma.currentText(),
                    observacao=observacao.text()
                )

                QMessageBox.information(
                    dialog,
                    "Sucesso",
                    "Lançamento atualizado com sucesso!"
                )

                dialog.accept()

            except ValueError as erro:

                QMessageBox.warning(
                    dialog,
                    "Atenção",
                    str(erro)
                )

            except Exception as erro:

                QMessageBox.critical(
                    dialog,
                    "Erro",
                    f"Não foi possível editar:\n{erro}"
                )

        salvar.clicked.connect(
            salvar_edicao
        )

        if dialog.exec():

            self.atualizar_dashboard()

            self.atualizar_lancamentos()

    # ==========================================================
    # EXCLUIR LANÇAMENTO
    # ==========================================================

    def excluir_lancamento(self):

        itens = (
            self.tabela_lancamentos
            .selectedItems()
        )

        if not itens:
            return

        linha = (
            self.tabela_lancamentos
            .currentRow()
        )

        item_data = (
            self.tabela_lancamentos
            .item(linha, 0)
        )

        recebimento_id = (
            item_data.data(32)
        )

        if not recebimento_id:

            QMessageBox.warning(
                self,
                "Erro",
                "Não foi possível identificar o lançamento."
            )

            return

        data = (
            self.tabela_lancamentos
            .item(linha, 0)
            .text()
        )

        recebedor = (
            self.tabela_lancamentos
            .item(linha, 1)
            .text()
        )

        forma = (
            self.tabela_lancamentos
            .item(linha, 2)
            .text()
        )

        valor = (
            self.tabela_lancamentos
            .item(linha, 3)
            .text()
        )

        resposta = QMessageBox.question(
            self,
            "Excluir lançamento",
            (
                "Tem certeza que deseja excluir este lançamento?\n\n"
                f"Data: {data}\n"
                f"Recebedor: {recebedor}\n"
                f"Forma: {forma}\n"
                f"Valor: {valor}\n\n"
                "Essa ação não pode ser desfeita."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if resposta != QMessageBox.Yes:
            return

        try:

            excluir_recebimento(
                recebimento_id
            )

            self.atualizar_dashboard()

            self.atualizar_lancamentos()

            self.btn_editar.setEnabled(
                False
            )

            self.btn_excluir.setEnabled(
                False
            )

            QMessageBox.information(
                self,
                "Sucesso",
                "Lançamento excluído com sucesso!"
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                f"Não foi possível excluir:\n{erro}"
            )


    def criar_interface(self):

        # ------------------------------------------------------
        # ÁREA DE ROLAGEM
        # ------------------------------------------------------

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        self.setCentralWidget(scroll)

        # ------------------------------------------------------
        # CONTEÚDO
        # ------------------------------------------------------

        central = QWidget()
        scroll.setWidget(central)

        layout_principal = QVBoxLayout(central)

        layout_principal.setContentsMargins(
            30, 25, 30, 25
        )

        layout_principal.setSpacing(16)
        layout_principal.setSizeConstraint(
            QVBoxLayout.SetMinAndMaxSize
        )

        # ======================================================
        # CABEÇALHO
        # ======================================================

        titulo = QLabel("Meu Caixa")
        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Controle de recebimentos"
        )
        subtitulo.setObjectName("subtitulo_pequeno")

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)

        # ======================================================
        # CARDS
        # ======================================================

        resumo_layout = QHBoxLayout()
        resumo_layout.setSpacing(12)

        self.card_total = self.criar_card(
            "RECEBIDO HOJE",
            "R$ 0,00"
        )

        self.card_fellipe = self.criar_card(
            "FELLIPE",
            "R$ 0,00"
        )

        self.card_tuany = self.criar_card(
            "TUANY",
            "R$ 0,00"
        )

        resumo_layout.addWidget(
            self.card_total,
            1
        )

        resumo_layout.addWidget(
            self.card_fellipe,
            1
        )

        resumo_layout.addWidget(
            self.card_tuany,
            1
        )

        layout_principal.addLayout(
            resumo_layout
        )

        # ======================================================
        # NOVO RECEBIMENTO
        # ======================================================

        titulo_lancamento = QLabel(
            "Novo recebimento"
        )

        titulo_lancamento.setObjectName(
            "titulo_secao"
        )

        layout_principal.addWidget(
            titulo_lancamento
        )

        # ======================================================
        # VALOR
        # ======================================================

        label_valor = QLabel("Valor")
        label_valor.setObjectName(
            "label_campo"
        )

        layout_principal.addWidget(
            label_valor
        )

        self.valor = QLineEdit()

        self.valor.setPlaceholderText(
            "Digite o valor recebido"
        )

        self.valor.setMinimumHeight(42)

        # Aceita números com até 2 casas decimais
        validador_valor = QRegularExpressionValidator(
            QRegularExpression(
                r"^\d{0,10}([,.]\d{0,2})?$"
            )
        )

        self.valor.setValidator(
            validador_valor
        )

        layout_principal.addWidget(
            self.valor
        )

        # ======================================================
        # RECEBEDOR
        # ======================================================

        label_recebedor = QLabel(
            "Recebedor"
        )

        label_recebedor.setObjectName(
            "label_campo"
        )

        layout_principal.addWidget(
            label_recebedor
        )

        recebedor_layout = QHBoxLayout()
        recebedor_layout.setSpacing(10)

        self.btn_fellipe = QPushButton(
            "Fellipe"
        )

        self.btn_tuany = QPushButton(
            "Tuany"
        )

        self.btn_fellipe.setMinimumHeight(42)
        self.btn_tuany.setMinimumHeight(42)

        self.btn_fellipe.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.btn_tuany.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        recebedor_layout.addWidget(
            self.btn_fellipe
        )

        recebedor_layout.addWidget(
            self.btn_tuany
        )

        layout_principal.addLayout(
            recebedor_layout
        )

        # ======================================================
        # FORMA DE PAGAMENTO
        # ======================================================

        label_pagamento = QLabel(
            "Forma de pagamento"
        )

        label_pagamento.setObjectName(
            "label_campo"
        )

        layout_principal.addWidget(
            label_pagamento
        )

        pagamento_layout = QHBoxLayout()
        pagamento_layout.setSpacing(10)

        self.btn_pix = QPushButton("PIX")
        self.btn_cartao = QPushButton("Cartão")
        self.btn_dinheiro = QPushButton("Dinheiro")

        botoes_pagamento = [
            self.btn_pix,
            self.btn_cartao,
            self.btn_dinheiro,
        ]

        for botao in botoes_pagamento:

            botao.setMinimumHeight(42)

            botao.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            pagamento_layout.addWidget(
                botao
            )

        layout_principal.addLayout(
            pagamento_layout
        )

        # ======================================================
        # OBSERVAÇÃO
        # ======================================================

        label_observacao = QLabel(
            "Observação"
        )

        label_observacao.setObjectName(
            "label_campo"
        )

        layout_principal.addWidget(
            label_observacao
        )

        self.observacao = QLineEdit()

        self.observacao.setPlaceholderText(
            "Observação (opcional)"
        )

        self.observacao.setMinimumHeight(42)

        layout_principal.addWidget(
            self.observacao
        )

        # ======================================================
        # SALVAR
        # ======================================================

        self.btn_salvar = QPushButton(
            "✓   SALVAR RECEBIMENTO"
        )

        self.btn_salvar.setObjectName(
            "botao_salvar"
        )

        self.btn_salvar.setMinimumHeight(48)

        layout_principal.addWidget(
            self.btn_salvar
        )

        # ======================================================
        # ÚLTIMOS LANÇAMENTOS
        # ======================================================

        cabecalho_lancamentos = QHBoxLayout()

        titulo_lancamentos = QLabel(
            "Últimos lançamentos"
        )

        titulo_lancamentos.setObjectName(
            "titulo_secao"
        )

        cabecalho_lancamentos.addWidget(
            titulo_lancamentos
        )

        cabecalho_lancamentos.addStretch()

        self.btn_historico = QPushButton(
            "VER HISTÓRICO E RELATÓRIOS →"
        )

        self.btn_historico.setObjectName(
            "botao_historico"
        )

        cabecalho_lancamentos.addWidget(
            self.btn_historico
        )

        layout_principal.addLayout(
            cabecalho_lancamentos
        )

        # ======================================================
        # TABELA
        # ======================================================

        self.tabela_lancamentos = QTableWidget()

        self.tabela_lancamentos.setColumnCount(5)

        self.tabela_lancamentos.setHorizontalHeaderLabels([
            "Data",
            "Recebedor",
            "Forma",
            "Valor",
            "Observação"
        ])

        self.tabela_lancamentos.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabela_lancamentos.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabela_lancamentos.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.tabela_lancamentos.verticalHeader().setVisible(
            False
        )

        self.tabela_lancamentos.setAlternatingRowColors(
            True
        )

        self.tabela_lancamentos.setMinimumHeight(
            180
        )

        header = self.tabela_lancamentos.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.Stretch
        )

        layout_principal.addWidget(
            self.tabela_lancamentos
        )

        # ======================================================
        # AÇÕES DO LANÇAMENTO
        # ======================================================

        acoes_lancamento = QHBoxLayout()

        acoes_lancamento.setSpacing(10)

        self.btn_editar = QPushButton(
            "✏  Editar lançamento"
        )

        self.btn_editar.setObjectName(
            "botao_editar"
        )

        self.btn_excluir = QPushButton(
            "🗑  Excluir lançamento"
        )

        self.btn_excluir.setObjectName(
            "botao_excluir"
        )

        self.btn_editar.setEnabled(False)
        self.btn_excluir.setEnabled(False)

        acoes_lancamento.addWidget(
            self.btn_editar
        )

        acoes_lancamento.addWidget(
            self.btn_excluir
        )

        acoes_lancamento.addStretch()

        layout_principal.addLayout(
            acoes_lancamento
        )

        layout_principal.addStretch()

        self.aplicar_estilo()



    # ==========================================================
    # CARD
    # ==========================================================

    def criar_card(self, titulo, valor):

        card = QFrame()
        card.setObjectName("card")

        card.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        card.setMinimumHeight(115)

        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            20, 18, 20, 18
        )

        layout.setSpacing(8)

        label_titulo = QLabel(titulo)

        label_titulo.setObjectName(
            "titulo_card"
        )

        label_titulo.setWordWrap(True)

        label_valor = QLabel(valor)

        label_valor.setObjectName(
            "valor_card"
        )

        label_valor.setWordWrap(False)

        layout.addWidget(
            label_titulo
        )

        layout.addWidget(
            label_valor
        )

        layout.addStretch()

        return card
    # ==========================================================
    # EVENTOS
    # ==========================================================

    def configurar_eventos(self):

        self.btn_fellipe.clicked.connect(
            lambda: self.selecionar_recebedor(
                "Fellipe"
            )
        )

        self.btn_tuany.clicked.connect(
            lambda: self.selecionar_recebedor(
                "Tuany"
            )
        )

        self.btn_pix.clicked.connect(
            lambda: self.selecionar_forma(
                "PIX"
            )
        )

        self.btn_cartao.clicked.connect(
            lambda: self.selecionar_forma(
                "Cartão"
            )
        )

        self.btn_dinheiro.clicked.connect(
            lambda: self.selecionar_forma(
                "Dinheiro"
            )
        )

        self.btn_salvar.clicked.connect(
            self.salvar_recebimento
        )

        self.btn_historico.clicked.connect(
            self.abrir_historico
        )

        self.tabela_lancamentos.itemSelectionChanged.connect(
            self.atualizar_botoes_lancamento
        )

        self.btn_editar.clicked.connect(
            self.editar_lancamento
        )

        self.btn_excluir.clicked.connect(
            self.excluir_lancamento
        ) 

    # ==========================================================
    # ABRIR HISTÓRICO
    # ==========================================================

    def abrir_historico(self):

        from ui.historico_window import HistoricoWindow

        janela = HistoricoWindow(self)

        janela.exec()

        self.atualizar_dashboard()
        self.atualizar_lancamentos()

    # ==========================================================
    # SELECIONAR RECEBEDOR
    # ==========================================================

    def selecionar_recebedor(self, nome):

        self.recebedor_selecionado = nome

        self.btn_fellipe.setProperty(
            "selecionado",
            nome == "Fellipe"
        )

        self.btn_tuany.setProperty(
            "selecionado",
            nome == "Tuany"
        )

        self.atualizar_estilo_botoes()

    # ==========================================================
    # SELECIONAR FORMA
    # ==========================================================

    def selecionar_forma(self, forma):

        self.forma_selecionada = forma

        self.btn_pix.setProperty(
            "selecionado",
            forma == "PIX"
        )

        self.btn_cartao.setProperty(
            "selecionado",
            forma == "Cartão"
        )

        self.btn_dinheiro.setProperty(
            "selecionado",
            forma == "Dinheiro"
        )

        self.atualizar_estilo_botoes()

    # ==========================================================
    # ATUALIZAR ESTILO DOS BOTÕES
    # ==========================================================

    def atualizar_estilo_botoes(self):

        botoes = [
            self.btn_fellipe,
            self.btn_tuany,
            self.btn_pix,
            self.btn_cartao,
            self.btn_dinheiro,
        ]

        for botao in botoes:

            botao.style().unpolish(botao)
            botao.style().polish(botao)
            botao.update()

    # ==========================================================
    # ATUALIZAR BOTÕES DO LANÇAMENTO
    # ==========================================================

    def atualizar_botoes_lancamento(self):

        selecionado = (
            len(
                self.tabela_lancamentos
                .selectedItems()
            ) > 0
        )

        self.btn_editar.setEnabled(
            selecionado
        )

        self.btn_excluir.setEnabled(
            selecionado
        )



    # ==========================================================
    # SALVAR
    # ==========================================================

    def salvar_recebimento(self):

        valor = self.valor.text().strip()

        # Aceita vírgula ou ponto como separador decimal
        valor = valor.replace(",", ".")

        if not valor:

            QMessageBox.warning(
                self,
                "Atenção",
                "Digite um valor."
            )

            self.valor.setFocus()

            return

        if not self.recebedor_selecionado:

            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione o recebedor."
            )

            return

        if not self.forma_selecionada:

            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione a forma de pagamento."
            )

            return

        try:

            criar_recebimento(
                valor=valor,
                recebedor=self.recebedor_selecionado,
                forma_pagamento=self.forma_selecionada,
                observacao=self.observacao.text().strip()
            )

            self.limpar_formulario()

            self.atualizar_dashboard()

            self.atualizar_lancamentos()

            QMessageBox.information(
                self,
                "Sucesso",
                "Recebimento registrado com sucesso!"
            )

        except ValueError as erro:

            QMessageBox.warning(
                self,
                "Erro",
                str(erro)
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                f"Não foi possível salvar:\n{erro}"
            )

    # ==========================================================
    # ATUALIZAR DASHBOARD
    # ==========================================================

    def atualizar_dashboard(self):

        resumo = buscar_resumo()

        self.card_total.findChildren(
            QLabel
        )[1].setText(
            f"R$ {resumo['total']:.2f}".replace(
                ".",
                ","
            )
        )

        self.card_fellipe.findChildren(
            QLabel
        )[1].setText(
            f"R$ {resumo['fellipe']:.2f}".replace(
                ".",
                ","
            )
        )

        self.card_tuany.findChildren(
            QLabel
        )[1].setText(
            f"R$ {resumo['tuany']:.2f}".replace(
                ".",
                ","
            )
        )

    # ==========================================================
    # ATUALIZAR LANÇAMENTOS
    # ==========================================================

    def atualizar_lancamentos(self):

        recebimentos = buscar_ultimos_recebimentos(10)

        self.tabela_lancamentos.setRowCount(
            len(recebimentos)
        )

        for linha, recebimento in enumerate(
            recebimentos
        ):
            self.tabela_lancamentos.item(
                linha,
                0
            )

            data = recebimento.data_hora.strftime(
                "%d/%m/%Y %H:%M"
            )

            recebedor = (
                recebimento.recebedor.nome
            )

            forma = (
                recebimento.forma_pagamento
            )

            valor = (
                f"R$ {float(recebimento.valor):.2f}"
                .replace(".", ",")
            )

            observacao = (
                recebimento.observacao or ""
            )

            valores = [
                data,
                recebedor,
                forma,
                valor,
                observacao,
            ]

            for coluna, texto in enumerate(
                valores
            ):

                item = QTableWidgetItem(
                    texto
                )

                self.tabela_lancamentos.setItem(
                    linha,
                    coluna,
                    item
                )

            # Guarda o ID do recebimento
            # sem mostrar para o usuário.

            self.tabela_lancamentos.item(
                linha,
                0
            ).setData(
                32,
                recebimento.id
            )

    # ==========================================================
    # LIMPAR FORMULÁRIO
    # ==========================================================

    def limpar_formulario(self):

        self.valor.clear()
        self.observacao.clear()

        self.recebedor_selecionado = None
        self.forma_selecionada = None

        botoes = [
            self.btn_fellipe,
            self.btn_tuany,
            self.btn_pix,
            self.btn_cartao,
            self.btn_dinheiro,
        ]

        for botao in botoes:

            botao.setProperty(
                "selecionado",
                False
            )

        self.atualizar_estilo_botoes()

        self.valor.setFocus()

    # ==========================================================
    # ESTILO
    # ==========================================================

    def aplicar_estilo(self):

        self.setStyleSheet("""

            /* ==================================================
               GERAL
               ================================================== */

            QMainWindow {
                background-color: #f4f6fa;
            }

            QScrollArea {
                background-color: #f4f6fa;
                border: none;
            }

            QWidget {
                font-family: "Segoe UI";
                font-size: 14px;
                color: #273142;
            }


            /* ==================================================
               TÍTULOS
               ================================================== */

            QLabel#titulo {
                font-size: 32px;
                font-weight: 700;
                color: #172554;
                padding-top: 3px;
            }

            QLabel#subtitulo_pequeno {
                font-size: 14px;
                color: #7b8798;
                margin-bottom: 4px;
            }

            QLabel#titulo_secao {
                font-size: 20px;
                font-weight: 700;
                color: #172554;
                padding-top: 4px;
            }

            QLabel#label_campo {
                font-size: 13px;
                font-weight: 600;
                color: #596579;
                margin-top: 2px;
            }


            /* ==================================================
               CARDS
               ================================================== */

            QFrame#card {
                background-color: #ffffff;
                border: 1px solid #e5e9f0;
                border-radius: 14px;
            }

            QFrame#card:hover {
                border: 1px solid #cbd5e1;
            }

            QLabel#titulo_card {
                font-size: 11px;
                font-weight: 700;
                color: #8a96a8;
                letter-spacing: 0px;
            }

            QLabel#valor_card {
                font-size: 26px;
                font-weight: 700;
                color: #172554;
                padding-top: 2px;
            }


            /* ==================================================
               CAMPOS
               ================================================== */

            QLineEdit {
                background-color: #ffffff;
                color: #273142;
                border: 1px solid #dce2ea;
                border-radius: 9px;
                padding: 10px 13px;
                font-size: 14px;
                selection-background-color: #dbe5ff;
                selection-color: #172554;
            }

            QLineEdit:hover {
                border: 1px solid #bfc9d8;
            }

            QLineEdit:focus {
                border: 2px solid #3855b3;
                padding: 9px 12px;
            }


            /* ==================================================
               BOTÕES
               ================================================== */

            QPushButton {
                background-color: #ffffff;
                color: #354052;
                border: 1px solid #dce2ea;
                border-radius: 9px;
                padding: 10px 14px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #f5f7fb;
                border-color: #aeb9ca;
            }

            QPushButton:pressed {
                background-color: #edf1f7;
            }
            QComboBox {
                background-color: #ffffff;
                color: #273142;
                border: 1px solid #dce2ea;
                border-radius: 9px;
                padding: 10px 13px;
                font-size: 14px;
                min-height: 20px;
            }

            QComboBox:hover {
                border: 1px solid #bfc9d8;
            }

            QComboBox:focus {
                border: 2px solid #3855b3;
                padding: 9px 12px;
            }

            QComboBox::drop-down {
                border: none;
                width: 32px;
            }

            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #273142;
                border: 1px solid #dce2ea;
                selection-background-color: #e5ebfa;
                selection-color: #172554;
                padding: 5px;
            }

            /* ==================================================
               BOTÕES SELECIONADOS
               ================================================== */

            QPushButton[selecionado="true"] {
                background-color: #273c75;
                color: #ffffff;
                border: 1px solid #273c75;
                font-weight: 700;
            }

            QPushButton[selecionado="true"]:hover {
                background-color: #314b91;
                border-color: #314b91;
            }

            QPushButton[selecionado="true"]:pressed {
                background-color: #1f3160;
            }


            /* ==================================================
               SALVAR
               ================================================== */

            QPushButton#botao_salvar {
                background-color: #273c75;
                color: #ffffff;
                border: none;
                border-radius: 9px;
                padding: 12px 16px;
                font-size: 15px;
                font-weight: 700;
            }

            QPushButton#botao_salvar:hover {
                background-color: #314b91;
            }

            QPushButton#botao_salvar:pressed {
                background-color: #1f3160;
            }


            /* ==================================================
               HISTÓRICO
               ================================================== */

            QPushButton#botao_historico {
                background-color: transparent;
                color: #314b91;
                border: none;
                padding: 7px 4px;
                font-size: 13px;
                font-weight: 700;
            }

            QPushButton#botao_historico:hover {
                color: #172554;
                background-color: #e9edf7;
                border-radius: 7px;
            }


            /* ==================================================
               BOTÃO EDITAR
               ================================================== */

            QPushButton#botao_editar {
                background-color: #ffffff;
                color: #273c75;
                border: 1px solid #cfd7e6;
                border-radius: 8px;
                padding: 9px 14px;
                font-weight: 600;
            }

            QPushButton#botao_editar:hover {
                background-color: #eef2fb;
                border-color: #273c75;
            }

            QPushButton#botao_editar:disabled {
                background-color: #f5f6f8;
                color: #a5adba;
                border-color: #e1e4e9;
            }


            /* ==================================================
               BOTÃO EXCLUIR
               ================================================== */

            QPushButton#botao_excluir {
                background-color: #ffffff;
                color: #c0392b;
                border: 1px solid #ead1ce;
                border-radius: 8px;
                padding: 9px 14px;
                font-weight: 600;
            }

            QPushButton#botao_excluir:hover {
                background-color: #fff3f1;
                border-color: #c0392b;
            }

            QPushButton#botao_excluir:disabled {
                background-color: #f5f6f8;
                color: #a5adba;
                border-color: #e1e4e9;
            }            

            /* ==================================================
               TABELA
               ================================================== */

            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f8f9fc;
                color: #354052;

                border: 1px solid #e3e7ed;
                border-radius: 10px;

                gridline-color: #edf0f4;

                selection-background-color: #e5ebfa;
                selection-color: #172554;

                outline: none;
            }

            QTableWidget::item {
                padding: 7px;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #e5ebfa;
                color: #172554;
            }


            /* ==================================================
               CABEÇALHO DA TABELA
               ================================================== */

            QHeaderView::section {
                background-color: #f1f4f8;
                color: #596579;

                border: none;
                border-bottom: 1px solid #dfe4eb;

                padding: 9px 8px;

                font-size: 12px;
                font-weight: 700;
            }


            /* ==================================================
               SCROLLBAR VERTICAL
               ================================================== */

            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #c7cfdb;
                border-radius: 5px;
                min-height: 35px;
            }

            QScrollBar::handle:vertical:hover {
                background: #aeb8c7;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }


            /* ==================================================
               SCROLLBAR HORIZONTAL
               ================================================== */

            QScrollBar:horizontal {
                background: transparent;
                height: 10px;
                margin: 2px;
            }

            QScrollBar::handle:horizontal {
                background: #c7cfdb;
                border-radius: 5px;
                min-width: 35px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #aeb8c7;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }

        """)