from flask import Flask, render_template, request, redirect, url_for, send_from_directory,send_file
import pandas as pd
import os
import seaborn as sns
from werkzeug.utils import secure_filename
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt
from time import time 

app = Flask(__name__,static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_csv_file(filepath):
    try:
        return pd.read_csv(filepath)
    except UnicodeDecodeError:
        return pd.read_csv(filepath, encoding='latin1')

@app.route('/summary/<filename>')
def summary(filename):
    # Ensure the file is allowed (based on its extension)
    if not allowed_file(filename):
        return redirect(url_for('index', error='Invalid file type'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Check if the file exists
    if not os.path.exists(filepath):
        return redirect(url_for('index', error='File not found'))

    # Attempt to read the CSV file
    try:
        data = read_csv_file(filepath)
    except Exception as e:
        # Handle file reading errors
        return redirect(url_for('index', error='Error reading file: ' + str(e)))

    # Proceed with generating summary statistics, visualizations, etc.
    # Make sure to end with a return statement that returns a valid response,
    # such as render_template or send_file.
    
    # Example:
    summary_stats = data.describe().to_html(classes='table table-striped table-bordered')
    return render_template('summary.html', summary_stats=summary_stats)

# Ensure the read_csv_file function also ends with a return statement
def read_csv_file(filepath):
    try:
        return pd.read_csv(filepath)
    except UnicodeDecodeError as e:
        # Handle specific exceptions or return a default value
        return pd.DataFrame()  # Return an empty DataFrame or handle as needed



@app.route('/dashboard')
def dashboard():
    # Your dashboard logic here
    return render_template('dashboard.html')


@app.route('/some-route')
def some_view_function():
    return render_template('visualize.html', current_time=time())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('visualize', filename=filename))
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/data_alteration/<filename>', methods=['GET', 'POST'])
def data_alteration(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    data = read_csv_file(filepath)
    
    if request.method == 'POST':
        if 'drop_duplicates' in request.form:
            data.drop_duplicates(inplace=True)
        if 'fill_na' in request.form:
            fill_value = request.form['fill_value']
            data.fillna(fill_value, inplace=True)
        # Save the altered data back to the file
        data.to_csv(filepath, index=False)
        return redirect(url_for('visualize', filename=filename))

    return render_template('data_alteration.html', data=data.to_html(), filename=filename)

@app.route('/visualize/<filename>', methods=['GET', 'POST'])
def visualize(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    data = read_csv_file(filepath)
    columns = data.columns.tolist()  # Get the list of columns

    if request.method == 'POST':
        chart_type = request.form.get('chart_type', 'bar')
        x_input = request.form.get('x_input')
        y_input = request.form.get('y_input')
        
        if x_input in data.columns and y_input in data.columns:
            if chart_type == 'bar':
                fig = px.bar(data, x=x_input, y=y_input)
            elif chart_type == 'line':
                fig = px.line(data, x=x_input, y=y_input)
            elif chart_type == 'scatter':
                fig = px.scatter(data, x=x_input, y=y_input)
            elif chart_type == 'pie':
                fig = px.pie(data, names=x_input, values=y_input)

            fig.update_layout(
                width=1400,
                height=800,
                xaxis_tickangle=-45,
                margin=dict(l=50, r=50, t=50, b=150),
                title=f'{chart_type.capitalize()} Chart of {x_input} vs {y_input}',
                xaxis_title=x_input,
                yaxis_title=y_input
            )

            graph_html = pio.to_html(fig, full_html=False)
            return render_template('visualize.html', data=data.to_html(classes='table table-striped table-bordered'), filename=filename, graph_html=graph_html, columns=columns)
    
    return render_template('visualize.html', data=data.to_html(classes='table table-striped table-bordered'), filename=filename, columns=columns)

    
   

@app.route('/graph_info')
def graph_info():
    return render_template('graph_info.html')

if __name__ == '__main__':
    app.run(debug=True)