import pandas as pd


def validate_csv(file):
    """
    Validates a CSV file for proper formatting and data integrity.

    Args:
        file: File object of the uploaded CSV file.

    Returns:
        Tuple of (bool, list): Returns (True, []) if valid, or (False, list of errors).
    """
    errors = []

    try:
        df = pd.read_csv(file)

        # Check for required columns
        if df.empty or not all(col in df.columns for col in ['sr.no', 'product name', 'image URL']):
            errors.append("Invalid or missing columns: 'sr.no', 'product name', 'image URL'")
            return False, errors

        # Validate URL format (basic check for illustration, you can improve it)
        for index, row in df.iterrows():
            urls = row['image URL'].split(',')
            for url in urls:
                if not url.startswith('http'):
                    errors.append(f"Row {index + 1}: Invalid URL - {url}")

        return True, []

    except Exception as e:
        errors.append(f"Error reading CSV: {str(e)}")
        return False, errors