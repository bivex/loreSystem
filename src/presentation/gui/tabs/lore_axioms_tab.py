"""
LoreAxiomsTab - Tab for managing lore axioms.
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QMessageBox, QComboBox, QSpinBox, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.lore_axioms import LoreAxioms, LoreAxiom, AxiomType
from src.domain.value_objects.common import TenantId, EntityId, Description


class LoreAxiomsTab(QWidget):
    """Tab for managing lore axioms."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Lore Axioms")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and details
        splitter = QSplitter()
        layout.addWidget(splitter)

        # Left side - Axioms table
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # Axioms table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Type", "Predicate", "Description", "Parameters"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Axiom")
        self.add_btn.clicked.connect(self._add_axiom)

        self.update_btn = QPushButton("Update Axiom")
        self.update_btn.clicked.connect(self._update_axiom)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Axiom")
        self.delete_btn.clicked.connect(self._delete_axiom)
        self.delete_btn.setEnabled(False)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        left_layout.addLayout(button_layout)

        # Right side - Axiom details form
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Form
        form_group = QGroupBox("Axiom Details")
        form_layout = QFormLayout()

        self.type_combo = QComboBox()
        self.type_combo.addItems([t.value for t in AxiomType])

        self.predicate_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)

        # Parameters as key-value pairs (simplified)
        self.parameters_input = QTextEdit()
        self.parameters_input.setMaximumHeight(100)
        self.parameters_input.setPlaceholderText("key1=value1\nkey2=value2")

        form_layout.addRow("Type:", self.type_combo)
        form_layout.addRow("Predicate:", self.predicate_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Parameters:", self.parameters_input)

        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)

        # Derived data display
        derived_group = QGroupBox("Derived Data")
        derived_layout = QVBoxLayout()

        self.derived_tree = QTreeWidget()
        self.derived_tree.setHeaderLabel("World Rules")
        derived_layout.addWidget(self.derived_tree)

        derived_group.setLayout(derived_layout)
        right_layout.addWidget(derived_group)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])

        self.setLayout(layout)

        self.selected_world_id: Optional[EntityId] = None
        self.selected_axiom: Optional[LoreAxiom] = None

    def refresh(self):
        """Refresh the axioms table."""
        self.table.setRowCount(0)

        # Get current world
        if hasattr(self.lore_data, 'current_world_id') and self.lore_data.current_world_id:
            world_id = self.lore_data.current_world_id
            lore_axioms = self.lore_data.get_lore_axioms_by_world_id(world_id)
            if lore_axioms:
                for axiom in lore_axioms.axioms:
                    row = self.table.rowCount()
                    self.table.insertRow(row)

                    self.table.setItem(row, 0, QTableWidgetItem(axiom.axiom_type.value))
                    self.table.setItem(row, 1, QTableWidgetItem(axiom.predicate))
                    self.table.setItem(row, 2, QTableWidgetItem(axiom.description[:50] + "..." if len(axiom.description) > 50 else axiom.description))
                    self.table.setItem(row, 3, QTableWidgetItem(str(axiom.parameters)))

                self._update_derived_data(lore_axioms)

        self.table.resizeColumnsToContents()

    def _update_derived_data(self, lore_axioms: LoreAxioms):
        """Update the derived data tree."""
        self.derived_tree.clear()

        # Classes
        if lore_axioms.classes:
            classes_item = QTreeWidgetItem(["Character Classes"])
            for cls in sorted(lore_axioms.classes):
                QTreeWidgetItem(classes_item, [str(cls)])
            self.derived_tree.addTopLevelItem(classes_item)

        # Stats
        if lore_axioms.stats:
            stats_item = QTreeWidgetItem(["Stats"])
            for stat in sorted(lore_axioms.stats):
                QTreeWidgetItem(stats_item, [str(stat)])
            self.derived_tree.addTopLevelItem(stats_item)

        # Max stat bounds
        if lore_axioms.max_stat_bounds:
            bounds_item = QTreeWidgetItem(["Max Stat Bounds"])
            for stat, max_val in lore_axioms.max_stat_bounds.items():
                QTreeWidgetItem(bounds_item, [f"{stat}: {max_val}"])
            self.derived_tree.addTopLevelItem(bounds_item)

        # Required experience
        if lore_axioms.required_experience:
            exp_item = QTreeWidgetItem(["Level Requirements"])
            for level, exp in sorted(lore_axioms.required_experience.items()):
                QTreeWidgetItem(exp_item, [f"Level {level}: {exp} XP"])
            self.derived_tree.addTopLevelItem(exp_item)

        self.derived_tree.expandAll()

    def _on_selection_changed(self):
        """Handle axiom selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            # Get axiom from current lore axioms
            if hasattr(self.lore_data, 'current_world_id') and self.lore_data.current_world_id:
                lore_axioms = self.lore_data.get_lore_axioms_by_world_id(self.lore_data.current_world_id)
                if lore_axioms and row < len(lore_axioms.axioms):
                    self.selected_axiom = lore_axioms.axioms[row]

                    if self.selected_axiom:
                        self.type_combo.setCurrentText(self.selected_axiom.axiom_type.value)
                        self.predicate_input.setText(self.selected_axiom.predicate)
                        self.description_input.setPlainText(self.selected_axiom.description)
                        # Convert parameters dict to text
                        params_text = "\n".join([f"{k}={v}" for k, v in self.selected_axiom.parameters.items()])
                        self.parameters_input.setPlainText(params_text)

                        self.update_btn.setEnabled(True)
                        self.delete_btn.setEnabled(True)
        else:
            self.selected_axiom = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _add_axiom(self):
        """Add a new axiom."""
        try:
            # Parse parameters
            params = {}
            for line in self.parameters_input.toPlainText().strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    params[key.strip()] = value.strip()

            axiom = LoreAxiom(
                axiom_type=AxiomType(self.type_combo.currentText()),
                predicate=self.predicate_input.text(),
                parameters=params,
                description=self.description_input.toPlainText()
            )

            # Add to current world's lore axioms
            if hasattr(self.lore_data, 'current_world_id') and self.lore_data.current_world_id:
                lore_axioms = self.lore_data.get_lore_axioms_by_world_id(self.lore_data.current_world_id)
                if lore_axioms:
                    lore_axioms.axioms.append(axiom)
                    # Re-derive data
                    lore_axioms._derive_data()
                else:
                    # Create new lore axioms for this world
                    lore_axioms = LoreAxioms.create_default(
                        tenant_id=self.lore_data.tenant_id,
                        world_id=self.lore_data.current_world_id
                    )
                    lore_axioms.axioms.append(axiom)
                    self.lore_data.add_lore_axioms(lore_axioms)

                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Axiom added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add axiom: {e}")

    def _update_axiom(self):
        """Update selected axiom."""
        if not self.selected_axiom:
            return

        try:
            # Parse parameters
            params = {}
            for line in self.parameters_input.toPlainText().strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    params[key.strip()] = value.strip()

            self.selected_axiom.axiom_type = AxiomType(self.type_combo.currentText())
            self.selected_axiom.predicate = self.predicate_input.text()
            self.selected_axiom.parameters = params
            self.selected_axiom.description = self.description_input.toPlainText()

            # Re-derive data for the world
            if hasattr(self.lore_data, 'current_world_id') and self.lore_data.current_world_id:
                lore_axioms = self.lore_data.get_lore_axioms_by_world_id(self.lore_data.current_world_id)
                if lore_axioms:
                    lore_axioms._derive_data()

            self.refresh()
            QMessageBox.information(self, "Success", "Axiom updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update axiom: {e}")

    def _delete_axiom(self):
        """Delete selected axiom."""
        if not self.selected_axiom:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete this axiom?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.lore_data, 'current_world_id') and self.lore_data.current_world_id:
                lore_axioms = self.lore_data.get_lore_axioms_by_world_id(self.lore_data.current_world_id)
                if lore_axioms:
                    lore_axioms.axioms.remove(self.selected_axiom)
                    lore_axioms._derive_data()

            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Axiom deleted successfully!")

    def _clear_form(self):
        """Clear the form."""
        self.type_combo.setCurrentIndex(0)
        self.predicate_input.clear()
        self.description_input.clear()
        self.parameters_input.clear()
        self.selected_axiom = None