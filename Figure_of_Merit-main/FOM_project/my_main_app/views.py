from django.shortcuts import render
from .models import DeviceData, MaterialLimit
import plotly.graph_objs as go
from plotly.offline import plot
from collections import defaultdict
import numpy as np

global customdata
def home(request):
    devices = DeviceData.objects.all()

    traces = []

    for device in devices:
        # Only include devices with positive, non-zero values (required for log scale)
        if device.breakdown_voltage > 0 and device.r_on > 0:
            url = device.reference_file.url if device.reference_file else '#'
            print(url)
            traces.append(go.Scatter(
                x=[device.breakdown_voltage],
                y=[device.r_on],
                mode='markers',
                marker=dict(size=10),
                text=f"""
                    {device.semiconductor_material} {device.device_type}<br>
                    {device.first_author} ({device.year})<br>
                    <b>{device.title}</b><br>
                    <a href="{device.reference_file.url if device.reference_file else '#'}" target="_blank">PDF</a>
                """,
                customdata=[[device.reference_file.url if device.reference_file else '#']],
                name= f'{device.company_university} - {device.device_type}'
            ))
            

    layout = go.Layout(
        xaxis=dict(title="Breakdown Voltage (V)", type='log'),
        yaxis=dict(title="R<sub>on</sub> (mΩ·cm²)", type='log'),
        hovermode='closest'
    )

    fig = go.Figure(data=traces, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return render(request, 'my_main_app/home.html', {
        'plot_div': plot_div,
    })


def material_limits(request):
    limits = MaterialLimit.objects.all()
    devices = DeviceData.objects.all()

    ##############################
    #Plotting devices
    ##############################
    # Group devices by company_university
    grouped = defaultdict(list)
    for device in devices:
        grouped[device.company_university].append(device)

    
    device_traces = []

    # Map each semiconductor material to a marker symbol
    material_to_symbol = {
        'Si': 'circle',
        'SiC': 'square',
        'GaN': 'diamond',
        'Ga2O3': 'triangle-up',
        # Add more as needed
    }

    for company, devs in grouped.items():
        x = [d.breakdown_voltage for d in devs if d.breakdown_voltage > 0 and d.r_on > 0]
        y = [d.r_on for d in devs if d.breakdown_voltage > 0 and d.r_on > 0]
        symbols = [material_to_symbol.get(d.semiconductor_material, 'circle') for d in devs if d.breakdown_voltage > 0 and d.r_on > 0]
        texts = [f"{d.semiconductor_material} {d.device_type}<br>{d.first_author} ({d.year})<br><b>{d.title}</b>" for d in devs if d.breakdown_voltage > 0 and d.r_on > 0]

        if x and y:
            device_traces.append(go.Scatter(
                x=x,
                y=y,
                mode='markers',
                name=company,
                marker=dict(
                    size=10,
                    symbol=symbols,
                    line=dict(width=1, color='black')
                ),
                text=texts,
            ))

    traces = []

    # Only include devices with positive, non-zero values (required for log scale)
    for limit in limits:
        x_data = limit.br_voltage
        y_data = limit.r_on
       
       # for x, y in x_data, y_data

       # Plot a line for each MaterialLimit
        traces.append(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            name=str(limit.material) if hasattr(limit, 'material') else 'Material Limit'
        ))

        if not traces:
            traces.append(go.Scatter(x=[1], y=[1], mode='lines', name='Dummy'))


    # Set x and y axis upper limit (ranges)
    all_x = []
    all_y = []
    for trace in device_traces:
        all_x.extend(trace.x)
        all_y.extend(trace.y)

    if all_x:
        min_x = min(all_x)
        max_x = max(all_x)
        x_min = min_x * 0.8  # 20% less than the smallest x
        x_max = max_x * 1.2  # 20% more than the largest x
        xaxis_range = [np.log10(x_min), np.log10(x_max)]
    else:
        xaxis_range = None
    if all_y:
        min_y = min(all_y)
        max_y = max(all_y)
        y_min = min_y * 0.8  # 20% less than the smallest y
        y_max = max_y * 1.2  # 20% more than the largest y
        yaxis_range = [np.log10(y_min), np.log10(y_max)]
    else:
        yaxis_range = None


    all_traces = device_traces + traces

    layout = go.Layout(
        xaxis=dict(title="Breakdown Voltage (V)", type='log', range=xaxis_range),
        yaxis=dict(title="R<sub>on</sub> (mΩ·cm²)", type='log', range=yaxis_range),
        hovermode='closest'
    )

    fig = go.Figure(data=all_traces, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return render(request, 'my_main_app/FOM_plot.html', {
        'plot_div': plot_div,
    })
