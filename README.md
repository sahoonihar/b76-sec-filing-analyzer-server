# README

## Dependencies
- Python3.8
- MongoDB v5.0.2
- Sec API (<a href="https://pypi.org/project/sec-api/">sec-api</a>)
- YFinance (<a href="https://pypi.org/project/yfinance/">yfinance</a>)

## Installation and setup
- Clone the repository
- Create a new virtual environment in Python using the command
```
python3 -m venv .env
```
- Install Python dependencies using the command 
```
pip install requirements.txt
```
- Load the data into the database using the command
```
python3 loaddb.py <path_to_data_directory>
```
- Run the command
```
uvicorn main:app --reload
```
- The server will start running on **http://127.0.0.1:8000**



