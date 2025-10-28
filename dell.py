import pandas as pd
import xarray as xr
from pathlib import Path

excel_file = Path("C:/Users/obedenok/PycharmProjects/SWAN/report_tables_.xlsx")


xls = pd.ExcelFile(excel_file)

data_vars = {}

for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # Преобразуем дату + час в datetime
    df['datetime'] = pd.to_datetime(df['date'] + '/2025 ' + df['time'].astype(str) + ':00', format='%d/%m/%Y %H:%M')
    #print(df['datetime'])

    # Уберем столбцы date и time, оставим только численные переменные
    df_numeric = df.drop(columns=['date', 'time', 'datetime'])
    #print(sheet_name)

    # Добавим в data_vars, чтобы потом создать Dataset
    # Используем sheet_name как координату 'sheet'
    data_vars[sheet_name] = (('time', 'variable'), df_numeric.values)
    print(data_vars[sheet_name])

# Создаём Dataset
# Координаты времени будем использовать первую колонку datetime каждого листа (все листы должны быть одинаковой длины)
time = pd.to_datetime(pd.read_excel(xls, sheet_name=xls.sheet_names[0])['date'] + ' ' +
                      pd.read_excel(xls, sheet_name=xls.sheet_names[0])['time'].astype(str) + ':00', format='%d/%m %H:%M')

dataset = xr.Dataset(
    data_vars={sheet: (('time', 'variable'), pd.read_excel(xls, sheet_name=sheet).drop(columns=['date','time']).values)
               for sheet in xls.sheet_names},
    coords={'time': time}
)

# Сохраняем в NetCDF
dataset.to_netcdf("report.nc")
print("NetCDF создан: report.nc")
