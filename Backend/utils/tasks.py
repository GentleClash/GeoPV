import os
import json
import cv2
from redis import Redis
from utils.detect import detect_rooftops_with_solar_potential

# Initialize Redis connection
redis_conn = Redis(host='localhost', port=6379, db=0)

def process_image(image_path, job_id):
    """
    Worker function that processes the image and stores results
    """
    try:
        print(f"Starting to process image: {image_path} for job: {job_id}")
        
        # Check if model file exists
        model_path = 'best.pt'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        print(f"Model file found, beginning detection")
        
        results = detect_rooftops_with_solar_potential(
            image_path, 
            model_path,
            conf_threshold=0.5,
            color_opacity=0.7
        )
        
        print(f"Detection completed, saving results")
        
        # Generate unique filenames for this job
        result_image_path = f"results/{job_id}_rooftop_detection_result.png"
        report_path = f"results/{job_id}_rooftop_solar_potential_report.txt"
        
        # Check if result files were created
        if not os.path.exists("rooftop_detection_result.png"):
            raise FileNotFoundError("Result image was not generated")
            
        if not os.path.exists("rooftop_solar_potential_report.txt"):
            raise FileNotFoundError("Report file was not generated")
        
        # Move the generated files to their job-specific paths
        os.makedirs("results", exist_ok=True)
        os.rename("rooftop_detection_result.png", result_image_path)
        os.rename("rooftop_solar_potential_report.txt", report_path)
        
        print(f"Files moved to: {result_image_path} and {report_path}")
        
        # Store the results with the job ID
        response = {
            'total_coverage_percentage': results['total_coverage_percentage'],
            'total_energy_potential': results['total_energy_potential'],
            'rooftops': results['rooftops'],
            'image_path': result_image_path,
            'report_path': report_path,
            'status': 'completed'
        }
        
        # Store results in Redis (with TTL of 1 hour)
        redis_conn.setex(f"job_result:{job_id}", 3600, json.dumps(response))
        print(f"Results stored in Redis for job: {job_id}")
        
        # Clean up the temporary image
        if os.path.exists(image_path):
            os.unlink(image_path)
            print(f"Temporary image deleted: {image_path}")
            
        return response
        
    except Exception as e:
        import traceback
        print(f"Error processing image: {str(e)}")
        print(traceback.format_exc())
        
        error_response = {
            'status': 'error',
            'error': str(e)
        }
        redis_conn.setex(f"job_result:{job_id}", 3600, json.dumps(error_response))
        
        # Clean up on error
        if os.path.exists(image_path):
            os.unlink(image_path)
            
        return error_response
