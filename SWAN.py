from datetime import datetime, timedelta
import re
import numpy as np
import xarray as xr
from pathlib import Path
import subprocess
from netCDF4 import Dataset, date2num

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

output_file_wind = f"wind_SWAN_{ini_lon_bat}_{end_lon_bat}_{ini_lat_bat}_{end_lat_bat}.dat"    # готовый файл ветра

predict_file_input = "pred_NOAA_2025-08-01_12h00m_2025-08-01_18h00m.nc"
predict_file_output = predict_file_input
# Папки
predict_folder_input = Path(r"z:\NOAA\predict_noaa")
data_folder_input = Path(r"z:\NOAA\data_NOAA1")

folder_output_RUN = Path(r"c:\NOAA\SWAN_files\RUN")
folder_output_PREDICT = Path(r"z:\NOAA\predict_swan")
folder_output_SWANFILES = Path(r"c:\NOAA\SWAN_files")

timestep = "6 HR"
out_file_swn = "mycase.swn"

r = re.search(r"(\d{4})-(\d{2})-(\d{2})_(\d{2})h(\d{2})m", predict_file_input)

y, M, d, h, m = map(int, r.groups())
td = datetime(y,M,d,h,m)

date_72h = td - timedelta(hours=60)
date_66h = td - timedelta(hours = 54)
date_60h = td - timedelta(hours = 48)
date_54h = td - timedelta(hours=42)
date_48h = td - timedelta(hours=36)
date_42h = td - timedelta(hours=30)
date_36h = td - timedelta(hours=24)
date_30h = td - timedelta(hours=18)
date_24h = td - timedelta(hours=12)
date_18h = td - timedelta(hours=6)
date_12h = td - timedelta(hours=0)
date_6h = td + timedelta(hours=6)

start_date = date_72h.strftime("%Y%m%d.%H%M00")
end_date = date_6h+timedelta(hours=300)
end_date = end_date.strftime("%Y%m%d.%H%M00")

s_date = (td + timedelta(hours=12)).strftime("%Y%m%d.%H%M00")

a1 = date_72h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_66h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
a2 = date_66h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_60h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
a3 = date_60h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_54h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
a4 = date_54h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_48h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
a5 = date_48h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_42h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
a6 = date_42h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_36h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
a7 = date_36h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_30h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
a8 = date_30h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_24h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
a9 = date_24h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_18h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
a10 = date_18h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_12h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"

a11 = date_12h.strftime("NOAA_%Y-%m-%d_%Hh%Mm_")+date_6h.strftime("%Y-%m-%d_%Hh%Mm")+".nc"
aall = [a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11]

ds_list = []
for fp in aall:
    ds = xr.open_dataset(data_folder_input / fp)
    # Берём только переменные ветра
    ds_wind = ds[["10m_u_component_of_wind", "10m_v_component_of_wind"]]

    # Если нужно только первый временной срез (для первых 10 файлов)
    if fp != a11:
        ds_wind = ds_wind.isel(time=0)

    ds_list.append(ds_wind)

# Добавляем прогноз
ds_pred = xr.open_dataset(predict_folder_input / predict_file_input)
ds_pred_wind = ds_pred[["10m_u_component_of_wind", "10m_v_component_of_wind"]]
ds_list.append(ds_pred_wind)

ds_list_clean = []

for ds in ds_list:
    # берём только данные ветра
    ds_wind = ds[["10m_u_component_of_wind", "10m_v_component_of_wind"]].copy()

    # убираем координату datetime, если она есть
    if "datetime" in ds_wind.coords:
        ds_wind = ds_wind.drop_vars("datetime")

    ds_list_clean.append(ds_wind)

# соединяем по времени
ds_combined = xr.concat(ds_list_clean, dim="time")

# Сохраняем
ds_combined.to_netcdf(folder_output_SWANFILES / predict_file_output)

#ds = ds_combined.sel(lat=slice(ini_lat, end_lat), lon=slice(ini_lon, end_lon))
ds = ds_combined.sel(lat=slice(ini_lat_bat, end_lat_bat), lon=slice(ini_lon_bat, end_lon_bat))

U = ds["10m_u_component_of_wind"].squeeze().sortby("lat", ascending=True).sortby("lon").values
V = ds["10m_v_component_of_wind"].squeeze().sortby("lat", ascending=True).sortby("lon").values

#U = ds["10m_u_component_of_wind"].squeeze().sortby("lat", ascending=True).sortby("lon").values
#V = ds["10m_v_component_of_wind"].squeeze().sortby("lat", ascending=True).sortby("lon").values

U = np.transpose(U, (2, 0, 1))   # меняем местами оси lat и lon
V = np.transpose(V, (2, 0, 1))   # меняем местами оси lat и lon

#print(U.shape)
#print(V.shape)

out_file = folder_output_RUN / output_file_wind
with open(out_file,"w",encoding="utf-8") as f:
    for k in range(U.shape[0]):
        for row in U[k]:
            f.write(" ".join(f"{x:.6f}" for x in row) + "\n")
        for row in V[k]:
            f.write(" ".join(f"{x:.6f}" for x in row) + "\n")

print(f"Файл {out_file} записан.")

# сортируем список
lons_wind = np.sort(ds["lon"].values)
lats_wind = np.sort(ds["lat"].values)

# считаем разницу между соседними точками
dx_array_wind = np.diff(lons_wind)
dy_array_wind = np.diff(lats_wind)
# средний шаг
dx_wind = np.mean(dx_array_wind)
dy_wind = np.mean(dy_array_wind)

xlenc_INPGRID_wind = lons_wind[-1] - lons_wind[0]
ylenc_INPGRID_wind = lats_wind[-1] - lats_wind[0]

nx_wind = round(xlenc_INPGRID_wind/dx_wind)
ny_wind = round(ylenc_INPGRID_wind/dy_wind)


#xlenc = end_lon - ini_lon
#ylenc = end_lat - ini_lat

#x_point = len(ds.lon.values)
#y_point = len(ds.lat.values)

#dxinp = round((end_lon - ini_lon) / (x_point - 1), 8)
#dyinp = round((end_lat - ini_lat) / (y_point - 1), 8)

#print(f'INPGRID WIND REGULAR {ini_lon} {ini_lat} 0 {ds["10m_u_component_of_wind"].sizes["lon"] - 1} {ds["10m_u_component_of_wind"].sizes["lat"] - 1} {dxinp} {dyinp} NONSTATION  {20250304.000000} {6} HR {20250101.050000}')
#print(f"READINP  WIND 1 '{output_file_wind}' 3 0 FREE")
#print("\n")

#------------------------------создали файл ветра из файла предикт графкаста и добавили сначала перед ним ветер за 72 часа из БД ноа ---------------------------------------------------
#-----------------------------теперь создаем файл батометрии с общего файла z:/NOAA/SWAN_files/GEBCO_2025_sub_ice.nc и координат
#---------------------и сохраняем его в z:\NOAA\SWAN_files\RUN

# Название выходного файла батометрии
output_file_batym = f"bat_SWAN_{ini_lon_bat}_{end_lon_bat}_{ini_lat_bat}_{end_lat_bat}.dat"

# Загружаем NetCDF батометрии
depth = xr.open_dataset(r'z:/NOAA/SWAN_files/GEBCO_2025_sub_ice.nc')

# Вырезаем область 8 32 52 68
ds_bat = depth.sel(lat=slice(ini_lat_bat, end_lat_bat), lon=slice(ini_lon_bat, end_lon_bat))

# сортируем список lon и lat cетки 8 32 52 68
lons_bat = np.sort(ds_bat["lon"].values)
lats_bat = np.sort(ds_bat["lat"].values)

# считаем разницу между соседними точками
dx_array_bat = np.diff(lons_bat)
dy_array_bat = np.diff(lats_bat)

# средний шаг
dx_bat = np.mean(dx_array_bat)
dy_bat = np.mean(dy_array_bat)

xlenc_CGRID = end_lon - ini_lon
ylenc_CGRID = end_lat - ini_lat

xlenc_INPGRID_bat = lons_bat[-1] - lons_bat[0]
ylenc_INPGRID_bat = lats_bat[-1] - lats_bat[0]

nx_bat = round(xlenc_INPGRID_bat/dx_bat)
ny_bat = round(ylenc_INPGRID_bat/dy_bat)

# Берём elevation
if "elevation" in ds_bat:
    depth_values = ds_bat["elevation"].values
else:
    raise ValueError("В файле нет переменной 'elevation'!")

# Меняем знак (чтобы глубины стали положительные)
depth_values = -depth_values
depth_values = np.maximum(depth_values, 0)

#print("\n")
#print(f'CGRID REGULAR {ini_lon} {ini_lat} 0 {xlenc_CGRID} {ylenc_CGRID} {xlenc_CGRID*10} {ylenc_CGRID*10} CIRCLE 72 0.0345 1.00  34')
#print(f'INPGRID BOTTOM REGULAR {lons_bat[0]} {lats_bat[0]} 0 {nx_bat} {ny_bat} {dx_bat} {dy_bat}')
#print(f"READINP BOTTOM 1 '{output_file_batym}' 3 0 FREE")
#print("\n")

out_file_bat = folder_output_RUN / output_file_batym
with open(out_file_bat, "w") as f:
    for row in depth_values:       # перебор строк (широты)
        line = " ".join(f"{val:.2f}" for val in row)  # числа через пробел
        f.write(line + "\n")

print(f"Файл '{out_file_bat}' успешно записан.")

#-----------------батометрию сохранили -----------------------------------------------------------------------------------------------
#__________________начинаем собирать файл swn и запускаем модель-----------------------------------------

output_file_hsig_header = f"Graphcast_hsig_{start_date}_{end_date}_header.txt"
output_file_hsig_noheader = f"Graphcast_hsig_{start_date}_{end_date}_noheader.txt"

def swn_file(start_date, end_date, output_file_wind):
    # --- Параметры для шаблона ---
    project_name = f"Baltyk"
    run_name = "Run1"

    # --- Формируем текст ---
    swan_input = f"""PROJECT '{project_name}' '{run_name}'
MODE DYNAMIC TWODIMENSIONAL
$
SET   NAUTICAL
COORDINATES SPHERICAL
SET   DEPMIN=1.0
NUMERIC STOPC 0.005 0.05 0.005 99.0 NONSTAT 50
SET LEVEL 0
$SET MAXERR=1
$
$CGRID REGULAR 9 53 0 22 14 107 68 CIRCLE 120 0.0345 1.00 34        221 141
CGRID REGULAR {ini_lon} {ini_lat} 0 {xlenc_CGRID} {ylenc_CGRID} {int(xlenc_CGRID / lon_step)} {int(ylenc_CGRID / lat_step)} CIRCLE 72 0.0345 1.00  34
$
INPGRID BOTTOM REGULAR {lons_bat[0]} {lats_bat[0]} 0 {nx_bat} {ny_bat} {dx_bat} {dy_bat}
READINP BOTTOM 1 '{output_file_batym}' 3 0 FREE
$
INPGRID WIND REGULAR {lons_wind[0]} {lats_wind[0]} 0 {nx_wind} {ny_wind} {dx_wind} {dy_wind} NONSTATION {start_date} {timestep} {end_date}
READINP  WIND 1 '{output_file_wind}' 3 0 FREE
$
PROP BSBT
GEN3 KOMEN
INIT DEFAULT
$
BLOCK 'COMPGRID' NOHEADER '{output_file_hsig_noheader}' LAYOUT 1 HSIGN OUTPUT 0 {timestep}
BLOCK 'COMPGRID' HEADER '{output_file_hsig_header}' LAYOUT 1 HSIGN OUTPUT 0 {timestep}
$
COMPUTE NONSTAT {start_date} {timestep} {end_date}
$
STOP
"""

    # --- Сохраняем в файл swn в RUN---
    with open(folder_output_RUN / out_file_swn, "w") as f:
        f.write(swan_input)
    print(f"Файл {folder_output_RUN / out_file_swn} успешно записан.")

    # --- Сохраняем в файл swn в SWAN_files---
    s_file = "swn_" + start_date + "_" + out_file_swn
    with open(folder_output_SWANFILES / s_file, "w") as f:
        f.write(swan_input)
    print(f"Файл {folder_output_SWANFILES / s_file} успешно записан.")

swn_file(start_date, end_date, output_file_wind)

#cmd = ('wsl -d Ubuntu-22.04 bash -c "cd /home/obedenok/swan/swan4151_clean/test && ../swan.exe < mycase.swn 2>&1 | tee run.log"')
print("Запускаем SWAN")

#subprocess.run(cmd, shell=True, check=True)

# Название входного файла без расширения (Docker образ ожидает переменную INPUT)
input_file = "mycase"
# Папка на Windows, где лежат файлы SWAN (пример)
windows_path = r"c:\NOAA\SWAN_files"
cmd = [
    "docker", "run", "--rm",
    "-v", f"{windows_path}:/data",   # монтируем папку
    "-e", f"INPUT={input_file}",      # передаём имя входного файла
    "deltares/swan:latest"
]

print("Запускаем SWAN через Docker")
subprocess.run(cmd, check=True)

#---------------------- Теперь с выходного файла прогноза output_file_hsig_noheader делаем файл nc

input_txt = r"c:\NOAA\SWAN_files\RUN\Graphcast_hsig_20250730.000000_20250814.060000_noheader.txt"
output_nc = rf"c:\NOAA\SWAN_files\RUN\SWAN_predict_fala_{s_date}_{end_date}.nc"

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
assert len(values) == 1931982, 'Неправильный txt файл'
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
lat_var = ncfile.createVariable('lat', 'f4', ('lat',))
lon_var = ncfile.createVariable('lon', 'f4', ('lon',))

#Создаем список дат для файла nc
start_d = date_72h
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
