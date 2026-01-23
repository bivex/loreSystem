"""
ProgressionSimulatorTab - GUI tab for the lore-based progression simulator.
"""
from typing import Optional, List
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QTextEdit, QComboBox, QSpinBox, QFormLayout,
    QMessageBox, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.presentation.gui.lore_data import LoreData
from src.application.use_cases.progression_simulation import (
    create_sample_simulation,
    RunProgressionSimulationUseCase,
    ExportSimulationForVerificationUseCase,
    SimulationRequest,
)
from src.domain.value_objects.common import EntityId
from src.domain.value_objects.progression import StatType


class ProgressionSimulatorTab(QWidget):
    """GUI tab for the lore-based progression simulator with formal verification."""

    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self.simulator = create_sample_simulation()
        self.simulation_use_case = RunProgressionSimulationUseCase(self.simulator)
        self.export_use_case = ExportSimulationForVerificationUseCase(self.simulator)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the progression simulator user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Header
        header_label = QLabel("🎲 Lore-Based Progression Simulator")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #fff; margin-bottom: 10px;")
        layout.addWidget(header_label)

        subtitle_label = QLabel(
            "Simulate character progression with full observability and formal verification.\n"
            "All outcomes are derivable from immutable lore axioms."
        )
        subtitle_label.setStyleSheet("color: #ccc; font-size: 11px;")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)

        # Main content area - horizontal layout
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        layout.addWidget(content_widget)

        # Left panel - Current State
        left_panel = self._create_state_panel()
        content_layout.addWidget(left_panel)

        # Right panel - Simulation Controls & Logs
        right_panel = self._create_simulation_panel()
        content_layout.addWidget(right_panel)

        # Bottom panel - Export for Verification
        export_panel = self._create_export_panel()
        layout.addWidget(export_panel)

    def _create_state_panel(self) -> QWidget:
        """Create the current state display panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # State group
        state_group = QGroupBox("📊 Current Character State")
        state_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #666;
                border-radius: 5px;
                margin-top: 1ex;
                color: #fff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        state_layout = QVBoxLayout()
        state_group.setLayout(state_layout)

        # Character info
        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)
        self.state_display.setMaximumHeight(200)
        self.state_display.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 3px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        state_layout.addWidget(self.state_display)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh State")
        refresh_btn.clicked.connect(self._refresh_state_display)
        state_layout.addWidget(refresh_btn)

        layout.addWidget(state_group)

        # Lore axioms preview
        axioms_group = QGroupBox("📜 Active Lore Axioms")
        axioms_group.setStyleSheet(state_group.styleSheet())

        axioms_layout = QVBoxLayout()
        axioms_group.setLayout(axioms_layout)

        self.axioms_display = QTextEdit()
        self.axioms_display.setReadOnly(True)
        self.axioms_display.setMaximumHeight(150)
        self.axioms_display.setStyleSheet(self.state_display.styleSheet())
        axioms_layout.addWidget(self.axioms_display)

        layout.addWidget(axioms_group)

        # Initial refresh
        self._refresh_state_display()
        self._refresh_axioms_display()

        return panel

    def _create_simulation_panel(self) -> QWidget:
        """Create the simulation controls and logs panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Simulation controls
        controls_group = QGroupBox("🎮 Simulation Controls")
        controls_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #666;
                border-radius: 5px;
                margin-top: 1ex;
                color: #fff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        controls_layout = QFormLayout()
        controls_group.setLayout(controls_layout)

        # Character selection (for now, just the sample character)
        self.char_combo = QComboBox()
        self.char_combo.addItem("Sample Warrior (ID: 1)", 1)
        controls_layout.addRow("👤 Character:", self.char_combo)

        # Action selection
        self.action_combo = QComboBox()
        self.action_combo.addItem("Level Up", "level_up")
        self.action_combo.addItem("Gain Experience", "gain_xp")
        self.action_combo.addItem("Increase Strength", "increase_stat")
        self.action_combo.addItem("Increase Intellect", "increase_stat")
        self.action_combo.addItem("Increase Agility", "increase_stat")
        self.action_combo.currentTextChanged.connect(self._on_action_changed)
        controls_layout.addRow("⚡ Action:", self.action_combo)

        # Action parameters
        param_widget = QWidget()
        param_layout = QHBoxLayout(param_widget)
        param_layout.setContentsMargins(0, 0, 0, 0)

        self.xp_amount = QSpinBox()
        self.xp_amount.setRange(1, 10000)
        self.xp_amount.setValue(100)
        self.xp_amount.setPrefix("XP: ")
        param_layout.addWidget(self.xp_amount)

        self.xp_source = QComboBox()
        self.xp_source.addItem("defeating_goblin", "defeating_goblin")
        self.xp_source.addItem("completing_quest", "completing_quest")
        self.xp_source.addItem("training", "training")
        param_layout.addWidget(self.xp_source)

        self.stat_increase = QSpinBox()
        self.stat_increase.setRange(1, 10)
        self.stat_increase.setValue(1)
        self.stat_increase.setPrefix("Increase: ")
        self.stat_increase.hide()
        param_layout.addWidget(self.stat_increase)

        controls_layout.addRow("📊 Parameters:", param_widget)

        # Execute button
        execute_btn = QPushButton("▶️ Execute Simulation")
        execute_btn.setStyleSheet("""
            QPushButton {
                background: #4a4a4a;
                color: #fff;
                border: 2px solid #666;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5a5a5a;
            }
            QPushButton:pressed {
                background: #3a3a3a;
            }
        """)
        execute_btn.clicked.connect(self._execute_simulation)
        controls_layout.addRow("", execute_btn)

        layout.addWidget(controls_group)

        # Observation logs
        logs_group = QGroupBox("📋 Observation Log")
        logs_group.setStyleSheet(controls_group.styleSheet())

        logs_layout = QVBoxLayout()
        logs_group.setLayout(logs_layout)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 3px;
                font-family: monospace;
                font-size: 9px;
            }
        """)
        logs_layout.addWidget(self.log_display)

        # Clear log button
        clear_btn = QPushButton("🗑️ Clear Log")
        clear_btn.clicked.connect(self.log_display.clear)
        logs_layout.addWidget(clear_btn)

        layout.addWidget(logs_group)

        return panel

    def _create_export_panel(self) -> QWidget:
        """Create the export panel for formal verification."""
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)

        export_group = QGroupBox("🔍 Formal Verification Export")
        export_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #666;
                border-radius: 5px;
                margin-top: 1ex;
                color: #fff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        export_layout = QVBoxLayout()
        export_group.setLayout(export_layout)

        export_desc = QLabel(
            "Export simulation data to First-Order Logic files for formal verification with Prover9/Mace4.\n"
            "This proves lore consistency and detects unintended progression paths."
        )
        export_desc.setStyleSheet("color: #ccc; font-size: 10px;")
        export_desc.setWordWrap(True)
        export_layout.addWidget(export_desc)

        export_btn = QPushButton("📤 Export for Verification")
        export_btn.setStyleSheet("""
            QPushButton {
                background: #2a4a2a;
                color: #fff;
                border: 2px solid #4a6a4a;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3a5a3a;
            }
        """)
        export_btn.clicked.connect(self._export_for_verification)
        export_layout.addWidget(export_btn)

        self.export_status = QLabel("")
        self.export_status.setStyleSheet("color: #aaa; font-size: 9px;")
        export_layout.addWidget(self.export_status)

        layout.addWidget(export_group)
        layout.addStretch()

        return panel

    def _refresh_state_display(self):
        """Refresh the current state display."""
        try:
            char_id = EntityId(1)  # Sample character
            state = self.simulator.current_state.get_character_state(char_id)

            if state:
                state_text = f"""Character ID: {char_id.value}
Time Point: {state.time_point}
Level: {state.level.value if state.level else 'N/A'}
Class: {state.character_class.value if state.character_class else 'N/A'}
Experience: {state.experience.value if state.experience else 0}

Stats:
"""
                for stat_type, stat_value in state.stats.items():
                    state_text += f"  {stat_type.value}: {stat_value.value}\n"

                self.state_display.setPlainText(state_text.strip())
            else:
                self.state_display.setPlainText("No character state available")
        except Exception as e:
            self.state_display.setPlainText(f"Error refreshing state: {e}")

    def _refresh_axioms_display(self):
        """Refresh the lore axioms display."""
        try:
            axioms_text = "Active Lore Axioms:\n\n"
            for axiom in self.simulator.lore_axioms.axioms:
                axioms_text += f"• {axiom.predicate}\n"
                axioms_text += f"  {axiom.description}\n\n"

            self.axioms_display.setPlainText(axioms_text.strip())
        except Exception as e:
            self.axioms_display.setPlainText(f"Error loading axioms: {e}")

    def _on_action_changed(self, action_text: str):
        """Handle action selection change."""
        # Show/hide parameter controls based on action
        if "Experience" in action_text:
            self.xp_amount.show()
            self.xp_source.show()
            self.stat_increase.hide()
        elif "Increase" in action_text:
            self.xp_amount.hide()
            self.xp_source.hide()
            self.stat_increase.show()
        else:  # Level up
            self.xp_amount.hide()
            self.xp_source.hide()
            self.stat_increase.hide()

    def _execute_simulation(self):
        """Execute the selected simulation action."""
        try:
            char_id = EntityId(self.char_combo.currentData())
            action_type = self.action_combo.currentData()

            parameters = {}

            if action_type == "gain_xp":
                parameters["amount"] = self.xp_amount.value()
                parameters["source"] = self.xp_source.currentData()
            elif action_type == "increase_stat":
                stat_name = self.action_combo.currentText().split()[-1].lower()
                parameters["stat_type"] = stat_name
                parameters["amount"] = self.stat_increase.value()
                parameters["reason"] = f"{stat_name}_training"

            request = SimulationRequest(
                character_id=char_id,
                action_type=action_type,
                parameters=parameters
            )

            response = self.simulation_use_case.execute(request)

            if response.success and response.result:
                # Add to log
                current_log = self.log_display.toPlainText()
                new_log = response.result.observations[0]
                if current_log:
                    new_log = current_log + "\n\n" + "="*50 + "\n\n" + new_log
                self.log_display.setPlainText(new_log)

                # Refresh state display
                self._refresh_state_display()

                QMessageBox.information(
                    self, "Simulation Success",
                    f"✅ {self.action_combo.currentText()} completed successfully!\n\n"
                    "Check the observation log for full details."
                )
            else:
                QMessageBox.warning(
                    self, "Simulation Failed",
                    f"❌ {self.action_combo.currentText()} failed:\n\n{response.error_message}"
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Simulation Error",
                f"An error occurred during simulation:\n\n{str(e)}"
            )

    def _export_for_verification(self):
        """Export simulation data for formal verification."""
        try:
            from pathlib import Path
            output_dir = Path("simulation_verification_output")

            result = self.export_use_case.execute(output_dir)

            if result["success"]:
                files_info = "\n".join([f"• {name}: {path}" for name, path in result["files"].items()])
                self.export_status.setText(
                    f"✅ Exported to: {output_dir}\n"
                    f"Files created:\n{files_info}\n\n"
                    "Ready for Prover9/Mace4 verification!"
                )
                self.export_status.setStyleSheet("color: #4a4a; font-size: 9px;")

                QMessageBox.information(
                    self, "Export Successful",
                    f"✅ Simulation data exported for formal verification!\n\n"
                    f"Output directory: {output_dir}\n\n"
                    "Use Prover9 to verify invariants:\n"
                    "prover9 axioms.in invariants.in\n\n"
                    "Use Mace4 to find counterexamples:\n"
                    "mace4 -f state.in axioms.in"
                )
            else:
                self.export_status.setText(f"❌ Export failed: {result['error']}")
                self.export_status.setStyleSheet("color: #a44; font-size: 9px;")
                QMessageBox.warning(self, "Export Failed", f"❌ {result['error']}")

        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            self.export_status.setText(error_msg)
            self.export_status.setStyleSheet("color: #a44; font-size: 9px;")
            QMessageBox.critical(self, "Export Error", error_msg)

    def refresh(self):
        """Refresh the progression simulator tab."""
        # The simulator maintains its own state, so just ensure UI is up to date
        # This could be extended to refresh from lore_data if needed
        pass
