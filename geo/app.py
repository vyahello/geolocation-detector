import os
from typing import Optional

from flask import Flask, Response, render_template, request, send_file
from geopy.geocoders import Nominatim
import pandas
import datetime

app = Flask(__name__)
filename: Optional[str] = None


@app.route('/')
def index() -> str:
    return render_template('index.html', btn=None)


@app.route('/success-table', methods=['POST'])
def success_table() -> str:
    if request.method == 'POST':
        try:
            geo = Nominatim(scheme='http', user_agent='app')
            data_frame = pandas.read_csv(request.files['file'])
            data_frame['coordinates'] = data_frame['Address'].apply(geo.geocode)
            data_frame['Latitude'] = data_frame['coordinates'].apply(
                lambda entry: entry.latitude if entry else None
            )
            data_frame['Longitude'] = data_frame['coordinates'].apply(
                lambda entry: entry.longitude if entry else None
            )
            data_frame = data_frame.drop('coordinates', 1)
            global filename
            if not os.path.isdir('output'):
                os.mkdir('output')
            filename = datetime.datetime.now().strftime(
                'output/%Y-%m-%d-%H-%M-%S-%f.csv'
            )
            data_frame.to_csv(filename, index=None)
            return render_template(
                'index.html',
                text=data_frame.to_html(),
                btn='download.html',
            )
        except Exception as exp:
            return render_template('index.html', text=str(exp), btn=None)


@app.route('/download-file')
def download() -> Response:
    return send_file(filename, download_name='data.csv', as_attachment=True)


if __name__ == '__main__':
    app.run()
