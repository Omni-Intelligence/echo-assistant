# Echo Assist

A simple Python-based assistant for processing and responding to user queries through an HTTP interface.

## Features

* RESTful API endpoint for query processing
* Simple and lightweight implementation
* Easy to extend and customize

## Requirements

* Python 3.8+
* Flask
* Additional dependencies listed in `requirements.txt`

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Start the server:
```bash
python app.py
```

The server will be available at `http://localhost:5000`

## API

Send POST requests to `/query` endpoint:
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "your question here"}'
```

## License

MIT License
