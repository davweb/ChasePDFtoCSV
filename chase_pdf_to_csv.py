"""Convert Chase Statement PDFs to CSV files"""

import csv
from datetime import datetime
import os
import re
import shutil
from collections import defaultdict
import pdfplumber


ACCOUNT_NAME_PATTERN = re.compile(r'^(.*) statement Account number: \d{8}', re.M)
TRANSACTION_PATTERN = re.compile(r'(\d{2} \w{3} \d{4})\s+(.*)\s+(\+|-)£([0-9,]+\.\d{2})\s-?£[0-9,]+\.\d{2}')


def get_pdf_text(file_path):
    """Get the text from PDF file"""

    with pdfplumber.open(file_path) as pdf:
        return '\n'.join(page.extract_text() for page in pdf.pages)


def find_transactions(text):
    """Find the transactions in the text of a Chase statement"""
    transactions = []

    for (date, payee, sign, amount) in TRANSACTION_PATTERN.findall(text):
        date = datetime.strptime(date, '%d %b %Y').date()

        if sign == '-':
            amount = sign + amount

        transactions.append((date, payee, amount))

    return transactions


def find_account_name(text):
    """Find the Chase account name in the statement text"""

    match = ACCOUNT_NAME_PATTERN.search(text)
    return match.group(1)


def main():
    """Entry point"""

    active_folder_path = 'Active'
    output_path = 'Output'
    destination_folder = 'Processed'

    active_files = os.listdir(active_folder_path)
    account_transactions = defaultdict(list)

    for active_file_name in active_files:
        active_file_path = os.path.join(active_folder_path, active_file_name)
        pdf_text = get_pdf_text(active_file_path)
        account_name = find_account_name(pdf_text)
        account_transactions[account_name] += find_transactions(pdf_text)
        shutil.move(active_file_path, destination_folder)

    for account_name, transactions in account_transactions.items():
        transactions.sort()

        start_date = transactions[0][0]
        end_date = transactions[-1][0]
        output_file = f'{output_path}/{account_name} - {start_date} to {end_date}.csv'

        with open(output_file, 'w', encoding='utf8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(transactions)


if __name__ == "__main__":
    main()
