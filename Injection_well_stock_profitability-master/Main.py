import numpy as np
import pandas as pd
import xlwings as xw
import os

from dateutil.relativedelta import relativedelta
from loguru import logger

from gui.constants import OUT_NAME
from I_Cell_calculate import calculation_coefficients, calculation_injCelle
from II_Oil_increment_calculate import calculate_oil_increment
from III_Uncalculated_wells_and_summation_increments import final_adaptation_and_summation
from IV_Forecast_calculate import calculate_forecast
from Utility_function import get_period_of_working_for_calculating, merging_sheets
from Reader import Reader

from drainage_area import get_properties, calculate_zones
import warnings

warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None  # default='warn'

# Switches
drainage_areas, dynamic_coefficient = [None, None]

# CONSTANT
DEFAULT_HHT = 0.1  # meters
MAX_DISTANCE: int = 1000  # default maximum distance from injection well for reacting wells


class Calculate:
    def __init__(self, month_of_working: int,
                if_has_working_for_the_last_year: bool):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        logger.info(f"path:{self.dir_path}")

        self.reader = Reader(MONTHS_OF_WORKING=month_of_working,
                        HAS_WORKING_HOURS_FOR_THE_LAST_YEAR=if_has_working_for_the_last_year)

        self.initial_coefficient,\
        self.reservoir_properties,\
        self.max_reaction_distance,\
        self.parameters = self.reader.read_yml()

        self.max_overlap_percent, \
        self.angle_verWell, \
        self.angle_horWell_T1, \
        self.angle_horWell_T3, \
        self.time_predict, \
        self.volume_factor, \
        self.Rw, \
        self.drainage_areas, \
        self.dynamic_coefficient = self.parameters.values()

        self.conversion_factor = self.volume_factor * self.Rw


    def make_prediction(self, database_content: list,
                data_end_of_pred: int,
                user_directory: str = None
                ):
        for base in database_content:
            reservoir = base.replace(".db", "")
            logger.info(f"Upload database for reservoir: {reservoir}")

            self.reader.check_files_before_reading(base, user_directory)

            logger.info(f"load the contents of {base}")
            df_Coordinates = self.reader.read_coord()
            df_inj = self.reader.read_inj()
            df_prod = self.reader.read_prod()
            df_HHT = self.reader.read_hht()
            df_HHT.replace(to_replace=0, value=DEFAULT_HHT, inplace=True)

            df_inj.Date = pd.to_datetime(df_inj.Date)#, dayfirst=True)
            df_prod.Date = pd.to_datetime(df_prod.Date)#, dayfirst=True)

            # upload reservoir_properties
            actual_reservoir_properties = {}
            if drainage_areas:
                actual_reservoir_properties = self.reservoir_properties.get(reservoir)
                if actual_reservoir_properties is None:
                    raise KeyError(f"There is no properties for reservoirs: {reservoir}")

            list_horizons = df_inj.Horizon.unique()
            # set of wells with coordinates
            set_wells = set(df_Coordinates.Well_number.unique())
            # create empty dictionary for result
            dict_reservoir_df = {}
            # Пустой датафрейм для добавления скважин, исключенных из расчета
            df_exception_wells = pd.DataFrame()

            logger.info(f"list of horizons for calculation: {list_horizons}")
            for horizon in list_horizons:
                logger.info(f"Start calculation reservoir: {reservoir} horizon: {horizon}")

                # select the history and HHT for this horizon
                df_inj_horizon = df_inj[df_inj.Horizon == horizon]

                # Считаем количество месяцев работы от даты расчета. Минимально необходимо 6 месяцев, если меньше, то не
                # учитывать нагнетательную скважину в расчете
                date_before_six_month = df_inj_horizon.Date.max() - relativedelta(months=6)
                count_months = df_inj_horizon[df_inj_horizon.Date >= date_before_six_month].groupby(
                               'Well_number', as_index=False).agg({'Date': 'count'})
                df_inj_wells_no_working_six_months = df_inj_horizon[
                    df_inj_horizon.Well_number.isin(list(count_months[count_months.Date < 7].Well_number.unique()))]
                df_inj_wells_no_working_six_months.sort_values(by=['Date'], ascending=False, inplace=True)
                df_inj_wells_no_working_six_months = df_inj_wells_no_working_six_months.drop_duplicates(
                    subset=['Well_number'])
                df_inj_wells_no_working_six_months['Exception_reason'] = 'последний период работы менее 6 месяцев'
                #df_exception_wells = df_exception_wells.append(df_inj_wells_no_working_six_months, ignore_index=True)
                df_exception_wells = pd.concat([df_exception_wells, df_inj_wells_no_working_six_months], sort=False)

                df_inj_horizon = df_inj_horizon[df_inj_horizon.Well_number.isin(
                                 list(count_months[count_months.Date >= 7].Well_number.unique()))]
                df_prod_horizon = df_prod[df_prod.Horizon == horizon]
                df_HHT_horizon = df_HHT[df_HHT.Horizon == horizon]
                del df_HHT_horizon["Horizon"]

                # upload dict of effective oil height
                dict_HHT: object = df_HHT_horizon.set_index('Well_number').to_dict('index')

                # create list of inj and prod wells
                list_inj_wells = list(set_wells.intersection(set(df_inj_horizon.Well_number.unique())))
                list_prod_wells = list(set_wells.intersection(set(df_prod_horizon.Well_number.unique())))
                list_wells = list_inj_wells + list_prod_wells

                # leave the intersections with df_Coordinates_horizon
                df_Coordinates_horizon = df_Coordinates[df_Coordinates.Well_number.isin(list_wells)]
                df_Coordinates_horizon["well marker"] = 0
                df_Coordinates_horizon.loc[df_Coordinates_horizon.Well_number.isin(list_inj_wells), "well marker"] = "inj"
                df_Coordinates_horizon.loc[df_Coordinates_horizon.Well_number.isin(list_prod_wells), "well marker"] = "prod"

                # check dictionary for this reservoir
                reservoir_reaction_distance = self.max_reaction_distance.get(reservoir, {reservoir: None})
                last_data = pd.Timestamp(np.sort(df_inj_horizon.Date.unique())[-1])

                logger.info("0. Calculate drainage and injection zones for all wells")
                df_drainage_areas = pd.DataFrame()
                if drainage_areas:
                    dict_properties = get_properties(actual_reservoir_properties, [horizon])
                    df_drainage_areas = calculate_zones(list_wells, list_prod_wells, df_prod_horizon, df_inj_horizon,
                                                        dict_properties, df_Coordinates, dict_HHT, DEFAULT_HHT)

                logger.info("I. Start calculation of injCelle for each inj well")
                df_injCells_horizon, \
                    df_inj_wells_without_surrounding = calculation_injCelle(list_inj_wells,
                                                                            df_Coordinates_horizon,
                                                                            df_inj_horizon,
                                                                            df_prod_horizon,
                                                                            reservoir_reaction_distance,
                                                                            dict_HHT,
                                                                            df_drainage_areas,
                                                                            drainage_areas,
                                                                            max_overlap_percent=self.max_overlap_percent,
                                                                            default_distance=MAX_DISTANCE,
                                                                            angle_verWell=self.angle_verWell,
                                                                            angle_horWell_T1=self.angle_horWell_T1,
                                                                            angle_horWell_T3=self.angle_horWell_T3,
                                                                            DEFAULT_HHT=DEFAULT_HHT)
                df_inj_wells_without_surrounding['Exception_reason'] = 'отсутствует окружение'
                df_exception_wells = pd.concat([df_exception_wells, df_inj_wells_without_surrounding], sort=False)
                # Sheet "Ячейки"
                df_injCells_horizon = calculation_coefficients(df_injCells_horizon, self.initial_coefficient,
                                                               dynamic_coefficient)
                list_inj_wells = list(df_injCells_horizon["Ячейка"].unique())

                logger.info("II. Calculate oil increment for each injection well")
                df_final_prod_well, dict_averaged_effects, dict_uncalculated_cells = \
                    calculate_oil_increment(df_prod_horizon, last_data, horizon, df_injCells_horizon)

                logger.info("III. Adaptation of uncalculated wells")
                df_final_inj_well, df_final_prod_well = final_adaptation_and_summation(df_prod_horizon, df_inj_horizon,
                                                                                       df_final_prod_well, last_data,
                                                                                       horizon, df_injCells_horizon,
                                                                                       dict_uncalculated_cells,
                                                                                       dict_averaged_effects,
                                                                                       self.conversion_factor)
                logger.info("IV. Forecast")
                df_forecasts = calculate_forecast(list_inj_wells, df_final_inj_well, df_injCells_horizon,
                                                  horizon, data_end_of_pred)

                dict_df = {f"Ячейки_{horizon}": df_injCells_horizon, f"Прирост доб_{horizon}": df_final_prod_well,
                           f"Прирост наг_{horizon}": df_final_inj_well, f"Прогноз наг_{horizon}": df_forecasts}

                dict_reservoir_df.update(dict_df)

            # финальная обработка словаря перед загрузкой в эксель
            df_exception_wells = df_exception_wells.drop_duplicates(subset=['Well_number'])
            df_exception_wells = df_exception_wells.drop(labels=[
                'Date', 'Status', 'Choke_size', 'Pbh', 'Pkns', 'Pkust', 'Pwh', 'Pbf', 'Pr', 'Time_injection'],
                axis=1).reset_index().drop(labels=['index'], axis=1)
            # dict_reservoir_df.update(df_exception_wells)
            dict_reservoir_df = merging_sheets(df_injCells_horizon, df_forecasts, dict_reservoir_df, df_exception_wells, self.conversion_factor)

            # Start print in Excel for one reservoir
            app1 = xw.App(visible=False)
            new_wb = xw.Book()

            for key in dict_reservoir_df.keys():
                if f"{key}" in new_wb.sheets:
                    xw.Sheet[f"{key}"].delete()
                new_wb.sheets.add(f"{key}")
                sht = new_wb.sheets(f"{key}")
                sht.range('A1').options().value = dict_reservoir_df[key]

            new_wb.save(OUT_NAME + f"\\{reservoir}.xlsx")
            app1.kill()
