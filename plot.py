from flask import Flask, request, send_file, render_template_string
import pandas as pd
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
        <h1>CSV Line Graph Generator</h1>
        <form action="/plot" method="post" enctype="multipart/form-data">
            <label for="file">Choose a CSV file:</label>
            <input type="file" id="file" name="file">
            <input type="submit" value="Generate Line Graph">
        </form>
    ''')

@app.route('/plot', methods=['POST'])
def plot():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    df = pd.read_csv(file)

    # Assuming the first column is the x-axis and the rest are y-axis
    x = df.iloc[:, 0]
    for column in df.columns[1:]:
        plt.plot(x, df[column], label=column)

    plt.xlabel(df.columns[0])
    plt.ylabel('Values')
    plt.title('Line Graph')
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
