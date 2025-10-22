# код для очистки файлов ERA5 от ненужных переменных и\или переименования их

import xarray as xr

# 1️⃣ Открываем файл ERA5
file = "c:/NOAA/SWAN_files/batym/wind_ERA5_20250301.000000_20251031.180000.nc"
ds = xr.open_dataset(file)

# 3️⃣ Удаляем ненужные координаты expver и number (если они есть)
for coord in ["expver", "number"]:
    if coord in ds.coords:
        ds = ds.drop_vars(coord)
        print(f"❌ Удалена координата: {coord}")

# 3️⃣ Оставляем только нужные переменные
vars_to_keep = ['u10', 'v10']  # правильные имена
ds = ds[vars_to_keep]

# 4️⃣ Переименовываем координаты
ds = ds.rename({'latitude': 'lat', 'longitude': 'lon', 'valid_time': 'time'})

# 5️⃣ Сохраняем в новый файл
output_file = "c:/NOAA/SWAN_files/batym/wind_ERA5_cleaned.nc"
ds.to_netcdf(output_file)

print(f"\n✅ Готово! Файл сохранён: {output_file}")
print("📂 Новые координаты:", list(ds.coords))
print("📦 Новые переменные:", list(ds.data_vars))

