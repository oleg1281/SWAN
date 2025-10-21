from datetime import datetime, timedelta
import re
import numpy as np
import xarray as xr
from pathlib import Path
import subprocess
from netCDF4 import Dataset, date2num
import os

# Создание файла ветра с файла предикт модели GRAPHCAST и автоматическое добавление данных с NOAA перед этим Файлом для розагрева модели сван

# Границы
ini_lon = 9
end_lon = 31
ini_lat = 53
end_lat = 67

lat_step = 0.1
lon_step = 0.1

ini_lon_bat = ini_lon-1
end_lon_bat = end_lon+1
ini_lat_bat = ini_lat-1
end_lat_bat = end_lat+1


predict_file_output = "ERA5_SWAN_fala_20250301.000000_20251031.180000.nc"

#output_file_wind = f"wind_SWAN_{ini_lon_bat}_{end_lon_bat}_{ini_lat_bat}_{end_lat_bat}.dat"    # готовый файл ветра

# Папки
#predict_folder_input = Path(r"/mnt/mewo/Postprocesing/Oleh Bedenok/GRAPHCAST/NOAA/predict_noaa")
#data_folder_input = Path(r"/mnt/mewo/Postprocesing/Oleh Bedenok/GRAPHCAST/NOAA/data_NOAA1")
output_file_hsig_noheader = "ERA5_hsig_20250301.000000_20251031.180000_noheader.txt"

folder_output_RUN = Path(r"c:\NOAA\SWAN_files\RUN")
folder_output_PREDICT = Path(r"c:\NOAA\SWAN_files\batym")
#folder_output_SWANFILES = Path(r"/mnt/mewo/Postprocesing/Oleh Bedenok/GRAPHCAST/NOAA/SWAN_files")

timestep = "6 HR"
out_file_swn = "mycase.SWN"


input_txt = folder_output_RUN / output_file_hsig_noheader
output_nc = os.path.join(folder_output_PREDICT, predict_file_output)
#output_nc1 = os.path.join(folder_output_PREDICT, f"SWAN_predict_fala_{s_date}_{end_date}.nc")

lons = np.arange(ini_lon, end_lon + lon_step/2, lon_step)
lats = np.arange(ini_lat, end_lat + lat_step/2, lat_step)
nx, ny = len(lons), len(lats)

# === Чтение данных ===
values = []
with open(input_txt, 'r') as f:
    for line in f:
        #print('--', line.split(), '--')
        if line.strip() == '':
            continue
        for val in line.split():
            try:
                num = float(val)
                # значения <=0 заменяем на 0
                if num <= 0:
                    num = 0
                values.append(num)
            except ValueError:
                continue

values = np.array(values)
# === Определяем количество временных интервалов ===
grid_size = nx * ny
nt = int(np.ceil(len(values) / grid_size))

# === Формируем массив для NetCDF (time, lat, lon) ===
data_array = np.zeros((nt, ny, nx), dtype=np.float32)
#assert len(values) == 1931982, 'Неправильный txt файл'
for t in range(nt):
    start_idx = t * grid_size
    end_idx = start_idx + grid_size
    chunk = values[start_idx:end_idx]
    # если последняя часть меньше полного слоя, дополняем нулями
    #if len(chunk) < grid_size:
    #   chunk = np.pad(chunk, (0, grid_size - len(chunk)), 'constant', constant_values=0)
    # Заполняем массив
    data_array[t, :, :] = chunk.reshape((ny, nx))

# === Создание NetCDF ===
ncfile = Dataset(output_nc, 'w', format='NETCDF4')

ncfile.createDimension('time', nt)
ncfile.createDimension('lat', ny)
ncfile.createDimension('lon', nx)

time_var = ncfile.createVariable('time', 'f8', ('time',))
lat_var = ncfile.createVariable('lat', 'f8', ('lat',))
lon_var = ncfile.createVariable('lon', 'f8', ('lon',))

#Создаем список дат для файла nc
start_d = datetime(2025, 3, 1, 00, 00)
times = [start_d + timedelta(hours=6 * i) for i in range(nt)]
# === указываем формат времени CF ===
time_units = 'hours since 2025-10-14 00:00'
time_calendar = 'gregorian'

lat_var[:] = sorted(lats, reverse=True)
lon_var[:] = lons
time_var[:] = date2num(times, units=time_units, calendar=time_calendar)
time_var.units = time_units
time_var.calendar = time_calendar
hs_var = ncfile.createVariable('hs', 'f4', ('time', 'lat', 'lon'), fill_value=0)
hs_var[:, :, :] = data_array
hs_var.units = 'm'
hs_var.long_name = 'Significant wave height'

ncfile.close()
print(f"NetCDF файл {output_nc} успешно создан.")