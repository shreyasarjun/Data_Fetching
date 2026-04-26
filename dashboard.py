import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import os

# ===============================
# Load Data
# ===============================
CSV_DIR = "./csv_files"

csv_files = [
    os.path.join(CSV_DIR, f)
    for f in os.listdir(CSV_DIR)
    if f.endswith(".csv")
]

df = pd.concat(
    [pd.read_csv(f) for f in csv_files],
    ignore_index=True
)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

# ===============================
# Dash App
# ===============================
app = dash.Dash(__name__)
app.title = "Options Trading Dashboard"

# ===============================
# Layout
# ===============================
app.layout = html.Div(
    style={
        "backgroundColor": "#0b0b0b",
        "padding": "6px",
        "margin": "0",
        "height": "100vh",
        "overflow": "hidden",
    },
    children=[
        html.H3(
            "📊 Options Candlestick Chart",
            style={
                "color": "#ffffff",
                "textAlign": "center",
                "marginBottom": "6px",
                "marginTop": "0px",
            },
        ),

        # ===============================
        # Filters
        # ===============================
        html.Div(
            style={
                "display": "flex",
                "gap": "10px",
                "justifyContent": "center",
                "flexWrap": "wrap",
                "marginBottom": "6px",
            },
            children=[

                dcc.Dropdown(
                    id="index-dd",
                    options=[{"label": i, "value": i} for i in sorted(df["index"].unique())],
                    value=sorted(df["index"].unique())[0],
                    style={"width": "170px"},
                    clearable=False,
                ),

                dcc.Dropdown(
                    id="expiry-dd",
                    options=[{"label": i, "value": i} for i in sorted(df["expiry_date"].unique())],
                    value=sorted(df["expiry_date"].unique())[0],
                    style={"width": "170px"},
                    clearable=False,
                ),

                dcc.Dropdown(
                    id="option-dd",
                    options=[
                        {"label": "CE", "value": "CE"},
                        {"label": "PE", "value": "PE"},
                    ],
                    style={"width": "120px"},
                    clearable=False,
                ),

                dcc.Dropdown(
                    id="strike-dd",
                    style={"width": "140px"},
                    clearable=False,
                ),
            ],
        ),

        # ===============================
        # Chart
        # ===============================
        dcc.Graph(
            id="candlestick-chart",
            style={
                "height": "calc(100vh - 100px)",
                "width": "100%",
            },
            config={
                "scrollZoom": True,
                "displaylogo": False,
                "displayModeBar": True,
                "responsive": True,
                "modeBarButtonsToAdd": [
                    "drawline",
                    "drawrect",
                    "eraseshape",
                ],
                "modeBarButtonsToRemove": [
                    "select2d",
                    "lasso2d",
                    "autoScale2d",
                    "toggleSpikelines",
                    "toImage",
                ],
                "doubleClick": "reset",
            },
        ),
    ],
)

# ===============================
# Smart Default Strike Logic
# ===============================
@app.callback(
    Output("strike-dd", "options"),
    Output("strike-dd", "value"),
    Output("option-dd", "value"),
    Input("index-dd", "value"),
    Input("expiry-dd", "value"),
)
def update_strikes(index, expiry):

    dff = df[
        (df["index"] == index)
        & (df["expiry_date"] == expiry)
    ]

    if dff.empty:
        return [], None, None

    dff = dff.copy()

    # 🔥 Find strike where open nearest to 100
    dff["diff"] = (dff["open"] - 100).abs()
    nearest_row = dff.loc[dff["diff"].idxmin()]

    default_strike = nearest_row["strike_price"]
    default_option = nearest_row["option_type"]

    strikes = sorted(dff["strike_price"].unique())

    return (
        [{"label": str(s), "value": s} for s in strikes],
        default_strike,
        default_option,
    )

# ===============================
# Chart Update (Original Features Preserved)
# ===============================
@app.callback(
    Output("candlestick-chart", "figure"),
    Input("index-dd", "value"),
    Input("expiry-dd", "value"),
    Input("option-dd", "value"),
    Input("strike-dd", "value"),
    State("candlestick-chart", "relayoutData"),
)
def update_chart(index, expiry, option, strike, relayout_data):

    dff = df[
        (df["index"] == index)
        & (df["expiry_date"] == expiry)
        & (df["option_type"] == option)
        & (df["strike_price"] == strike)
    ]

    if dff.empty:
        return go.Figure()

    dff = dff.sort_values("timestamp")

    fig = go.Figure(
        go.Candlestick(
            x=dff["timestamp"],
            open=dff["open"],
            high=dff["high"],
            low=dff["low"],
            close=dff["close"],
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
            increasing_fillcolor="#26a69a",
            decreasing_fillcolor="#ef5350",
            line=dict(width=1),
            hovertemplate="<b>%{x|%d %b %Y, %H:%M}</b><extra></extra>",
        )
    )

    shapes = []
    if relayout_data and "shapes" in relayout_data:
        shapes = relayout_data["shapes"]

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b0b0b",
        plot_bgcolor="#131722",
        dragmode="pan",
        hovermode="x unified",
        uirevision="constant",
        transition=dict(duration=0),
        margin=dict(l=5, r=80, t=35, b=35),
        shapes=shapes,
        showlegend=False,
    )

    fig.update_xaxes(
        rangeslider=dict(visible=False),
        type="date",
        tickformat="%H:%M\n%d %b",
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="solid",
        spikethickness=1,
        spikecolor="#555555",
        showgrid=True,
        gridcolor="#1e222d",
        showline=True,
        linecolor="#2a2e39",
        rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[15.5, 9.25], pattern="hour"),
        ],
    )

    fig.update_yaxes(
        side="right",
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="solid",
        spikethickness=1,
        spikecolor="#555555",
        showgrid=True,
        gridcolor="#1e222d",
        zeroline=False,
        showline=True,
        linecolor="#2a2e39",
        tickformat=".2f",
    )

    return fig


# ===============================
# Run App
# ===============================
if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=8050,
    )
