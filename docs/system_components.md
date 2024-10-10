# System Components

## File Upload and Validation (API)
- Receives the CSV file.
- Validates the file format.
- Generates a unique request ID.
- Asynchronously initiates the image processing task.

## Image Processing
- Downloads the images from URLs provided in the CSV.
- Compresses the images to 50% quality.
- Uploads the processed images to a storage location (S3 or any other cloud service).
- Updates the database with input and output image URLs.

## Status Tracking
- Tracks the processing status (e.g., pending, in-progress, completed).
- Allows the user to check the status using the request ID.

## Webhook Integration
- Provides a mechanism to trigger a webhook when all images for a given request have been processed.

## Database
- Stores product information, input/output URLs, and processing statuses.

# Detailed Design

## 1. Database Schema Design
Given the requirements, the database needs to store products, image URLs, and track the status of processing. You can use either SQL or NoSQL depending on your performance and scaling needs. For this example, I’ll assume we’re using a SQL database.

### Tables

#### Requests Table (to track CSV file uploads)
- `id (UUID, Primary Key)` – Unique request ID for each file.
- `status (ENUM: pending, processing, completed, failed)` – The status of processing.
- `created_at (TIMESTAMP)` – When the request was created.
- `updated_at (TIMESTAMP)` – Last status update time.

#### Products Table (to track products in CSV)
- `id (UUID, Primary Key)` – Product unique identifier.
- `request_id (UUID, Foreign Key)` – Reference to the request in the Requests table.
- `product_name (VARCHAR)` – Name of the product.
- `created_at (TIMESTAMP)` – When the product was added.

#### Images Table (to track images for each product)
- `id (UUID, Primary Key)` – Unique image identifier.
- `product_id (UUID, Foreign Key)` – Reference to the product in the Products table.
- `input_image_url (TEXT)` – Original image URL.
- `output_image_url (TEXT)` – Processed image URL.
- `status (ENUM: pending, processing, completed, failed)` – Status of the image processing.
- `created_at (TIMESTAMP)` – When the image was created.
- `updated_at (TIMESTAMP)` – Last status update.

## 2. API Design

### Upload API
- **Endpoint:** `/upload`
- **Method:** `POST`
- **Request Body:** 
    - Form-data or JSON containing the CSV file.
- **Response:**
    - `request_id:` UUID generated for the file.
- **Tasks:**
    - Validate CSV format.
    - Create entries in requests, products, and images tables.
    - Return request_id to the user.
    - Initiate asynchronous processing (trigger worker).

### Status API
- **Endpoint:** `/status/{request_id}`
- **Method:** `GET`
- **Response:**
    - Returns processing status of the request (pending, in-progress, completed).
    - Returns a list of processed image URLs if completed.

### Webhook API
- **Endpoint:** `/webhook`
- **Method:** `POST`
- **Request Body:**
    - Contains `request_id` and `status`.
- **Tasks:**
    - Triggered when all images for a particular request have been processed.
