# этот код для создания файла ветра с значениями eRA5 и Graphcast с датами файла предикт и координатами 9*31 на 53*67

from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd

dir_intut_predict = Path("z:/NOAA/wyniky_GraphCast_SWAN/predict_noaa")
dir_input_ERA5 = Path("c:/NOAA/SWAN_files/batym")
dir_output = Path("z:/NOAA/wyniky_GraphCast_SWAN/wiatr")

file_input_ERA5 = "wind_ERA5_20250301.000000_20251031.180000.nc"

# Получаем список всех файлов
files = sorted(f for f in dir_intut_predict.iterdir() if f.is_file())

for file in files:

    # Открываем исходные файлы
    ds_era = xr.open_dataset(dir_input_ERA5 / file_input_ERA5)
    ds_pred = xr.open_dataset(file)

    ds_era = ds_era.assign_coords(
        lat=np.round(ds_era.lat.values, 1),
        lon=np.round(ds_era.lon.values, 1)
    )
    # Выбираем только нужную область
    ds_era = ds_era.sel(
        lat=slice(67, 53),  # от 53° до 67° широты
        lon=slice(9, 31)  # от 9° до 31° долготы
    )

    # Переворачиваем lat (обратный порядок)
    ds_era = ds_era.reindex(lat=ds_era.lat[::-1])

    ds_pred = ds_pred.assign_coords(
        lat=np.round(ds_pred.lat.values, 1),
        lon=np.round(ds_pred.lon.values, 1)
    )
    # Выбираем только нужную область
    ds_pred = ds_pred.sel(
        lat=slice(53, 67),  # от 53° до 67° широты
        lon=slice(9, 31)  # от 9° до 31° долготы
    )

    # Переворачиваем lat (обратный порядок)
    ds_pred = ds_pred.reindex(lat=ds_era.lat[::-1])

    # Получаем диапазон времени после фильтрации
    times_pred = ds_pred.time

    # Выбираем из ds_era только те даты, которые есть в ds_pred_filtered
    ds_era_matched = ds_era.sel(time=times_pred)

    # Допустим, переменная называется "hs"
    ds_pred["U10_ERA5"] = ds_era_matched["u10"]
    ds_pred["V10_ERA5"] = ds_era_matched["v10"]

    #переименуем переменную hs в ds_pred
    ds_pred = ds_pred.rename({"10m_u_component_of_wind": "U10_Graphcast"})
    ds_pred = ds_pred.rename({"10m_v_component_of_wind": "V10_Graphcast"})

    # Вычисляем скорость ветра в м/с
    ds_pred["WS_ERA5_ms"] = np.sqrt(ds_pred["U10_ERA5"] ** 2 + ds_pred["V10_ERA5"] ** 2)
    ds_pred["WS_Graphcast_ms"] = np.sqrt(ds_pred["U10_Graphcast"] ** 2 + ds_pred["V10_Graphcast"] ** 2)

    # Переводим в узлы
    ds_pred["WS_ERA5_kn"] = ds_pred["WS_ERA5_ms"] * 1.94384
    ds_pred["WS_Graphcast_kn"] = ds_pred["WS_Graphcast_ms"] * 1.94384

    # Оставляем только нужные переменные
    ds_pred = ds_pred[["U10_ERA5", "V10_ERA5", "U10_Graphcast", "V10_Graphcast", "WS_ERA5_ms", "WS_ERA5_kn", "WS_Graphcast_ms", "WS_Graphcast_kn"]]

    # Сохраняем координаты time, lat, lon
    ds_pred = ds_pred.assign_coords(time=times_pred, lat=ds_pred.lat, lon=ds_pred.lon)

    if "batch" in ds_pred.dims:                             # удаляем ось batch
        ds_pred = ds_pred.squeeze("batch", drop=True)

    out_file_name = f'out_wind{pd.to_datetime(times_pred[0].values).strftime("%Y_%m_%d_%H_%M")}__{pd.to_datetime(times_pred[-1].values).strftime("%Y_%m_%d_%H_%M")}.nc'
    # Сохраняем отдельные NetCDF
    ds_pred.to_netcdf(dir_output / out_file_name)
    print(f"✅ файл {out_file_name} сохранен")
