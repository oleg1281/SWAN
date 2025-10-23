# этот код соеденяет два файла fala and wiatr и создает файл out_wynik2025_05_15_00_00__2025_05_27_06_00.nc

import xarray as xr
from pathlib import Path

input_dir_fala = Path("z:/NOAA/wyniky_GraphCast_SWAN/fala")
input_dir_wiatr = Path("z:/NOAA/wyniky_GraphCast_SWAN/wiatr")
output_dir_fala_wiatr = Path("z:/NOAA/wyniky_GraphCast_SWAN")

fala_files = [f for f in input_dir_fala.iterdir() if f.is_file()]
existing_files = {f.name for f in output_dir_fala_wiatr.iterdir() if f.is_file()}

fala_to_process = [f for f in fala_files if f.name not in existing_files]

print(f"🔹 Найдено новых файлов: {len(fala_to_process)}")
for f in fala_to_process:
    print(f.name)

for file in fala_to_process:
    ds1 = xr.open_dataset(file)

    wiatr_name = file.name.replace("out_fala", "out_wind")
    wiatr_path = input_dir_wiatr / wiatr_name

    if not wiatr_path.exists():
        print(f"⚠️ Файл {wiatr_name} не найден, пропускаем.")
        continue

    ds2 = xr.open_dataset(wiatr_path)

    # Интерполируем низкое разрешение на сетку высокого
    ds2_interp = ds2.interp(lat=ds1.lat, lon=ds1.lon)

    # Объединяем переменные
    ds_merged = xr.merge([ds1, ds2_interp])

    # Имя файла вывода
    out_file = file.name.replace("out_fala", "out_wynik")
    out_path = output_dir_fala_wiatr / out_file

    ds_merged.to_netcdf(out_path)
    print(f"✅ Файл сохранён: {out_path}")
