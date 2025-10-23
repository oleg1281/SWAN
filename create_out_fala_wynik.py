# этот код для создания файла высоты волны с era5, era5-swan, era5-graphcast-swan с датами такими как в предикте graphcast с координатами только 9*31 на 53*67

from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd

dir_intut_predict = Path("z:/NOAA/predict_swan/")
dir_input_ERA5 = Path("c:/NOAA/SWAN_files/batym")
dir_output = Path("z:/NOAA/wyniky_GraphCast_SWAN/fala")

file_input_ERA5 = "fala_ERA5_20250301.000000_20251031.180000_clean.nc"
file_input_ERA5_SWAN = "ERA5_SWAN_fala_20250301.000000_20251031.180000.nc"

# Получаем список всех файлов
files = sorted(f for f in dir_intut_predict.iterdir() if f.is_file())

for file in files:

    # Открываем исходные файлы
    ds_era = xr.open_dataset(dir_input_ERA5 / file_input_ERA5)
    ds_pred = xr.open_dataset(file)
    ds_era_swan = xr.open_dataset(dir_input_ERA5 / file_input_ERA5_SWAN)

    ds_era = ds_era.assign_coords(
        lat=np.round(ds_era.lat.values, 1),
        lon=np.round(ds_era.lon.values, 1)
    )
    ds_pred = ds_pred.assign_coords(
        lat=np.round(ds_pred.lat.values, 1),
        lon=np.round(ds_pred.lon.values, 1)
    )
    ds_era_swan = ds_era_swan.assign_coords(
        lat =np.round(ds_era_swan.lat.values, 1),
        lon =np.round(ds_era_swan.lon.values, 1)
    )


    # Отбрасываем первые 3 дня в прогнозе
    start_time = ds_pred.time.values[0] + np.timedelta64(3, 'D')
    ds_pred_filtered = ds_pred.sel(time=slice(start_time, None))

    # Получаем диапазон времени после фильтрации
    times_pred = ds_pred_filtered.time

    # Выбираем из ds_era только те даты, которые есть в ds_pred_filtered
    ds_era_matched = ds_era.sel(time=times_pred)

    ds_era_swan_matched = ds_era_swan.sel(time=times_pred)

    # Допустим, переменная называется "hs"
    ds_pred_filtered["fala_era5"] = ds_era_matched["fala_era5"]

    ds_pred_filtered["fala_era5_swan"] = ds_era_swan_matched["hs"]

    #переименуем переменную hs в ds_pred
    ds_pred_filtered = ds_pred_filtered.rename({"hs": "fala_graphcast_swan"})

    out_file_name = f'out_fala{pd.to_datetime(times_pred[0].values).strftime("%Y_%m_%d_%H_%M")}__{pd.to_datetime(times_pred[-1].values).strftime("%Y_%m_%d_%H_%M")}.nc'
    # Сохраняем отдельные NetCDF
    ds_pred_filtered.to_netcdf(dir_output / out_file_name)
    print(f"✅ файл {out_file_name} сохранен")
