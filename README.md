# Automotive Parts Intelligence Tools

## Presented at ACPN 2025 - Autocare

This repository contains Streamlit applications designed to demonstrate how artificial intelligence can be leveraged to improve automotive parts search and fitment analysis in the aftermarket industry.

## How APIs Work

### What is an API?

An Application Programming Interface (API) is a set of rules that allows different software applications to communicate with each other. Think of it as a waiter in a restaurant:

1. **You (the client)** make a request from the menu
2. The **waiter (API)** takes your request to the kitchen
3. The **kitchen (server)** processes your request and prepares what you asked for
4. The **waiter (API)** brings back the response to you

### Key Components of API Communication

- **Endpoints**: Specific URLs where requests are sent
- **HTTP Methods**: GET (retrieve data), POST (send data), PUT (update data), DELETE (remove data)
- **Headers**: Metadata about the request, including authentication
- **Request Body**: Data sent to the server
- **Response**: Data received back from the server, typically in JSON format

## How We Utilize APIs

Our applications demonstrate integration with OpenAI's GPT-4 models through their REST API:

1. **Authentication**: We use API keys to authenticate requests to OpenAI's services
2. **Request Formation**: We structure requests with:
   - A clear system prompt defining the desired function
   - User input data (search queries or customer reviews)
   - Response format specifications (JSON)
3. **Response Processing**: We parse the structured JSON responses and present them in a user-friendly format

Key benefits of this architecture:

- **Modularity**: Easy to upgrade models or switch providers
- **Scalability**: Processing can happen in the cloud rather than locally
- **Rapid Innovation**: We can quickly integrate new AI capabilities as they become available

## Running the Code

### Prerequisites

- Python 3.8 or higher
- A valid OpenAI API key

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/ryexdev/ACPN2025.git
   cd ACPN2025
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

### Usage

1. Access the application through your web browser (typically at http://localhost:8501)
2. Enter your OpenAI API key when prompted (or set the environment variable `OwadmasdujU`)
3. Navigate to the desired tool using the sidebar
4. Follow the on-screen instructions for each tool

### Environment Variables

For security, we recommend setting your API key as an environment variable:

```
export OwadmasdujU=your_openai_api_key
```

## About the Authors

### Ryan Bachman
**CIO & VP Product**
**United Motor Products**

Ryan leverages technology to enhance automotive aftermarket operations and improve customer experiences. With extensive experience in building technology solutions for the automotive industry, Ryan focuses on implementing AI-driven processes to streamline parts identification and inventory management.

### Ryan Henderson
**Head of Data and Catalog**
**CarParts.com**

Ryan specializes in automotive data management, catalog optimization, and using data-driven approaches to solve complex fitment challenges. His expertise in building and maintaining comprehensive parts databases has helped transform how customers find the right parts for their vehicles.

## License

This project is provided for educational purposes as part of our presentation at ACPN 2025. Please contact the authors for permission before using in a production environment.
