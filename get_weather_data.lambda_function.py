import json
import urllib.request
import boto3
import datetime

def lambda_handler(event, context):
    # OpenWeatherMap API key
    api_key = '1e31fbfe6f05acb7b406d0ec519eba08'
    
    # City & Country code
    city = 'Melbourne'
    country_code = 'au'
    
    #OpenWeatherMap API URL
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&appid={api_key}'
    
    try:
        # GET request to the API
        response = urllib.request.urlopen(url)
        
        # Reading the response and decoding it from bytes to a string
        data = response.read().decode('utf-8')
        
        # Parsing the JSON response
        weather_data = json.loads(data)
        
        # Extracting the relevant information from the JSON response
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        weather_description = weather_data['weather'][0]['description']
        
        # Storing the data as a weather data object with the relevant timestamp
        weather_object = {
            'datetime' : str(datetime.datetime.now()),
            'temperature': temperature,
            'humidity': humidity,
            'description': weather_description
        }
        
        # Retrieve existing data from the lambda-weather-data-store S3 bucket
        s3 = boto3.client('s3')
        bucket_name = 'lambda-weather-data-store'
        file_name = 'weather_data.json'
        try:
            existing_data = s3.get_object(Bucket=bucket_name, Key=file_name)
            existing_data_body = existing_data['Body'].read().decode('utf-8')
            if existing_data_body:
                existing_data_list = json.loads(existing_data_body)
            else:
                existing_data_list = []
        except s3.exceptions.NoSuchKey:
            existing_data_list = []
        
        # Append the new data to the existing list
        existing_data_list.append(weather_object)
        
        # Store the updated data back in the lambda-weather-data-store S3 bucket
        s3.put_object(Body=json.dumps(existing_data_list), Bucket=bucket_name, Key=file_name)
        
        return weather_object
    except Exception as e:
        # Error Handling during API call
        error_response = {
            'statusCode': 500,
            'body': str(e)
        }

        return error_response