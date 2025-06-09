# app.py
import os, uuid, json, base64, cv2, requests
from flask import Flask, request, send_file, jsonify, render_template, send_from_directory
from flask_cors import CORS
from redis import Redis
import rq
from rq.job import Job
from utils.tasks import process_image
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import time
load_dotenv()
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

app = Flask(__name__)
redis_conn = Redis(host='localhost', port=6379, db=0)
queue = rq.Queue('rooftop_detection', connection=redis_conn)
CORS(app)

@app.route('/map_view')
def map_view():
    return render_template('map_view.html', api_key=GOOGLE_MAPS_API_KEY)

@app.route('/temp/<filename>')
def serve_temp_file(filename):
    return send_from_directory('temp', filename)

@app.route('/geocode', methods=['POST'])
def geocode_address():
    address = request.json.get('address')
    
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(geocode_url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return jsonify({
                'status': 'success',
                'lat': location['lat'],
                'lng': location['lng']
            })
    
    return jsonify({'status': 'error', 'message': 'Could not geocode address'})

@app.route('/capture_image', methods=['POST'])
def capture_image():
    data = request.json
    image_data = data.get('imageData')
    crop_dimensions = data.get('cropDimensions')
    
    image_data = image_data.replace('data:image/png;base64,', '')
    
    image_bytes = base64.b64decode(image_data)
    img = Image.open(BytesIO(image_bytes))
    
    width = crop_dimensions.get('width')
    height = crop_dimensions.get('height')
    
    cropped_img = img.crop((0, 0, width, height))
    
    #Clean up the temp directory if file created more than 1 hour ago
    temp_dir = "temp"
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path):
            file_age = os.path.getmtime(file_path)
            if (time.time() - file_age) > 3600:  
                os.remove(file_path)

    temp_image_path = os.path.join("temp", f"{str(uuid.uuid4())}_satellite_capture.png")
    os.makedirs(os.path.dirname(temp_image_path), exist_ok=True)
    cropped_img.save(temp_image_path)
    
    return jsonify({
        'status': 'success',
        'image_path': temp_image_path
    })


@app.route('/detect_rooftops', methods=['POST'])
def detect_rooftops():
    print("Request files:", request.files)
    print("Request form:", request.form)
    
    if len(request.files) == 0:
        return jsonify({
            'error': 'No files uploaded',
            'details': 'Make sure you are sending the file with key "image" in form-data'
        }), 400
    
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image uploaded',
            'available_keys': list(request.files.keys()),
            'instructions': 'Use key "image" when uploading the file'
        }), 400
    
    uploaded_file = request.files['image']
    
    if uploaded_file.filename == '':
        return jsonify({
            'error': 'No selected file',
            'details': 'Filename is empty. Make sure you selected a valid image file'
        }), 400
    
    try:
        os.makedirs("temp", exist_ok=True)
        
        job_id = str(uuid.uuid4())
        
        temp_image_path = os.path.join("temp", f"{job_id}_{uploaded_file.filename}")
        uploaded_file.save(temp_image_path)
        print(f"Saved file to {temp_image_path}")
        
        # Test if file is a valid image
        test_image = cv2.imread(temp_image_path)
        if test_image is None:
            return jsonify({
                'error': 'Invalid image file',
                'details': 'The uploaded file could not be read as an image'
            }), 400
        
        print(f"Image validated, size: {test_image.shape}")
        
        # Queue the job
        try:
            job = queue.enqueue(
                process_image, 
                args=(temp_image_path, job_id),
                job_id=job_id,
                result_ttl=3600  # Keep job result for 1 hour
            )
            print(f"Job enqueued with ID: {job_id}")
            
            return jsonify({
                'status': 'processing',
                'job_id': job_id,
                'message': 'Your image is being processed. Check status at /job_status/{job_id}'
            }), 202
        except Exception as job_error:
            print(f"Error enqueueing job: {str(job_error)}")
            return jsonify({
                'error': 'Job queue error',
                'details': str(job_error)
            }), 500
    
    except Exception as e:
        import traceback
        print(f"Processing failed: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Processing failed',
            'details': str(e)
        }), 500

# Rest of the app.py code remains the same...
@app.route('/job_status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Check the status of a job"""
    try:
        # First check if the result is in Redis
        result_data = redis_conn.get(f"job_result:{job_id}")
        if result_data:
            result = json.loads(result_data)
            return jsonify(result), 200
        
        # If not in Redis, check job status in queue
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            if job.is_finished:
                return jsonify({
                    'status': 'completed',
                    'message': 'Job completed but results not found. They may have expired.'
                }), 200
            elif job.is_failed:
                return jsonify({
                    'status': 'failed',
                    'error': str(job.exc_info)
                }), 500
            else:
                return jsonify({
                    'status': 'processing',
                    'position_in_queue': job.get_position()
                }), 200
        except:
            return jsonify({
                'status': 'not_found',
                'message': f'No job found with ID {job_id}'
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': 'Error checking job status',
            'details': str(e)
        }), 500


@app.route('/get_result_image/<job_id>', methods=['GET'])
def get_result_image(job_id):
    try:
        #Clean the results directory if file created more than 1 hour ago
        results_dir = "results"
        for filename in os.listdir(results_dir):
            file_path = os.path.join(results_dir, filename)
            if os.path.isfile(file_path):
                file_age = os.path.getmtime(file_path)
                if (time.time() - file_age) > 3600:  
                    os.remove(file_path)


        # Check if job result exists
        result_data = redis_conn.get(f"job_result:{job_id}")
        if not result_data:
            return jsonify({'error': 'Job not found or results expired'}), 404
            
        # Get image path from job result
        result = json.loads(result_data)
        if 'image_path' not in result or result.get('status') != 'completed':
            return jsonify({'error': 'Result image not available'}), 404
            
        return send_file(result['image_path'], mimetype='image/png')
    except FileNotFoundError:
        return jsonify({'error': 'Result image file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_report/<job_id>', methods=['GET'])
def get_report(job_id):
    try:
        # Check if job result exists
        result_data = redis_conn.get(f"job_result:{job_id}")
        if not result_data:
            return jsonify({'error': 'Job not found or results expired'}), 404
            
        # Get report path from job result
        result = json.loads(result_data)
        if 'report_path' not in result or result.get('status') != 'completed':
            return jsonify({'error': 'Report not available'}), 404
            
        return send_file(result['report_path'], mimetype='text/plain')
    except FileNotFoundError:
        return jsonify({'error': 'Report file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Create required directories
    os.makedirs("temp", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    app.run(debug=True, port=5000)