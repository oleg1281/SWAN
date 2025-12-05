import xarray as xr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State
from dash import callback_context
import os

# === Настройка папки с файлами ===
data_dir = "c:/NOAA/SWAN_files"
files = sorted([f for f in os.listdir(data_dir) if f.endswith(".nc")])

# === Функция для построения графика ===
def make_figure(file_path, lat_point=55.0, lon_point=17.0):
    ds = xr.open_dataset(file_path)

    #lat_point = 55.0
    #lon_point = 19.0
    ds_point = ds.sel(lat=lat_point, lon=lon_point, method="nearest")
    times = pd.to_datetime(ds.time.values)

    # Создаем фигуру с 2 подграфиками
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        subplot_titles=("Średna wysokość fali dla badanego obszaru", f"Fala w zadanym punkcie ({lat_point}, {lon_point})",
                                        f"Wiatr w zadanym punkcie ({lat_point}, {lon_point})"))

    # --- 1️⃣ Среднее по области ---
    fig.add_trace(go.Scatter(x=times, y=ds['fala_era5'].mean(dim=["lat", "lon"]),
                mode='lines', name='ERA5 (Średnia fala dla obszaru)', line=dict(width=2, color='black')), row=1, col=1)
    fig.add_trace(go.Scatter(x=times, y=ds['fala_graphcast_swan'].mean(dim=["lat", "lon"]),
                mode='lines', name='GraphCast SWAN (Średnia fala dla obszaru)', line=dict(width=2, color='red')), row=1, col=1)
    fig.add_trace(go.Scatter(x=times, y=ds['fala_era5_swan'].mean(dim=["lat", "lon"]),
                mode='lines', name='ERA5 SWAN (Średnia fala dla obszaru)', line=dict(width=2, color='green')), row=1, col=1)  # цвет линии)

    # --- 2️⃣ Конкретная точка ---
    fig.add_trace(go.Scatter(x=times, y=ds_point['fala_era5'],
                mode='lines', name=f'ERA5 (Fala w punkte {lat_point}, {lon_point})', line=dict(dash='dash', width=2, color='black')), row=2, col=1)
    fig.add_trace(go.Scatter(x=times, y=ds_point['fala_graphcast_swan'],
                mode='lines', name=f'GraphCast SWAN (Fala w punkte {lat_point}, {lon_point})', line=dict(dash='dash', width=2, color='red')), row=2,
                  col=1)
    fig.add_trace(go.Scatter(x=times, y=ds_point['fala_era5_swan'],
                mode='lines', name=f'ERA5 SWAN (Fala w punkte {lat_point}, {lon_point})', line=dict(dash='dash', width=2, color='green')), row=2, col=1)

    # --- 3 ветер ---
    fig.add_trace(go.Scatter(x=times, y=ds_point['WS_ERA5_kn'],
                mode='lines', name=f'WS_ERA5_kn (Wiatr w punkte {lat_point}, {lon_point})', line=dict(dash='dashdot', width=2, color='black')), row=3, col=1)
    fig.add_trace(go.Scatter(x=times, y=ds_point['WS_Graphcast_kn'],
                mode='lines', name=f'WS_Graphcast_kn (Wiatr w punkte {lat_point}, {lon_point})', line=dict(dash='dashdot', width=2, color='red')), row=3, col=1)

    # Цветные зоны
    for r in [1, 2, 3]:  # для всех трех графиков
        fig.add_vrect(x0=times[0], x1=times[0] + pd.Timedelta(days=2),
                      fillcolor="green", opacity=0.3, row=r, col=1, line_width=0)
        fig.add_vrect(x0=times[0] + pd.Timedelta(days=2), x1=times[0] + pd.Timedelta(days=5),
                      fillcolor="yellow", opacity=0.3, row=r, col=1, line_width=0)
        fig.add_vrect(x0=times[0] + pd.Timedelta(days=5), x1=times[0] + pd.Timedelta(days=8),
                      fillcolor="red", opacity=0.3, row=r, col=1, line_width=0)

    # Настройки осей и легенды
    fig.update_layout(
        height=900,
        #title_text="Высота волны: среднее по области и по точке",
        yaxis1=dict(range=[0, 3.5], dtick=0.2, showline=True, linewidth=2, linecolor='black', mirror=True, gridcolor='rgba(0,0,0,0.2)'),
        yaxis2=dict(range=[0, 3.5], dtick=0.2, showline=True, linewidth=2, linecolor='black', mirror=True, gridcolor='rgba(0,0,0,0.2)'),
        yaxis3=dict(range=[0, 35], dtick=2, showline=True, linewidth=2, linecolor='black', mirror=True, gridcolor='rgba(0,0,0,0.2)'),
        xaxis1=dict(showline=True, linewidth=1, linecolor='black', mirror=True, gridcolor='rgba(0,0,0,0.2)'),
        xaxis2=dict(showline=True, linewidth=1, linecolor='black', mirror=True, gridcolor='rgba(0,0,0,0.2)'),
        xaxis3=dict(showline=True, linewidth=1, linecolor='black', mirror=True, gridcolor='rgba(0,0,0,0.2)'),
        plot_bgcolor="rgba(220,220,220,0.1)",  # слабосерый полупрозрачный фон области графика
        paper_bgcolor="white",  # фон всей фигуры
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=1, y1=1,
        xref="paper", yref="paper",
        line=dict(color="black", width=0),
        fillcolor="rgba(0,0,0,0)"  # прозрачная заливка
    )

    # === Вставляем после всех trace и vrect ===
    all_times = times  # список всех временных меток

    # Верхний график (row=1)
    fig.update_xaxes(
        tickvals=all_times,
        ticktext=[t.strftime("%Y-%m-%d %H:%M") for t in all_times],
        tickangle=270,
        row=1, col=1,
        tickfont=dict(size=12, color='black')  # размер и цвет подписей
    )

    # Нижний график (row=2)
    fig.update_xaxes(
        tickvals=all_times,
        ticktext=[t.strftime("%Y-%m-%d %H:%M") for t in all_times],
        tickangle=270,
        row=2, col=1,
        tickfont=dict(size=12, color='black')  # размер и цвет подписей
    )

    # Нижний график (row=3)
    fig.update_xaxes(
        tickvals=all_times,
        ticktext=[t.strftime("%Y-%m-%d %H:%M") for t in all_times],
        tickangle=270,
        row=3, col=1,
        tickfont=dict(size=12, color='black')  # размер и цвет подписей
    )

    return fig


# === Dash приложение с выбором координат ===
app = Dash(__name__)
# === Dash приложение с выбором координат и даты ===
app.layout = html.Div([
    html.H4("Wyniki prognozy GraphCast, SWAN w porównaniu do ERA5", style={'textAlign': 'center'}),

    html.Div([
        html.Label("🌍 Szerokość geograficzna:"),
        dcc.Input(id='lat-input', type='number', value=55.0, step=0.1,
                  style={'width': '80px', 'padding': '5px', 'borderRadius': '6px'}),

        html.Label("Długość geograficzna:"),
        dcc.Input(id='lon-input', type='number', value=19.0, step=0.1,
                  style={'width': '80px', 'padding': '5px', 'borderRadius': '6px'}),

        html.Button("◀ Poprzedni (-6h)", id="prev-btn", n_clicks=0,
                    style={'backgroundColor': '#e0e0e0', 'border': 'none', 'borderRadius': '6px',
                           'padding': '6px 10px'}),
        html.Button("Następny (+6h) ▶", id="next-btn", n_clicks=0,
                    style={'backgroundColor': '#e0e0e0', 'border': 'none', 'borderRadius': '6px',
                           'padding': '6px 10px'}),

        html.Label("📅 Data prognozy:"),
        dcc.Dropdown(
            id='date-dropdown',
            options=[{'label': f, 'value': f} for f in files],
            value=files[0],
            clearable=False,
            style={
                'width': '220px', 'fontSize': '12px',
                'borderRadius': '6px', 'backgroundColor': 'white'
            }
        )
    ],
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'gap': '10px',
            'flexWrap': 'wrap',
            'padding': '10px',
            'backgroundColor': '#f7f9fb',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
            'margin': '15px auto',
            'width': '90%'
        }),

    dcc.Graph(id='plot'),
    html.Div(id='filename', style={'textAlign': 'center', 'fontSize': 8})
])


# === Колбэк с выбором координат и переключением файлов ===
@app.callback(
    Output('plot', 'figure'),
    Output('filename', 'children'),
    Input('prev-btn', 'n_clicks'),
    Input('next-btn', 'n_clicks'),
    Input('lat-input', 'value'),
    Input('lon-input', 'value'),
    Input('date-dropdown', 'value'),  # добавили выбор из Dropdown
    State('filename', 'children')
)


def update_plot(prev, next, lat_value, lon_value, dropdown_value, current_name):
    try:
        # Определяем индекс текущего файла
        if current_name in files:
            idx = files.index(current_name)
        else:
            idx = 0

        ctx = callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'prev-btn' and idx > 0:
                idx -= 1
            elif button_id == 'next-btn' and idx < len(files) - 1:
                idx += 1
            elif button_id == 'date-dropdown':
                idx = files.index(dropdown_value)

        file_path = os.path.join(data_dir, files[idx])
        fig = make_figure(file_path, lat_value, lon_value)
        return fig, files[idx]

    except Exception as e:
        # Если что-то пошло не так (ошибка чтения файла, доступа и т.д.)
        import plotly.graph_objects as go
        error_message = f"Błąd: {str(e)}"

        # Возвращаем простую фигуру с сообщением об ошибке
        fig = go.Figure()
        fig.add_annotation(
            text=f"❌ Nie można otworzyć pliku lub utworzyć wykresu.\n{error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(
            title="Błąd podczas wczytywania danych",
            paper_bgcolor="white",
            plot_bgcolor="#ffeeee",
            height=400
        )
        return fig, f"❌ Błąd przy pliku: {files[idx] if 'idx' in locals() else 'nieznany'}"


if __name__ == "__main__":
    # Отобразить первый файл сразу
    first_fig = make_figure(os.path.join(data_dir, files[0]))
    print("Открыт файл:", files[0])
    app.run_server(host='0.0.0.0', port=8050, debug=True)

