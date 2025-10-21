import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 1️⃣ Открываем NetCDF-файл
ds = xr.open_dataset("c:/NOAA/SWAN_files/out_fala2025_06_01_12_00__2025_06_13_18_00.nc")

# Задаём координаты точки
lat_point = 55.0
lon_point = 19.0

# Выбираем ближайшую точку
ds_point = ds.sel(lat=lat_point, lon=lon_point, method="nearest")

# Преобразуем время в pandas.DatetimeIndex
times = pd.to_datetime(ds.time.values)

# Создаем график
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)  # 2 строки, 1 столбец

# === 1️⃣ Среднее по области ===
axes[0].plot(times, ds['fala_era5'].mean(dim=["lat", "lon"]), label='ERA5 (среднее по области)', linewidth=2)
axes[0].plot(times, ds['fala_graphcast_swan'].mean(dim=["lat", "lon"]), label='GraphCast SWAN (среднее по области)', linewidth=2)
axes[0].plot(times, ds['fala_era5_swan'].mean(dim=["lat", "lon"]), label='ERA5 SWAN (среднее по области)', linewidth=2)

axes[0].set_title("Среднее по области", fontsize=13)
axes[0].set_ylabel("Высота волны, м", fontsize=12)
axes[0].set_ylim(0, 5)
axes[0].set_yticks(np.arange(0, 5.1, 0.2))   # <<< фиксированное деление
axes[0].grid(True, alpha=0.4)
axes[0].legend()

# 🎨 Цветные зоны (на обоих графиках)
start = times[0]
for ax in axes:
    ax.axvspan(start, start + np.timedelta64(2, 'D'), color='green', alpha=0.15)
    ax.axvspan(start + np.timedelta64(2, 'D'), start + np.timedelta64(5, 'D'), color='yellow', alpha=0.15)
    ax.axvspan(start + np.timedelta64(5, 'D'), start + np.timedelta64(8, 'D'), color='red', alpha=0.15)

# === 2️⃣ Конкретная точка ===
axes[1].plot(times, ds_point['fala_era5'], '--', label=f'ERA5 (точка {lat_point},{lon_point})', linewidth=2)
axes[1].plot(times, ds_point['fala_graphcast_swan'], '--', label=f'GraphCast SWAN (точка {lat_point},{lon_point})', linewidth=2)
axes[1].plot(times, ds_point['fala_era5_swan'], '--', label=f'ERA5 SWAN (точка {lat_point},{lon_point})', linewidth=2)

axes[1].set_title(f"Точка ({lat_point}, {lon_point})", fontsize=13)
axes[1].set_xlabel("Дата и время", fontsize=12)
axes[1].set_ylabel("Высота волны, м", fontsize=12)
axes[1].set_ylim(0, 5)
axes[1].set_yticks(np.arange(0, 5.1, 0.2))   # <<< фиксированное деление
axes[1].grid(True, alpha=0.4)
axes[1].legend()

# === Общая настройка оси X ===
plt.xticks(
    ticks=times,
    labels=[t.strftime("%Y-%m-%d %H:%M") for t in times],
    rotation=90,
    ha='center'
)
plt.tight_layout()
plt.show()

