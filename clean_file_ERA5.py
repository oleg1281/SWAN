import xarray as xr

# 1️⃣ Открываем файл ERA5
file = "c:/NOAA/SWAN_files/batym/wind_ERA5_20250301.000000_20251031.180000.nc"
ds = xr.open_dataset(file)

# 2️⃣ Посмотрим, какие переменные есть
print(ds)

# 3️⃣ Удаляем ненужные переменные
# Например, оставляем только нужные:
vars_to_keep = ['10m_u_component_of_wind', '10m_v_component_of_wind']  # замени на свои
ds = ds[vars_to_keep]

# 4️⃣ Переименовываем координату latitude в lat и longitude в lon
ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})

# 5️⃣ Сохраняем в новый файл
ds.to_netcdf("путь_к_новому_файлу.nc")
