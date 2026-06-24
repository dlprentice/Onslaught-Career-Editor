"""
Onslaught Career Editor - Goodie Viewer Tab
Inspect the 300 goodie slots (233 displayable + 67 reserved) in .bes/.bea files.
"""

from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from ...core.bes_file import BesFile
from ...core.constants import (
    OFFSET_GOODIES,
    GOODIE_SIZE,
    GOODIE_DISPLAYABLE_COUNT,
    GOODIE_UNKNOWN,
    GOODIE_INSTRUCTIONS_SHOWN,
    GOODIE_NEW,
    GOODIE_OLD,
)
from ..widgets import SaveSelector


@dataclass
class GoodieRow:
    index: int
    file_offset: str
    state: str
    raw_hex: str
    scope: str


class GoodieViewerTab(QWidget):
    """Browse per-slot goodie state from a selected .bes/.bea file."""

    STATE_ORDER = ["All", "NEW", "OLD", "LOCKED", "INSTRUCTIONS", "OTHER", "RESERVED"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file: Path | None = None
        self._all_rows: list[GoodieRow] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.selector = SaveSelector(label="Source Save/Options File")
        self.selector.fileSelected.connect(self._on_file_selected)
        layout.addWidget(self.selector)

        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("State:"))
        self.state_filter = QComboBox()
        self.state_filter.addItems(self.STATE_ORDER)
        self.state_filter.currentIndexChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.state_filter)

        self.show_reserved = QCheckBox("Show reserved slots (233-299)")
        self.show_reserved.setChecked(True)
        self.show_reserved.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.show_reserved)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self._reload_current)
        filter_layout.addWidget(self.reload_button)

        filter_layout.addStretch()
        layout.addWidget(filter_group)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Index", "File Offset", "State", "Raw", "Scope"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table, 1)

        self.summary_label = QLabel("Load a .bes/.bea file to inspect goodie slot states.")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

    def _on_file_selected(self, path: Path):
        self.current_file = path
        self._load_rows(path)

    def _reload_current(self):
        if self.current_file is None:
            QMessageBox.information(self, "Goodie Viewer", "Select a source .bes/.bea file first.")
            return
        self._load_rows(self.current_file)

    @staticmethod
    def _classify_state(index: int, raw: int) -> str:
        if index >= GOODIE_DISPLAYABLE_COUNT:
            return "RESERVED"
        if raw == GOODIE_NEW:
            return "NEW"
        if raw == GOODIE_OLD:
            return "OLD"
        if raw == GOODIE_UNKNOWN:
            return "LOCKED"
        if raw == GOODIE_INSTRUCTIONS_SHOWN:
            return "INSTRUCTIONS"
        return "OTHER"

    def _load_rows(self, path: Path):
        try:
            bes = BesFile.load(path, strict_version=False)
        except Exception as exc:
            QMessageBox.critical(self, "Goodie Viewer", f"Failed to load file:\n{exc}")
            self._all_rows = []
            self.table.setRowCount(0)
            self.summary_label.setText("Failed to load file.")
            return

        self._all_rows = []
        for idx, raw in enumerate(bes.goodies):
            state = self._classify_state(idx, raw)
            scope = "Displayable" if idx < GOODIE_DISPLAYABLE_COUNT else "Reserved"
            file_offset = OFFSET_GOODIES + (idx * GOODIE_SIZE)
            self._all_rows.append(
                GoodieRow(
                    index=idx,
                    file_offset=f"0x{file_offset:04X}",
                    state=state,
                    raw_hex=f"0x{raw:08X}",
                    scope=scope,
                )
            )

        self._apply_filters()
        self._update_summary(path)

    def _update_summary(self, path: Path):
        displayable = [r for r in self._all_rows if r.scope == "Displayable"]
        new_count = sum(1 for r in displayable if r.state == "NEW")
        old_count = sum(1 for r in displayable if r.state == "OLD")
        locked_count = sum(1 for r in displayable if r.state == "LOCKED")
        instructions_count = sum(1 for r in displayable if r.state == "INSTRUCTIONS")
        other_count = sum(1 for r in displayable if r.state == "OTHER")
        unlocked = new_count + old_count

        self.summary_label.setText(
            f"Loaded {path.name}. "
            f"Unlocked: {unlocked}/{GOODIE_DISPLAYABLE_COUNT} "
            f"(NEW {new_count}, OLD {old_count}); "
            f"Locked: {locked_count}; Instructions: {instructions_count}; Other: {other_count}; "
            f"Reserved slots: {len(self._all_rows) - GOODIE_DISPLAYABLE_COUNT}."
        )

    def _state_color(self, state: str) -> QColor | None:
        if state == "NEW":
            return QColor("#fff3c4")
        if state == "OLD":
            return QColor("#dff0ff")
        if state == "LOCKED":
            return QColor("#f3f5f7")
        if state == "INSTRUCTIONS":
            return QColor("#f2e8ff")
        if state == "OTHER":
            return QColor("#ffe5e5")
        return None

    def _apply_filters(self):
        selected_state = self.state_filter.currentText()
        include_reserved = self.show_reserved.isChecked()

        filtered = []
        for row in self._all_rows:
            if not include_reserved and row.scope == "Reserved":
                continue
            if selected_state != "All" and row.state != selected_state:
                continue
            filtered.append(row)

        self.table.setRowCount(len(filtered))

        for i, row in enumerate(filtered):
            values = [str(row.index), row.file_offset, row.state, row.raw_hex, row.scope]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col < 4 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                color = self._state_color(row.state)
                if color is not None:
                    item.setBackground(color)
                self.table.setItem(i, col, item)

        self.table.resizeRowsToContents()
