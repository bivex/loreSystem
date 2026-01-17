"""
FlowchartTab - Tab for managing story flowcharts
"""
from typing import Optional
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.flowchart import Flowchart
from src.domain.value_objects.common import TenantId, EntityId


class FlowchartTab(QWidget):
    """Tab for managing story flowcharts."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_flowchart: Optional[Flowchart] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📊 Flowcharts")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Flowcharts table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Nodes", "Connections", "Active", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Flowchart Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Story selection (optional)
        self.story_combo = QComboBox()
        self.story_combo.addItem("None", None)
        form_layout.addRow("Story (optional):", self.story_combo)

        # Flowchart name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter flowchart name...")
        form_layout.addRow("Name:", self.name_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Flowchart description...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        # Nodes (JSON array)
        self.nodes_input = QTextEdit()
        self.nodes_input.setPlaceholderText('[{"id": 1, "label": "Start", "x": 0, "y": 0}]')
        self.nodes_input.setMaximumHeight(100)
        form_layout.addRow("Nodes (JSON):", self.nodes_input)

        # Connections (JSON array)
        self.connections_input = QTextEdit()
        self.connections_input.setPlaceholderText('[{"from": 1, "to": 2, "label": "next"}]')
        self.connections_input.setMaximumHeight(80)
        form_layout.addRow("Connections (JSON):", self.connections_input)

        # Active checkbox
        self.active_check = QCheckBox("This flowchart is currently displayed")
        form_layout.addRow("", self.active_check)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Flowchart")
        self.add_btn.clicked.connect(self._add_flowchart)

        self.update_btn = QPushButton("Update Flowchart")
        self.update_btn.clicked.connect(self._update_flowchart)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Flowchart")
        self.delete_btn.clicked.connect(self._delete_flowchart)
        self.delete_btn.setEnabled(False)

        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self._clear_form)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the flowcharts table and combo boxes."""
        # Update worlds combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"{world.name.value}", world.id.value)

        # Update stories combo
        self.story_combo.clear()
        self.story_combo.addItem("None", None)
        for story in self.lore_data.stories:
            self.story_combo.addItem(f"{story.name.value}", story.id.value if story.id else None)

        # Update flowcharts table
        self.table.setRowCount(0)
        for flowchart in self.lore_data.flowcharts:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(flowchart.id.value) if flowchart.id else ""))

            # World
            world_name = "Unknown"
            for world in self.lore_data.worlds:
                if world.id == flowchart.world_id:
                    world_name = world.name.value
                    break
            self.table.setItem(row, 1, QTableWidgetItem(world_name))

            # Name
            self.table.setItem(row, 2, QTableWidgetItem(flowchart.name))

            # Nodes count
            self.table.setItem(row, 3, QTableWidgetItem(str(len(flowchart.nodes))))

            # Connections count
            self.table.setItem(row, 4, QTableWidgetItem(str(len(flowchart.connections))))

            # Active
            self.table.setItem(row, 5, QTableWidgetItem("✅" if flowchart.is_active else ""))

            # Updated
            self.table.setItem(row, 6, QTableWidgetItem(flowchart.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle flowchart selection changes."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            flowchart_id = int(self.table.item(row, 0).text())
            self.selected_flowchart = next((f for f in self.lore_data.flowcharts if f.id and f.id.value == flowchart_id), None)
            if self.selected_flowchart:
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
            else:
                self._clear_form()
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.selected_flowchart = None
            self._clear_form()
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected flowchart data."""
        if not self.selected_flowchart:
            return

        # Set world
        for i in range(self.world_combo.count()):
            if self.world_combo.itemData(i) == self.selected_flowchart.world_id.value:
                self.world_combo.setCurrentIndex(i)
                break

        # Set story
        story_index = 0
        if self.selected_flowchart.story_id:
            for i in range(1, self.story_combo.count()):
                if self.story_combo.itemData(i) == self.selected_flowchart.story_id.value:
                    story_index = i
                    break
        self.story_combo.setCurrentIndex(story_index)

        # Set fields
        self.name_input.setText(self.selected_flowchart.name)
        self.description_input.setText(self.selected_flowchart.description or "")
        self.nodes_input.setText(json.dumps(self.selected_flowchart.nodes, indent=2))
        self.connections_input.setText(json.dumps(self.selected_flowchart.connections, indent=2))
        self.active_check.setChecked(self.selected_flowchart.is_active)

    def _clear_form(self):
        """Clear all form fields."""
        self.name_input.clear()
        self.description_input.clear()
        self.nodes_input.clear()
        self.connections_input.clear()
        self.active_check.setChecked(False)
        if self.world_combo.count() > 0:
            self.world_combo.setCurrentIndex(0)
        if self.story_combo.count() > 0:
            self.story_combo.setCurrentIndex(0)

    def _add_flowchart(self):
        """Add a new flowchart."""
        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Flowchart name cannot be empty.")
                return

            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Parse JSON fields
            try:
                nodes = json.loads(self.nodes_input.toPlainText().strip())
                if not isinstance(nodes, list) or len(nodes) == 0:
                    raise ValueError("Nodes must be a non-empty list")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Nodes JSON: {str(e)}")
                return

            try:
                connections = json.loads(self.connections_input.toPlainText().strip()) if self.connections_input.toPlainText().strip() else []
                if not isinstance(connections, list):
                    raise ValueError("Connections must be a list")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Connections JSON: {str(e)}")
                return

            # Get story ID
            story_id = None
            if self.story_combo.currentData() is not None:
                story_id = EntityId(self.story_combo.currentData())

            # Create flowchart
            flowchart = Flowchart.create(
                tenant_id=TenantId(1),
                world_id=EntityId(self.world_combo.currentData()),
                name=self.name_input.text().strip(),
                nodes=nodes,
                description=self.description_input.toPlainText().strip() or None,
                story_id=story_id,
                connections=connections,
                is_active=self.active_check.isChecked()
            )

            self.lore_data.add_flowchart(flowchart)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Flowchart added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add flowchart: {str(e)}")

    def _update_flowchart(self):
        """Update the selected flowchart."""
        if not self.selected_flowchart:
            return

        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Flowchart name cannot be empty.")
                return

            # Parse JSON fields
            try:
                nodes = json.loads(self.nodes_input.toPlainText().strip())
                if not isinstance(nodes, list) or len(nodes) == 0:
                    raise ValueError("Nodes must be a non-empty list")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Nodes JSON: {str(e)}")
                return

            try:
                connections = json.loads(self.connections_input.toPlainText().strip()) if self.connections_input.toPlainText().strip() else []
                if not isinstance(connections, list):
                    raise ValueError("Connections must be a list")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Connections JSON: {str(e)}")
                return

            # Get story ID
            story_id = None
            if self.story_combo.currentData() is not None:
                story_id = EntityId(self.story_combo.currentData())

            # Update flowchart
            object.__setattr__(self.selected_flowchart, 'name', self.name_input.text().strip())
            object.__setattr__(self.selected_flowchart, 'description', self.description_input.toPlainText().strip() or None)
            object.__setattr__(self.selected_flowchart, 'story_id', story_id)
            object.__setattr__(self.selected_flowchart, 'nodes', nodes)
            object.__setattr__(self.selected_flowchart, 'connections', connections)

            # Update active status
            if self.active_check.isChecked() and not self.selected_flowchart.is_active:
                self.selected_flowchart.activate()
            elif not self.active_check.isChecked() and self.selected_flowchart.is_active:
                self.selected_flowchart.deactivate()

            # Update metadata
            object.__setattr__(self.selected_flowchart, 'updated_at', self.selected_flowchart.updated_at.__class__.now())
            object.__setattr__(self.selected_flowchart, 'version', self.selected_flowchart.version.increment())

            self.refresh()
            QMessageBox.information(self, "Success", "Flowchart updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update flowchart: {str(e)}")

    def _delete_flowchart(self):
        """Delete the selected flowchart."""
        if not self.selected_flowchart:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the flowchart '{self.selected_flowchart.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.flowcharts.remove(self.selected_flowchart)
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Flowchart deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete flowchart: {str(e)}")
