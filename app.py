from flask import Flask, render_template, request,send_file
import pandas as pd
import numpy as np
import os
import io

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

processed_data = {}  # ✅ Store DataFrame temporarily

# ✅ Clean column names
def clean_column_names(df):
    clean_columns = []
    for col in df.columns:
        col = col.strip().lower()
        col = ''.join(char for char in col if char.isalnum() or char == ' ')
        col = col.replace(' ', '_')
        clean_columns.append(col)
    df.columns = clean_columns
    return df

# ✅ Clean string values
def clean_string_data(df):
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].apply(
            lambda x: ''.join(char for char in str(x).strip().lower() if pd.notna(x) and (char.isalnum() or char == ' '))
            if pd.notna(x) else np.nan
        )
    return df
# ✅ Detect number-like string columns


def check_null_columns(df):
    null_cols = df.columns[df.isnull().any()].tolist()
    null_details = []
    for col in null_cols:
        null_count = df[col].isnull().sum()
        col_type = 'numeric' if pd.api.types.is_numeric_dtype(df[col]) else 'categorical'
        null_details.append({'column': col, 'null_count': null_count, 'type': col_type})
    return null_details

def detect_and_convert_dates(df, sample_size=20):
    for col in df.columns:
        # Only check columns with object dtype (strings), ignore numeric columns completely
        if df[col].dtype == 'object':
            sample = df[col].dropna().head(sample_size)
            if sample.empty:
                continue

            success_count = 0
            for val in sample:
                try:
                    pd.to_datetime(val, errors='raise', infer_datetime_format=True)
                    success_count += 1
                except Exception:
                    pass

            if success_count / len(sample) >= 0.7:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    print(f"Converted '{col}' to datetime")
                except Exception:
                    pass

    return df




@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file part in request")
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        print("No file selected")
        return 'No selected file', 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='latin1', low_memory=False)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return f"Error reading CSV: {e}", 400


    # ✅ Read CSV
    

    # ✅ Step 1: Clean column names
    df = clean_column_names(df)

    # ✅ Step 2: Clean string data
    df = clean_string_data(df)

    # ✅ Step 3: Drop duplicate rows
    df = df.drop_duplicates()

    # ✅ Step 4: Detect and convert dates
    df = detect_and_convert_dates(df)

    # ✅ Step 5: Check null columns
    null_columns = check_null_columns(df)

    # ✅ Store dataframe and file path
    processed_data['df'] = df.copy()
    processed_data['file_path'] = file_path

    # ✅ Final Decision:
    if not null_columns:
        # No null values, show preview directly
        table_html = df.head(10).to_html(classes='table', index=False)
        return render_template('preview.html', table=table_html)

    # If null values present, go to upload.html and show them
    return render_template('upload.html', null_columns=null_columns)

    

   


@app.route('/convert', methods=['POST'])
def convert_columns():
    df = processed_data.get('df')

    if df is None:
        return 'No data found. Please upload a file first.', 400

    selected_cols = [col for col in request.form if request.form.get(col) == 'yes']

    for col in selected_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
@app.route('/handle_nulls', methods=['POST'])
def handle_nulls():
    df = processed_data.get('df')
    if df is None:
        return 'No Data Found', 400

    for col in df.columns[df.isnull().any()]:
        option = request.form.get(f"{col}_option")
        custom_value = request.form.get(f"{col}_custom")
        if option == 'mean':
            df[col].fillna(df[col].mean(), inplace=True)
        elif option == 'median':
            df[col].fillna(df[col].median(), inplace=True)
        elif option == 'mode':
            df[col].fillna(df[col].mode()[0], inplace=True)
        elif option == 'custom' and custom_value != '':
            if pd.api.types.is_numeric_dtype(df[col]):
                try:
                    custom_value = float(custom_value)
                except ValueError:
                    continue
            df[col].fillna(custom_value, inplace=True)

    processed_data['df'] = df.copy()

    table_html = df.head(10).to_html(classes='table', index=False)
    return render_template('preview.html', table=table_html)

@app.route('/download')
def download_file():
     df = processed_data.get('df')
     file_path = processed_data.get('file_path')

    
     if df is None:
        return "No data to download", 400

     csv_io = io.StringIO()
     df.to_csv(csv_io, index=False)
     csv_io.seek(0)


     if file_path and os.path.exists(file_path):
        os.remove(file_path)
     processed_data.clear() 

     return send_file(
        io.BytesIO(csv_io.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='processed_data.csv'
    )



if __name__ == '__main__':
    app.run(debug=True)
