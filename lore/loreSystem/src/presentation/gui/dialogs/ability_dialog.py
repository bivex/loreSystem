"""
AbilityDialog - Dialog for adding/editing abilities.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QSpinBox,
    QDialogButtonBox, QMessageBox
)

from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel


class AbilityDialog(QDialog):
    """Dialog for adding/editing abilities."""
    
    def __init__(self, parent=None, ability: Optional[Ability] = None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Ability")
        self.setModal(True)
        self.ability = ability
        self._setup_ui()
        
        if ability:
            self._load_ability(ability)
    
    def _setup_ui(self):
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.power_input = QSpinBox()
        self.power_input.setRange(1, 10)
        self.power_input.setValue(5)
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Power Level (1-10):", self.power_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
    
    def _load_ability(self, ability: Ability):
        self.name_input.setText(str(ability.name))
        self.description_input.setPlainText(ability.description)
        self.power_input.setValue(ability.power_level.value)
    
    def get_ability(self) -> Optional[Ability]:
        """Get the ability from form data."""
        try:
            return Ability(
                name=AbilityName(self.name_input.text()),
                description=self.description_input.toPlainText(),
                power_level=PowerLevel(self.power_input.value())
            )
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", str(e))
            return None