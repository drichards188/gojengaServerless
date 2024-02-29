# Gojenga Serverless Backend

## About The Project
***
Gojenga is a web application inspired by financial dashboards like Schwab. It offers limited portfolio, risk, and diversification features. The backend of this application is built using AWS Api Gateway, Lambda, and RDS, making it a cloud-native solution.

## Built With
- Python
- AWS Api Gateway
- AWS Lambda
- AWS RDS

## Architecture
The backend architecture of Gojenga is broken down into microservices. Each microservice is responsible for a specific functionality, making the system modular and scalable. The microservices communicate with each other via API calls.

## Code Structure
The codebase is divided into different Python scripts, each handling a specific task. For instance, `risk/get_all_sharpe_symbols/lambda_function.py` is responsible for fetching all symbols from the sharpe_calc database. Similarly, `misc/db_proxy/lambda_function.py` acts as a proxy for database operations.

## Running the Project
To run the project, you need to set up the necessary environment variables such as `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`, and `TOKEN`. Set up the appropriate Api Gateway endpoints and deploy the Lambda functions.

## Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.