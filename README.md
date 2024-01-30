# chase-pdf-to-csv
As Chase UK don't offer an option to download transactions in any other format than PDF statements, this script will extract transactions from PDF files and write them to CSV files.  This for occasions where you can't use [Open Banking](https://www.chase.co.uk/gb/en/support/open-banking/).

The script will read transactions from multiple PDFs and create one CSV file per account.

## How to Use
1. Checkout this repository.
2. Set up a python virtual environment with:

    ```
    python -m venv --prompt chase-pdf-to-csv .venv
    ```

3. Source the virtual environment with:

    ```
    source .venv/bin/activate
    ```

4. Install required packages using `pip`:

    ```
    pip install pip-tools
    pip-compile requirements.in
    pip-sync
    ```

5. Create a directory called `input` in the same directory as the script and put the relevant PDF files there.  (The input directory can be changed through command line options.)

6. Run the script with:

    ```
    python chase_pdf_to_csv.py
    ```
7. The CSV files will in the the `output` directory.

## Options

The command line options available to the script are shown below.

| Option | Description | Default |
| ------ | ------ | ------ |
| `-h`, `--help` | Show the help message. | |
  `-i <folder>`, `--input <folder>` | Folder containing input PDFs | `input` |
  `-o <folder>`, `--output <folder>` | Folder for output CSVs | `output` |
  `-a <folder>`, `--archive <folder>` | If specified move PDFs to this folder once processed |
