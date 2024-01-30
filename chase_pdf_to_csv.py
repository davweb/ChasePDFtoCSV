"""Convert Chase Statement PDFs to CSV files"""

import argparse
import csv
from datetime import datetime
from pathlib import Path
import re
import sys
from collections import defaultdict
import pdfplumber


ACCOUNT_NAME_PATTERN = re.compile(r'^(.*) statement Account number: \d{8}', re.M)
TRANSACTION_PATTERN = re.compile(r'(\d{2} \w{3} \d{4})\s+(.*)\s+(\+|-)£([0-9,]+\.\d{2})\s-?£[0-9,]+\.\d{2}')


def get_pdf_text(file_path):
    """Get the text from PDF file"""

    try:
        with pdfplumber.open(file_path) as pdf:
            return '\n'.join(page.extract_text() for page in pdf.pages)
    except:
        return None

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
    return match.group(1) if match else None


def fatal_error(error):
    """Display error message and exit"""

    print(f'Error: {error}', file=sys.stderr)
    sys.exit(1)


def main():
    """Entry point"""

    parser = argparse.ArgumentParser('Convert Chase Statement PDFs to CSV files')
    parser.add_argument('-i', '--input',
                        help='folder containing input PDFs',
                        default='input', metavar='<folder>')
    parser.add_argument('-o', '--output',
                        help='folder for output CSVs',
                        default='output', metavar='<folder>')
    parser.add_argument('-a', '--archive',
                        help='if specified move PDFs to this folder once processed',
                        metavar='<folder>')

    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    archive_path = Path(args.archive) if args.archive else None

    if not input_path.is_dir():
        fatal_error(f'"{input_path}" is not a directory.')

    if not output_path.exists():
        output_path.mkdir()
    elif not output_path.is_dir():
        fatal_error(f'"{output_path}" is not a directory.')

    if archive_path:
        if not archive_path.exists():
            archive_path.mkdir()
        elif not archive_path.is_dir():
            fatal_error(f'"{archive_path}" is not a directory.')

    statements = [input_file for input_file in input_path.iterdir() if input_file.suffix.lower() == '.pdf']

    if len(statements) == 0:
        fatal_error(f'Did not find any PDF files in "{input_path}".')

    account_transactions = defaultdict(list)

    for statement_pdf in statements:
        pdf_text = get_pdf_text(statement_pdf)

        if pdf_text is None:
            fatal_error(f'Could not parse PDF File "{statement_pdf}".')

        account_name = find_account_name(pdf_text)

        if account_name is None:
            fatal_error(f'Could not find account details in PDF File "{statement_pdf}".')

        transactions = find_transactions(pdf_text)

        if len(transactions) == 0:
            fatal_error(f'Could not find any transactions in PDF File "{statement_pdf}".')

        account_transactions[account_name] += transactions

    for account_name, transactions in account_transactions.items():
        transactions.sort()

        start_date = transactions[0][0]
        end_date = transactions[-1][0]
        output_file = output_path / f'{account_name} - {start_date} to {end_date}.csv'

        with open(output_file, 'w', encoding='utf8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(transactions)

    if archive_path:
        for statement_pdf in statements:
            statement_pdf.rename(archive_path / statement_pdf.name)

    print(f'Processed {len(statements)} PDF file(s) and produced {len(account_transactions)} CSV file(s).')

if __name__ == "__main__":
    main()
