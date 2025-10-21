from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd

dir_intut_predict = Path("z:/NOAA/predict_noaa")
dir_input_ERA5 = Path("c:/NOAA/SWAN_files/batym")
dir_output = Path("z:/NOAA/wyniky_GraphCast_SWAN")

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
    ds_pred = ds_pred.assign_coords(
        lat=np.round(ds_pred.lat.values, 1),
        lon=np.round(ds_pred.lon.values, 1)
    )

    # Получаем диапазон времени после фильтрации
    times_pred = ds_pred.time

    # Выбираем из ds_era только те даты, которые есть в ds_pred_filtered
    ds_era_matched = ds_era.sel(time=times_pred)

    # Допустим, переменная называется "hs"
    ds_pred["U10_ERA5"] = ds_era_matched["U10"]

    ds_pred["V10_ERA5"] = ds_era_matched["V10"]

    #переименуем переменную hs в ds_pred
    ds_pred_filtered = ds_pred_filtered.rename({"10m_u_component_of_wind": "U10_predict"})
    ds_pred_filtered = ds_pred_filtered.rename({"10m_v_component_of_wind": "V10_predict"})

    out_file_name = f'out_wind{pd.to_datetime(times_pred[0].values).strftime("%Y_%m_%d_%H_%M")}__{pd.to_datetime(times_pred[-1].values).strftime("%Y_%m_%d_%H_%M")}.nc'
    # Сохраняем отдельные NetCDF
    ds_pred_filtered.to_netcdf(dir_output / out_file_name)
    print(f"✅ файл {out_file_name} сохранен")
