# data-preprocessing
# Data Preprocessing Web App

A simple and interactive Flask-based web application to upload, preview, clean, and preprocess CSV data files. It helps you transform messy datasets by cleaning column names, handling missing values, detecting and converting data types, and previewing processed data before download.

---

## Features

- Upload CSV files with ease
- Clean column names (remove special chars, lowercase, etc.)
- Preview first few rows of uploaded data
- Detect and convert date columns automatically
- Identify and convert number-like string columns
- Handle missing values with options (mean, median, mode, or custom value)
- Remove duplicate rows
- Preview cleaned data with stats (rows, columns)
- Download processed CSV file
- Beautiful, responsive UI with file preview and interaction

---

## Tech Stack

- Python 3.x  
- Flask  
- Pandas  
- HTML, CSS (custom styles)

---

## Installation

1. Clone the repo:
git clone https://github.com/yourusername/data-preprocessing.git
cd data-preprocessing
2.(Optional) Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3.Install dependencies:
pip install -r requirements.txt
4.Run the app:
flask run
5.Open your browser and visit: http://localhost:5000
