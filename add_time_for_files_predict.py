# этот код для того чтобы все файлы в папке z:/NOAA/predict_noaa в которых нет дат в координате time записать их туда и сохранить в папку z:\NOAA\wyniky_GraphCast_SWAN\predict_noaa\

from pathlib import Path
import xarray as xr
import pandas as pd
import re

# Папка с файлами
dir_input = Path("z:/NOAA/predict_noaa")
dir_output = Path("z:/NOAA/wyniky_GraphCast_SWAN/predict_noaa")

# Регулярка для извлечения второй даты
pattern = re.compile(r"_(\d{4}-\d{2}-\d{2})_(\d{2})h(\d{2})m_(\d{4}-\d{2}-\d{2})_(\d{2})h(\d{2})m")

# Получаем список всех имён файлов в папке output
existing_files = {f.name for f in dir_output.iterdir() if f.is_file()}

# Оставляем только те, которых нет в output
file_names = [
    f.name for f in dir_input.iterdir()
    if f.is_file() and f.name not in existing_files
]

print("📁 Файлы, которых ещё нет в output:")

for file in file_names:

    # Поиск по имени
    match = pattern.search(file)
    if not match:
        print(f"Формат имени не распознан: {file}")
    else:
        print("Совпадение найдено!")
        print(match.groups())

    # Извлекаем дату конца прогноза (вторая)
    date2 = match.group(4)
    hour2 = match.group(5)
    minute2 = match.group(6)

    # Создаём Timestamp и прибавляем 6 часов
    start_time = pd.Timestamp(f"{date2} {hour2}:{minute2}") + pd.Timedelta(hours=6)
    print(f"⏰ Новый старт времени для {file}: {start_time}")

    # Открываем NetCDF
    ds = xr.open_dataset(dir_input / file)

    # Создаём новые значения времени
    n_steps = ds.dims.get("time", len(ds["time"]))
    new_times = pd.date_range(start=start_time, periods=n_steps, freq="6H")

    # Перезаписываем координату time
    ds = ds.assign_coords(time=new_times)

    # Сохраняем обратно
    output_file = dir_output / file  # создаёт файл в той же папке с префиксом 'out_'
    ds.to_netcdf(output_file)
    ds.close()

    print(f"✅ Файл обновлён: {output_file}")
