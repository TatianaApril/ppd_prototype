import os

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQL_NAME = path + "\\database"
OUT_NAME = path + "\\output"
INPUT_NAME = path + "\\input"

prefix = '_OUTPUT'

HOURS_IN_DAY = 24
DAYS_IN_YEAR = 365
MONTHS_IN_YEAR = 12

AVG_DAYS_IN_YEAR = 365.2425
AVG_DAYS_IN_MONTH = AVG_DAYS_IN_YEAR / MONTHS_IN_YEAR
INF_COLUMNS_NUMBER = 2


class StringConstants:
    FIELD = 'Месторождение'
    WELL = '№ скв.'
    LAYER = 'Пласт'
    SUBORGANIZATION = 'ДО'
    WELLS_GROUP = 'Куст'
    PREPARATION_OBJECT = 'Объект подготовки'
    TOTAL = 'Итого'
    DATE = 'Дата'
    OIL_PRODUCTION = 'Добыча нефти'
    LIQUID_PRODUCTION = 'Добыча жидкости'
    PUMPING = 'Закачка, тыс.м3'
    GENERAL_INJECTION = 'Общая закачка'
    AVERAGE_OPERATING_FUND = 'СДФ доб. скважин, шт.'
    OPERATING_FACTOR = 'КЭ доб. скважин, д.ед.'
    GAS_PRODUCTION = 'Добыча ПНГ, млн.м3'
    OPERATING_FUND_MONTH = 'Действующий фонд доб. скважин на конец периода, шт.'
    WELLS_IN_MONTH = 'Прибытие доб скважин, скв'
    WELLS_OUT_MONTH = 'Выбытие доб. скважин, скв'
    WELLS_OUT_PPD = 'Перевод доб. скважин в ППД, скв.'
    WELLS_OUT_UNUSED = 'Выбытие доб. скважин в бездействие, скв.'
    WELLS_OUT_ZBS = 'Выбытие под ЗБС, шт.'
    WELLS_OUT_TO_RETURN = 'Выбытие под ВОЗВРАТ, шт.'
    WELL_TYPE_OIL = 'неф'
    WELL_TYPE_INJ = 'наг'
    FUND_STATE_WORK = 'раб.'
    FUND_STATE_STOP = 'ост.'
    NONAME = 'Noname'
    DEFAULT_OUTPUT_PREFIX = '_OUTPUT'
    BF_OUTPUT_PREFIX = 'BF_OUTPUT'
    DEFAULT_OUTPUT_JSON_PREFIX = 'DATA_FOR_GRAPHS'
    EXTENSION = '.xlsx'
    EXTENSION_JSON = '.json'
    ACCUMULATE_TIME = 'accumulate_time'
    FICTITIOUS_WELLS = 'Фиктивные скважины'
    FICTITIOUS_PREPARATION_OBJECT = 'Фиктивная_ДНС_'
    UEP = 'БРД'  # блок разведки и добычи
    VALUE = 'value'
    KEY = 'key'
    SUM = 'sum'
    CUMULATIVE_TIME = 'CumulativeTime'
    INJECTION = 'Закачка агента, м3 за месяц'
    TERRA_FILE = 'Терра'
    UNNAMED = 'Unnamed'
    TERRA_DATA = 'terra'
    MER_DATA = 'mer'
    PRODUCT = 'Product'
    PICKLE_FOR_SUMMATOR = 'Data_for_summator'
    MONTHLY_INDICATORS = 'MonthlyIndicators'
    GTM = 'gtm'


class DO:
    MURAVLEN = 'ГПН-Муравленко'
    NNG = 'ГПН-ННГ'
    MESSOYAH = 'Мессояханефтегаз'
    ZAPOLYAR = 'ГПН-Заполярье'
    YAMAL = 'ГПН-Ямал'
    VOSTOK = 'ГПН-Восток'
    ORENBURG = 'ГПН-Оренбург'
    HANTOS = 'ГПН-Хантос'
    MERETOYAH = 'Меретояханефтегаз'
    SLAVNEFT_MNG = 'Славнефть-Мегионнефтегаз'
    TP_PALYAN = 'ТП_(Пальян+Салым)'
    _all = ['ГПН-Муравленко', 'ГПН-ННГ', 'Мессояханефтегаз', 'ГПН-Заполярье', 'ГПН-Ямал', 'ГПН-Восток', 'ГПН-Оренбург',
            'ГПН-Хантос', 'Меретояханефтегаз', 'Славнефть-Мегионнефтегаз', 'ТП_(Пальян+Салым)']


class Fields:
    fields_MURAVLEN = ['Валынтойское', "Восточно-Пякутинское", "Вынгаяхинское", "Еты-Пуровское", "Крайнее",
                       "Малопякутинское", "Муравленковское", "Пякутинское", "Романовское", "Северо-Пямалияхское",
                       "Северо-Янгтинское", 'Сугмутское', 'Суторминское', "Умсейское+Южно-Пурпейское"
                       ]
    fields_NNG = ['Воргенское', 'Вынгапуровское', 'Западно-Чатылькинское', "Западно-Ноябрьское", 'Карамовское', 'Новогоднее',
                  'Отдельное', 'Пограничное', 'Равнинное', 'Спорышевское', 'Средне-Итурское', "Стакановское",
                  'Холмистое', 'Холмогорское', 'Чатылькинское', "Южно-Удмуртское", 'Ярайнерское'
                  ]
    fields_MESSOYAH = ['Восточно-Мессояхское', 'Западно-Мессояхское', "Пякяхинское"]
    fields_ZAPOLYAR = ["Бованенковское", "Ен-Яхинское", "Западно-Таркосалинское", "Песцовое", "Уренгойское",
                       "Чаяндинское", "Ямбургское"]
    fields_YAMAL = ["Ближненовопортовское", "Новопортовское", "ПСП Мыс Каменный участок"]
    fields_VOSTOK = ['Арчинское', 'Восточно-Мыгинское', 'Восточно-Солоновское', 'Западно-Лугинецкое', 'Западно-Солоновское',
                     'Крапивинское', 'Кулгинское', "Мыгинское", 'Нижнелугинецкое', "Осиновое", "Северо-Таволгинское",
                     "Северо-Шингинское локальное поднятие", "Смоляное", "Солоновское", "Тунжинское локальное поднятие",
                     'Урманское', 'Шингинское', 'Южно-Табаганское'
                     ]
    fields_ORENBURG = ['Балейкинское', 'Землянское', 'Капитоновское', 'Новозаринское', 'Новосамарское',
                       'Оренбургское', 'Рощинское', "Уранская площадь", 'Царичанское+Филатовское', "Центрально-Уранское", 'Ягодное'
                       ]
    fields_HANTOS = ["Восточно-Кимяхинское", "Зимнее",  'Им. Александра Жагрина', 'Малоюганское',
                     'Орехово-Ермаковское', 'Приобское', "Северо-Вайское", 'Северо-Ингольское', "Средневайское", "Южное",
                     'Южно-Киняминское']
    fields_MERETOYAH = ['Меретояхинское', 'Северо-Самбургское', 'Тазовское']
    fields_SLAVNEFT_MNG = ['Аганское', 'Аригольское', 'Ачимовское', 'Ватинское', 'Восточно-Охтеурское', 'Западно-Асомкинское',
                           'Западно-Усть-Балыкское', 'Западно-Чистинное', 'Ининское', 'Кетовское', 'Луговое',
                           "Максимкинское", 'Мегионское', 'Мыхпайское', 'Ново-Покурское', 'Островное', 'Покамасовское',
                           "Полевое", "Северо-Нагуньское", 'Северо-Ореховское', 'Северо-Островное', 'Северо-Покурское', 'Тайлаковское',
                           'Узунское', 'Чистинное', 'Южно-Аганское', 'Южно-Островное', 'Южно-Покамасовское', "Южно-Юганское"
                           ]
    fields_TP_PALYAN = ['Красноленинское', "Пальяновское ТРИЗ", "Солизм"]


class DO_dictionary:
    dict = {
        DO.MURAVLEN: Fields.fields_MURAVLEN,
        DO.NNG: Fields.fields_NNG,
        DO.MESSOYAH: Fields.fields_MESSOYAH,
        DO.ZAPOLYAR: Fields.fields_ZAPOLYAR,
        DO.YAMAL: Fields.fields_YAMAL,
        DO.VOSTOK: Fields.fields_VOSTOK,
        DO.ORENBURG: Fields.fields_ORENBURG,
        DO.HANTOS: Fields.fields_HANTOS,
        DO.MERETOYAH: Fields.fields_MERETOYAH,
        DO.SLAVNEFT_MNG: Fields.fields_SLAVNEFT_MNG,
        DO.TP_PALYAN: Fields.fields_TP_PALYAN
    }

