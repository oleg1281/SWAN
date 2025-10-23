import xarray as xr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

# === Настройка папки с файлами ===
data_dir = "z:/NOAA/wyniky_GraphCast_SWAN"
files = sorted([f for f in os.listdir(data_dir) if f.endswith(".nc")])

# Открываем NetCDF
ds = xr.open_dataset("z:/NOAA/wyniky_GraphCast_SWAN/out_wynik2025_09_04_12_00__2025_09_16_18_00.nc")

# Координаты точки
lat_point = 55.0
lon_point = 19.0
ds_point = ds.sel(lat=lat_point, lon=lon_point, method="nearest")

# Время
times = pd.to_datetime(ds.time.values)

# Создаем фигуру с 2 подграфиками
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                    subplot_titles=("Среднее по области", f"Точка ({lat_point}, {lon_point})", "Wiatr"))

# --- 1️⃣ Среднее по области ---
fig.add_trace(go.Scatter(x=times, y=ds['fala_era5'].mean(dim=["lat","lon"]),
                         mode='lines', name='ERA5 (среднее по области)', line=dict(width=2)), row=1, col=1)
fig.add_trace(go.Scatter(x=times, y=ds['fala_graphcast_swan'].mean(dim=["lat","lon"]),
                         mode='lines', name='GraphCast SWAN (среднее по области)', line=dict(width=2)), row=1, col=1)
fig.add_trace(go.Scatter(x=times, y=ds['fala_era5_swan'].mean(dim=["lat","lon"]),
                         mode='lines', name='ERA5 SWAN (среднее по области)', line=dict(width=2)), row=1, col=1)

# --- 2️⃣ Конкретная точка ---
fig.add_trace(go.Scatter(x=times, y=ds_point['fala_era5'],
                         mode='lines', name=f'ERA5 (точка)', line=dict(dash='dash', width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=times, y=ds_point['fala_graphcast_swan'],
                         mode='lines', name=f'GraphCast SWAN (точка)', line=dict(dash='dash', width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=times, y=ds_point['fala_era5_swan'],
                         mode='lines', name=f'ERA5 SWAN (точка)', line=dict(dash='dash', width=2)), row=2, col=1)

# --- 3 ветер ---
fig.add_trace(go.Scatter(x=times, y=ds_point['WS_ERA5_kn'],
                         mode='lines', name=f'WS_ERA5_kn', line=dict(dash='dash', width=2)), row=3, col=1)
fig.add_trace(go.Scatter(x=times, y=ds_point['WS_Graphcast_kn'],
                         mode='lines', name=f'WS_Graphcast_kn', line=dict(dash='dash', width=2)), row=3, col=1)

# Цветные зоны для первого графика
for r in [1, 2, 3]:  # для всех трех графиков
    fig.add_vrect(x0=times[0], x1=times[0]+pd.Timedelta(days=2),
                  fillcolor="green", opacity=0.1, row=r, col=1, line_width=0)
    fig.add_vrect(x0=times[0]+pd.Timedelta(days=2), x1=times[0]+pd.Timedelta(days=5),
                  fillcolor="yellow", opacity=0.1, row=r, col=1, line_width=0)
    fig.add_vrect(x0=times[0]+pd.Timedelta(days=5), x1=times[0]+pd.Timedelta(days=8),
                  fillcolor="red", opacity=0.1, row=r, col=1, line_width=0)

# Настройки осей и легенды
fig.update_layout(
    height=900,
    title_text="Высота волны: среднее по области и по точке",
    yaxis=dict(range=[0,5], dtick=0.5),
    yaxis2=dict(range=[0,5], dtick=0.5),
    yaxis3=dict(range=[0,30], dtick=5),
    #xaxis=dict(range=[times[0], times[-1]], title="Дата и время"),
    xaxis2=dict(title="Дата и время"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# === Вставляем после всех trace и vrect ===
all_times = times  # список всех временных меток

# Верхний график (row=1)
fig.update_xaxes(
    tickvals=all_times,
    ticktext=[t.strftime("%Y-%m-%d %H:%M") for t in all_times],
    tickangle=270,
    row=1, col=1,
    #showticklabels=True  # <--- Важно!
)

# Нижний график (row=2)
fig.update_xaxes(
    tickvals=all_times,
    ticktext=[t.strftime("%Y-%m-%d %H:%M") for t in all_times],
    tickangle=270,
    row=2, col=1,
    #showticklabels=True
)

# Нижний график (row=3)
fig.update_xaxes(
    tickvals=all_times,
    ticktext=[t.strftime("%Y-%m-%d %H:%M") for t in all_times],
    tickangle=270,
    row=3, col=1,
    #showticklabels=True
)

# Показываем график
fig.show()
