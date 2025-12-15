from flask import Flask, render_template, request, send_from_directory
import os
import math
import arithmetic
import limpell_ziv
from decimal import localcontext

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')

def calculate_efficiency(original_text, compressed_binary):
    if not original_text: return 0, 0, 0
    unique_chars = len(set(original_text))
    
    if unique_chars < 2: 
        bits_per_symbol = 1
    else: 
        bits_per_symbol = math.ceil(math.log2(unique_chars))
    
    fixed_len = len(original_text) * bits_per_symbol
    compressed_len = len(compressed_binary)
    
    if fixed_len == 0: return 0, compressed_len, fixed_len
    
    efficiency = (compressed_len / fixed_len) * 100
    return efficiency, compressed_len, fixed_len

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/arithmetic', methods=['GET', 'POST'])
def arithmetic_page():
    # ... (Arithmetic code remains unchanged) ...
    result = None
    error = None
    mode = 'encoder' 
    input_text = ''      
    binary_input = ''    

    if request.method == 'POST':
        mode = request.form.get('mode')
        try:
            with localcontext() as ctx:
                ctx.prec = 5000
                if mode == 'encoder':
                    text = request.form.get('text_input', '')
                    input_text = text 
                    if not text: raise ValueError("Input text cannot be empty.")
                    unique_symbols = set(text)
                    model = arithmetic.AdaptiveModelGeneral(unique_symbols)
                    encoder = arithmetic.ArithmeticEncoder()
                    low, high = encoder.encode(text, model)
                    binary_output = arithmetic.finish_encoding(low, high)
                    efficiency, comp_len, fix_len = calculate_efficiency(text, binary_output)
                    result = {
                        'type': 'encoding',
                        'binary': binary_output,
                        'efficiency': round(efficiency, 2),
                        'unique_symbols': "".join(sorted(list(unique_symbols))),
                        'length': len(text),
                        'comp_len': comp_len,   
                        'fix_len': fix_len      
                    }
                elif mode == 'decoder':
                    binary = request.form.get('binary_input', '')
                    binary_input = binary 
                    length = request.form.get('length_input', 0)
                    alphabet = request.form.get('alphabet_input', '')
                    if not binary or not length or not alphabet:
                        raise ValueError("All fields are required for decoding.")
                    length = int(length)
                    model = arithmetic.AdaptiveModelGeneral(set(alphabet))
                    decimal_val = arithmetic.binary_to_decimal(binary)
                    decoder = arithmetic.ArithmeticDecoder(decimal_val, length)
                    decoded_text = decoder.decode(model)
                    result = {'type': 'decoding', 'text': decoded_text}
        except Exception as e:
            error = str(e)
    return render_template('arithmetic.html', result=result, error=error, mode=mode, input_text=input_text, binary_input=binary_input)

@app.route('/limpell_ziv', methods=['GET', 'POST'])
def limpell_ziv_page():
    result = None
    error = None
    mode = 'encoder'
    input_text = '' 

    if request.method == 'POST':
        mode = request.form.get('mode')
        try:
            if mode == 'encoder':
                text = request.form.get('text_input', '')
                input_text = text 
                
                if not text: raise ValueError("Input cannot be empty")
                
                # Removed idx_bits from return
                binary_output, alphabet_str = limpell_ziv.lz78_encode(text)
                
                efficiency, comp_len, fix_len = calculate_efficiency(text, binary_output)
                
                result = {
                    'type': 'encoding',
                    'binary': binary_output,
                    'efficiency': round(efficiency, 2),
                    # 'index_bits': Removed
                    'comp_len': comp_len,
                    'fix_len': fix_len,
                    'length': len(text), 
                    'unique_symbols': alphabet_str 
                }
                
            elif mode == 'decoder':
                binary = request.form.get('binary_input', '')
                # Removed index_bits input reading
                alphabet = request.form.get('alphabet_input', '')
                
                if not alphabet:
                    raise ValueError("Alphabet is required.")

                decoded_text = limpell_ziv.lz78_decode(binary, alphabet)
                
                result = {
                    'type': 'decoding',
                    'text': decoded_text
                }
                
        except Exception as e:
            error = str(e)

    return render_template('limpell_ziv.html', result=result, error=error, mode=mode, input_text=input_text)

if __name__ == '__main__':
    app.run(debug=True)