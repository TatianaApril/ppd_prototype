import os

from glob import glob
from datetime import *
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from loguru import logger

from gui.constants import prefix, INPUT_NAME

global checked_list
checked_list = []


def clearLayout(pagelayout=None, sublayout=None):
    if sublayout is not None:
        currlayot = sublayout
    else:
        currlayot = pagelayout
    while currlayot.count():
        child = currlayot.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(sublayout=child.layout())


def get_stopped_month_number(month_number):
    try:
        month_number = int(month_number)
    except:
        month_number = 24
    return month_number


def stopped_month_var_checked(on, stopped_month_box):
    if on:
        stopped_month_box.setEnabled(True)
    else:
        stopped_month_box.setEnabled(False)


def get_dates():
    fold_name = os.listdir(path=INPUT_NAME)
    if fold_name:
        csv_file = glob(os.path.join(INPUT_NAME + '\\' + fold_name[0], '*.csv'))[0]
        dates = pd.read_csv(csv_file, usecols=['Дата'],  encoding='mbcs', sep=';', decimal=',', low_memory=False).squeeze()
        dates = pd.to_datetime(dates, format='mixed', dayfirst=True) #.unique()
        start_date = dates.max()
        print(start_date)
    else:
        start_date = datetime(1999, 1, 1)
    return start_date


def get_data_end(end_date):
    try:
        end_date = end_date.toPython()
    except:
        end_date = datetime(2025, 12, 1)
    return end_date


def get_fields():
    db_names = os.listdir(path=INPUT_NAME)
    return db_names


def get_well_marker(well_box):
    if well_box.toggled:
        return True
    else:
        return False


def get_layer_filter(mess):
    if mess == 0:
        return True
    else:
        return False


# def get_field_for_calc():
#     checked = []
#     root = self.tree.invisibleRootItem()
#     signal_count = root.childCount()
#     for i in range(signal_count):
#         signal = root.child(i)
#         num_children = signal.childCount()
#
#         for n in range(num_children):
#             child = signal.child(n)
#
#             if child.checkState(0) == Qt.Checked:
#                 checked.append(child.text(0))
#     return checked


def write_res(last_prod, filename, excel):
    parameters_name = ['delta_Qliq, тыс.т', 'delta_Qoil, тыс.т']

    result = pd.DataFrame()
    result_prod = pd.DataFrame()
    df = pd.read_excel(excel, sheet_name="Прогноз_суммарный")
    cells = pd.read_excel(excel, sheet_name="Ячейки")
    base_fact = pd.read_excel(excel, sheet_name="Прирост доб")

    df = df.astype({"Ячейка": 'str'})
    cells = cells.astype({'№ добывающей': 'str', "Ячейка": 'str'})
    base_fact = base_fact.astype({"Ячейка": 'str', '№ добывающей': 'str'})

    wells = cells['№ добывающей'].unique().tolist()
    cells_with_wells = cells.loc[cells['№ добывающей'].isin(wells)]
    df_in_cells = df.loc[df["Ячейка"].isin(cells_with_wells["Ячейка"])]#.set_index(['Ячейка'], drop=False)
    base_fact = base_fact.loc[base_fact["Ячейка"].isin(cells_with_wells["Ячейка"])]#.set_index(['Ячейка'], drop=False)

    for well in wells:
        #GET CONSTANTS FOR CURR WELL
        curr_cells = cells_with_wells.loc[cells_with_wells['№ добывающей']==well]["Ячейка"]
        curr_ku = cells_with_wells.loc[cells_with_wells['№ добывающей']==well]["Куч"]
        curr_kdob = cells_with_wells.loc[cells_with_wells['№ добывающей']==well]["Куч Итог"]
        curr_ku.index = curr_cells
        curr_kdob.index = curr_cells
        curr_cells = curr_cells.unique()
        curr_ku = curr_ku[~curr_ku.index.duplicated(keep='first')]
        curr_kdob =curr_kdob[~curr_kdob.index.duplicated(keep='first')]

        #GET BASE
        base_by_wells = base_fact.loc[base_fact["№ добывающей"].isin([well])].iloc[:, 1:]
        base_by_wells = base_by_wells.drop(columns=['Объект', 'Статус', 'Арпс/Полка', "№ добывающей"]).loc[
            base_by_wells['Параметр'] != 'Параметр']
        base_by_wells = base_by_wells.groupby(['Ячейка', "Параметр"], as_index=False).sum()
        #extracting longest base
        first_slice= base_by_wells.iloc[:, 3:].loc[:, (base_by_wells.iloc[:, 3:] != 0).any(axis=0)].iloc[:, 0]
        first_cell = base_by_wells.loc[first_slice.loc[first_slice > 0].index[0], 'Ячейка']
        fact = base_by_wells.loc[(base_by_wells['Параметр'].isin(['Qliq_fact, tons/day', 'Qoil_fact, tons/day'])) &
                                 (base_by_wells['Ячейка'] == first_cell)].reset_index(drop=True)
        fact.iloc[:, 3:] = fact.groupby(["Параметр"], as_index=False).apply(
                            lambda row:
                            row.iloc[:, 3:] / curr_kdob.loc[curr_kdob.index == first_cell].values[0])
        delta = base_by_wells.loc[
            base_by_wells['Параметр'].isin(['delta_Qliq, tons/day', 'delta_Qoil, tons/day'])].reset_index(drop=True)
        delta_sum = delta.groupby(["Параметр"], as_index=False).sum()
        base = fact.groupby(["Параметр"], as_index=False).apply(
            lambda row:
            row.iloc[:, 3:].subtract(delta_sum.iloc[row.index, 3:]))
        base.insert(0, 'Параметр', ['base LIQ, tons/day', 'base OIL, tons/day'])
        base.insert(0, 'Ячейка', [0, 0])

        #another method
        # partial_fact = base_by_wells.loc[base_by_wells['Параметр'].isin(['Qliq_fact, tons/day', 'Qoil_fact, tons/day'])
        #                                 ].reset_index(drop=True)
        # another_base = partial_fact.groupby(["Параметр"], as_index=False).apply(
        #     lambda row:
        #     pd.concat([row.iloc[:, :2], row.iloc[:, 2:].subtract(delta.iloc[row.index, 2:])],
        #               axis=1).reset_index(drop=True)
        # )
        # #another_base.insert(0, "Параметр", partial_fact["Параметр"])
        # another_base = another_base.groupby(["Параметр"], as_index=False).sum()

        # DELTA INCREMENT BY CELLS
        df_by_wells = df_in_cells.loc[df_in_cells["Ячейка"].isin(curr_cells)].iloc[:, 1:]
        df_by_wells = df_by_wells.drop(columns=['Последняя дата работы'])
        df_by_wells.iloc[:, 2:] = df_by_wells.groupby(["Ячейка"]).apply(
            lambda row: row.iloc[:, 2:] *
                        curr_ku.loc[curr_ku.index==row.name].values[0])

        # GET COLUMNS
        basedate = base.columns[-1]
        dateline = [basedate + relativedelta(months=1 + i) for i in range(df_by_wells.iloc[:, 2:].shape[1])]
        df_by_wells.columns = df_by_wells.columns[:2].tolist() + dateline

        # MERGE DELTA
        df_by_wells = delta.merge(df_by_wells, how='right', on=['Ячейка', 'Параметр'])

        # SUMM INCREMENT FOR WELL
        df_by_wells_sum = df_by_wells.groupby(['Параметр'], as_index=False).sum()
        df_by_wells_sum = df_by_wells_sum.reset_index(drop=True).drop(columns=["Ячейка"])
        df_by_wells_sum['Параметр'] = ['sum delta_Qliq, т/сут', 'sum delta_Qoil, т/сут']

        #GET COLUMNS
        df_by_wells_sum.columns = df_by_wells.columns[1:]

        # COUNTING PRODUCTION FROM DEB
        df_by_wells_prod = df_by_wells.iloc[:, 2:] * 30.45 / 1000
        df_by_wells_prod.insert(0, 'Ячейка', df_by_wells['Ячейка'])
        df_by_wells_prod.insert(1, 'Параметр', parameters_name * curr_cells.size)

        df_by_wells_sum_prod = df_by_wells_sum.iloc[:, 1:] * 30.45 / 1000
        df_by_wells_sum_prod.insert(0, 'Параметр', ['sum delta_Qliq, тыс.т', 'sum delta_Qoil, тыс.т'])

        # GET COLUMNS
        df_by_wells_prod.columns = df_by_wells.columns
        df_by_wells_sum_prod.columns = df_by_wells_sum.columns

        # GET INDEXES
        df_by_wells.index = [well] * len(df_by_wells.index)
        df_by_wells_prod.index = [well, well] * curr_cells.size
        df_by_wells_sum.index = [well, well]
        df_by_wells_sum_prod.index = [well, well]
        base.index = [well, well]
        delta.index = [well, well] * curr_cells.size

        result = pd.concat([result, base, df_by_wells, df_by_wells_sum]).fillna(0)
        result_prod = pd.concat([result_prod, df_by_wells_prod, df_by_wells_sum_prod]).fillna(0)

    new_columns = result.columns[2:] <= last_prod
    result = result.loc[:, np.insert(new_columns, 0, [True, True])]

    result = result.loc[:, (result != 0).any(axis=0)]
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    save = path+'\output' + r'\new'
    output = os.path.join(save, 'new' + filename)
    writer = pd.ExcelWriter(output)
    result.to_excel(writer, sheet_name='Прогноз по скважинам', index=True)
    result_prod.to_excel(writer, sheet_name='Добыча по скважинам', index=True)
    cells_with_wells.to_excel(writer, sheet_name='Ячейки', index=True)
    writer.close()

    logger.info(f"Поскважинный формат выгрузки для: {filename}")
