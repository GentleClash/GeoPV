# app.py
import os
import tempfile
import time
import uuid
import json
from flask import Flask, request, send_file, jsonify
import cv2
from flask_cors import CORS
from redis import Redis
import rq
from rq.job import Job
from utils.tasks import process_image 

app = Flask(__name__)
CORS(app)

# Initialize Redis and RQ
redis_conn = Redis(host='localhost', port=6379, db=0)
queue = rq.Queue('rooftop_detection', connection=redis_conn)


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
        # Create a directory for temporary files if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded file with job ID in the filename
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
    app.run(debug=True)