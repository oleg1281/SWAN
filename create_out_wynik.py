import xarray as xr

ds2 = xr.open_dataset("z:/NOAA/wyniky_GraphCast_SWAN/wiatr/out_wind2025_05_17_00_00__2025_05_29_06_00.nc")  # 0.1°
ds1 = xr.open_dataset("z:/NOAA/wyniky_GraphCast_SWAN/fala/out_fala2025_05_17_00_00__2025_05_29_06_00.nc")   # 1°

# Интерполируем низкое разрешение на сетку высокого
ds2_interp = ds2.interp(lat=ds1.lat, lon=ds1.lon)

# Объединяем переменные
ds_merged = xr.merge([ds1, ds2_interp])

ds_merged.to_netcdf("z:/NOAA/wyniky_GraphCast_SWAN/merged_on_highres_grid.nc")
print("✅ Файл сохранён: merged_on_highres_grid.nc")
