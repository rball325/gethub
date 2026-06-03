from flask import Flask, request, send_from_directory, jsonify, render_template_string
import pandas as pd
import os

app = Flask(__name__)

# Directory where CSV files are stored
CSV_DIR = os.path.expanduser('~/.logs/monitoring')

@app.route('/')
def home():
    files = os.listdir(CSV_DIR)
    csv_files = [f for f in files if f.endswith('.csv') and os.path.getsize(os.path.join(CSV_DIR, f)) > 0]
    csv_files.sort(key=lambda f: os.path.getmtime(os.path.join(CSV_DIR, f)), reverse=True)
    return render_template_string('''
        <h1>CSV Interactive Line Graph Generator</h1>
        <form id="file-select-form">
            <label for="file">Choose a CSV file:</label>
            <select id="file" name="file">
                {% for file in csv_files %}
                    <option value="{{ file }}">{{ file }}</option>
                {% endfor %}
            </select>
            <button type="submit">Generate Interactive Line Graph</button>
        </form>
        <div id="graph"></div>

        <script>
            document.getElementById('file-select-form').addEventListener('submit', async function (e) {
                e.preventDefault();
                const selectElement = document.getElementById('file');
                const selectedFile = selectElement.value;

                const response = await fetch('/data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ file: selectedFile })
                });

                if (!response.ok) {
                    alert('Failed to retrieve data');
                    return;
                }

                const data = await response.json();
                const x = data[Object.keys(data)[0]].map(ts => {
                    const [date, time] = ts.split(' ');
                    const [m, d, y] = date.split('/');
                    return `${y}-${m}-${d} ${time}`;
                });
                const traces = Object.keys(data).slice(1).map(key => ({
                    x: x,
                    y: data[key],
                    mode: 'lines',
                    name: key
                }));

                const parts = selectedFile.replace('.csv', '').split('_');
                const monthNames = ['January','February','March','April','May','June',
                                    'July','August','September','October','November','December'];
                const title = monthNames[parseInt(parts[1], 10) - 1] + ' ' + parts[0];

                // Build day-boundary vertical lines and day labels
                const startDay = x[0].substring(0, 10);
                const endDay   = x[x.length-1].substring(0, 10);
                const dayShapes = [];
                const dayAnnotations = [];
                let cur = new Date(startDay + 'T00:00:00');
                const end = new Date(endDay + 'T00:00:00');
                while (cur <= end) {
                    const ds = cur.getFullYear() + '-'
                             + String(cur.getMonth()+1).padStart(2,'0') + '-'
                             + String(cur.getDate()).padStart(2,'0') + ' 00:00:00';
                    dayShapes.push({
                        type: 'line', xref: 'x', yref: 'paper',
                        x0: ds, x1: ds, y0: 0, y1: 1,
                        line: { color: '#aaa', width: 2 }
                    });
                    dayAnnotations.push({
                        x: ds, xref: 'x', yref: 'paper',
                        y: -0.30, showarrow: false,
                        text: String(cur.getDate()).padStart(2,'0'),
                        font: { size: 13, color: '#333' },
                        xanchor: 'left'
                    });
                    cur.setDate(cur.getDate() + 1);
                }

                const layout = {
                    title: title,
                    shapes: dayShapes,
                    annotations: dayAnnotations,
                    xaxis: {
                        type: 'date',
                        tickformat: '%H',
                        dtick: 3600000,
                        tick0: x[0].substring(0, 10) + ' 00:00:00',
                        ticks: 'outside',
                        ticklen: 5,
                        tickwidth: 1,
                        tickcolor: '#000',
                        tickangle: -45,
                        showgrid: true,
                        gridcolor: '#eee',
                        range: [x[0].substring(0, 10) + ' 00:00:00',
                                x[x.length-1].substring(0, 10) + ' 23:59:59'],
                        automargin: true
                    },
                    yaxis: {
                        title: 'Values'
                    },
                    margin: { b: 160 }
                };

                Plotly.newPlot('graph', traces, layout);
            });
        </script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    ''', csv_files=csv_files)

@app.route('/data', methods=['POST'])
def get_data():
    data = request.get_json()
    file_name = data.get('file')
    if not file_name:
        return 'No file selected', 400

    file_path = os.path.join(CSV_DIR, file_name)
    if not os.path.exists(file_path):
        return 'File not found', 404

    df = pd.read_csv(file_path)
    data = df.to_dict(orient='list')
    return jsonify(data)

if __name__ == '__main__':
    # Ensure the CSV_DIR exists
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)
    app.run(host='0.0.0.0', port=5000, debug=True)
