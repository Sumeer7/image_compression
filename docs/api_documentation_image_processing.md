
# API Documentation: Image Processing System

## 1. File Upload API

**Endpoint**: `/upload`  
**Method**: `POST`  
**Description**: This endpoint allows you to upload a CSV file for processing. The CSV is validated, and a unique `request_id` is generated for tracking the image processing status.

### Request:
- **Content-Type**: multipart/form-data  
- **Body**:  
    - `file`: The CSV file containing product information and image URLs.

### Response:
- **Status**: 201 Created  
- **Body**:  
    ```json
    {
      "message": "CSV uploaded successfully",
      "request_id": "req_20231008123456"
    }
    ```

### Error Responses:
- **400 Bad Request**:  
    ```json
    {
      "error": "CSV validation failed",
      "details": ["Missing columns: product name", "Invalid URL format in row 2"]
    }
    ```
- **500 Internal Server Error**:  
    ```json
    {
      "error": "Error description"
    }
    ```

## 2. Image Processing Webhook API

**Endpoint**: `/webhook/image-processing`  
**Method**: `POST`  
**Description**: This webhook is triggered once a CSV file is uploaded. It processes each image in the file and initiates background image compression.

### Request:
- **Content-Type**: application/json  
- **Body**:  
    ```json
    {
      "request_id": "req_20231008123456",
      "csv_data": [
        {
          "sr.no": 1,
          "product name": "Product A",
          "image URL": "https://example.com/image1.jpg"
        },
        {
          "sr.no": 2,
          "product name": "Product B",
          "image URL": "https://example.com/image2.jpg"
        }
      ]
    }
    ```

### Response:
- **Status**: 200 OK  
- **Body**:  
    ```json
    {
      "message": "Image processing initiated successfully"
    }
    ```

### Error Responses:
- **400 Bad Request**:  
    ```json
    {
      "error": "Invalid data"
    }
    ```
- **500 Internal Server Error**:  
    ```json
    {
      "error": "Error description"
    }
    ```

## 3. Request Status API

**Endpoint**: `/request/<request_id>`  
**Method**: `GET`  
**Description**: Fetches the status of an image processing request by its `request_id`. This helps track the progress of the CSV file processing.

### Path Parameter:
- `request_id` (string): The unique ID of the request.

### Response:
- **Status**: 200 OK  
- **Body**:  
    ```json
    {
      "request_id": "req_20231008123456",
      "status": "completed",
      "created_at": "2023-10-08T12:34:56",
      "updated_at": "2023-10-08T12:45:10"
    }
    ```

### Error Responses:
- **404 Not Found**:  
    ```json
    {
      "error": "Request not found"
    }
    ```
- **500 Internal Server Error**:  
    ```json
    {
      "error": "Error description"
    }
    ```

## Error Handling

In case of errors in any of the API endpoints, the server responds with a relevant HTTP status code (400, 500, etc.) and a JSON body containing the error message. Example structure:

```json
{
  "error": "Error message or description"
}
```

## Summary of Status Codes:
- 200 OK: The request was successful.
- 201 Created: Resource was successfully created (e.g., file uploaded).
- 400 Bad Request: Invalid input or missing required fields.
- 404 Not Found: Requested resource not found.
- 500 Internal Server Error: General server error.
