"""
Onslaught Career Editor - Lore Browser Tab
Browse game history, characters, and developer info from markdown docs
"""

import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextBrowser, QLineEdit,
    QLabel, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QDesktopServices

from ..theme import ACCENT_COLOR, TEXT_COLOR

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


class LoreBrowserTab(QWidget):
    """Lore browser tab - view markdown documentation"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_root = self._find_project_root()
        self.lore_book_dir = self.project_root / 'lore-book'
        self.book_path = self.lore_book_dir / 'BOOK.md'
        self.current_file = None
        self._home_doc: Path | None = None
        self._home_title: str | None = None
        self._all_docs = []
        self._item_by_path: dict[Path, QTreeWidgetItem] = {}
        self._toc_nodes: list[dict] | None = None
        self._using_lore_toc = False
        self._loader = None
        self._search_query = ""
        self._has_loaded = False
        self._setup_ui()

    def ensure_loaded(self):
        """Load lore tree on first activation to avoid startup work on non-lore workflows."""
        if self._has_loaded:
            return
        self._load_lore_tree()

    def _find_project_root(self) -> Path:
        """Find the project root directory (contains AGENTS.md or lore-book/)."""
        module_dir = Path(__file__).parent.parent.parent.parent
        candidates = [module_dir, Path.cwd()]
        for start in candidates:
            for parent in [start] + list(start.parents):
                if (parent / 'AGENTS.md').exists() or (parent / 'lore-book').exists():
                    return parent
        return module_dir

    def _setup_ui(self):
        """Set up the tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Search bar
        search_layout = QVBoxLayout()
        search_layout.setSpacing(6)
        search_layout.addWidget(QLabel("Search:"))
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search in documents...")
        self.search_edit.setMinimumHeight(28)
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._on_search)
        search_row.addWidget(self.search_edit)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setMinimumHeight(28)
        self.refresh_btn.clicked.connect(self._load_lore_tree)
        search_row.addWidget(self.refresh_btn)
        search_layout.addLayout(search_row)

        layout.addLayout(search_layout)

        # Splitter for tree and content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Document tree
        tree_group = QGroupBox("Documents")
        tree_layout = QVBoxLayout(tree_group)
        tree_layout.setContentsMargins(8, 12, 8, 8)
        self.doc_tree = QTreeWidget()
        self.doc_tree.setHeaderLabels(["Document"])
        self.doc_tree.itemClicked.connect(self._on_doc_selected)
        self.doc_tree.setMinimumWidth(200)
        tree_layout.addWidget(self.doc_tree)
        splitter.addWidget(tree_group)

        # Content viewer
        content_group = QGroupBox("Content")
        content_layout = QVBoxLayout(content_group)
        content_layout.setContentsMargins(10, 12, 10, 10)

        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(False)
        self.content_browser.anchorClicked.connect(self._on_anchor_clicked)
        self.content_browser.setFont(QFont("Sans", 10))

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        self.back_btn = QPushButton("← Back")
        self.back_btn.setEnabled(False)
        self.back_btn.setMinimumHeight(28)
        self.back_btn.clicked.connect(self.content_browser.backward)
        title_row.addWidget(self.back_btn)

        self.forward_btn = QPushButton("Forward →")
        self.forward_btn.setEnabled(False)
        self.forward_btn.setMinimumHeight(28)
        self.forward_btn.clicked.connect(self.content_browser.forward)
        title_row.addWidget(self.forward_btn)

        self.home_btn = QPushButton("Home")
        self.home_btn.setEnabled(False)
        self.home_btn.setMinimumHeight(28)
        self.home_btn.clicked.connect(self._go_home)
        title_row.addWidget(self.home_btn)

        self.title_label = QLabel("Select a document to view")
        self.title_label.setFont(QFont("Sans", 12, QFont.Weight.Bold))
        title_row.addWidget(self.title_label, 1)
        content_layout.addLayout(title_row)

        self.content_browser.backwardAvailable.connect(self.back_btn.setEnabled)
        self.content_browser.forwardAvailable.connect(self.forward_btn.setEnabled)
        content_layout.addWidget(self.content_browser)

        splitter.addWidget(content_group)

        splitter.setSizes([250, 650])
        layout.addWidget(splitter, 1)  # Give splitter all the stretch

        # Compact status bar (footer style)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px;")
        self.status_label.setMaximumHeight(20)
        layout.addWidget(self.status_label)

    def _load_lore_tree(self):
        """Load the document tree with WPF-style categories."""
        self._has_loaded = True
        if not self.lore_book_dir.exists():
            self.doc_tree.clear()
            self._all_docs = []
            self._item_by_path = {}
            self.status_label.setText(f"Lore book not found: {self.lore_book_dir}")
            return

        if self._loader and self._loader.isRunning():
            self._loader.requestInterruption()
            self._loader.wait(1000)

        self.doc_tree.clear()
        self._all_docs = []
        self._item_by_path = {}
        self.title_label.setText("Loading documents...")
        self.status_label.setText("Loading lore book...")

        self._loader = LoreLoader(self.lore_book_dir, self.book_path)
        self._loader.loaded.connect(self._on_lore_loaded)
        self._loader.failed.connect(self._on_lore_failed)
        self._loader.start()

    def _on_lore_loaded(self, docs: list[dict], toc_nodes: object):
        self._all_docs = docs
        self._toc_nodes = toc_nodes if isinstance(toc_nodes, list) else None
        self._using_lore_toc = self._toc_nodes is not None
        self._rebuild_tree(docs)
        if not docs:
            self.status_label.setText("No markdown files found in lore-book")
            self.title_label.setText("Select a document")
            self.home_btn.setEnabled(False)
        else:
            self.status_label.setText(f"Loaded {len(docs)} documents")
            self.title_label.setText(f"Select a document ({len(docs)} files)")
            self._select_default_doc(docs)
        if isinstance(self.current_file, Path):
            self._sync_tree_selection(self.current_file)

    def _on_lore_failed(self, message: str):
        self.status_label.setText(f"Failed to load lore documents: {message}")
        self.title_label.setText("Select a document")

    def _select_default_doc(self, docs: list[dict]):
        """Select the first book entry (or first doc) after loading."""
        if not docs:
            return

        def_key = lambda d: (d.get("order") if d.get("order") is not None else 10**9, d.get("title", "").lower())
        default_doc = sorted(docs, key=def_key)[0] if docs else None

        target_path = default_doc.get("path")
        self._home_doc = target_path if isinstance(target_path, Path) else None
        self._home_title = default_doc.get("title") if isinstance(default_doc, dict) else None
        self.home_btn.setEnabled(self._home_doc is not None)
        if isinstance(target_path, Path) and target_path in self._item_by_path:
            self.doc_tree.setCurrentItem(self._item_by_path[target_path])
        elif isinstance(target_path, Path):
            self._load_document(target_path, default_doc.get("title"))

    def _go_home(self):
        """Return to the default (home) document."""
        if not self._home_doc:
            return
        item = self._item_by_path.get(self._home_doc)
        if item is not None:
            self.doc_tree.setCurrentItem(item)
            return
        self._load_document(self._home_doc, self._home_title)

    def _on_doc_selected(self, item: QTreeWidgetItem, column: int):
        """Handle document selection"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path is None:
            return  # Category item, not a file

        self._load_document(file_path, item.text(0))

    def _load_document(self, file_path: Path, display_title: str | None = None):
        """Load and display a markdown document"""
        self.current_file = file_path

        try:
            content = file_path.read_text(encoding='utf-8')
            content = self._strip_frontmatter(content)
        except Exception as e:
            self.content_browser.setPlainText(f"Error reading file: {e}")
            return

        # Set title
        display_name = display_title or self._format_title(file_path.stem)
        self.title_label.setText(display_name)

        # Base URL for relative links/images
        try:
            self.content_browser.document().setBaseUrl(QUrl.fromLocalFile(str(file_path.parent) + "/"))
        except Exception:
            pass

        # Render markdown to HTML (or fallback)
        if MARKDOWN_AVAILABLE:
            html = markdown.markdown(
                content,
                extensions=['tables', 'fenced_code', 'toc']
            )
            styled_html = f"""
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; color: {TEXT_COLOR}; }}
                h1, h2, h3 {{ color: {ACCENT_COLOR}; }}
                code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background: #f4f4f4; }}
                blockquote {{ border-left: 3px solid #ccc; margin: 10px 0; padding-left: 15px; color: #666; }}
                a {{ color: {ACCENT_COLOR}; }}
            </style>
            {html}
            """
            self.content_browser.setHtml(styled_html)
        else:
            # Fallback: use Qt's markdown support if available
            try:
                self.content_browser.setMarkdown(content)
            except Exception:
                self.content_browser.setPlainText(content)

        self.status_label.setText(f"Viewing: {file_path.name}")
        self._sync_tree_selection(file_path)

    def _on_anchor_clicked(self, url: QUrl):
        url_str = url.toString()
        if not url_str:
            return

        if url_str.startswith("#"):
            self.content_browser.scrollToAnchor(url_str[1:])
            return

        path_part, anchor = (url_str.split("#", 1) + [None])[:2]
        path_part = path_part or ""
        if "?" in path_part:
            path_part = path_part.split("?", 1)[0]

        target_path = None
        if url.isRelative() or (not url.scheme()):
            if self.current_file:
                target_path = (self.current_file.parent / path_part).resolve()
        elif url.scheme() == "file":
            target_path = Path(url.toLocalFile())

        resolved = self._resolve_markdown_target(target_path)
        if resolved is not None:
            self._load_document(resolved, None)
            if anchor:
                self.content_browser.scrollToAnchor(anchor)
            return

        if path_part:
            fallback = (self.project_root / path_part.lstrip("./")).resolve()
            resolved = self._resolve_markdown_target(fallback)
            if resolved is not None:
                self._load_document(resolved, None)
                if anchor:
                    self.content_browser.scrollToAnchor(anchor)
                return

        QDesktopServices.openUrl(url)

    @staticmethod
    def _strip_frontmatter(content: str) -> str:
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return content
        end_index = None
        for i in range(1, min(len(lines), 60)):
            if lines[i].strip() == "---":
                end_index = i
                break
        if end_index is None:
            return content
        return "\n".join(lines[end_index + 1:])

    @staticmethod
    def _resolve_markdown_target(target_path: Path | None) -> Path | None:
        if target_path is None:
            return None
        if target_path.is_file():
            if target_path.suffix.lower() == ".md":
                return target_path
            if target_path.suffix == "":
                candidate = target_path.with_suffix(".md")
                if candidate.exists():
                    return candidate
            return None
        if target_path.is_dir():
            for name in ("_index.md", "index.md", "README.md", "readme.md"):
                candidate = target_path / name
                if candidate.exists():
                    return candidate
        if target_path.suffix == "":
            candidate = target_path.with_suffix(".md")
            if candidate.exists():
                return candidate
        return None

    def _on_search(self, text: str):
        """Filter documents by search text"""
        query = text.strip().lower()
        self._search_query = query
        expanded = self._capture_expanded_paths()

        if not query:
            self._rebuild_tree(self._all_docs)
            if self._all_docs:
                self.title_label.setText(f"Select a document ({len(self._all_docs)} files)")
                self.status_label.setText(f"Loaded {len(self._all_docs)} documents")
            else:
                self.title_label.setText("Select a document")
                self.status_label.setText("No markdown files found in lore-book")
            self._restore_expanded_paths(expanded)
            if isinstance(self.current_file, Path):
                self._sync_tree_selection(self.current_file)
            return

        filtered = []
        for doc in self._all_docs:
            if query in doc["title"].lower():
                filtered.append(doc)
                continue

            if len(query) >= 3:
                try:
                    content = doc["path"].read_text(encoding="utf-8").lower()
                    if query in content:
                        filtered.append(doc)
                except Exception:
                    pass

        self._rebuild_tree(filtered)
        self.title_label.setText(f"Found {len(filtered)} document(s)")
        self.status_label.setText(f"Search: {len(filtered)} match(es)")
        self._restore_expanded_paths(expanded)
        if isinstance(self.current_file, Path):
            self._sync_tree_selection(self.current_file)

    def _rebuild_tree(self, docs: list[dict]):
        """Rebuild folder-based tree."""
        self.doc_tree.clear()
        self._item_by_path = {}

        if self._using_lore_toc and self._toc_nodes is not None:
            allowed_paths = {doc["path"] for doc in docs if isinstance(doc.get("path"), Path)}
            self._build_tree_from_toc(self._toc_nodes, allowed_paths)
            return

        root_items = {}
        node_map: dict[tuple[str, tuple[str, ...]], QTreeWidgetItem] = {}

        for doc in docs:
            source = doc["source"]
            root_item = root_items.setdefault(source, QTreeWidgetItem([source]))
            root_item.setData(0, Qt.ItemDataRole.UserRole, None)

            parts = list(doc["relative_parts"])
            folder_parts = parts[:-1]
            parent_item = root_item
            current_path: list[str] = []

            for folder in folder_parts:
                current_path.append(folder)
                key = (source, tuple(current_path))
                if key not in node_map:
                    folder_title = self._format_title(folder)
                    folder_item = QTreeWidgetItem([folder_title])
                    folder_item.setData(0, Qt.ItemDataRole.UserRole, None)
                    folder_item.setData(0, Qt.ItemDataRole.UserRole + 1, False)
                    folder_item.setData(0, Qt.ItemDataRole.UserRole + 2, True)
                    parent_item.addChild(folder_item)
                    node_map[key] = folder_item
                parent_item = node_map[key]

            file_item = QTreeWidgetItem([doc["title"]])
            file_item.setData(0, Qt.ItemDataRole.UserRole, doc["path"])
            file_item.setData(0, Qt.ItemDataRole.UserRole + 1, doc["is_index"])
            file_item.setData(0, Qt.ItemDataRole.UserRole + 2, False)
            file_item.setData(0, Qt.ItemDataRole.UserRole + 3, doc.get("order"))
            file_item.setToolTip(0, str(doc["path"]))
            parent_item.addChild(file_item)
            if isinstance(doc.get("path"), Path):
                self._item_by_path[doc["path"]] = file_item

            if doc.get("is_index") and doc.get("order") is not None:
                if parent_item.data(0, Qt.ItemDataRole.UserRole + 3) is None:
                    parent_item.setData(0, Qt.ItemDataRole.UserRole + 3, doc.get("order"))

        ordered_roots = ["Lore Book"]
        for name in ordered_roots:
            root = root_items.get(name)
            if root:
                self._sort_tree(root)
                root.setExpanded(True)
                self.doc_tree.addTopLevelItem(root)

        for name, root in root_items.items():
            if name in ordered_roots:
                continue
            self._sort_tree(root)
            root.setExpanded(True)
            self.doc_tree.addTopLevelItem(root)

        # Keep top-level sections expanded, but avoid expanding every subfolder at once.

    def _build_tree_from_toc(self, toc_nodes: list[dict], allowed_paths: set[Path]):
        """Build tree from toc structure, filtering by allowed paths when searching."""
        root_item = QTreeWidgetItem(["Lore Book"])
        root_item.setData(0, Qt.ItemDataRole.UserRole, None)

        def build_node(parent: QTreeWidgetItem, node: dict) -> bool:
            title = node.get("title") or "Untitled"
            path = node.get("path")
            children = node.get("children") or []

            include_self = isinstance(path, Path) and path in allowed_paths
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.ItemDataRole.UserRole, path if include_self else None)
            item.setData(0, Qt.ItemDataRole.UserRole + 1, bool(node.get("is_index")))
            item.setData(0, Qt.ItemDataRole.UserRole + 2, not isinstance(path, Path))
            item.setData(0, Qt.ItemDataRole.UserRole + 3, node.get("order"))
            if isinstance(path, Path):
                item.setToolTip(0, str(path))
                self._item_by_path[path] = item

            included_children = False
            for child in children:
                if build_node(item, child):
                    included_children = True

            if include_self or included_children:
                parent.addChild(item)
                return True

            return False

        for node in toc_nodes:
            build_node(root_item, node)

        self._sort_tree(root_item)
        root_item.setExpanded(True)
        self.doc_tree.addTopLevelItem(root_item)

    def _sort_tree(self, item: QTreeWidgetItem):
        children = [item.child(i) for i in range(item.childCount())]

        def sort_key(child: QTreeWidgetItem):
            is_index = bool(child.data(0, Qt.ItemDataRole.UserRole + 1))
            is_folder = bool(child.data(0, Qt.ItemDataRole.UserRole + 2))
            group = 0 if is_index else 1 if is_folder else 2
            order = child.data(0, Qt.ItemDataRole.UserRole + 3)
            order_value = order if isinstance(order, int) else 10**9
            return (group, order_value, child.text(0).lower())

        children.sort(key=sort_key)
        item.takeChildren()
        for child in children:
            item.addChild(child)
            if child.childCount() > 0:
                self._sort_tree(child)

    @staticmethod
    def _format_title(file_name: str) -> str:
        """Convert kebab/snake case to Title Case, preserving acronyms."""
        parts = [p for p in file_name.replace("_", "-").split("-") if p]
        return " ".join(LoreBrowserTab._format_token(p) for p in parts)

    @staticmethod
    def _indent_level(indent: str) -> int:
        level = 0
        spaces = 0
        for ch in indent:
            if ch == "\t":
                level += 1
            elif ch == " ":
                spaces += 1
                if spaces == 2:
                    level += 1
                    spaces = 0
        return level + (spaces // 2)

    @staticmethod
    def _format_token(token: str) -> str:
        if token.isupper() or any(ch.isdigit() for ch in token):
            return token
        if any(ch.isupper() for ch in token) and any(ch.islower() for ch in token):
            return token
        return token[:1].upper() + token[1:].lower()

    @staticmethod
    def _is_index_file(stem: str) -> bool:
        return stem.lower() in {"index", "readme", "_index", "lore-index", "re-index", "roadmap-index"}

    def _sync_tree_selection(self, file_path: Path) -> None:
        item = self._item_by_path.get(file_path)
        if item is None:
            return
        self.doc_tree.setCurrentItem(item)
        self.doc_tree.scrollToItem(item)

    def _expand_all(self) -> None:
        def expand_item(node: QTreeWidgetItem) -> None:
            node.setExpanded(True)
            for i in range(node.childCount()):
                expand_item(node.child(i))

        for i in range(self.doc_tree.topLevelItemCount()):
            expand_item(self.doc_tree.topLevelItem(i))

    def _capture_expanded_paths(self) -> set[str]:
        paths: set[str] = set()

        def walk(item: QTreeWidgetItem, stack: list[str]) -> None:
            title = item.text(0)
            new_stack = [*stack, title]
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(data, Path):
                key = f"file:{data}"
            else:
                key = f"title:{'>'.join(new_stack)}"
            if item.isExpanded():
                paths.add(key)
            for i in range(item.childCount()):
                walk(item.child(i), new_stack)

        for i in range(self.doc_tree.topLevelItemCount()):
            walk(self.doc_tree.topLevelItem(i), [])
        return paths

    def _restore_expanded_paths(self, paths: set[str]) -> None:
        if not paths:
            return

        def walk(item: QTreeWidgetItem, stack: list[str]) -> None:
            title = item.text(0)
            new_stack = [*stack, title]
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(data, Path):
                key = f"file:{data}"
            else:
                key = f"title:{'>'.join(new_stack)}"
            if key in paths:
                item.setExpanded(True)
            for i in range(item.childCount()):
                walk(item.child(i), new_stack)

        for i in range(self.doc_tree.topLevelItemCount()):
            walk(self.doc_tree.topLevelItem(i), [])

    @staticmethod
    def _should_skip_index(path: Path, stem: str) -> bool:
        lower = stem.lower()
        if (path.parent / "_index.md").exists():
            return lower != "_index"
        if lower == "readme" and (path.parent / "index.md").exists():
            return True
        return False

    @staticmethod
    def _is_generic_title(title: str) -> bool:
        return title.strip().lower() in {"index", "overview", "readme"}

    @staticmethod
    def _read_frontmatter(path: Path) -> tuple[str | None, int | None]:
        title = None
        order = None
        try:
            with path.open("r", encoding="utf-8") as handle:
                in_frontmatter = False
                saw_frontmatter = False
                for i in range(40):
                    line = handle.readline()
                    if not line:
                        break
                    stripped = line.strip()
                    if i == 0 and stripped == "---":
                        in_frontmatter = True
                        saw_frontmatter = True
                        continue
                    if in_frontmatter:
                        if stripped == "---":
                            in_frontmatter = False
                            if title:
                                return title, order
                            continue
                        if stripped.lower().startswith("title:"):
                            value = stripped[6:].strip().strip('"')
                            if value:
                                title = value
                        if stripped.lower().startswith("order:"):
                            value = stripped[6:].strip().strip('"')
                            if value.isdigit():
                                order = int(value)
                        continue

                    if saw_frontmatter and title:
                        return title, order

                    if not stripped:
                        continue
                    if stripped.startswith("# "):
                        return stripped[2:].strip(), order
                    if stripped.startswith("## "):
                        return stripped[3:].strip(), order
        except Exception:
            return None, None
        return None, order

    @staticmethod
    def _resolve_title(path: Path, source_label: str, relative_path: Path, is_index: bool) -> tuple[str, int | None]:
        content_title, order = LoreBrowserTab._read_frontmatter(path)
        if is_index:
            if content_title and not LoreBrowserTab._is_generic_title(content_title):
                return content_title, order
            if relative_path.parent == Path("."):
                return f"{source_label} Index", order
            return f"{LoreBrowserTab._format_title(relative_path.parent.name)} Index", order

        if content_title and not LoreBrowserTab._is_generic_title(content_title):
            return content_title, order

        return LoreBrowserTab._format_title(path.stem), order

    @staticmethod
    def _disambiguate_titles(docs: list[dict]) -> None:
        by_key: dict[tuple[str, str, str], list[dict]] = {}
        for doc in docs:
            folder = str(doc["path"].parent)
            key = (doc["source"].lower(), folder.lower(), doc["title"].lower())
            by_key.setdefault(key, []).append(doc)

        for group in by_key.values():
            if len(group) <= 1:
                continue
            for doc in group:
                stem_title = LoreBrowserTab._format_title(doc["path"].stem)
                doc["title"] = f"{doc['title']} ({stem_title})"

    @staticmethod
    def _load_book(book_path: Path, lore_book_root: Path) -> tuple[list[dict], list[dict] | None]:
        if not book_path.exists():
            return [], None

        try:
            lines = book_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            return [], None

        docs: list[dict] = []
        nodes: list[dict] = []
        stack: list[tuple[int, dict]] = []
        order = 0
        in_code = False

        for raw in lines:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                continue
            if in_code or not stripped:
                continue

            match = re.match(r"^(?P<indent>[ \t]*)[-*+]\s+(?P<content>.+)$", line)
            if not match:
                continue

            indent = match.group("indent") or ""
            level = LoreBrowserTab._indent_level(indent)
            content = match.group("content").strip()
            if not content:
                continue

            title = content
            file_name = None
            link_match = re.match(r"^\[(?P<title>.+?)\]\((?P<file>.+?)\)$", content)
            if link_match:
                title = link_match.group("title").strip()
                file_name = link_match.group("file").strip()

            file_path = None
            is_index = False
            relative_parts = ()
            if file_name:
                candidate = (lore_book_root / file_name).resolve()
                if candidate.exists():
                    file_path = candidate
                    relative_parts = candidate.relative_to(lore_book_root).parts
                    is_index = LoreBrowserTab._is_index_file(candidate.stem)

            node = {
                "title": title if title else "Section",
                "order": order,
                "path": file_path,
                "is_index": is_index,
                "children": []
            }
            order += 1

            while stack and stack[-1][0] >= level:
                stack.pop()
            if stack:
                stack[-1][1]["children"].append(node)
            else:
                nodes.append(node)
            stack.append((level, node))

            if file_path is not None:
                docs.append({
                    "title": node["title"],
                    "order": node["order"],
                    "path": file_path,
                    "source": "Lore Book",
                    "relative_parts": relative_parts,
                    "is_index": is_index,
                })

        return docs, nodes if nodes else None


class LoreLoader(QThread):
    loaded = pyqtSignal(list, object)
    failed = pyqtSignal(str)

    def __init__(self, lore_book_root: Path, book_path: Path, parent=None):
        super().__init__(parent)
        self._lore_book_root = lore_book_root
        self._book_path = book_path

    def run(self):
        docs = []
        toc_nodes = None
        try:
            if self.isInterruptionRequested():
                return

            if not self._lore_book_root.exists():
                self.loaded.emit([], None)
                return

            docs, toc_nodes = LoreBrowserTab._load_book(self._book_path, self._lore_book_root)
            if toc_nodes is not None:
                LoreBrowserTab._disambiguate_titles(docs)
                self.loaded.emit(docs, toc_nodes)
                return

            for md_file in self._lore_book_root.rglob("*.md"):
                if self.isInterruptionRequested():
                    return
                if LoreBrowserTab._is_index_file(md_file.stem) and LoreBrowserTab._should_skip_index(md_file, md_file.stem):
                    continue
                relative_path = md_file.relative_to(self._lore_book_root)
                is_index = LoreBrowserTab._is_index_file(md_file.stem)
                display_title, order = LoreBrowserTab._resolve_title(md_file, "Lore Book", relative_path, is_index)
                docs.append({
                    "title": display_title,
                    "order": order,
                    "path": md_file,
                    "source": "Lore Book",
                    "relative_parts": relative_path.parts,
                    "is_index": is_index,
                })

            LoreBrowserTab._disambiguate_titles(docs)
            self.loaded.emit(docs, None)
        except Exception as exc:
            self.failed.emit(str(exc))
