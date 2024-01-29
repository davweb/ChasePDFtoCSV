import pdfplumber
import os
import re
import csv
from datetime import datetime, timedelta
import shutil
import sys

# ACCOUNT_NUMBER = re.compile(r'Account number: (\d+)')
TRANSACTION_PATTERN = re.compile(r'(\d{2} \w{3} \d{4})\s+(.*)\s+(\+|-)£([0-9,]+\.\d{2})\s-?£[0-9,]+\.\d{2}')

def get_pdf_text(file_path):
    with pdfplumber.open(file_path) as pdf:
        return '\n'.join(page.extract_text() for page in pdf.pages)

def find_transactions(text):
    transactions = []

    for (date, payee, sign, amount) in TRANSACTION_PATTERN.findall(text):
        date = datetime.strptime(date, '%d %b %Y').date()

        if sign == '-':
            amount = sign + amount

        transactions.append((date, payee, amount))

    return transactions

#main

active_folder_path = 'Active'
output_path = 'Output'
destination_folder = 'Processed'


active_files = os.listdir(active_folder_path)
active_file_name = active_files[0]
active_file_path = os.path.join(active_folder_path, active_file_name)

pdf_desired_text = get_pdf_text(active_file_path)
transactions = find_transactions(pdf_desired_text)

# Export the data to a CSV file
today = transactions[0][0]
year = today.year
month = today.month
DesiredCSVName = f"{year}-{month:02d}"

output_file = fr"{output_path}/{DesiredCSVName}.csv"

with open(output_file, 'w') as csvfile:
    csv_writer = csv.writer(csvfile)

    for row in transactions:
        csv_writer.writerow(row)



shutil.move(active_file_path, destination_folder)
