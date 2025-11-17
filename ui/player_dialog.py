# wakfu_translator/ui/player_dialog.py
"""
Player tracking management dialog.
Allows users to add, edit, and remove tracked players with their language settings.
"""

import re
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLineEdit,
    QComboBox,
    QLabel,
    QMessageBox,
    QListWidgetItem,
)
from settings import load_tracked_players, save_tracked_players
from constants import SUPPORTED_LANGUAGES


def clean_player_name(name: str) -> str:
    """
    Clean player name by removing whisper commands and quotes.
    Examples:
        '/w "PlayerName"' -> 'PlayerName'
        '/w PlayerName' -> 'PlayerName'
        '"PlayerName"' -> 'PlayerName'
        'PlayerName' -> 'PlayerName'
    """
    name = name.strip()
    # Remove /w or /whisper command
    name = re.sub(r'^/w(?:hisper)?\s+', '', name, flags=re.IGNORECASE)
    # Remove quotes
    name = name.strip('"\'')
    return name.strip()


class PlayerDialog(QDialog):
    """Dialog for managing tracked players"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Player Tracking Management")
        self.resize(450, 400)
        
        # Load current tracked players
        self.tracked_players = load_tracked_players()
        
        self.init_ui()
        self.populate_list()

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # Player list
        list_label = QLabel("Tracked Players:")
        layout.addWidget(list_label)
        
        self.player_list = QListWidget()
        self.player_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.player_list)
        
        # Input section
        input_layout = QHBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Player name...")
        input_layout.addWidget(self.name_input)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(SUPPORTED_LANGUAGES)
        self.lang_combo.setCurrentText("en")
        input_layout.addWidget(self.lang_combo)
        
        layout.addLayout(input_layout)
        
        # Buttons section
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_player)
        button_layout.addWidget(self.add_btn)
        
        self.update_btn = QPushButton("Update")
        self.update_btn.clicked.connect(self.update_player)
        self.update_btn.setEnabled(False)
        button_layout.addWidget(self.update_btn)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_player)
        self.remove_btn.setEnabled(False)
        button_layout.addWidget(self.remove_btn)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        
        save_btn = QPushButton("Save & Close")
        save_btn.clicked.connect(self.accept)
        dialog_buttons.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        dialog_buttons.addWidget(cancel_btn)
        
        layout.addLayout(dialog_buttons)
        
        self.setLayout(layout)

    def populate_list(self):
        """Populate the list widget with tracked players"""
        self.player_list.clear()
        for player_name, lang in sorted(self.tracked_players.items()):
            item_text = f"{player_name} ({lang})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, player_name)  # Store player name in item data
            self.player_list.addItem(item)

    def on_item_clicked(self, item):
        """Handle list item click"""
        player_name = item.data(Qt.UserRole)
        lang = self.tracked_players.get(player_name, "en")
        
        self.name_input.setText(player_name)
        self.lang_combo.setCurrentText(lang)
        
        self.update_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.add_btn.setEnabled(False)

    def add_player(self):
        """Add a new player to the tracked list"""
        player_name = clean_player_name(self.name_input.text())
        
        if not player_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a player name.")
            return
        
        # Check for case-insensitive duplicates
        existing_names_lower = {name.lower(): name for name in self.tracked_players.keys()}
        if player_name.lower() in existing_names_lower:
            QMessageBox.warning(self, "Duplicate Player", f"Player '{existing_names_lower[player_name.lower()]}' is already tracked.")
            return
        
        lang = self.lang_combo.currentText()
        self.tracked_players[player_name] = lang
        
        self.populate_list()
        self.clear_inputs()

    def update_player(self):
        """Update an existing player's language"""
        selected_items = self.player_list.selectedItems()
        if not selected_items:
            return
        
        old_name = selected_items[0].data(Qt.UserRole)
        new_name = clean_player_name(self.name_input.text())
        
        if not new_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a player name.")
            return
        
        # Remove old entry
        if old_name in self.tracked_players:
            del self.tracked_players[old_name]
        
        # Add updated entry
        lang = self.lang_combo.currentText()
        self.tracked_players[new_name] = lang
        
        self.populate_list()
        self.clear_inputs()

    def remove_player(self):
        """Remove a player from the tracked list"""
        selected_items = self.player_list.selectedItems()
        if not selected_items:
            return
        
        player_name = selected_items[0].data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove player '{player_name}' from tracking?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if player_name in self.tracked_players:
                del self.tracked_players[player_name]
            
            self.populate_list()
            self.clear_inputs()

    def clear_inputs(self):
        """Clear input fields and reset button states"""
        self.name_input.clear()
        self.lang_combo.setCurrentText("en")
        self.player_list.clearSelection()
        
        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)

    def accept(self):
        """Save tracked players and close dialog"""
        save_tracked_players(self.tracked_players)
        super().accept()
