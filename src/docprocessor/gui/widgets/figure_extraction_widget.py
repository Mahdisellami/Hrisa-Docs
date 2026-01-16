"""Widget for displaying and managing extracted figures."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from docprocessor.gui.styles import Colors, Styles
from docprocessor.models.extracted_figure import FigureExtractionResult, FigureType
from docprocessor.utils.language_manager import get_language_manager


class FigureExtractionWidget(QWidget):
    """Widget for extracting and displaying figures from documents."""

    extract_requested = pyqtSignal(str)  # document_path
    figure_selected = pyqtSignal(object)  # ExtractedFigure

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.extraction_result = None
        self.all_figures = []
        self.filtered_figures = []
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(self.lang_manager.get("figure_extraction_title"))
        header.setStyleSheet(Styles.LABEL_HEADER)
        layout.addWidget(header)

        # Control panel
        control_group = QGroupBox(self.lang_manager.get("figure_extraction_control"))
        control_layout = QHBoxLayout()

        self.extract_btn = QPushButton(self.lang_manager.get("btn_extract_figures"))
        self.extract_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.extract_btn.setEnabled(False)
        control_layout.addWidget(self.extract_btn)

        control_layout.addStretch()
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(Styles.PROGRESS_BAR)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel(self.lang_manager.get("status_no_document"))
        self.status_label.setStyleSheet(Styles.LABEL_SECONDARY)
        layout.addWidget(self.status_label)

        # Statistics panel
        stats_group = QGroupBox(self.lang_manager.get("figure_statistics"))
        stats_layout = QHBoxLayout()

        self.total_figures_label = QLabel(f"{self.lang_manager.get('label_total')}: 0")
        stats_layout.addWidget(self.total_figures_label)

        self.currency_count_label = QLabel(f"{self.lang_manager.get('label_currency')}: 0")
        stats_layout.addWidget(self.currency_count_label)

        self.percentage_count_label = QLabel(f"{self.lang_manager.get('label_percentage')}: 0")
        stats_layout.addWidget(self.percentage_count_label)

        self.date_count_label = QLabel(f"{self.lang_manager.get('label_dates')}: 0")
        stats_layout.addWidget(self.date_count_label)

        stats_layout.addStretch()
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Filter panel
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel(self.lang_manager.get("label_filter_type")))

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            [
                self.lang_manager.get("filter_all"),
                self.lang_manager.get("filter_currency"),
                self.lang_manager.get("filter_percentage"),
                self.lang_manager.get("filter_date"),
                self.lang_manager.get("filter_range"),
                self.lang_manager.get("filter_quantity"),
                self.lang_manager.get("filter_number"),
            ]
        )
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)

        self.show_tables_only_check = QCheckBox(self.lang_manager.get("label_tables_only"))
        self.show_tables_only_check.stateChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.show_tables_only_check)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels(
            [
                self.lang_manager.get("table_header_select"),
                self.lang_manager.get("table_header_type"),
                self.lang_manager.get("table_header_value"),
                self.lang_manager.get("table_header_numeric"),
                self.lang_manager.get("table_header_unit_currency"),
                self.lang_manager.get("table_header_year"),
                self.lang_manager.get("table_header_location"),
                self.lang_manager.get("table_header_context"),
            ]
        )

        # Configure table
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setAlternatingRowColors(True)

        # Set column widths
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.results_table)

        # Action buttons
        action_layout = QHBoxLayout()

        self.export_btn = QPushButton(self.lang_manager.get("btn_export_csv"))
        self.export_btn.setEnabled(False)
        self.export_btn.setToolTip(self.lang_manager.get("tooltip_export_csv"))
        self.export_btn.clicked.connect(self.export_to_csv)
        action_layout.addWidget(self.export_btn)

        self.update_figures_btn = QPushButton(self.lang_manager.get("btn_update_figures"))
        self.update_figures_btn.setEnabled(False)
        self.update_figures_btn.setToolTip(self.lang_manager.get("tooltip_update_figures"))
        self.update_figures_btn.clicked.connect(self.update_selected_figures)
        action_layout.addWidget(self.update_figures_btn)

        action_layout.addStretch()

        self.clear_btn = QPushButton(self.lang_manager.get("btn_clear_results"))
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self.clear_results)
        action_layout.addWidget(self.clear_btn)

        layout.addLayout(action_layout)

    def set_document(self, document_path: str):
        """Set the document to extract from."""
        self.document_path = document_path
        self.extract_btn.setEnabled(True)
        self.status_label.setText(
            self.lang_manager.get("status_ready_extract").format(document_path)
        )

    def show_results(self, result: FigureExtractionResult):
        """Display extraction results."""
        self.extraction_result = result
        self.all_figures = result.figures
        self.filtered_figures = result.figures

        # Update statistics
        self.total_figures_label.setText(
            f"{self.lang_manager.get('label_total')}: {result.total_figures}"
        )
        self.currency_count_label.setText(
            f"{self.lang_manager.get('label_currency')}: {result.figures_by_type.get('currency', 0)}"
        )
        self.percentage_count_label.setText(
            f"{self.lang_manager.get('label_percentage')}: {result.figures_by_type.get('percentage', 0)}"
        )
        self.date_count_label.setText(
            f"{self.lang_manager.get('label_dates')}: {result.figures_by_type.get('date', 0)}"
        )

        # Populate table
        self.populate_table(result.figures)

        # Enable buttons
        self.export_btn.setEnabled(True)
        self.update_figures_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)

        # Update status
        if result.errors:
            self.status_label.setText(
                self.lang_manager.get("status_extraction_complete").format(
                    result.total_figures, result.extraction_time_seconds
                )
                + f" ({len(result.errors)} errors)"
            )
            self.status_label.setStyleSheet(f"color: {Colors.ERROR}; font-style: italic;")
        else:
            self.status_label.setText(
                self.lang_manager.get("status_extraction_complete").format(
                    result.total_figures, result.extraction_time_seconds
                )
            )
            self.status_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-style: italic;")

    def populate_table(self, figures: list):
        """Populate table with figures."""
        self.results_table.setRowCount(len(figures))

        for row, figure in enumerate(figures):
            # Checkbox
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.results_table.setCellWidget(row, 0, checkbox_widget)

            # Type - use translated type name
            type_key = f"figure_type_{figure.figure_type.value}"
            type_text = self.lang_manager.get(type_key)
            type_item = QTableWidgetItem(type_text)
            # Color code by type
            if figure.figure_type == FigureType.CURRENCY:
                type_item.setBackground(QColor(200, 255, 200))  # Light green
            elif figure.figure_type == FigureType.PERCENTAGE:
                type_item.setBackground(QColor(255, 230, 200))  # Light orange
            elif figure.figure_type == FigureType.DATE:
                type_item.setBackground(QColor(200, 230, 255))  # Light blue
            self.results_table.setItem(row, 1, type_item)

            # Value
            value_item = QTableWidgetItem(figure.value)
            value_item.setToolTip(figure.value)
            self.results_table.setItem(row, 2, value_item)

            # Numeric value
            numeric_str = f"{figure.numeric_value:,.2f}" if figure.numeric_value else "-"
            numeric_item = QTableWidgetItem(numeric_str)
            self.results_table.setItem(row, 3, numeric_item)

            # Unit/Currency
            unit_str = figure.currency_code or figure.unit or "-"
            unit_item = QTableWidgetItem(unit_str)
            self.results_table.setItem(row, 4, unit_item)

            # Year
            year_str = str(figure.year) if figure.year else "-"
            year_item = QTableWidgetItem(year_str)
            self.results_table.setItem(row, 5, year_item)

            # Location
            if figure.is_from_table:
                location = f"{self.lang_manager.get('location_table')} {figure.table_index + 1}, R{figure.table_row}C{figure.table_column}"
            elif figure.page_number:
                location = f"{self.lang_manager.get('location_page')} {figure.page_number}, {self.lang_manager.get('location_para')} {figure.paragraph_number or '?'}"
            else:
                location = (
                    f"{self.lang_manager.get('location_para')} {figure.paragraph_number or '?'}"
                )
            location_item = QTableWidgetItem(location)
            self.results_table.setItem(row, 6, location_item)

            # Context (truncated)
            context = (
                figure.context_sentence[:100] + "..."
                if len(figure.context_sentence) > 100
                else figure.context_sentence
            )
            context_item = QTableWidgetItem(context)
            context_item.setToolTip(figure.context_sentence)  # Full context in tooltip
            self.results_table.setItem(row, 7, context_item)

    def apply_filter(self):
        """Apply filter to results."""
        if not self.all_figures:
            return

        filter_type = self.filter_combo.currentText()
        show_tables_only = self.show_tables_only_check.isChecked()

        # Filter by type
        if filter_type == self.lang_manager.get("filter_all"):
            filtered = self.all_figures
        else:
            # Map translated filter names back to FigureType enum values
            filter_map = {
                self.lang_manager.get("filter_currency"): "currency",
                self.lang_manager.get("filter_percentage"): "percentage",
                self.lang_manager.get("filter_date"): "date",
                self.lang_manager.get("filter_range"): "range",
                self.lang_manager.get("filter_quantity"): "quantity",
                self.lang_manager.get("filter_number"): "number",
            }
            filter_enum_value = filter_map.get(filter_type, filter_type.lower())
            filter_type_enum = FigureType(filter_enum_value)
            filtered = [f for f in self.all_figures if f.figure_type == filter_type_enum]

        # Filter by table location
        if show_tables_only:
            filtered = [f for f in filtered if f.is_from_table]

        self.filtered_figures = filtered
        self.populate_table(filtered)
        self.status_label.setText(
            self.lang_manager.get("status_showing_figures").format(
                len(filtered), len(self.all_figures)
            )
        )

    def get_selected_figures(self) -> list:
        """Get list of selected figures."""
        selected = []
        for row in range(self.results_table.rowCount()):
            checkbox_widget = self.results_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    # Get corresponding figure
                    if row < len(self.filtered_figures):
                        selected.append(self.filtered_figures[row])
        return selected

    def clear_results(self):
        """Clear all results."""
        self.results_table.setRowCount(0)
        self.extraction_result = None
        self.all_figures = []
        self.filtered_figures = []
        self.total_figures_label.setText(f"{self.lang_manager.get('label_total')}: 0")
        self.currency_count_label.setText(f"{self.lang_manager.get('label_currency')}: 0")
        self.percentage_count_label.setText(f"{self.lang_manager.get('label_percentage')}: 0")
        self.date_count_label.setText(f"{self.lang_manager.get('label_dates')}: 0")
        self.export_btn.setEnabled(False)
        self.update_figures_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.status_label.setText(self.lang_manager.get("status_results_cleared"))
        self.status_label.setStyleSheet(Styles.LABEL_SECONDARY)

    def update_status(self, status: str, is_error: bool = False):
        """Update status label."""
        self.status_label.setText(status)
        if is_error:
            self.status_label.setStyleSheet(f"color: {Colors.ERROR}; font-style: italic;")
        else:
            self.status_label.setStyleSheet(Styles.LABEL_SECONDARY)

    def export_to_csv(self):
        """Export extraction results to CSV file."""
        if not self.filtered_figures:
            QMessageBox.warning(
                self,
                self.lang_manager.get("dialog_no_data_export"),
                self.lang_manager.get("dialog_no_data_export_msg"),
            )
            return

        # Get save location from user
        from datetime import datetime

        from PyQt6.QtWidgets import QFileDialog

        default_filename = f"figures_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.lang_manager.get("dialog_export_csv"),
            default_filename,
            self.lang_manager.get("dialog_csv_filter"),
        )

        if not file_path:
            return  # User cancelled

        # Export to CSV
        try:
            import csv

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(
                    [
                        self.lang_manager.get("csv_header_type"),
                        self.lang_manager.get("csv_header_value"),
                        self.lang_manager.get("csv_header_numeric_value"),
                        self.lang_manager.get("csv_header_unit_currency"),
                        self.lang_manager.get("csv_header_year"),
                        self.lang_manager.get("csv_header_page"),
                        self.lang_manager.get("csv_header_paragraph"),
                        self.lang_manager.get("csv_header_is_from_table"),
                        self.lang_manager.get("csv_header_table_index"),
                        self.lang_manager.get("csv_header_table_row"),
                        self.lang_manager.get("csv_header_table_column"),
                        self.lang_manager.get("csv_header_table_row_header"),
                        self.lang_manager.get("csv_header_table_column_header"),
                        self.lang_manager.get("csv_header_context_sentence"),
                        self.lang_manager.get("csv_header_confidence_score"),
                    ]
                )

                # Write data rows
                for figure in self.filtered_figures:
                    # Translate figure type
                    type_key = f"figure_type_{figure.figure_type.value}"
                    type_text = self.lang_manager.get(type_key)

                    writer.writerow(
                        [
                            type_text,
                            figure.value,
                            figure.numeric_value if figure.numeric_value else "",
                            figure.currency_code or figure.unit or "",
                            figure.year if figure.year else "",
                            figure.page_number if figure.page_number else "",
                            figure.paragraph_number if figure.paragraph_number else "",
                            (
                                self.lang_manager.get("csv_value_yes")
                                if figure.is_from_table
                                else self.lang_manager.get("csv_value_no")
                            ),
                            figure.table_index if figure.table_index is not None else "",
                            figure.table_row if figure.table_row is not None else "",
                            figure.table_column if figure.table_column is not None else "",
                            figure.table_row_header or "",
                            figure.table_column_header or "",
                            figure.context_sentence,
                            figure.confidence_score,
                        ]
                    )

            # Show success message
            QMessageBox.information(
                self,
                self.lang_manager.get("dialog_export_success"),
                self.lang_manager.get("dialog_export_success_msg").format(
                    len(self.filtered_figures), file_path
                ),
            )

            self.update_status(
                self.lang_manager.get("dialog_export_success_msg").format(
                    len(self.filtered_figures), file_path
                ),
                is_error=False,
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                self.lang_manager.get("dialog_export_error"),
                self.lang_manager.get("dialog_export_error_msg").format(str(e)),
            )
            self.update_status(
                self.lang_manager.get("dialog_export_error_msg").format(str(e)), is_error=True
            )

    def update_selected_figures(self):
        """Update selected figures with online data."""
        selected = self.get_selected_figures()

        if not selected:
            QMessageBox.information(
                self,
                self.lang_manager.get("dialog_no_selection"),
                self.lang_manager.get("dialog_no_selection_msg"),
            )
            return

        # Show info about selected figures
        figure_summary = "\n".join(
            [
                f"- {fig.value} ({self.lang_manager.get(f'figure_type_{fig.figure_type.value}')})"
                for fig in selected[:10]  # Show first 10
            ]
        )

        if len(selected) > 10:
            figure_summary += (
                f"\n... {self.lang_manager.get('and_more').format(len(selected) - 10)}"
            )

        message = self.lang_manager.get("dialog_update_figures_msg").format(
            len(selected), figure_summary
        )

        QMessageBox.information(self, self.lang_manager.get("dialog_update_figures_title"), message)
