"""
Onslaught Career Editor - Asset Browser Tab
Browse game assets by type with filtering/search.
"""

import subprocess
import sys
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QHeaderView,
)

from ...core.config import AppConfig


@dataclass
class AssetRow:
    full_path: Path
    relative_path: str
    category: str
    size_bytes: int
    modified: float


class AssetBrowserTab(QWidget):
    """File-oriented browser for BEA game assets."""

    IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
    MODEL_EXTS = {".fbx", ".obj", ".gltf", ".glb"}

    CATEGORY_ORDER = [
        "All",
        "AYA Archives",
        "Video",
        "Audio",
        "Saves/Options",
        "Text/Data",
        "Other",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_dir: Path | None = None
        self._all_rows: list[AssetRow] = []
        self._selected_file: Path | None = None
        self._setup_ui()
        self._use_config_root()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        root_group = QGroupBox("Game Folder")
        root_layout = QHBoxLayout(root_group)

        self.root_edit = QLineEdit()
        self.root_edit.setReadOnly(True)
        self.root_edit.setPlaceholderText("Set game directory in Settings or browse manually")
        root_layout.addWidget(self.root_edit, 1)

        use_config_btn = QPushButton("Use Config")
        use_config_btn.clicked.connect(self._use_config_root)
        root_layout.addWidget(use_config_btn)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_root)
        root_layout.addWidget(browse_btn)

        self.rescan_btn = QPushButton("Rescan")
        self.rescan_btn.clicked.connect(self._scan_assets)
        root_layout.addWidget(self.rescan_btn)

        self.use_output_btn = QPushButton("Use Extractor Output")
        self.use_output_btn.clicked.connect(self._use_extractor_output)
        root_layout.addWidget(self.use_output_btn)

        self.open_repo_btn = QPushButton("Open AYA Repo")
        self.open_repo_btn.clicked.connect(self._open_aya_repo)
        root_layout.addWidget(self.open_repo_btn)

        self.launch_extractor_btn = QPushButton("Launch Extractor")
        self.launch_extractor_btn.clicked.connect(self._launch_aya_extractor)
        root_layout.addWidget(self.launch_extractor_btn)

        layout.addWidget(root_group)

        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(self.CATEGORY_ORDER)
        self.category_filter.currentIndexChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.category_filter)

        filter_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter by file name/path")
        self.search_edit.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_edit, 1)

        open_file_btn = QPushButton("Open Selected")
        open_file_btn.clicked.connect(self._open_selected_file)
        filter_layout.addWidget(open_file_btn)

        open_containing_btn = QPushButton("Open Containing")
        open_containing_btn.clicked.connect(self._open_containing_folder)
        filter_layout.addWidget(open_containing_btn)

        self.extract_selected_btn = QPushButton("Extract Selected AYA")
        self.extract_selected_btn.clicked.connect(self._extract_selected_aya)
        filter_layout.addWidget(self.extract_selected_btn)

        layout.addWidget(filter_group)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Relative Path", "Category", "Size", "Modified"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._update_details)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table, 1)

        preview_group = QGroupBox("Preview")
        preview_layout = QHBoxLayout(preview_group)

        self.preview_label = QLabel("Select a file to preview.")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(320, 220)
        self.preview_label.setStyleSheet("background: #f4f6f8; border: 1px solid #c9d1d9;")
        preview_layout.addWidget(self.preview_label, 1)

        self.preview_info = QLabel("")
        self.preview_info.setWordWrap(True)
        self.preview_info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        preview_layout.addWidget(self.preview_info, 1)

        layout.addWidget(preview_group)

        self.summary_label = QLabel("No root directory selected.")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        self.details_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.details_label)

    def set_root_directory(self, path: Path):
        self.root_dir = path if path and path.exists() else None
        self.root_edit.setText(str(self.root_dir) if self.root_dir else "")
        self._scan_assets()

    @staticmethod
    def _find_repo_root() -> Path | None:
        cur = Path(__file__).resolve()
        for parent in [cur] + list(cur.parents):
            if (parent / "references" / "AYAResourceExtractor").exists():
                return parent
        return None

    def _open_aya_repo(self):
        repo_root = self._find_repo_root()
        if repo_root is None:
            QMessageBox.warning(self, "AYA Integration", "Could not resolve repo root from current runtime path.")
            return

        aya_repo = repo_root / "references" / "AYAResourceExtractor"
        if not aya_repo.exists():
            QMessageBox.warning(self, "AYA Integration", f"AYAResourceExtractor folder not found:\n{aya_repo}")
            return

        try:
            if sys.platform.startswith("win"):
                import os
                os.startfile(str(aya_repo))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(aya_repo)])
            else:
                subprocess.Popen(["xdg-open", str(aya_repo)])
        except Exception as exc:
            QMessageBox.critical(self, "AYA Integration", f"Failed to open folder:\n{exc}")

    @staticmethod
    def _extractor_output_dir() -> Path:
        return Path.home() / "Documents" / "Battle Engine Aquila Models"

    def _use_extractor_output(self):
        out_dir = self._extractor_output_dir()
        if not out_dir.exists():
            QMessageBox.information(
                self,
                "AYA Integration",
                "Extractor output folder was not found yet.\n\n"
                f"Expected:\n{out_dir}\n\n"
                "Run AYAResourceExtractor first, or browse to another extracted-assets folder.",
            )
            return
        self.set_root_directory(out_dir)

    def _launch_aya_extractor(self):
        repo_root = self._find_repo_root()
        if repo_root is None:
            QMessageBox.warning(self, "AYA Integration", "Could not resolve repo root from current runtime path.")
            return

        exe = self._find_aya_extractor_exe(repo_root)
        if exe is None:
            project_dir = repo_root / "references" / "AYAResourceExtractor" / "Code" / "AyaResourceExtractor"
            QMessageBox.information(
                self,
                "AYA Integration",
                "AYAResourceExtractor executable not found under expected bin paths.\n\n"
                f"Build from:\n{project_dir}\n\n"
                "Then click 'Launch Extractor' again.",
            )
            return

        try:
            subprocess.Popen([str(exe)], shell=False)
        except Exception as exc:
            QMessageBox.critical(self, "AYA Integration", f"Failed to launch extractor:\n{exc}")

    @staticmethod
    def _find_aya_extractor_exe(repo_root: Path) -> Path | None:
        candidates = [
            repo_root / "references" / "AYAResourceExtractor" / "Code" / "AyaResourceExtractor" / "bin" / cfg / tfm / "AYAResourceExtractor.exe"
            for cfg in ("Debug", "Release")
            for tfm in ("net10.0-windows", "net9.0-windows", "net8.0-windows", "net7.0-windows", "net6.0-windows")
        ]
        return next((p for p in candidates if p.exists()), None)

    def _use_config_root(self):
        config = AppConfig.load()
        game_dir = config.get_game_dir()
        if game_dir and game_dir.exists():
            self.set_root_directory(game_dir)
        else:
            self.root_dir = None
            self.root_edit.clear()
            self._all_rows = []
            self.table.setRowCount(0)
            self.summary_label.setText("Game directory is not configured. Set it in Settings or browse manually.")
            self.details_label.clear()

    def _browse_root(self):
        start_dir = str(self.root_dir) if self.root_dir else ""
        folder = QFileDialog.getExistingDirectory(self, "Select Game Folder", start_dir)
        if folder:
            self.set_root_directory(Path(folder))

    @staticmethod
    def _categorize(path: Path) -> str:
        ext = path.suffix.lower()
        if ext == ".aya":
            return "AYA Archives"
        if ext in {".vid", ".bik", ".avi", ".wmv", ".mp4"}:
            return "Video"
        if ext in {".wav", ".ogg", ".mp3", ".wma"}:
            return "Audio"
        if ext in {".bes", ".bea"}:
            return "Saves/Options"
        if ext in {".txt", ".md", ".ini", ".cfg", ".dat", ".json", ".xml", ".csv", ".tsv"}:
            return "Text/Data"
        return "Other"

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        if size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def _scan_assets(self):
        if self.root_dir is None:
            return

        if not self.root_dir.exists():
            QMessageBox.warning(self, "Asset Browser", f"Directory does not exist:\n{self.root_dir}")
            return

        rows: list[AssetRow] = []
        try:
            for file_path in self.root_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                try:
                    stat = file_path.stat()
                except OSError:
                    continue

                category = self._categorize(file_path)
                rel = str(file_path.relative_to(self.root_dir))
                rows.append(
                    AssetRow(
                        full_path=file_path,
                        relative_path=rel,
                        category=category,
                        size_bytes=stat.st_size,
                        modified=stat.st_mtime,
                    )
                )
        except Exception as exc:
            QMessageBox.critical(self, "Asset Browser", f"Failed while scanning assets:\n{exc}")
            return

        self._all_rows = sorted(rows, key=lambda r: r.relative_path.lower())
        self._apply_filters()

    def _open_selected_file(self):
        if self._selected_file is None or not self._selected_file.exists():
            QMessageBox.information(self, "Asset Browser", "Select a file first.")
            return

        try:
            if sys.platform.startswith("win"):
                import os
                os.startfile(str(self._selected_file))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(self._selected_file)])
            else:
                subprocess.Popen(["xdg-open", str(self._selected_file)])
        except Exception as exc:
            QMessageBox.critical(self, "Asset Browser", f"Failed to open file:\n{exc}")

    def _open_containing_folder(self):
        if self._selected_file is None or not self._selected_file.exists():
            QMessageBox.information(self, "Asset Browser", "Select a file first.")
            return

        folder = self._selected_file.parent
        try:
            if sys.platform.startswith("win"):
                import os
                os.startfile(str(folder))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except Exception as exc:
            QMessageBox.critical(self, "Asset Browser", f"Failed to open folder:\n{exc}")

    def _extract_selected_aya(self):
        if self._selected_file is None or not self._selected_file.exists():
            QMessageBox.information(self, "AYA Integration", "Select an .aya file first.")
            return

        if self._selected_file.suffix.lower() != ".aya":
            QMessageBox.information(self, "AYA Integration", "Selected file is not an .aya archive.")
            return

        repo_root = self._find_repo_root()
        if repo_root is None:
            QMessageBox.warning(self, "AYA Integration", "Could not resolve repo root from current runtime path.")
            return

        exe = self._find_aya_extractor_exe(repo_root)
        if exe is None:
            project_dir = repo_root / "references" / "AYAResourceExtractor" / "Code" / "AyaResourceExtractor"
            QMessageBox.information(
                self,
                "AYA Integration",
                "AYAResourceExtractor executable not found under expected bin paths.\n\n"
                f"Build from:\n{project_dir}\n\n"
                "Then retry extraction.",
            )
            return

        output_dir = self._extractor_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)

        args = [
            str(exe),
            "--extract",
            str(self._selected_file),
            "--output",
            str(output_dir),
        ]

        config_game_dir = AppConfig.load().get_game_dir()
        if config_game_dir and config_game_dir.exists():
            args.extend(["--root", str(config_game_dir)])

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.extract_selected_btn.setEnabled(False)
        try:
            completed = subprocess.run(args, capture_output=True, text=True, shell=False)
        except Exception as exc:
            QMessageBox.critical(self, "AYA Integration", f"Failed to run extractor:\n{exc}")
            return
        finally:
            self.extract_selected_btn.setEnabled(True)
            QApplication.restoreOverrideCursor()

        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "(no output)"
            QMessageBox.critical(
                self,
                "AYA Integration",
                f"Extractor failed with exit code {completed.returncode}.\n\n{detail}",
            )
            return

        detail = completed.stdout.strip()
        msg = f"Extraction completed.\n\nOutput folder:\n{output_dir}"
        if detail:
            msg += f"\n\n{detail}"
        QMessageBox.information(self, "AYA Integration", msg)
        self.set_root_directory(output_dir)

    @staticmethod
    def _try_extract_fbx_texture_names(path: Path) -> list[str]:
        if path.suffix.lower() != ".fbx":
            return []
        try:
            with path.open("rb") as f:
                sample = f.read(1024 * 768)
        except OSError:
            return []

        text = sample.decode("latin-1", errors="ignore")
        matches = re.findall(r"([A-Za-z0-9_\\/\-\. ]+\.png)", text, flags=re.IGNORECASE)
        cleaned: list[str] = []
        seen: set[str] = set()
        for m in matches:
            candidate = Path(m.strip().replace("\\", "/")).name
            if candidate and candidate.lower() not in seen:
                seen.add(candidate.lower())
                cleaned.append(candidate)
        return cleaned

    def _resolve_preview_image(self, path: Path) -> Path | None:
        ext = path.suffix.lower()
        if ext in self.IMAGE_EXTS and path.exists():
            return path

        candidates: list[Path] = []
        stem = path.stem

        if ext in {".aya", ".fbx"}:
            candidates.extend(
                [
                    path.parent / "MeshTextures" / f"{stem}.png",
                    path.parent / "MeshTextures" / f"{stem.lower()}.png",
                    path.parent.parent / "MeshTextures" / f"{stem}.png",
                    path.parent.parent / "MeshTextures" / f"{stem.lower()}.png",
                ]
            )

        if ext == ".fbx":
            for tex_name in self._try_extract_fbx_texture_names(path):
                candidates.extend(
                    [
                        path.parent / "MeshTextures" / tex_name,
                        path.parent / tex_name,
                    ]
                )

        for c in candidates:
            if c.exists() and c.suffix.lower() in self.IMAGE_EXTS:
                return c

        return None

    def _set_preview_image(self, image_path: Path | None):
        if image_path is None:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("Preview unavailable for this asset.")
            return

        pix = QPixmap(str(image_path))
        if pix.isNull():
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText(f"Preview image could not be loaded:\n{image_path.name}")
            return

        scaled = pix.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setText("")
        self.preview_label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._selected_file is not None:
            self._set_preview_image(self._resolve_preview_image(self._selected_file))

    def _describe_asset(self, path: Path, category: str) -> str:
        ext = path.suffix.lower()
        rel = str(path)
        rel_l = rel.lower()

        hints: list[str] = []
        if ext == ".aya":
            if "meshes" in rel_l:
                hints.append("Likely compressed model archive from data/resources/meshes.")
            elif "dxtntextures" in rel_l:
                hints.append("Likely compressed texture archive from data/resources/dxtntextures.")
            hints.append("Use 'Extract Selected AYA' for one-click extraction, or 'Launch Extractor' for batch/manual runs.")
        elif ext in self.MODEL_EXTS:
            hints.append("Extracted model file. Open with Blender or Windows 3D Viewer.")
        elif ext in self.IMAGE_EXTS:
            hints.append("Texture/image asset previewed inline.")
        elif ext in {".bea", ".bes"}:
            if path.name.lower().startswith("defaultoptions.bea"):
                hints.append("Global options snapshot loaded at boot in the Steam build.")
            else:
                hints.append("Career/options save buffer (10,004 bytes expected).")

        return (
            f"Type: {category}\n"
            f"Name: {path.name}\n"
            f"Extension: {ext or '(none)'}\n"
            + ("\n".join(hints) if hints else "No specialized hint for this asset type.")
        )

    def _apply_filters(self):
        category = self.category_filter.currentText()
        search = self.search_edit.text().strip().lower()

        filtered: list[AssetRow] = []
        for row in self._all_rows:
            if category != "All" and row.category != category:
                continue
            if search and search not in row.relative_path.lower():
                continue
            filtered.append(row)

        self.table.setRowCount(len(filtered))
        for i, row in enumerate(filtered):
            modified_text = datetime.fromtimestamp(row.modified).strftime("%Y-%m-%d %H:%M")
            values = [
                row.relative_path,
                row.category,
                self._format_size(row.size_bytes),
                modified_text,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                if col in (2, 3):
                    align = Qt.AlignmentFlag.AlignCenter
                item.setTextAlignment(align)
                if col == 0:
                    item.setData(Qt.ItemDataRole.UserRole, str(row.full_path))
                self.table.setItem(i, col, item)

        if self.root_dir is None:
            self.summary_label.setText("No root directory selected.")
        else:
            self.summary_label.setText(
                f"Root: {self.root_dir} | Showing {len(filtered):,} of {len(self._all_rows):,} files"
            )

        self._selected_file = None
        self.preview_info.clear()
        self._set_preview_image(None)
        self.details_label.clear()

    def _update_details(self):
        items = self.table.selectedItems()
        if not items:
            self.details_label.clear()
            return

        path_item = self.table.item(items[0].row(), 0)
        full_path = path_item.data(Qt.ItemDataRole.UserRole) if path_item else None
        if not full_path:
            self.details_label.clear()
            return

        p = Path(full_path)
        self._selected_file = p
        self.details_label.setText(f"Selected: {p}")
        row = next((r for r in self._all_rows if r.full_path == p), None)
        category = row.category if row else self._categorize(p)

        self.preview_info.setText(self._describe_asset(p, category))
        self._set_preview_image(self._resolve_preview_image(p))
