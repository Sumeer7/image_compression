# MySQL Database Setup Guide

This guide will help you set up the MySQL database locally for the application.

## Prerequisites

- **MySQL Server**: Ensure you have MySQL Server installed on your machine. You can download it from the [official MySQL website](https://dev.mysql.com/downloads/mysql/).

- **Python**: Make sure you have Python installed. You can download it from the [official Python website](https://www.python.org/downloads/).

- **Required Python Packages**: Install the required packages using pip. You can install them using the following command:

    ```bash
    pip install -r requirements.txt
    ```

## Database Configuration

Before running the application, you need to configure the database connection settings.

1. Navigate to the `db` folder where your project is located.
2. Open the `config.properties` file and update the database connection details as follows:

    ```properties
    [database]
    host=localhost
    user=your_username
    password=your_password
    database=your_database_name
    ```

   Replace the placeholder values:
   - `your_username`: Your MySQL username (e.g., `root`).
   - `your_password`: Your MySQL password.
   - `your_database_name`: The name of the database you want to use.

## Creating the Database and Tables

1. Start your MySQL Server.
2. Open a terminal or command prompt and log in to MySQL using the following command:

    ```bash
    mysql -u your_username -p
    ```

   Enter your password when prompted.

3. Create a new database for your application (if it doesn't already exist):

    ```sql
    CREATE DATABASE your_database_name;
    ```

4. Exit the MySQL prompt:

    ```sql
    EXIT;
    ```

## Running the Application

Once the database is set up and the configuration file is updated, you can run the application. Make sure to connect to the database using the configured settings.

### Example Command to Run the Application

```bash
python run.py
