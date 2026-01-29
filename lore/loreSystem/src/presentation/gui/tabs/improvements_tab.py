"""
ImprovementsTab - Tab for managing improvements.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.improvement import Improvement
from src.domain.value_objects.common import (
    TenantId, EntityId, EntityType
)
from src.presentation.gui.lore_data import LoreData

class ImprovementsTab(QWidget):
    """Tab for managing improvements."""
    
    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Improvements")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Improvements table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Entity", "Suggestion", "Status", "Created"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Form
        form_group = QGroupBox("Improvement Details")
        form_layout = QFormLayout()
        
        self.entity_type_combo = QComboBox()
        self.entity_type_combo.addItems(["world", "character", "event"])
        self.entity_type_combo.currentTextChanged.connect(self._on_entity_type_changed)
        
        self.entity_combo = QComboBox()
        self.suggestion_input = QTextEdit()
        self.suggestion_input.setMaximumHeight(100)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["proposed", "approved", "applied", "rejected"])
        
        form_layout.addRow("Entity Type:", self.entity_type_combo)
        form_layout.addRow("Entity:", self.entity_combo)
        form_layout.addRow("Suggestion:", self.suggestion_input)
        form_layout.addRow("Status:", self.status_combo)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Propose Improvement")
        self.add_btn.clicked.connect(self._add_improvement)
        
        self.update_btn = QPushButton("Update Status")
        self.update_btn.clicked.connect(self._update_improvement)
        self.update_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete Improvement")
        self.delete_btn.clicked.connect(self._delete_improvement)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.selected_improvement: Optional[Improvement] = None
        self._update_entity_combo()
    
    def _on_entity_type_changed(self):
        """Handle entity type change."""
        self._update_entity_combo()
    
    def _update_entity_combo(self):
        """Update entity combo based on selected type."""
        entity_type = self.entity_type_combo.currentText()
        self.entity_combo.clear()
        
        if entity_type == "world":
            for world in self.lore_data.worlds:
                self.entity_combo.addItem(f"World: {world.name}", (entity_type, world.id.value))
        elif entity_type == "character":
            for character in self.lore_data.characters:
                world = self.lore_data.get_world_by_id(character.world_id)
                world_name = world.name if world else "Unknown"
                self.entity_combo.addItem(f"Character: {character.name} ({world_name})", (entity_type, character.id.value))
        elif entity_type == "event":
            for event in self.lore_data.events:
                world = self.lore_data.get_world_by_id(event.world_id)
                world_name = world.name if world else "Unknown"
                self.entity_combo.addItem(f"Event: {event.name} ({world_name})", (entity_type, event.id.value))
    
    def refresh(self):
        """Refresh the improvements table."""
        self.table.setRowCount(0)
        
        for improvement in self.lore_data.improvements:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Find entity name
            entity_name = self._get_entity_name(improvement.entity_type, improvement.entity_id)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(improvement.id.value)))
            self.table.setItem(row, 1, QTableWidgetItem(entity_name))
            self.table.setItem(row, 2, QTableWidgetItem(improvement.suggestion[:50] + "..."))
            self.table.setItem(row, 3, QTableWidgetItem(improvement.status.value))
            self.table.setItem(row, 4, QTableWidgetItem(improvement.created_at.value.strftime("%Y-%m-%d")))
        
        self.table.resizeColumnsToContents()
    
    def _get_entity_name(self, entity_type: EntityType, entity_id: EntityId) -> str:
        """Get display name for entity."""
        if entity_type.value == "world":
            world = self.lore_data.get_world_by_id(entity_id)
            return f"World: {world.name}" if world else "Unknown World"
        elif entity_type.value == "character":
            character = next((c for c in self.lore_data.characters if c.id == entity_id), None)
            return f"Character: {character.name}" if character else "Unknown Character"
        elif entity_type.value == "event":
            event = next((e for e in self.lore_data.events if e.id == entity_id), None)
            return f"Event: {event.name}" if event else "Unknown Event"
        return "Unknown"
    
    def _on_selection_changed(self):
        """Handle improvement selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            improvement_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_improvement = next((i for i in self.lore_data.improvements if i.id == improvement_id), None)
            
            if self.selected_improvement:
                # Update form
                entity_type_idx = self.entity_type_combo.findText(self.selected_improvement.entity_type.value)
                if entity_type_idx >= 0:
                    self.entity_type_combo.setCurrentIndex(entity_type_idx)
                    self._update_entity_combo()
                
                # Find entity in combo
                for i in range(self.entity_combo.count()):
                    entity_data = self.entity_combo.itemData(i)
                    if entity_data and entity_data[1] == self.selected_improvement.entity_id.value:
                        self.entity_combo.setCurrentIndex(i)
                        break
                
                self.suggestion_input.setPlainText(self.selected_improvement.suggestion)
                self.status_combo.setCurrentText(self.selected_improvement.status.value)
                
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
        else:
            self.selected_improvement = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def _add_improvement(self):
        """Add a new improvement."""
        try:
            entity_data = self.entity_combo.currentData()
            if not entity_data:
                QMessageBox.warning(self, "No Entity", "Please select an entity.")
                return
            
            entity_type, entity_id = entity_data
            
            improvement = Improvement.propose(
                tenant_id=self.lore_data.tenant_id,
                entity_type=EntityType(entity_type),
                entity_id=EntityId(entity_id),
                suggestion=self.suggestion_input.toPlainText(),
                git_commit_hash=__import__('src.domain.value_objects.common', fromlist=['GitCommitHash']).GitCommitHash("temp_commit_hash")
            )
            self.lore_data.add_improvement(improvement)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Improvement proposed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to propose improvement: {e}")
    
    def _update_improvement(self):
        """Update selected improvement."""
        if not self.selected_improvement:
            return
        
        try:
            new_status = __import__('src.domain.value_objects.common', fromlist=['ImprovementStatus']).ImprovementStatus(self.status_combo.currentText())
            
            # Apply status transition
            if new_status.value == "approved" and self.selected_improvement.status.value == "proposed":
                self.selected_improvement.approve()
            elif new_status.value == "applied" and self.selected_improvement.status.value == "approved":
                self.selected_improvement.apply()
            elif new_status.value == "rejected":
                self.selected_improvement.reject()
            
            self.refresh()
            QMessageBox.information(self, "Success", "Improvement updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update improvement: {e}")
    
    def _delete_improvement(self):
        """Delete selected improvement."""
        if not self.selected_improvement:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete this improvement?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.improvements.remove(self.selected_improvement)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Improvement deleted successfully!")
    
    def _clear_form(self):
        """Clear the form."""
        self.suggestion_input.clear()
        self.selected_improvement = None


