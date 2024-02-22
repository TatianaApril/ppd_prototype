import pandas as pd
import yaml
import os
import warnings

from pydantic import ValidationError
from loguru import logger


from Schema import Validator_Coord, Validator_inj, Validator_prod, \
    Validator_HHT, dict_prod_column, dict_inj_column, dict_coord_column, dict_HHT_column
from Utility_function import df_Coordinates_prepare, get_period_of_working_for_calculating, history_prepare
from gui.constants import path, INPUT_NAME

warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None  # default='warn'

# Parameters
min_length_horWell = 150  # minimum length between points T1 and T3 to consider the well as horizontal
time_work_min = 0  # minimum well's operation time per month, days


class Reader:
    def __init__(self,
                 MONTHS_OF_WORKING: int,
                 HAS_WORKING_HOURS_FOR_THE_LAST_YEAR: bool
                 ):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        logger.info(f"path:{self.dir_path}")

        self.MONTHS_OF_WORKING = MONTHS_OF_WORKING
        self.HAS_WORKING_HOURS_FOR_THE_LAST_YEAR = HAS_WORKING_HOURS_FOR_THE_LAST_YEAR


    def read_yml(self):
        """Read yml data from the root + conf_files folder"""
        logger.info(f"upload conf_files")
        initial_coefficient = pd.DataFrame(self.get_file('\\conf_files/initial_coefficient.yml'))
        reservoir_properties = self.get_yml('\\conf_files/reservoir_properties.yml')
        max_reaction_distance = self.get_yml('\\conf_files/max_reaction_distance.yml')
        parameters = self.get_yml('\\conf_files/parameters.yml')

        if not parameters.values():
            parameters = [0, 0, 0, 0, 0, 0, 0]

        return initial_coefficient, reservoir_properties, max_reaction_distance, parameters


    def get_file(self, file: str):
        with open(path + file) as f:
            return yaml.safe_load(f)


    def get_yml(self, yaml_file: str):
        with open(path + yaml_file, 'rt', encoding='utf8') as yml:
            return yaml.load(yml, Loader=yaml.Loader)


    def check_files_before_reading(self, csv_name: str, input_directory: str=None):
        """Checking if folder with input file is not empty"""

        if input_directory is not None:
            self.input_path = str(input_directory)
        else:
            self.input_path = INPUT_NAME + '\\' + csv_name
        input_content = os.listdir(self.input_path)

        logger.info(f"check the contents of {csv_name}")
        if "Техрежим доб.csv" not in input_content:
            raise FileExistsError("Техрежим доб.csv")
        elif "Техрежим наг.csv" not in input_content:
            raise FileExistsError("Техрежим нагн.csv")
        elif "Координаты.xlsx" not in input_content:
            raise FileExistsError("Координаты.xlsx")
        elif "Толщины" not in input_content:
            raise FileExistsError("no folder Толщины")
        else:
            logger.info(f"check the contents of folder Толщины")
            folder_path = self.input_path + "\\Толщины"
            folder_content = os.listdir(path=folder_path)
            if folder_content:
                logger.info(f"objects: {len(folder_content)} ")
            else:
                raise FileExistsError("no files!")


    def read_coord(self) -> pd.DataFrame:
        """Load and prepare df coordinates"""

        logger.info(f"load Координаты.xlsx")
        df_coordinates = pd.read_excel(self.input_path + "\\Координаты.xlsx")
        df_coordinates.columns = dict_coord_column.values()

        logger.info(f"validate file")
        try:
            Validator_Coord(df_dict=df_coordinates.to_dict(orient="records"))
        except ValidationError as e:
            print(e)

        reservoir = df_coordinates.Reservoir_name.unique()
        if len(reservoir) > 1:
            raise ValueError(f"Non-unique field name: {reservoir}")

        logger.info(f"file preparation")
        df_coordinates = df_coordinates.astype({'Well_number': 'str'})
        df_coordinates = df_Coordinates_prepare(df_coordinates, min_length_horWell)
        return df_coordinates


    def read_inj(self) -> pd.DataFrame:
        """Load and prepare injection csv"""

        logger.info(f"load Техрежим наг.csv")
        df_inj = self.read_csv("\\Техрежим наг.csv")
        df_inj = df_inj[list(dict_inj_column.keys())]
        df_inj.columns = dict_inj_column.values()
        df_inj = self.prepare_data(df_inj, 'inj')
        return df_inj


    def read_prod(self) -> pd.DataFrame:
        """Load and prepare prodaction csv"""

        logger.info(f"load Техрежим доб.csv")
        df_prod = self.read_csv("\\Техрежим доб.csv")
        df_prod = df_prod[list(dict_prod_column.keys())]
        df_prod.columns = dict_prod_column.values()
        df_prod = self.prepare_data(df_prod, 'prod')
        return df_prod


    def read_hht(self) -> pd.DataFrame:
        """Load and prepare hht excel files"""

        logger.info(f"load Толщины")
        folder_path = self.input_path + "\\Толщины"
        folder_content = os.listdir(path=folder_path)
        df_hht = pd.DataFrame()
        for file in folder_content:
            name_horizon = file.replace('.xlsx', '')
            logger.info(f"load object: {name_horizon}")
            df = pd.read_excel(folder_path + f"\\{file}", header=1).fillna(0.1)
            df.columns = dict_HHT_column.values()
            df['Horizon'] = name_horizon
            df_hht = pd.concat([df_hht, df])

        logger.info(f"validate file")
        try:
            Validator_HHT(df_dict=df_hht.to_dict(orient="records"))
        except ValidationError as e:
            print(e)
        return df_hht


    def read_csv(self, file: str) -> pd.DataFrame:
        """Just normaly reading csv"""
        df = pd.read_csv(self.input_path + file, encoding='mbcs', sep=";",
                         index_col=False, decimal=',', low_memory=False).fillna(0)
        return df


    def prepare_data(self, df: pd.DataFrame, key: str) -> pd.DataFrame:
        """Validate and parse history for csv files"""

        df.Date = pd.to_datetime(df.Date, dayfirst=True)
        df = get_period_of_working_for_calculating(df, self.MONTHS_OF_WORKING)

        logger.info(f"validate file")
        try:
            if key == 'inj':
                Validator_inj(df_dict=df.to_dict(orient="records"))
            else:
                Validator_prod(df_dict=df.to_dict(orient="records"))
        except ValidationError as e:
            print(e)

        logger.info(f"file preparation")
        df = history_prepare(df,
                             type_wells=key,
                             time_work_min=time_work_min,
                             HAS_WORKING_HOURS_FOR_THE_LAST_YEAR=self.HAS_WORKING_HOURS_FOR_THE_LAST_YEAR)

        return df
