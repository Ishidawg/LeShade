from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from scripts_core.script_addons import fetch_addons
from scripts_core.script_shaders import ShadersWorker, fetch_effect_packages
from utils.utils import get_renodx_assets


class CatalogWorker(QObject):
    """
    Fetches the effect package list, the add-on list and the RenoDX snapshot
    assets off the UI thread so the window does not freeze on startup.
    """
    loaded: Signal = Signal(object, object, object)

    def run(self) -> None:
        try:
            packages = fetch_effect_packages()
        except Exception as e:
            print(f"Failed to fetch effect packages: {e}")
            packages = []

        try:
            addons = fetch_addons(is_64bit=True)
        except Exception as e:
            print(f"Failed to fetch addons: {e}")
            addons = []

        try:
            renodx_assets = get_renodx_assets() or ["None"]
        except Exception as e:
            print(f"Failed to fetch RenoDX assets: {e}")
            renodx_assets = ["None"]

        self.loaded.emit(packages, addons, renodx_assets)


class PageClone(QWidget):
    clone_finished: Signal = Signal(bool)

    def __init__(self, is_addon_param: bool):
        super().__init__()

        self.is_addon: bool = is_addon_param
        self.game_name: str = ""
        self.package_items: list[dict] = []
        self.addon_items: list[dict] = []
        self.catalog_loaded: bool = False

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Header description
        label_description = QLabel("Select effect packages and add-ons to install.")
        label_description.setStyleSheet("font-size: 12pt; font-weight: 100")
        label_description.setWordWrap(True)

        # Filter & Action toolbar
        toolbar_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter packages...")
        self.filter_input.textChanged.connect(self.on_filter_changed)

        self.btn_select_all = QPushButton("Select all")
        self.btn_select_all.setFixedWidth(90)
        self.btn_select_all.clicked.connect(self.on_select_all_clicked)

        self.btn_clear_all = QPushButton("Clear all")
        self.btn_clear_all.setFixedWidth(90)
        self.btn_clear_all.clicked.connect(self.on_clear_all_clicked)

        toolbar_layout.addWidget(self.filter_input)
        toolbar_layout.addWidget(self.btn_select_all)
        toolbar_layout.addWidget(self.btn_clear_all)

        # Scrollable container for packages & addons
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.label_loading = QLabel("Loading package catalog...")
        self.label_loading.setStyleSheet("color: #888888; font-size: 10pt;")
        self.container_layout.addWidget(self.label_loading)

        # Packages container (filled when the catalog arrives)
        self.widget_packages = QWidget()
        self.layout_packages = QVBoxLayout(self.widget_packages)
        self.layout_packages.setContentsMargins(0, 0, 0, 0)
        self.container_layout.addWidget(self.widget_packages)

        # Addons container
        self.widget_addons = QWidget()
        self.layout_addons = QVBoxLayout(self.widget_addons)
        self.layout_addons.setContentsMargins(0, 10, 0, 0)

        label_addons_section = QLabel("Official Add-ons (Optional)")
        label_addons_section.setStyleSheet("font-size: 11pt; font-weight: bold; margin-top: 10px;")
        self.layout_addons.addWidget(label_addons_section)

        # RenoDX section
        self.renodx_assets: list[str] | None = None
        self.lbl_renodx = QLabel("RenoDX - Select game snapshot")
        self.lbl_renodx.setStyleSheet("font-size: 10pt; font-weight: bold; margin-top: 5px;")
        self.renodx_addon = QComboBox()
        self.layout_addons.addWidget(self.lbl_renodx)
        self.layout_addons.addWidget(self.renodx_addon)

        self.container_layout.addWidget(self.widget_addons)
        self.widget_addons.setVisible(self.is_addon)

        self.scroll_area.setWidget(self.container_widget)

        # Progress bar & Install button
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # The click is handled by MainWindow (it owns the game directory).
        self.btn_install = QPushButton("Install")
        self.btn_install.setEnabled(False)

        # Assemble layout
        layout.addWidget(label_description)
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.btn_install)

        self.setLayout(layout)
        self.update_renodx()
        self.start_catalog_load()

    def start_catalog_load(self) -> None:
        self.catalog_thread: QThread = QThread()
        self.catalog_worker: CatalogWorker = CatalogWorker()
        self.catalog_worker.moveToThread(self.catalog_thread)

        self.catalog_thread.started.connect(self.catalog_worker.run)
        self.catalog_worker.loaded.connect(self.on_catalog_loaded)
        self.catalog_worker.loaded.connect(self.catalog_thread.quit)
        self.catalog_worker.loaded.connect(self.catalog_worker.deleteLater)
        self.catalog_thread.finished.connect(self.catalog_thread.deleteLater)

        self.catalog_thread.start()

    @Slot(object, object, object)
    def on_catalog_loaded(self, packages: list[dict], addons: list[dict], renodx_assets: list[str]) -> None:
        self.load_packages(packages)
        self.load_addons(addons)
        self.renodx_assets = renodx_assets
        self.catalog_loaded = True

        self.label_loading.hide()
        self.btn_install.setEnabled(True)
        self.update_renodx()
        self.on_filter_changed(self.filter_input.text())

    def load_packages(self, packages: list[dict]) -> None:
        for pkg in packages:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 2, 0, 4)
            item_layout.setSpacing(2)

            cxb = QCheckBox(pkg["name"])
            if pkg.get("required") or pkg.get("enabled"):
                cxb.setChecked(True)

            lbl = QLabel(pkg.get("description", ""))
            lbl.setStyleSheet("color: #888888; font-size: 9pt; padding-left: 20px;")
            lbl.setWordWrap(True)

            item_layout.addWidget(cxb)
            if pkg.get("description"):
                item_layout.addWidget(lbl)

            self.layout_packages.addWidget(item_widget)
            self.package_items.append({
                "pkg": pkg,
                "checkbox": cxb,
                "label": lbl,
                "widget": item_widget,
            })

    def load_addons(self, addons: list[dict]) -> None:
        # Insert before the RenoDX label so RenoDX stays at the bottom of the section
        insert_index = self.layout_addons.indexOf(self.lbl_renodx)

        for addon in addons:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 2, 0, 4)
            item_layout.setSpacing(2)

            cxb = QCheckBox(addon["name"])
            lbl = QLabel(addon.get("description", ""))
            lbl.setStyleSheet("color: #888888; font-size: 9pt; padding-left: 20px;")
            lbl.setWordWrap(True)

            item_layout.addWidget(cxb)
            if addon.get("description"):
                item_layout.addWidget(lbl)

            self.layout_addons.insertWidget(insert_index, item_widget)
            insert_index += 1
            self.addon_items.append({
                "addon": addon,
                "checkbox": cxb,
                "label": lbl,
                "widget": item_widget,
            })

    def on_filter_changed(self, text: str) -> None:
        query = text.strip().lower()
        for item in self.package_items:
            name = item["pkg"].get("name", "").lower()
            desc = item["pkg"].get("description", "").lower()
            match = (query in name) or (query in desc)
            item["widget"].setVisible(match)

        for item in self.addon_items:
            name = item["addon"].get("name", "").lower()
            desc = item["addon"].get("description", "").lower()
            match = (query in name) or (query in desc)
            item["widget"].setVisible(match)

    def on_select_all_clicked(self) -> None:
        for item in self.package_items:
            if not item["widget"].isHidden():
                item["checkbox"].setChecked(True)

    def on_clear_all_clicked(self) -> None:
        for item in self.package_items:
            if not item["widget"].isHidden():
                item["checkbox"].setChecked(False)

        for item in self.addon_items:
            if not item["widget"].isHidden():
                item["checkbox"].setChecked(False)

    def update_renodx(self) -> None:
        if not self.is_addon:
            self.renodx_addon.clear()
            self.renodx_addon.addItem("None")
            self.renodx_addon.setEnabled(False)
            return

        if self.renodx_assets is None:
            self.renodx_addon.clear()
            self.renodx_addon.addItem("Loading...")
            self.renodx_addon.setEnabled(False)
            return

        current_items = [
            self.renodx_addon.itemText(i) for i in range(self.renodx_addon.count())
        ]
        if current_items != self.renodx_assets:
            self.renodx_addon.clear()
            self.renodx_addon.addItems(self.renodx_assets)

        self.renodx_addon.setEnabled(True)

    def set_game_name(self, value: str) -> None:
        self.game_name = value
        self.update_renodx()

    def set_is_addon(self, value: bool) -> None:
        self.is_addon = value
        self.widget_addons.setVisible(value)
        self.update_renodx()

    def on_install(self, game_dir: str) -> None:
        if not self.catalog_loaded:
            self.progress_bar.setFormat("Package catalog is still loading...")
            return

        selected_pkgs = [
            item["pkg"] for item in self.package_items if item["checkbox"].isChecked()
        ]
        selected_addons = [
            item["addon"] for item in self.addon_items if item["checkbox"].isChecked()
        ]

        renodx_choice = "None"
        if self.is_addon and self.renodx_assets is not None:
            renodx_choice = self.renodx_addon.currentText()

        if not selected_pkgs and not selected_addons and renodx_choice == "None":
            self.clone_finished.emit(True)
            return

        self.start_animation()
        self.btn_install.setEnabled(False)

        self.clone_thread: QThread = QThread()
        self.clone_worker: ShadersWorker = ShadersWorker(
            selected_pkgs, renodx_choice, game_dir, selected_addons=selected_addons
        )

        self.clone_worker.moveToThread(self.clone_thread)
        self.clone_thread.started.connect(self.clone_worker.run)

        self.clone_worker.clone_finished.connect(self.on_success)
        self.clone_worker.clone_finished.connect(self.on_error)
        self.clone_worker.clone_finished.connect(self.clone_thread.quit)
        self.clone_worker.clone_finished.connect(self.clone_worker.deleteLater)
        self.clone_thread.finished.connect(self.clone_thread.deleteLater)

        self.clone_thread.start()

    def start_animation(self) -> None:
        self.progress_bar.setRange(0, 0)

    @Slot(bool)
    def on_success(self, value: bool) -> None:
        self.btn_install.setEnabled(True)
        if value:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Installation finished!")
            self.clone_finished.emit(value)

    @Slot(bool)
    def on_error(self, value: bool) -> None:
        self.btn_install.setEnabled(True)
        if not value:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Failed shader process")
            self.clone_finished.emit(value)
