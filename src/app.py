from flask import Flask, request, jsonify, render_template
from evaluate import evaluate
from helpers import read_local_keys, read_instructions
import logging
import traceback

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['searchTerm']
    logging.info(f"Received search term: {search_term}")

    try:
        keys = read_local_keys()
        logging.info("Keys successfully read.")
    except Exception as e:
        logging.error(f"Error reading keys: {e}")
        return jsonify({'status': 'error', 'message': 'Error reading keys. Please check the keys configuration.'})

    try:
        instructions = read_instructions()
        logging.info("Instructions successfully read.")
    except Exception as e:
        logging.error(f"Error reading instructions: {e}")
        return jsonify({'status': 'error', 'message': 'Error reading instructions. Please check the instructions configuration.'})

    try:
        result = evaluate(search_term, keys, instructions)
        logging.info(f"Evaluation completed successfully. Result: {result}")
        logging.info(f"Returning result: {result}")
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        logging.error(f"Error during evaluation: {e}")
        logging.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': f'Error during evaluation: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
