"""
WorldsTab - Tab for managing worlds.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.world import World
from src.domain.value_objects.common import TenantId, EntityId, WorldName, Description


class WorldsTab(QWidget):
    """Tab for managing worlds."""
    
    world_selected = pyqtSignal(EntityId)
    
    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Worlds")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Worlds table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Version"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Form
        form_group = QGroupBox("World Details")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add World")
        self.add_btn.clicked.connect(self._add_world)
        
        self.update_btn = QPushButton("Update World")
        self.update_btn.clicked.connect(self._update_world)
        self.update_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete World")
        self.delete_btn.clicked.connect(self._delete_world)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.selected_world: Optional[World] = None
    
    def refresh(self):
        """Refresh the worlds table."""
        self.table.setRowCount(0)
        
        for world in self.lore_data.worlds:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(world.id.value)))
            self.table.setItem(row, 1, QTableWidgetItem(str(world.name)))
            self.table.setItem(row, 2, QTableWidgetItem(str(world.description)[:50] + "..."))
            self.table.setItem(row, 3, QTableWidgetItem(str(world.version)))
        
        self.table.resizeColumnsToContents()
    
    def _on_selection_changed(self):
        """Handle world selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            world_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_world = self.lore_data.get_world_by_id(world_id)
            
            if self.selected_world:
                self.name_input.setText(str(self.selected_world.name))
                self.description_input.setPlainText(str(self.selected_world.description))
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.world_selected.emit(world_id)
        else:
            self.selected_world = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def _add_world(self):
        """Add a new world."""
        try:
            world = World.create(
                tenant_id=self.lore_data.tenant_id,
                name=WorldName(self.name_input.text()),
                description=Description(self.description_input.toPlainText())
            )
            self.lore_data.add_world(world)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "World created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create world: {e}")
    
    def _update_world(self):
        """Update selected world."""
        if not self.selected_world:
            return
        
        try:
            self.selected_world.rename(WorldName(self.name_input.text()))
            self.selected_world.update_description(Description(self.description_input.toPlainText()))
            self.refresh()
            QMessageBox.information(self, "Success", "World updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update world: {e}")
    
    def _delete_world(self):
        """Delete selected world."""
        if not self.selected_world:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_world.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.worlds.remove(self.selected_world)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "World deleted successfully!")
    
    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.description_input.clear()
        self.selected_world = None