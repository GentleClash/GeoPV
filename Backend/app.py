import os
import tempfile
from flask import Flask, request, send_file, jsonify
import cv2
from flask_cors import CORS
from utils.detect import detect_rooftops_with_solar_potential

app = Flask(__name__)
CORS(app) 


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
    
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.filename)[1]) as temp_file:
        uploaded_file.save(temp_file.name)
        temp_image_path = temp_file.name
    
    try:
        test_image = cv2.imread(temp_image_path)
        if test_image is None:
            return jsonify({
                'error': 'Invalid image file',
                'details': 'The uploaded file could not be read as an image'
            }), 400
        
        
        model_path = 'best.pt'
        
        
        results = detect_rooftops_with_solar_potential(
            temp_image_path, 
            model_path,
            conf_threshold=0.5,
            color_opacity=0.7
        )
        
       
        report_path = 'rooftop_solar_potential_report.txt'
        
        
        response = {
            'total_coverage_percentage': results['total_coverage_percentage'],
            'total_energy_potential': results['total_energy_potential'],
            'rooftops': results['rooftops']
        }
        
        
        return jsonify({
            'analysis': response,
            'image': 'rooftop_detection_result.png',
            'report': report_path
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Processing failed',
            'details': str(e)
        }), 500
    
    finally:
        if os.path.exists(temp_image_path):
            os.unlink(temp_image_path)

@app.route('/get_result_image', methods=['GET'])
def get_result_image():
    try:
        return send_file('rooftop_detection_result.png', mimetype='image/png')
    except FileNotFoundError:
        return jsonify({'error': 'Result image not found'}), 404

@app.route('/get_report', methods=['GET'])
def get_report():
    try:
        return send_file('rooftop_solar_potential_report.txt', mimetype='text/plain')
    except FileNotFoundError:
        return jsonify({'error': 'Report not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)