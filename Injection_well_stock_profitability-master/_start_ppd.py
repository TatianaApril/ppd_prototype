from datetime import datetime
from dateutil.relativedelta import relativedelta

# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QMainWindow,
    QScrollArea,
    QPushButton,
    QHBoxLayout,
    )
from PySide6.QtCore import QThread
from qt_material import apply_stylesheet


from gui import (
    gui_manager,
    gui_func,
    gui_threads
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Эффекты ГТМ по скважинам")
        self.resize(1200, 800)
        self.field_folder = None
        self.checked_list = []
        self.layers_mess = 0

        # main layouts of gui: ing = left + right
        self.inj_right_sidelayout = QVBoxLayout()
        self.inj_left_sidelayout = QVBoxLayout()
        self.inj_ing_pagelayout = QHBoxLayout()
        scrollarea = QScrollArea()

        # date box
        self.last_fact = gui_func.get_dates()
        date_groupbox,\
        self.end_date_entry,\
        self.month_edit = gui_manager.create_date_layout(self.last_fact)
        self.end_date_entry.dateChanged.connect(self.date_changed)
        self.month_edit.textChanged.connect(self.months_changed)

        # layers box
        layers_groupbox, \
        self.left_lay_button, self.right_lay_button = gui_manager.create_layers_layout()
        self.left_lay_button.setChecked(True)
        self.left_lay_button.clicked.connect(self.layer_button_pressed)
        self.right_lay_button.clicked.connect(self.layer_button_pressed)

        # options box
        options_groupbox,\
        self.stopped_month_box, self.well_format_box = gui_manager.create_options_layout()

        # tree of DO
        self.fields_from_db = gui_func.get_fields()
        gui_manager.get_field_tabs(self, self.fields_from_db)

        # main button
        self.button = QPushButton('Рассчитать')
        self.button.setShortcut('Return')
        self.button.clicked.connect(self.start_ppd)

        self.inj_right_sidelayout.addSpacing(40)
        self.inj_right_sidelayout.addWidget(date_groupbox)
        self.inj_right_sidelayout.addSpacing(30)
        self.inj_right_sidelayout.addWidget(layers_groupbox)
        self.inj_right_sidelayout.addSpacing(30)
        self.inj_right_sidelayout.addWidget(options_groupbox)
        self.inj_right_sidelayout.addSpacing(30)

        self.inj_left_sidelayout.addSpacing(30)
        self.inj_left_sidelayout.addWidget(self.button)
        self.inj_left_sidelayout.addSpacing(30)

        self.inj_ing_pagelayout.addSpacing(50)
        self.inj_ing_pagelayout.addLayout(self.inj_right_sidelayout)
        self.inj_ing_pagelayout.addSpacing(50)
        self.inj_ing_pagelayout.addLayout(self.inj_left_sidelayout)
        self.inj_ing_pagelayout.addSpacing(50)

        scrollarea.setLayout(self.inj_ing_pagelayout)
        scrollarea.setWidgetResizable(True)
        self.setCentralWidget(scrollarea)


    def date_changed(self, date: datetime.date):
        # change event connects date entry with line edit window
        d1 = self.last_fact
        d2 = date.toPython()
        months = (d2.year - d1.year) * 12 + d2.month - d1.month
        self.month_edit.setText(str(months))

    def months_changed(self, month: str):
        # change event connects date entry with line edit window
        if month != '':
            d1 = self.last_fact
            d2 = d1 + relativedelta(months=int(month))
            self.end_date_entry.setDate(d2)

    def layer_button_pressed(self):
        # button clicked event connects two buttons together
        if self.right_lay_button.isChecked() and self.layers_mess == 0:
            self.layers_mess = 1
            self.left_lay_button.setChecked(False)
            self.right_lay_button.setChecked(True)
        else:
            self.layers_mess = 0
            self.left_lay_button.setChecked(True)
            self.right_lay_button.setChecked(False)


    def start_ppd(self):
        #get flags from self.field_layot
        if self.month_edit.text() != '':
            last_pred = int(self.month_edit.text())
        else:
            last_pred = 1

        if self.field_folder is not None:
            self.checked_list = [self.field_folder.name]
        month_of_working = int(self.stopped_month_box.currentText())
        last_year_work = gui_func.get_layer_filter(self.layers_mess)
        well_format = gui_func.get_well_marker(self.well_format_box)

        self.worker = gui_threads.Thread(
            db_list=self.checked_list,
            last_fact=self.last_fact,
            last_pred=last_pred,
            month_of_working=month_of_working,
            last_year_work=last_year_work,
            well_format=well_format,
            directory=self.field_folder)
        self.worker_thread = QThread()
        #######  COMMIT IF WANT  TO DEBUG
        #self.worker.moveToThread(self.worker_thread)
        #######
        self.worker_thread.started.connect(self.worker.predict)
        #self.worker.finished.connect(self.get_output)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.start()


app = QApplication([])
window = MainWindow()
app.setQuitOnLastWindowClosed(False)
extra_css = """
    QPushButton
    {
    color: white;
    font: light 12px;
    }
    QDateEdit
    {
    color: dodgerblue;
    }
    QLineEdit
    {
    color: white;
    }
    QComboBox
    {
    color: white;
    }
    QListView::item 
    {
    background-color: dimgrey;
    selection-background-color: mediumorchid;
    }"""
apply_stylesheet(app, theme='dark_blue.xml')
app.setStyleSheet(app.styleSheet() + extra_css)
window.show()
app.exec()

# def get_output(self, field=None):
#     path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     dirname = os.path.join(path + '\output' + r'\new', '*.xlsx')
#     list_of_xlsx = glob(dirname)
#     filenames = [Path(excel).name for excel in list_of_xlsx]
#     names = [name[:-5] for name in filenames]
#
#     if field is None:
#         field = names[0]
#     else:
#         gui_func.clearLayout(self.inj_ing_pagelayout)
#
#     df = pd.read_excel(list_of_xlsx[names.index(field)], sheet_name="Прогноз по скважинам").fillna(0)
#     df = df.rename(columns={'Unnamed: 0': "wells"})
#     df = df.astype({"Ячейка": 'str', 'wells': 'str'})
#     self.wells = df["wells"].unique().tolist()
#     self.wells.sort()

# field_choose = QComboBox()
# field_choose.addItems(names)
# field_choose.setCurrentText(field)
# field_choose.currentTextChanged.connect(self.get_output)
#
# self.scroll_well = QListWidget()
# self.scroll_well.addItems(self.wells)
# self.scroll_well.itemClicked.connect(lambda item: self.get_graph(item.text(), self.last_fact, df))
# self.scroll_well.setAlternatingRowColors(True)
#
# self.pagelayout.addWidget(field_choose)
# self.pagelayout.addWidget(self.scroll_well)


