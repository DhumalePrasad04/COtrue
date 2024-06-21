from flask import Flask, request, jsonify, render_template
import subprocess
from threading import Timer
import os
import tempfile
import time
import psutil

app = Flask(__name__)

CARBON_INTENSITY = 715  

def estimate_carbon_emission_manual(duration):

    
    duration_hours = duration / 3600
    server_power_kw = 0.2  
    energy_consumption_kwh = server_power_kw * duration_hours
    carbon_emission = energy_consumption_kwh * CARBON_INTENSITY / 1000  
    return carbon_emission

@app.route('/')  
# add funtionalities to the function without changing the source code :decorators
def index():
    return render_template('index.html')

@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data['code']
    language = data['language']
    compare_code = data.get('compareCode')  

    temp_dir = tempfile.mkdtemp()
    source_file = os.path.join(temp_dir, f'code.{language}')
    compare_source_file = os.path.join(temp_dir, f'compare_code.{language}')  

    try:
        with open(source_file, 'w') as f:
            f.write(code)
        
        if compare_code:  
            with open(compare_source_file, 'w') as f:
                f.write(compare_code)
        
       
        start_time = time.time()
        if language == 'python':
            result = subprocess.run(['python', source_file], capture_output=True, text=True)
        elif language == 'c':
            executable = os.path.join(temp_dir, 'a.out')
            compile_result = subprocess.run(['gcc', source_file, '-o', executable], capture_output=True, text=True) 
            if compile_result.returncode != 0:
                return jsonify({'error': f'Compilation failed: {compile_result.stderr}'}), 400
            result = subprocess.run([executable], capture_output=True, text=True)
        else:
            return jsonify({'error': 'Unsupported language'}), 400
        end_time = time.time()
        duration = end_time - start_time
        carbon_emission = estimate_carbon_emission_manual(duration)

        response_data = {
            'output': result.stdout or result.stderr,
            'carbonEmission': carbon_emission
        }

        if compare_code:
            
            start_time_compare = time.time()
            if language == 'python':
                compare_result = subprocess.run(['python', compare_source_file], capture_output=True, text=True)
            elif language == 'c':
                compare_executable = os.path.join(temp_dir, 'compare_a.out')
                compile_result = subprocess.run(['gcc', compare_source_file, '-o', compare_executable], capture_output=True, text=True) 
                if compile_result.returncode != 0:
                    return jsonify({'error': f'Compilation failed for the compare code: {compile_result.stderr}'}), 400
                compare_result = subprocess.run([compare_executable], capture_output=True, text=True)
            end_time_compare = time.time()
            duration_compare = end_time_compare - start_time_compare
            compare_carbon_emission = estimate_carbon_emission_manual(duration_compare)
            response_data['compareOutput'] = compare_result.stdout or compare_result.stderr
            response_data['compareCarbonEmission'] = compare_carbon_emission
            response_data['betterCode'] = 'code' if carbon_emission < compare_carbon_emission else 'compare_code'

        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        os.remove(source_file)
        if compare_code:
            os.remove(compare_source_file)
        if language == 'c':
            executable = os.path.join(temp_dir, 'a.out')
            if os.path.exists(executable):
                os.remove(executable)
            if compare_code:
                compare_executable = os.path.join(temp_dir, 'compare_a.out')
                if os.path.exists(compare_executable):
                    os.remove(compare_executable)
        os.rmdir(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
