import threading
from PyQt5.QtCore import Qt, QPoint, QRect, QTime
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QMenu,
    QTextEdit,
    QLineEdit,
    QMessageBox,
)
from signals import ui_signals
from translation.argostranslator import translate_text_via_argos
from workers.file_reader import file_reader_worker
from workers.translator import translator_worker
from settings import load_settings
from ui.settings_dialog import SettingsDialog
from translation.parser import parse_wakfu_colors


# --- Component: ChatTabs ---
class ChatTabs(QTabWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.setStyleSheet(
            """
            QTabWidget::pane { background: rgba(0,0,0,0); border: none; }
            QTabBar::tab { background: rgba(40,40,40,180); padding:3px 10px; border-radius:5px; }
            QTabBar::tab:selected { background: rgba(70,70,70,200); font-weight:bold; }
            """
        )

    def contextMenuEvent(self, event):
        tab_index = self.tabBar().tabAt(event.pos())
        if tab_index < 0:
            return

        tab_widget = self.widget(tab_index)
        if not tab_widget.property("player_name"):
            return  # only for player tabs

        menu = QMenu(self)
        langs = ["auto", "fr", "es", "de", "ja", "zh", "ru"]

        for lang in langs:
            action = menu.addAction(lang)
            # use lambda to capture tab_widget, tab_index, lang
            action.triggered.connect(
                lambda _, l=lang, tw=tab_widget, idx=tab_index: self.update_tab_label(
                    tw, idx, l
                )
            )

        menu.exec_(event.globalPos())

    # 👇 Add this method inside the class
    def update_tab_label(self, tab_widget, tab_index, lang):
        tab_widget.setProperty("source_lang", lang)
        player_name = tab_widget.property("player_name") or "Player"
        target_lang = "en"  # or read from settings if you want dynamic target
        self.setTabText(tab_index, f"{player_name} [{lang}→{target_lang}]")

    def add_tab(self, name, ai_tab=False, player_name=None):
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        # Default per-tab source language
        text_edit.setProperty("source_lang", "en")
        if ai_tab:
            text_edit.setStyleSheet(
                """
                background: rgba(20,20,40,180);
                border: none; border-radius: 4px; padding: 4px;
                font-weight: bold; font-size: 14px;
            """
            )
            text_edit.setProperty("is_ai_tab", True)
        elif player_name:
            text_edit.setStyleSheet(
                """
                background: rgba(30,30,50,180);
                border: none; border-radius: 4px; padding: 4px;
                font-weight: bold; font-size: 14px;
            """
            )
            text_edit.setProperty("player_name", player_name)
        else:
            text_edit.setStyleSheet(
                """
                background: rgba(0,0,0,120);
                border: none; border-radius: 4px; padding: 4px;
                font-weight: 900; font-size: 16px;
            """
            )
        self.addTab(text_edit, name)
        self.setCurrentWidget(text_edit)
        return text_edit

    def close_tab(self, index):
        if index == 0:
            QMessageBox.information(self, "Notice", "Cannot close General tab")
            return
        self.removeTab(index)

    def append_to_tab(self, tab_widget, message, is_ai=False):
        if tab_widget.property("is_ai_tab") and not is_ai:
            return
        try:
            # translated = translate_line(message, self.settings.get("target_lang", "en"),
            #                             self.settings.get("model_name", ""))
            safe = parse_wakfu_colors(message)
            tab_widget.append(safe)
            tab_widget.ensureCursorVisible()
        except Exception as e:
            print("Append error:", e)


# --- Component: ChatInputBar ---
class ChatInputBar(QHBoxLayout):
    def __init__(self, parent, send_callback):
        super().__init__()
        self.parent = parent
        self.send_callback = send_callback

        self.input_bar = QLineEdit()
        self.input_bar.setPlaceholderText(
            "/w player name then click + to add a player tab or type message and press Enter to see translation"
        )
        self.input_bar.returnPressed.connect(self.send_callback)

        self.add_tab_btn = QPushButton("+")
        self.add_tab_btn.setToolTip("Add a new tab")

        self.minimize_btn = QPushButton("▼")
        self.minimize_btn.setToolTip("Minimize/restore chat window")

        self.grab_btn = QPushButton("🤚")
        self.grab_btn.setToolTip("Drag the chat window")

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setToolTip("Open settings")

        self.close_btn = QPushButton("✖")
        self.close_btn.setToolTip("Close the chat window")

        for b in [
            self.add_tab_btn,
            self.minimize_btn,
            self.grab_btn,
            self.settings_btn,
            self.close_btn,
        ]:
            b.setFixedSize(22, 22)
            b.setStyleSheet(
                """
                QPushButton {
                    background: rgba(40,40,40,180);
                    color: white; border: none; border-radius: 4px;
                }
                QPushButton:hover { background: rgba(80,80,80,230); }
            """
            )

        self.addWidget(self.input_bar, 1)
        self.addWidget(self.add_tab_btn)
        self.addWidget(self.minimize_btn)
        self.addWidget(self.grab_btn)
        self.addWidget(self.settings_btn)
        self.addWidget(self.close_btn)


# --- Main UI ---
class ChatUI(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        try:
            self.setWindowOpacity(float(self.settings.get("transparency", 0.85)))
        except Exception:
            pass
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.dragging = False
        self.resizing = False
        self.resize_dir = None
        self.drag_start = QPoint()
        self.start_geom = QRect()
        self.resize_margin = 8
        self.is_minimized = False
        self.normal_height = 280

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Tabs
        self.tabs = ChatTabs(self.settings)
        layout.addWidget(self.tabs)

        # Input bar
        self.input_bar_layout = ChatInputBar(self, self.send_message)
        layout.addLayout(self.input_bar_layout)

        self.setStyleSheet(
            """
            QWidget { background: rgba(0,0,0,120); color: white; font-family: Consolas, monospace; font-size: 12px; }
            QLineEdit { background: rgba(30,30,30,160); border: 1px solid white; padding: 4px; border-radius: 5px; color: white; }
        """
        )

        self.resize(600, self.normal_height)

        # Connect buttons
        self.input_bar_layout.add_tab_btn.clicked.connect(self.handle_add_tab)
        self.input_bar_layout.close_btn.clicked.connect(self.close)
        self.input_bar_layout.grab_btn.mousePressEvent = self.grab_button_pressed
        self.input_bar_layout.minimize_btn.clicked.connect(self.toggle_minimize)
        self.input_bar_layout.settings_btn.clicked.connect(self.open_settings)

        # Default tab
        self.tabs.add_tab("General")

        # Connect signals
        ui_signals.append_text.connect(self.append_chat)
        ui_signals.status_text.connect(self.append_chat)
        ui_signals.append_text_to_tab.connect(self.tabs.append_to_tab)
        ui_signals.chat_ui = self

        # Start workers
        self._stop_event = threading.Event()
        threading.Thread(
            target=file_reader_worker,
            args=(self._stop_event, self.settings, ui_signals),
            daemon=True,
        ).start()
        threading.Thread(
            target=translator_worker, args=(self._stop_event,), daemon=True
        ).start()
        # threading.Thread(target=self._check_ollama_and_models, daemon=True).start()

    # --- Message Handling ---
    def append_chat(self, message):
        try:
            html = parse_wakfu_colors(message)

            for i in range(self.tabs.count()):
                tab_name = self.tabs.tabText(i)
                if tab_name != "General" and tab_name.lower() not in message.lower():
                    continue

                tab_widget = self.tabs.widget(i)

                print(tab_name, message)

                if not tab_widget or tab_widget.property("is_ai_tab"):
                    continue

                scrollbar = tab_widget.verticalScrollBar()
                at_bottom = scrollbar.value() == scrollbar.maximum()

                max_lines = 1000
                if tab_widget.document().blockCount() > max_lines:
                    cursor = tab_widget.textCursor()
                    cursor.movePosition(cursor.Start)
                    cursor.select(cursor.LineUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deleteChar()

                tab_widget.append(html)

                if at_bottom:
                    tab_widget.ensureCursorVisible()

        except Exception as e:
            print("Append error:", e)

    def handle_add_tab(self):
        text = self.input_bar_layout.input_bar.text().strip()
        if text.startswith('/w "'):
            try:
                name = text.split('"')[1].strip() or "YOU"
            except IndexError:
                name = "YOU"
        else:
            name = "YOU"

        self.tabs.add_tab(name, player_name=name)
        self.input_bar_layout.input_bar.clear()

    def send_message(self):
        text = self.input_bar_layout.input_bar.text().strip()
        if not text:
            return
        current_tab = self.tabs.currentWidget()
        if not current_tab:
            return

        current_index = self.tabs.currentIndex()
        tab_name = self.tabs.tabText(current_index)

        current_time = QTime.currentTime().toString("HH:mm:ss")
        is_ai_tab = bool(current_tab.property("is_ai_tab"))

        self.input_bar_layout.input_bar.clear()

        # If it's NOT the "General" tab, translate message
        if tab_name != "General":
            try:
                target_lang = current_tab.property("source_lang") or "en"
                source_lang = self.settings.get("target_lang", "en")

                _, text = translate_text_via_argos(text, source_lang, target_lang)
            except Exception as e:
                print("Translation error:", e)

        # Now send to the current tab
        current_tab.append(f"[{current_time}] You : {text}")

    # --- Settings ---
    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec_():
            self.settings = load_settings()
            self.append_chat("✅ Settings updated.")

    # --- Drag / Resize ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.globalPos()
            self.start_geom = self.geometry()
            edge = self.get_edge_at_pos(event.pos())
            if edge:
                self.resizing = True
                self.resize_dir = edge
            else:
                self.dragging = True

    def mouseMoveEvent(self, event):
        if self.resizing:
            diff = event.globalPos() - self.drag_start
            geom = QRect(self.start_geom)
            if "right" in self.resize_dir:
                geom.setWidth(max(200, geom.width() + diff.x()))
            if "bottom" in self.resize_dir:
                geom.setHeight(max(150, geom.height() + diff.y()))
            if "left" in self.resize_dir:
                geom.setLeft(geom.left() + diff.x())
            if "top" in self.resize_dir:
                geom.setTop(geom.top() + diff.y())
            self.setGeometry(geom)
        elif self.dragging:
            diff = event.globalPos() - self.drag_start
            self.move(self.start_geom.topLeft() + diff)
        else:
            edge = self.get_edge_at_pos(event.pos())
            if edge in ("left", "right"):
                self.setCursor(Qt.SizeHorCursor)
            elif edge in ("top", "bottom"):
                self.setCursor(Qt.SizeVerCursor)
            elif edge in ("top-left", "bottom-right"):
                self.setCursor(Qt.SizeFDiagCursor)
            elif edge in ("top-right", "bottom-left"):
                self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.resize_dir = None
        self.setCursor(Qt.ArrowCursor)

    def grab_button_pressed(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start = event.globalPos()
            self.start_geom = self.geometry()

    def get_edge_at_pos(self, pos):
        x, y, w, h, m = (
            pos.x(),
            pos.y(),
            self.width(),
            self.height(),
            self.resize_margin,
        )
        if x <= m and y <= m:
            return "top-left"
        if x >= w - m and y <= m:
            return "top-right"
        if x <= m and y >= h - m:
            return "bottom-left"
        if x >= w - m and y >= h - m:
            return "bottom-right"
        if x <= m:
            return "left"
        if x >= w - m:
            return "right"
        if y <= m:
            return "top"
        if y >= h - m:
            return "bottom"
        return None

    def toggle_minimize(self):
        if not self.is_minimized:
            self.normal_height = self.height()
            stacked = self.tabs.findChild(QWidget, "qt_tabwidget_stackedwidget")
            if stacked:
                stacked.setVisible(False)
            self.tabs.tabBar().setVisible(False)
            spacing = 8
            new_height = (
                self.input_bar_layout.input_bar.sizeHint().height()
                + max(
                    self.input_bar_layout.add_tab_btn.height(),
                    self.input_bar_layout.minimize_btn.height(),
                    self.input_bar_layout.grab_btn.height(),
                    self.input_bar_layout.settings_btn.height(),
                    self.input_bar_layout.close_btn.height(),
                )
                + spacing
            )
            self.resize(self.width(), new_height)
            self.is_minimized = True
            self.input_bar_layout.minimize_btn.setText("▼")
        else:
            stacked = self.tabs.findChild(QWidget, "qt_tabwidget_stackedwidget")
            if stacked:
                stacked.setVisible(True)
            self.tabs.tabBar().setVisible(True)
            self.resize(self.width(), self.normal_height)
            self.is_minimized = False
            self.input_bar_layout.minimize_btn.setText("▲")
