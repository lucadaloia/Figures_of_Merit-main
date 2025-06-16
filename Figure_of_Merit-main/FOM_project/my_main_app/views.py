from django.shortcuts import render
from .models import DeviceData, MaterialLimit
import plotly.graph_objs as go
from plotly.offline import plot

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
                name=device.device_type
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

    layout = go.Layout(
        xaxis=dict(title="Breakdown Voltage (V)", type='log'),
        yaxis=dict(title="R<sub>on</sub> (mΩ·cm²)", type='log'),
        hovermode='closest'
    )

    fig = go.Figure(data=traces, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return render(request, 'my_main_app/FOM_plot.html', {
        'plot_div': plot_div,
    })

