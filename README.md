# Zoom Group Manager API (MVP)
## Overview
This project provides a simple interface for managing Zoom users via the Zoom API. Built with FastAPI, it aims to offer rapid setup and execution, catering to developers and administrators looking to streamline their Zoom user management processes. The API focuses on managing user groups efficiently, adhering to Zoom's least privilege methodology.

### Example Usecase
Zoom implements a least privilege methodology, which means that users are assigned to groups with specific permissions. This API can be used to automate the process of adding and removing users from groups, ensuring that users have the appropriate permissions at all times.

## Getting Started
### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn (for running the API server)
### Installation
Clone this repository:
```bash
git clone https://github.com/jbhoorasingh/zoom-group-manager-api.git
```

Navigate to the project directory:
```bash
cd zoom-user-management-api
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

Running the API
Execute the following command to run the API server:
```bash
uvicorn app.main:app --reload
```


## Using the API
Access the interactive API documentation provided by FastAPI at http://127.0.0.1:8000/docs to test and explore the available API endpoints.

## Contributing
Contributions to the Zoom User Management API are welcome! Please refer to CONTRIBUTING.md for guidelines on how to make a contribution.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This project is not affiliated with or endorsed by Zoom Video Communications, Inc.

