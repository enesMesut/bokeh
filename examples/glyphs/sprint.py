from __future__ import print_function

from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.browserlib import view
from bokeh.resources import INLINE
from bokeh.models.glyphs import Circle, Text
from bokeh.models import ColumnDataSource, Range1d, DataRange1d, Plot, LinearAxis, SingleIntervalTicker, Grid, HoverTool
from bokeh.sampledata.sprint import sprint

# Based on http://www.nytimes.com/interactive/2012/08/05/sports/olympics/the-100-meter-dash-one-race-every-medalist-ever.html

abbrev_to_country = {
    "USA": "United States",
    "GBR": "Britain",
    "JAM": "Jamaica",
    "CAN": "Canada",
    "TRI": "Trinidad and Tobago",
    "AUS": "Australia",
    "GER": "Germany",
    "CUB": "Cuba",
    "NAM": "Namibia",
    "URS": "Soviet Union",
    "BAR": "Barbados",
    "BUL": "Bulgaria",
    "HUN": "Hungary",
    "NED": "Netherlands",
    "NZL": "New Zealand",
    "PAN": "Panama",
    "POR": "Portugal",
    "RSA": "South Africa",
    "EUA": "United Team of Germany",
}

gold_fill   = "#efcf6d"
gold_line   = "#c8a850"
silver_fill = "#cccccc"
silver_line = "#b0b0b1"
bronze_fill = "#c59e8a"
bronze_line = "#98715d"

fill_color = { "gold": gold_fill, "silver": silver_fill, "bronze": bronze_fill }
line_color = { "gold": gold_line, "silver": silver_line, "bronze": bronze_line }

t0 = sprint.Time[0]

sprint["Abbrev"]       = sprint.Country
sprint["Country"]      = sprint.Abbrev.map(lambda abbr: abbrev_to_country[abbr])
sprint["Medal"]        = sprint.Medal.map(lambda medal: medal.lower())
sprint["Speed"]        = 100.0/sprint.Time
sprint["MetersBack"]   = 100.0*(1.0 - t0/sprint.Time)
sprint["MedalFill"]    = sprint.Medal.map(lambda medal: fill_color[medal])
sprint["MedalLine"]    = sprint.Medal.map(lambda medal: line_color[medal])
sprint["SelectedName"] = sprint[["Name", "Medal", "Year"]].apply(tuple, axis=1) \
    .map(lambda (name, medal, year): name if medal == "gold" and year in [1988, 1968, 1936, 1896] else None)

source = ColumnDataSource(sprint)
title = "Usain Bolt vs. 116 years of Olympic sprinters"

xdr = Range1d(start=sprint.MetersBack.max()+3, end=0)
ydr = DataRange1d(sources=[source.columns("Year")])

plot = Plot(title=title, x_range=xdr, y_range=ydr, plot_width=800, plot_height=800, toolbar_location=None, outline_line_color=None)

xticker = SingleIntervalTicker(interval=5, num_minor_ticks=0)
xaxis = LinearAxis(ticker=xticker, axis_line_color=None, major_tick_line_color=None)
plot.add_layout(xaxis, "below")
xgrid = Grid(dimension=0, ticker=xaxis.ticker, grid_line_dash="dashed")
plot.add_layout(xgrid)
yticker = SingleIntervalTicker(interval=4, num_minor_ticks=0)
yaxis = LinearAxis(ticker=yticker, major_tick_in=-5, major_tick_out=10)
plot.add_layout(yaxis, "right")

radius = dict(value=5, units="screen")
medal_glyph = Circle(x="MetersBack", y="Year", radius=radius, fill_color="MedalFill", line_color="MedalLine", fill_alpha=0.5)
medal = plot.add_glyph(source, medal_glyph)

athlete_glyph = Text(x="MetersBack", y="Year", x_offset=10, text="SelectedName",
    text_align="left", text_baseline="middle", text_font_size="10pt")
athlete = plot.add_glyph(source, athlete_glyph)

tooltips = [
    ("Name",          "@Name"),
    ("Country",       "@Abbrev"),
    ("Year",          "@Year"),
    ("Time",          "@Time{0.00} s"),
    ("Meters behind", "@{MetersBack}{0.00} m"),
]

hover = HoverTool(tooltips=tooltips, renderers=[medal])
plot.add_tools(hover)

doc = Document()
doc.add(plot)

if __name__ == "__main__":
    filename = "sprint.html"
    with open(filename, "w") as f:
        f.write(file_html(doc, INLINE, title))
    print("Wrote %s" % filename)
    view(filename)
