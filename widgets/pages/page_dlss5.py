import os
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, Slot, QStandardPaths
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from scripts_core.script_dlss5 import (
    DLSS5InstallWorker,
    detect_anticheat,
    detect_game_dlss_capability,
    detect_nvidia_gpu,
)
from scripts_core.script_prefix import (
    find_heroic_game_config,
    find_wine_prefix,
    get_steam_launch_options,
)
from scripts_core.script_scanner import scan_all_games
from utils.utils import dialog_box

HOME = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)


class PageDLSS5(QWidget):
    dlss5_finished: Signal = Signal(bool)
    back_requested: Signal = Signal()

    def __init__(self):
        super().__init__()

        self.game_path: str = ""
        self.is_steam: bool = False
        self.wine_prefix: str = ""
        self.gpu_info: dict = detect_nvidia_gpu()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(12)

        # 1. GPU Card / Banner
        self.gpu_card = QGroupBox("Hardware NVIDIA")
        gpu_layout = QVBoxLayout(self.gpu_card)

        gpu_name = self.gpu_info.get("name", "NVIDIA GPU")
        arch = self.gpu_info.get("arch", "Unknown")
        supported = self.gpu_info.get("supported", False)
        cost = self.gpu_info.get("cost", "")

        status_color = "#4CAF50" if supported else "#FF9800"
        status_text = "Suportado" if supported else "Não suportado"

        self.lbl_gpu = QLabel(f"<b>GPU:</b> {gpu_name} ({arch}) | <font color='{status_color}'><b>{status_text}</b></font>")
        self.lbl_gpu.setStyleSheet("font-size: 11pt;")
        self.lbl_gpu.setWordWrap(True)
        self.lbl_gpu_desc = QLabel(f"Desempenho estimado: {cost} | Modelo: {self.gpu_info.get('recommended_build', 'N/A')}")
        self.lbl_gpu_desc.setStyleSheet("color: #888888; font-size: 9pt;")
        self.lbl_gpu_desc.setWordWrap(True)

        gpu_layout.addWidget(self.lbl_gpu)
        gpu_layout.addWidget(self.lbl_gpu_desc)
        layout.addWidget(self.gpu_card)

        # 2. Game Selection
        self.game_card = QGroupBox("Seleção do Jogo")
        game_layout = QVBoxLayout(self.game_card)

        row_games = QHBoxLayout()
        self.combo_games = QComboBox()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setFixedWidth(80)
        self.btn_refresh.clicked.connect(self.populate_games)
        self.combo_games.currentIndexChanged.connect(self.on_game_selected)

        row_games.addWidget(self.combo_games)
        row_games.addWidget(self.btn_refresh)
        game_layout.addLayout(row_games)

        row_browse = QHBoxLayout()
        self.browse_input = QLineEdit()
        self.browse_input.setPlaceholderText("Ou selecione o executável (.exe) manualmente...")
        self.browse_input.textChanged.connect(self.on_browse_text_changed)
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.clicked.connect(self.on_browse_clicked)

        row_browse.addWidget(self.browse_input)
        row_browse.addWidget(self.btn_browse)
        game_layout.addLayout(row_browse)
        layout.addWidget(self.game_card)

        # 3. Route Selection
        self.route_card = QGroupBox("Rota do DLSS 5")
        route_layout = QVBoxLayout(self.route_card)

        self.lbl_route_reason = QLabel("Selecione um executável para análise automática.")
        self.lbl_route_reason.setStyleSheet("color: #4CAF50; font-size: 9pt; font-weight: bold;")
        route_layout.addWidget(self.lbl_route_reason)

        self.radio_route_feeder = QRadioButton("Rota Feeder (DLSS 5 Feeder + Lumenite + RenoDX)")
        self.radio_route_feeder.setToolTip("Gera contrato DLAA através do depth buffer e vetores de movimento por shader.")
        self.radio_route_feeder.setChecked(True)

        self.radio_route_optiscaler = QRadioButton("Rota OptiScaler (Pre-SR Multipass)")
        self.radio_route_optiscaler.setToolTip("Substitui o upscaler nativo do jogo e aplica o modelo DLSS 5 sobre ele.")

        route_layout.addWidget(self.radio_route_feeder)
        route_layout.addWidget(self.radio_route_optiscaler)
        layout.addWidget(self.route_card)

        # 4. Performance Profile
        self.perf_card = QGroupBox("Perfil de Desempenho (work_resolution)")
        perf_layout = QHBoxLayout(self.perf_card)

        self.radio_perf_balanced = QRadioButton("Equilibrado (70% - Recomendado)")
        self.radio_perf_balanced.setToolTip("Reconstrução a 70% com FSR1 upscale. Protege FPS e folga de GPU.")
        self.radio_perf_balanced.setChecked(True)

        self.radio_perf_performance = QRadioButton("Desempenho (50%)")
        self.radio_perf_performance.setToolTip("Reconstrução a 50% de resolução. Maior ganho de taxa de quadros.")

        self.radio_perf_quality = QRadioButton("Qualidade (100% DLAA)")
        self.radio_perf_quality.setToolTip("Reconstrução neural a 100% nativo. Carga máxima na GPU.")

        perf_layout.addWidget(self.radio_perf_balanced)
        perf_layout.addWidget(self.radio_perf_performance)
        perf_layout.addWidget(self.radio_perf_quality)
        layout.addWidget(self.perf_card)

        # 5. Wine Prefix Info
        self.prefix_card = QGroupBox("Prefixo Wine / Proton")
        prefix_layout = QVBoxLayout(self.prefix_card)

        self.lbl_prefix_status = QLabel("Nenhum prefixo detectado.")
        self.lbl_prefix_status.setStyleSheet("font-size: 9pt; color: #888888;")
        self.lbl_prefix_status.setWordWrap(True)

        row_prefix = QHBoxLayout()
        self.input_prefix = QLineEdit()
        self.input_prefix.setPlaceholderText("Caminho do Wine Prefix (ex: .../pfx)...")
        self.btn_prefix_browse = QPushButton("Browse")
        self.btn_prefix_browse.clicked.connect(self.on_prefix_browse_clicked)

        row_prefix.addWidget(self.input_prefix)
        row_prefix.addWidget(self.btn_prefix_browse)

        prefix_layout.addWidget(self.lbl_prefix_status)
        prefix_layout.addLayout(row_prefix)
        layout.addWidget(self.prefix_card)

        # 6. Anti-Cheat Warning
        self.anticheat_banner = QLabel()
        self.anticheat_banner.setWordWrap(True)
        self.anticheat_banner.setStyleSheet(
            "background-color: rgba(244, 67, 54, 0.15); "
            "color: #ff6b6b; "
            "border: 1px solid #ff6b6b; "
            "border-radius: 4px; "
            "padding: 8px; "
            "font-size: 10pt; "
            "font-weight: bold;"
        )
        self.anticheat_banner.hide()

        self.check_anticheat_confirm = QCheckBox("Estou ciente do risco de banimento e confirmo a instalação.")
        self.check_anticheat_confirm.stateChanged.connect(self.update_install_state)
        self.check_anticheat_confirm.hide()

        layout.addWidget(self.anticheat_banner)
        layout.addWidget(self.check_anticheat_confirm)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Bottom Actions
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        bottom_buttons = QHBoxLayout()
        self.btn_back = QPushButton("Voltar")
        self.btn_back.setFixedWidth(100)
        self.btn_back.clicked.connect(self.back_requested.emit)

        self.btn_install = QPushButton("Instalar DLSS 5 Autopilot")
        self.btn_install.setEnabled(False)
        self.btn_install.clicked.connect(self.on_install_clicked)

        bottom_buttons.addWidget(self.btn_back)
        bottom_buttons.addWidget(self.btn_install)

        main_layout.addWidget(self.progress_bar)
        main_layout.addLayout(bottom_buttons)

        self.populate_games()

    def populate_games(self) -> None:
        self.combo_games.blockSignals(True)
        self.combo_games.clear()
        self.combo_games.addItem("-- Selecione um jogo detectado --", userData=None)

        games = scan_all_games()
        for g in games:
            title = g.get("title", "Desconhecido")
            source = g.get("source", "Jogo")
            self.combo_games.addItem(f"[{source}] {title}", userData=g)

        self.combo_games.blockSignals(False)

    def on_game_selected(self, index: int) -> None:
        if index <= 0:
            return
        data = self.combo_games.itemData(index)
        if data and isinstance(data, dict):
            exe = data.get("exe", "")
            if exe and os.path.exists(exe):
                self.browse_input.setText(exe)
                self.is_steam = data.get("source") == "Steam"
                self.set_game_path(exe)

    def on_browse_clicked(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Selecione o executável do jogo", HOME, "Executables (*.exe)"
        )
        if file_name:
            self.browse_input.setText(file_name)
            self.set_game_path(file_name)

    def on_browse_text_changed(self, text: str) -> None:
        clean = text.strip().strip('"').strip("'")
        if os.path.isfile(clean) and clean.lower().endswith(".exe"):
            if clean != self.game_path:
                self.set_game_path(clean)
        else:
            self.game_path = clean
            self.update_install_state()

    def on_prefix_browse_clicked(self) -> None:
        dir_name = QFileDialog.getExistingDirectory(self, "Selecione a pasta do Wine Prefix", HOME)
        if dir_name:
            self.input_prefix.setText(dir_name)
            self.wine_prefix = dir_name

    def set_game_path(self, exe_path: str) -> None:
        self.game_path = exe_path

        # 1. Analyze DLSS capability & route
        cap = detect_game_dlss_capability(exe_path)
        self.lbl_route_reason.setText(cap.get("reason", ""))

        if cap.get("recommended_route") == "optiscaler":
            self.radio_route_optiscaler.setChecked(True)
        else:
            self.radio_route_feeder.setChecked(True)

        # 2. Analyze anti-cheat
        ac_list = detect_anticheat(exe_path)
        if ac_list:
            self.anticheat_banner.setText(
                f"Atenção: Anti-Cheat detectado ({', '.join(ac_list)}). "
                "O uso de add-ons e DLLs customizadas pode resultar em banimento em jogos online!"
            )
            self.anticheat_banner.show()
            self.check_anticheat_confirm.setChecked(False)
            self.check_anticheat_confirm.show()
        else:
            self.anticheat_banner.hide()
            self.check_anticheat_confirm.hide()

        # 3. Detect Wine Prefix
        detected_prefix = find_wine_prefix(exe_path, self.is_steam)
        if detected_prefix:
            self.wine_prefix = detected_prefix
            self.input_prefix.setText(detected_prefix)
            self.lbl_prefix_status.setText(f"Prefixo detectado automaticamente: {detected_prefix}")
        else:
            self.lbl_prefix_status.setText("Nenhum prefixo detectado automaticamente. Se necessário, informe acima.")

        self.update_install_state()

    def update_install_state(self) -> None:
        valid_exe = bool(self.game_path and os.path.isfile(self.game_path))
        has_ac = not self.anticheat_banner.isHidden()
        ac_ok = (not has_ac) or self.check_anticheat_confirm.isChecked()

        can_install = valid_exe and ac_ok
        self.btn_install.setEnabled(can_install)

    def on_install_clicked(self) -> None:
        if not self.game_path:
            return

        route = "feeder" if self.radio_route_feeder.isChecked() else "optiscaler"
        if self.radio_perf_performance.isChecked():
            preset = "performance"
        elif self.radio_perf_quality.isChecked():
            preset = "quality"
        else:
            preset = "balanced"

        prefix = self.input_prefix.text().strip() or self.wine_prefix

        self.btn_install.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Iniciando instalação...")

        self.worker_thread = QThread()
        self.worker = DLSS5InstallWorker(
            game_exe_path=self.game_path,
            route=route,
            performance_preset=preset,
            is_steam=self.is_steam,
            wine_prefix=prefix,
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.finished.connect(self.on_worker_finished)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    @Slot(int, str)
    def on_worker_progress(self, val: int, msg: str) -> None:
        self.progress_bar.setValue(val)
        self.progress_bar.setFormat(msg)

    @Slot(bool, str)
    def on_worker_finished(self, success: bool, msg: str) -> None:
        self.btn_install.setEnabled(True)
        if success:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("DLSS 5 Autopilot instalado com sucesso!")

            info_msg = (
                "DLSS 5 instalado com sucesso!\n\n"
                "Instruções:\n"
                "- Pressione HOME dentro do jogo para abrir a barra do ReShade.\n"
                "- Marque Lumenite_Kernel e DLSS 5 Feed.\n"
                "- Na aba DLSS 5, ative o Neural Rendering."
            )
            if self.is_steam:
                steam_args = get_steam_launch_options()
                info_msg += f"\n\nOpções de Inicialização da Steam (Launch Options):\n{steam_args}"

            dialog_box(
                parent=self,
                title="DLSS 5 Autopilot",
                icon=QMessageBox.Icon.Information,
                text="Instalação Concluída!",
                info_text=info_msg,
                buttons=False,
            )
            self.dlss5_finished.emit(True)
        else:
            self.progress_bar.setFormat(f"Erro: {msg}")
            dialog_box(
                parent=self,
                title="Erro DLSS 5",
                icon=QMessageBox.Icon.Critical,
                text="Falha na instalação do DLSS 5",
                info_text=msg,
                buttons=False,
            )
            self.dlss5_finished.emit(False)
