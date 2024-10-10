import os
import threading
import uuid
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO
import http.server
import socketserver


class ImageModel:
    def __init__(self, MySQLConnection):
        self.db_connection = MySQLConnection
        self.db_connection.connect()

    def create_image(self, image_id, product_id, input_url, status):
        """Create a new image record."""
        created_at = datetime.utcnow()
        self.db_connection.insert(
            '''
            INSERT INTO images (id, product_id, input_url, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (image_id, product_id, input_url, status, created_at)
        )

    def get_image(self, image_id):
        """Retrieve an image record by image_id."""
        return self.db_connection.get(
            'SELECT id, product_id, input_url, status, created_at, updated_at FROM images WHERE id = %s',
            (image_id,)
        )

    def update_status(self, product_id, output_url):
        """Update an image's status and optionally its output URL."""
        self.db_connection.insert('''
            UPDATE images SET status = %s, output_url = %s WHERE product_id = %s
        ''', ('completed', output_url, product_id))

    import os

    def processing_image(self, input_url):
        """Compress an image from the given URL by 50%."""
        try:
            # Fetch the image from the URL
            response = requests.get(input_url)
            image = Image.open(BytesIO(response.content))

            # Calculate the new dimensions
            new_width = int(image.width * 0.5)
            new_height = int(image.height * 0.5)

            # Resize the image using LANCZOS filter
            compressed_image = image.resize((new_width, new_height), Image.LANCZOS)

            # Ensure the directory exists
            save_dir = os.getcwd()  # Save in the current working directory
            compressed_image_filename = f"compressed_{uuid.uuid4()}.jpg"
            compressed_image_path = os.path.join(save_dir, compressed_image_filename)

            # Save the compressed image to the file system
            compressed_image.save(compressed_image_path, format='JPEG', quality=50)
            print(f"Image saved and compressed at {compressed_image_path}")

            # Serve the image using a background thread
            PORT = 8000

            def start_server():
                # Change directory to the one where the image is saved
                os.chdir(save_dir)

                # Create handler for serving files
                Handler = http.server.SimpleHTTPRequestHandler

                with socketserver.TCPServer(("", PORT), Handler) as httpd:
                    print(f"Serving the image at http://localhost:{PORT}/{compressed_image_filename}")
                    httpd.serve_forever()

            # Run the server in a separate thread
            server_thread = threading.Thread(target=start_server)
            server_thread.daemon = True
            server_thread.start()

            def delete_image():
                try:
                    os.remove(compressed_image_path)
                    print(f"Image {compressed_image_path} deleted.")
                except Exception as e:
                    print(f"Error deleting image: {e}")

            # Schedule the image for deletion after 60 seconds
            delete_timer = threading.Timer(1, delete_image)
            delete_timer.start()

            # Return the path or URL where the image is served
            return f"http://localhost:{PORT}/{compressed_image_filename}"

        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def __del__(self):
        """Ensure the database connection is closed when the object is deleted."""
        self.db_connection.close()
