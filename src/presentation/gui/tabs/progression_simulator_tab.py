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
    create_dark_fantasy_simulation,
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
        self.simulator = create_dark_fantasy_simulation()
        self.simulation_use_case = RunProgressionSimulationUseCase(self.simulator)
        self.export_use_case = ExportSimulationForVerificationUseCase(self.simulator)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the progression simulator user interface with clear lore development view."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Header with clear purpose
        header_label = QLabel("🎲 Lore Development Simulator")
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #fff; margin-bottom: 5px;")
        layout.addWidget(header_label)

        subtitle_label = QLabel(
            "🔍 See exactly how your lore rules affect character progression. Every change is traceable to specific axioms."
        )
        subtitle_label.setStyleSheet("color: #ccc; font-size: 12px;")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)

        # Main development area - organized in clear sections
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)

        # Left side - Character State & Progression
        left_widget = self._create_character_development_panel()
        main_splitter.addWidget(left_widget)

        # Right side - Lore Rules & Simulation
        right_widget = self._create_lore_rules_panel()
        main_splitter.addWidget(right_widget)

        # Set splitter proportions
        main_splitter.setSizes([600, 600])

        # Bottom panel - Verification & Export
        export_panel = self._create_verification_panel()
        layout.addWidget(export_panel)

        # Initial refresh after all components are created
        self._refresh_all_displays()

    def _create_character_development_panel(self) -> QWidget:
        """Create the character development panel with clear progression visualization."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        panel.setLayout(layout)

        # Character Selection
        char_group = QGroupBox("👤 Character Selection")
        char_group.setStyleSheet(self._get_group_style())
        char_layout = QVBoxLayout()
        char_group.setLayout(char_layout)

        self.char_combo = QComboBox()
        for char_id, char_state in self.simulator.current_state.character_states.items():
            char_name = f"Character {char_id.value}"
            for character in self.lore_data.characters:
                if character.id == char_id:
                    char_name = str(character.name)
                    break
            self.char_combo.addItem(f"{char_name} (ID: {char_id.value})", char_id.value)

        if self.char_combo.count() == 0:
            self.char_combo.addItem("Sample Warrior (ID: 1)", 1)

        self.char_combo.currentIndexChanged.connect(self._refresh_all_displays)
        char_layout.addWidget(self.char_combo)

        layout.addWidget(char_group)

        # Current State Display
        state_group = QGroupBox("📊 Current State")
        state_group.setStyleSheet(self._get_group_style())
        state_layout = QVBoxLayout()
        state_group.setLayout(state_layout)

        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)
        self.state_display.setMaximumHeight(150)
        self.state_display.setStyleSheet(self._get_text_display_style())
        state_layout.addWidget(self.state_display)

        layout.addWidget(state_group)

        # Visual Stats Display
        stats_group = QGroupBox("⚔️ Stats Overview")
        stats_group.setStyleSheet(self._get_group_style())
        stats_layout = QVBoxLayout()
        stats_group.setLayout(stats_layout)

        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(120)
        self.stats_display.setStyleSheet(self._get_text_display_style())
        stats_layout.addWidget(self.stats_display)

        layout.addWidget(stats_group)

        # Progression Timeline
        timeline_group = QGroupBox("📈 Progression Timeline")
        timeline_group.setStyleSheet(self._get_group_style())
        timeline_layout = QVBoxLayout()
        timeline_group.setLayout(timeline_layout)

        self.timeline_display = QTextEdit()
        self.timeline_display.setReadOnly(True)
        self.timeline_display.setStyleSheet(self._get_text_display_style())
        timeline_layout.addWidget(self.timeline_display)

        layout.addWidget(timeline_group)

        return panel

    def _create_lore_rules_panel(self) -> QWidget:
        """Create the lore rules and simulation panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        panel.setLayout(layout)

        # Lore Axioms Display
        axioms_group = QGroupBox("📜 Lore Axioms (Rules)")
        axioms_group.setStyleSheet(self._get_group_style())
        axioms_layout = QVBoxLayout()
        axioms_group.setLayout(axioms_layout)

        axioms_intro = QLabel("These immutable rules govern all progression:")
        axioms_intro.setStyleSheet("color: #ccc; font-size: 11px; margin-bottom: 5px;")
        axioms_layout.addWidget(axioms_intro)

        self.axioms_display = QTextEdit()
        self.axioms_display.setReadOnly(True)
        self.axioms_display.setMaximumHeight(200)
        self.axioms_display.setStyleSheet(self._get_text_display_style())
        axioms_layout.addWidget(self.axioms_display)

        layout.addWidget(axioms_group)

        # Simulation Controls
        controls_group = QGroupBox("🎮 Simulation Controls")
        controls_group.setStyleSheet(self._get_group_style())
        controls_layout = QFormLayout()
        controls_group.setLayout(controls_layout)

        # Action selection
        self.action_combo = QComboBox()
        self.action_combo.addItem("⚔️ Level Up", "level_up")
        self.action_combo.addItem("💰 Gain Experience", "gain_xp")
        self.action_combo.addItem("⬆️ Increase Strength", "increase_stat")
        self.action_combo.addItem("🧠 Increase Intellect", "increase_stat")
        self.action_combo.addItem("🏃 Increase Agility", "increase_stat")
        self.action_combo.currentTextChanged.connect(self._on_action_changed)
        controls_layout.addRow("🎯 Action:", self.action_combo)

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
        execute_btn = QPushButton("▶️ Execute Action")
        execute_btn.setStyleSheet(self._get_button_style())
        execute_btn.clicked.connect(self._execute_simulation)
        controls_layout.addRow("", execute_btn)

        layout.addWidget(controls_group)

        # Simulation Log
        log_group = QGroupBox("📋 Simulation Log")
        log_group.setStyleSheet(self._get_group_style())
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet(self._get_text_display_style())
        log_layout.addWidget(self.log_display)

        clear_btn = QPushButton("🗑️ Clear Log")
        clear_btn.clicked.connect(self.log_display.clear)
        log_layout.addWidget(clear_btn)

        layout.addWidget(log_group)

        return panel

    def _create_verification_panel(self) -> QWidget:
        """Create the verification panel for formal verification."""
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)

        verification_group = QGroupBox("🔍 Formal Verification")
        verification_group.setStyleSheet(self._get_group_style())
        verification_layout = QVBoxLayout()
        verification_group.setLayout(verification_layout)

        verification_desc = QLabel(
            "Export simulation data to First-Order Logic files for formal verification.\n"
            "This proves lore consistency and detects unintended progression paths."
        )
        verification_desc.setStyleSheet("color: #ccc; font-size: 10px;")
        verification_desc.setWordWrap(True)
        verification_layout.addWidget(verification_desc)

        export_btn = QPushButton("📤 Export for Verification")
        export_btn.setStyleSheet(self._get_button_style())
        export_btn.clicked.connect(self._export_for_verification)
        verification_layout.addWidget(export_btn)

        self.export_status = QLabel("")
        self.export_status.setStyleSheet("color: #aaa; font-size: 9px;")
        verification_layout.addWidget(self.export_status)

        layout.addWidget(verification_group)
        layout.addStretch()

        return panel

    def _refresh_all_displays(self):
        """Refresh all displays in the progression simulator."""
        self._refresh_state_display()
        self._refresh_stats_display()
        self._refresh_timeline_display()
        self._refresh_axioms_display()

    def _refresh_state_display(self):
        """Refresh the current state display."""
        try:
            # Get currently selected character
            selected_char_id = self.char_combo.currentData()
            if selected_char_id is None:
                self.state_display.setPlainText("No character selected")
                return

            char_id = EntityId(selected_char_id)
            state = self.simulator.current_state.get_character_state(char_id)

            if state:
                # Get character name
                char_name = f"Character {char_id.value}"
                for character in self.lore_data.characters:
                    if character.id == char_id:
                        char_name = str(character.name)
                        break

                state_text = f"""Character: {char_name}
ID: {char_id.value}
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

    def _refresh_stats_display(self):
        """Refresh the visual stats display."""
        try:
            selected_char_id = self.char_combo.currentData()
            if selected_char_id is None:
                self.stats_display.setPlainText("No character selected")
                return

            char_id = EntityId(selected_char_id)
            state = self.simulator.current_state.get_character_state(char_id)

            if state:
                stats_text = "📊 STAT BREAKDOWN:\n\n"
                for stat_type, stat_value in state.stats.items():
                    stats_text += f"⚔️ {stat_type.value}: {stat_value.value}\n"

                # Add derived stats if available
                if hasattr(state, 'derived_stats') and state.derived_stats:
                    stats_text += "\n🔮 DERIVED STATS:\n"
                    for stat_type, stat_value in state.derived_stats.items():
                        stats_text += f"✨ {stat_type.value}: {stat_value.value}\n"

                self.stats_display.setPlainText(stats_text.strip())
            else:
                self.stats_display.setPlainText("No stats available")
        except Exception as e:
            self.stats_display.setPlainText(f"Error refreshing stats: {e}")

    def _refresh_timeline_display(self):
        """Refresh the progression timeline display."""
        try:
            selected_char_id = self.char_combo.currentData()
            if selected_char_id is None:
                self.timeline_display.setPlainText("No character selected")
                return

            char_id = EntityId(selected_char_id)
            timeline_text = f"📈 PROGRESSION TIMELINE for Character {char_id.value}\n\n"

            # Show current state as starting point
            state = self.simulator.current_state.get_character_state(char_id)
            if state:
                timeline_text += f"🔸 T={state.time_point}: Initial state\n"
                timeline_text += f"   Level {state.level.value if state.level else 'N/A'}, "
                timeline_text += f"XP: {state.experience.value if state.experience else 0}\n\n"

            timeline_text += "💡 TIP: Execute actions above to see progression steps!\n"
            timeline_text += "Each action will be logged here with its effects."

            self.timeline_display.setPlainText(timeline_text)
        except Exception as e:
            self.timeline_display.setPlainText(f"Error refreshing timeline: {e}")

    def _refresh_axioms_display(self):
        """Refresh the lore axioms display with clear explanations."""
        try:
            axioms_text = "📜 LORE AXIOMS (Immutable Rules)\n"
            axioms_text += "=" * 50 + "\n\n"

            if not self.simulator.lore_axioms.axioms:
                axioms_text += "No axioms loaded. This simulation may not be properly configured.\n"
            else:
                axioms_text += f"Found {len(self.simulator.lore_axioms.axioms)} active rules:\n\n"

                for i, axiom in enumerate(self.simulator.lore_axioms.axioms, 1):
                    axioms_text += f"🔸 Rule {i}: {axiom.predicate}\n"
                    axioms_text += f"   📝 {axiom.description}\n\n"

            axioms_text += "💡 These rules govern ALL progression mechanics.\n"
            axioms_text += "   Every stat change must be derivable from these axioms!"

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

                # Update timeline with the action
                self._update_timeline_with_action(char_id, action_type, parameters, response.result)

                # Refresh all displays
                self._refresh_all_displays()

                QMessageBox.information(
                    self, "Simulation Success",
                    f"✅ {self.action_combo.currentText()} completed successfully!\n\n"
                    "Check the observation log and timeline for full details."
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

    def _update_timeline_with_action(self, char_id, action_type, parameters, result):
        """Update the timeline display with the executed action."""
        try:
            current_timeline = self.timeline_display.toPlainText()

            # Get current state for context
            state = self.simulator.current_state.get_character_state(char_id)
            if not state:
                return

            # Create timeline entry
            timeline_entry = f"🔸 T={state.time_point}: {self.action_combo.currentText()}\n"

            if action_type == "gain_xp":
                timeline_entry += f"   +{parameters['amount']} XP from {parameters['source']}\n"
            elif action_type == "increase_stat":
                timeline_entry += f"   +{parameters['amount']} to {parameters['stat_type']}\n"
            elif action_type == "level_up":
                timeline_entry += f"   Character leveled up!\n"

            timeline_entry += f"   Result: Level {state.level.value if state.level else 'N/A'}, "
            timeline_entry += f"XP: {state.experience.value if state.experience else 0}\n"

            # Add to timeline (insert after the initial state)
            lines = current_timeline.split('\n')
            insert_pos = -1
            for i, line in enumerate(lines):
                if "TIP:" in line:
                    insert_pos = i
                    break

            if insert_pos > 0:
                lines.insert(insert_pos, timeline_entry)
                self.timeline_display.setPlainText('\n'.join(lines))
            else:
                # Fallback: append to end
                self.timeline_display.setPlainText(current_timeline + '\n\n' + timeline_entry)

        except Exception as e:
            # Don't crash if timeline update fails
            print(f"Timeline update error: {e}")

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

    def _get_group_style(self) -> str:
        """Get consistent styling for group boxes."""
        return """
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
        """

    def _get_text_display_style(self) -> str:
        """Get consistent styling for text displays."""
        return """
            QTextEdit {
                background: #1a1a1a;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 3px;
                font-family: monospace;
                font-size: 10px;
            }
        """

    def _get_button_style(self) -> str:
        """Get consistent styling for buttons."""
        return """
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
        """

    def refresh(self):
        """Refresh the progression simulator tab."""
        # The simulator maintains its own state, so just ensure UI is up to date
        # This could be extended to refresh from lore_data if needed
        pass
