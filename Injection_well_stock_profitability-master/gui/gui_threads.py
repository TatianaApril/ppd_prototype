import os
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Signal, QObject

from gui import gui_func
from Main import Calculate


class Thread(QObject):
    finished = Signal()

    def __init__(self,
                 db_list: list,
                 last_fact: datetime,
                 last_pred: int,
                 month_of_working: int,
                 last_year_work: bool,
                 well_format: bool,
                 directory: str = None
                 ):
        super(Thread, self).__init__()
        self.db_list = db_list
        self.user_directory = directory
        self.last_fact = last_fact
        self.last_pred = last_pred
        self.if_well_format = well_format

        self.calculator = Calculate(month_of_working, last_year_work)


    def predict(self):
        self.calculator.make_prediction(self.db_list, self.last_pred, self.user_directory)
        if self.if_well_format:
            path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            list_of_xlsx = [os.path.join(path + '\output', name + '.xlsx') for name in self.db_list]
            for excel in list_of_xlsx:
                filename = Path(excel).name
                gui_func.write_res(self.last_fact, filename, excel)
        self.finished.emit()