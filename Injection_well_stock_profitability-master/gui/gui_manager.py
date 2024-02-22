import os
from pathlib import Path
from typing import Tuple
from datetime import datetime

from gui import gui_func
from gui.constants import DO, DO_dictionary

from PySide6.QtCore import Qt, QDate, QLocale
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QLineEdit,
    QGroupBox,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
    QSizePolicy,
    QLabel,
    QWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QFileDialog,
    QPushButton
)


def create_date_layout(start_date) -> Tuple[QGroupBox, QDateEdit, QLineEdit]:
    date_groupbox = QGroupBox('Даты начала и конца прогноза')
    entry_date_layout = QFormLayout()
    date_groupbox.setLayout(entry_date_layout)

    # displays last fact from csv
    start_date_entry = QDateEdit(date=start_date)
    start_date_entry.setEnabled(False)
    start_date_entry.setStyleSheet('font: dodgerblue')

    # auto or manual choice of last prediction date
    end_date_entry = QDateEdit(date=QDate(2024, 12, 1))
    end_date_entry.setStyleSheet('font: dodgerblue')

    # manual choice of last prediction date by number
    month_edit = QLineEdit()
    month_edit.setStyleSheet('font: dodgerblue; qproperty-alignment: AlignCenter')
    last_date = datetime(2024, 12, 1)
    months = (last_date.year - start_date.year) * 12 + last_date.month - start_date.month
    month_edit.setText(str(months))

    # no letters in month_edit
    val = QDoubleValidator(1, 300, 0)
    val.setLocale(QLocale("en_US"))
    month_edit.setValidator(val)

    entry_date_layout.addRow('Последний месяц факта:', start_date_entry)
    entry_date_layout.addRow('Последний месяц прогноза: ', end_date_entry)
    entry_date_layout.addRow('Задать количество месяцев: ', month_edit)
    return date_groupbox, end_date_entry, month_edit


def get_nice_button(text: str) -> QPushButton:
    button = QPushButton()
    button.setFixedSize(200, 100)
    button.setStyleSheet("QPushButton:pressed { background-color: mediumslateblue }")
    button.setText(text)
    button.setCheckable(True)
    return button


def create_layers_layout() -> Tuple[QGroupBox, QPushButton, QPushButton]:
    layers_groupbox = QGroupBox('Учёт пластов в рассчитываемых месторождениях')
    main = QVBoxLayout()
    hor = QHBoxLayout()

    # comments for user
    label_mid = QLabel('Выбор способа оценки')
    label_left = 'с учётом скважин, \n работавших \n за последний год'
    label_right = 'с учётом скважин, \n работающих \n на месяц прогноза'
    label_mid.setStyleSheet('qproperty-alignment: AlignCenter; font: 13px;')

    # creating basic buttons
    button_left = get_nice_button(label_left)
    button_right = get_nice_button(label_right)

    hor.addWidget(button_left)
    hor.addWidget(button_right)
    main.addWidget(label_mid)
    main.addLayout(hor)
    layers_groupbox.setLayout(main)
    return layers_groupbox, button_left, button_right


def create_options_layout() -> Tuple[QGroupBox, QComboBox, QCheckBox]:
    options_groupbox = QGroupBox('Дополнительные настройки')
    vertical = QVBoxLayout()
    options_layout = QFormLayout()
    options_groupbox.setLayout(vertical)

    # you can choose period after unlocking it in checkbox
    check_predict_stopped_wells = QCheckBox("Прогноз для остановленных скважин")
    check_predict_stopped_wells.toggled.connect(lambda on: gui_func.stopped_month_var_checked(on, stopped_month_box))

    # prediction for stopped wells (work in 0 to X months)
    stopped_month_box = QComboBox()
    modes = [str(i + 1) for i in range(36)]
    stopped_month_box.addItems(modes)
    stopped_month_box.setCurrentText("24")
    stopped_month_box.setStyleSheet('font: dodgerblue 13px;')
    stopped_month_box.setEnabled(False)

    # check if one wants to well format, not objects
    check_well_format = QCheckBox('Поскважинный формат выгрузки')
    check_well_format.setCheckState(Qt.Checked)

    vertical.addWidget(check_predict_stopped_wells)
    vertical.addSpacing(10)
    options_layout.addRow('Допустимые месяцы бездействия:', stopped_month_box)
    vertical.addLayout(options_layout)
    vertical.addSpacing(10)
    vertical.addWidget(check_well_format)
    vertical.addSpacing(10)
    return options_groupbox, stopped_month_box, check_well_format


# def view_adv_options(toggleButton, contentArea):
#     arrow_type = Qt.DownArrow if toggleButton.isChecked() else Qt.RightArrow
#     toggleButton.setArrowType(arrow_type)
#     heigt = 0 if toggleButton.isChecked() else 400
#     contentArea.setFixedHeight(heigt)
#
#
# def get_collapsible_box(box: QGroupBox, text: str='Отобразить дополнительные настройки'):
#     mainLayout = QVBoxLayout()
#
#     button = QToolButton()
#     button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
#     button.setText(text)
#     button.setArrowType(Qt.ArrowType.DownArrow)
#     button.setCheckable(True)
#     button.setChecked(True)
#     button.clicked.connect(lambda: view_adv_options(button, contentArea))
#
#     contentArea = QScrollArea()
#     contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
#     contentArea.setMaximumHeight(0)
#     contentArea.setMinimumHeight(0)
#     contentArea.setWidgetResizable(True)
#
#     contentArea.setWidget(box)
#     mainLayout.addWidget(button)
#     mainLayout.addWidget(contentArea)
#     mainLayout.addSpacing(5)
#     return mainLayout


def handle_item_changed(
        checked_list: list,
        item: QTreeWidgetItem,
        column: int,
    ):
    if item.checkState(column) == Qt.Checked:
        children = item.takeChildren()
        item.addChildren(children)
        if children:
            for child in children:
                text = child.text(0)
                if text not in checked_list:
                    checked_list.append(text)
                else:
                    continue
        else:
            text = item.text(0)
            if text not in checked_list:
                checked_list.append(text)
    elif item.checkState(column) == Qt.Unchecked:
        children = item.takeChildren()
        item.addChildren(children)
        if children:
            for child in children:
                text = child.text(0)
                try:
                    checked_list.remove(text)
                except:
                    pass
        else:
            text = item.text(0)
            try:
                checked_list.remove(text)
            except:
                pass


def load_file(parent_widget):
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.FileMode.Directory)
    dialog.setOption(QFileDialog.DontUseCustomDirectoryIcons)
    dialog.setDirectory(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    #dialog.setNameFilter('(*.csv)')
    if dialog.exec():
        parent_widget.field_folder = Path(dialog.selectedFiles()[0])


def get_field_tabs(_parent, fields_from_db):
    # Initialize tab screen
    tabs = QTabWidget()
    tab1 = QWidget()
    tab3 = QWidget()
    tabs.addTab(tab1, "Выбор месторождений")
    tabs.addTab(tab3, "Загрузить новый файл")

    # Create layout
    tab1.layout = QVBoxLayout()
    tab1.setLayout(tab1.layout)
    tab3.layout = QVBoxLayout(_parent)
    tab3.setLayout(tab3.layout)

    _parent.checked_list = []
    # first tab
    tree = QTreeWidget()
    tree.setHeaderLabels(['Выберите месторождения для расчёта'])
    tree.itemClicked.connect(lambda item, column:
                             handle_item_changed(_parent.checked_list, item, column))
    for do in DO._all:
        #if set(fields_from_db).issubset(set(DO_dictionary.dict[do])):
        if list(set(fields_from_db) & set(DO_dictionary.dict[do])):
            parent = QTreeWidgetItem(tree)
            parent.setText(0, do)
            parent.setFlags(parent.flags() | Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable)
            parent.setCheckState(0, Qt.Unchecked)
            parent.setExpanded(True)
            for field in DO_dictionary.dict[do]:
                if field in fields_from_db:
                    child = QTreeWidgetItem(parent)
                    child.setText(0, field)
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    child.setCheckState(0, Qt.Unchecked)
                    parent.addChild(child)
            else:
                continue
        else:
            continue
    tab1.layout.addSpacing(20)
    tab1.layout.addWidget(tree)

    # second tab
    label_tab_3 = QLabel('Выберите папку с техрежимами')
    label_tab_3.setStyleSheet('qproperty-alignment: AlignCenter; font: 14px;')
    tab3.layout.addWidget(label_tab_3)
    button_tab_3 = QPushButton('Загрузить файл')
    button_tab_3.setFixedSize(tab3.size()/3)
    button_tab_3.clicked.connect(lambda: load_file(_parent))
    tab3.layout.addWidget(button_tab_3, alignment=Qt.AlignCenter)
    tab3.layout.addWidget(QLabel())

    _parent.inj_left_sidelayout.addWidget(tabs)


# def create_constants_ppd_layout(_parent, fields_from_db):
#     mainlayout = QVBoxLayout()
#     date_layout = QFormLayout()
#     _parent.field_layot = QFormLayout()
#     _parent.last_prediction_date = QDateEdit(QDate(2025, 1, 1))
#
#     options_groupbox = QGroupBox('Настройки расчёта ППД')
#     date_layout.addRow('Длительность прогноза', _parent.last_prediction_date)
#     label = QLabel('Расчёт для месторождений:')
#
#     for name in fields_from_db:
#         box = QCheckBox()
#         box.setCheckState(Qt.CheckState.Checked)
#         _parent.field_layot.addRow(name, box)
#
#     mainlayout.addLayout(date_layout)
#     mainlayout.addWidget(label)
#     mainlayout.addLayout(_parent.field_layot)
#     options_groupbox.layout = mainlayout
#     options_groupbox.setLayout(options_groupbox.layout)
#     return options_groupbox
