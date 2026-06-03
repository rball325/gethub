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
                const x = data[Object.keys(data)[0]];
                const traces = Object.keys(data).slice(1).map(key => ({
                    x: x,
                    y: data[key],
                    mode: 'lines',
                    name: key
                }));

                const layout = {
                    title: 'Interactive Line Graph',
                    xaxis: {
                        title: Object.keys(data)[0],
                        tickangle: -45,
                        automargin: true
                    },
                    yaxis: {
                        title: 'Values'
                    },
                    margin: { b: 120 }
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
