from flask import Flask, request, jsonify
import numpy as np
import requests

app = Flask(__name__)

# Funciones de cifrado y descifrado
def generate_key_pair(size):
    """Genera un par de claves (pública y privada) de tamaño dado."""
    max_attempts = 100  # Limitar intentos para evitar bucles infinitos
    attempts = 0

    while attempts < max_attempts:
        # Generar una matriz cuadrada con valores aleatorios
        public_key = np.random.randint(1, 20, (size, size))

        # Verificar que la matriz sea invertible
        determinant = np.linalg.det(public_key)
        if determinant != 0:  # Si el determinante no es cero, es invertible
            try:
                # Calcular la inversa de la matriz pública
                private_key = np.linalg.inv(public_key)

                # Convertir a listas y retornar
                return public_key.tolist(), private_key.tolist()
            except np.linalg.LinAlgError:
                # En caso de error al calcular la inversa, intentar de nuevo
                pass

        attempts += 1

    # Si no se encuentra una matriz válida después de varios intentos, lanzar un error
    raise ValueError(f"No se pudo generar una matriz invertible después de {max_attempts} intentos.")

#Resultado:
#	•	Clave Pública ( A ).
#	•	Clave Privada ( A^{-1} ).


def text_to_blocks(text, block_size):
    """Convierte un texto en bloques para cifrado matricial."""
    ascii_values = [ord(char) for char in text]
    padding = (block_size - len(ascii_values) % block_size) % block_size
    ascii_values.extend([0] * padding)
    blocks = [
        np.array(ascii_values[i:i + block_size]).reshape((int(block_size**0.5), -1))
        for i in range(0, len(ascii_values), block_size)
    ]
    return blocks

#Conversión a ASCII:
#	•	Convierte cada carácter del texto en su valor numérico ASCII con ord(char).
#	•	Ejemplo: "hola" → [104, 111, 108, 97].

def encrypt_blocks(blocks, public_key):
    """Cifra bloques usando una clave pública."""
    public_key_matrix = np.array(public_key)
    return [np.dot(public_key_matrix, block).tolist() for block in blocks]

#Si el tamaño del bloque es 4 (2 x 2), el texto "hola" se convierte en:

#M =
#104 & 111 \\
#108 & 97  \\

#Multiplicación Matricial:
#	•	Por cada bloque  M , calcula el producto:

#C = A * M

#np.dot(public_key_matrix, block) realiza la multiplicación matricial con alta precisión.


def decrypt_blocks(blocks, private_key):
    """Descifra bloques usando una clave privada."""
    private_key_matrix = np.array(private_key, dtype=np.float64)  # Aseguramos precisión
    decrypted_blocks = []

    for block in blocks:
        block_matrix = np.array(block, dtype=np.float64)  # Aseguramos precisión
        decrypted_block = np.round(np.dot(private_key_matrix, block_matrix)).astype(int)
        decrypted_blocks.append(decrypted_block)

    return decrypted_blocks


#Multiplicación con la Inversa:
#	•	Por cada bloque cifrado  C , calcula:

#M = A^{-1} * C

#Como  A^{-1}  y  C  contienen valores flotantes, los resultados se redondean con np.round() 
#se convierten a enteros con .astype(int) para evitar problemas con valores aproximados.

@app.route('/')
def index():
    """Ruta raíz para comprobar que el backend funciona."""
    return jsonify({
        'message': 'Backend Flask funcionando correctamente',
        'available_endpoints': [
            '/generate_keys',
            '/random_message',
            '/encrypt_message',
            '/decrypt_message'
        ]
    }), 200


@app.route('/generate_keys', methods=['GET'])
def generate_keys():
    """Genera y devuelve un par de claves (pública y privada)."""
    try:
        size = int(request.args.get('size', 4))
        public_key, private_key = generate_key_pair(size)
        return jsonify({
            'public_key': public_key,
            'private_key': private_key
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error al generar claves: {str(e)}'}), 500


@app.route('/encrypt_message', methods=['POST'])
def encrypt_message():
    """Cifra un mensaje con una clave pública."""
    try:
        data = request.get_json()
        message = data.get('message')
        public_key = data.get('public_key')

        if not message or not public_key:
            return jsonify({'error': 'Faltan parámetros (message, public_key).'}), 400

        block_size = len(public_key) ** 2
        blocks = text_to_blocks(message, block_size)
        encrypted_blocks = encrypt_blocks(blocks, public_key)
        return jsonify({'encrypted_message': encrypted_blocks}), 200
    except Exception as e:
        return jsonify({'error': f'Error al cifrar el mensaje: {str(e)}'}), 500


@app.route('/decrypt_message', methods=['POST'])
def decrypt_message():
    """Descifra un mensaje con una clave privada."""
    try:
        data = request.get_json()
        encrypted_message = data.get('encrypted_message')
        private_key = data.get('private_key')

        if not encrypted_message or not private_key:
            return jsonify({'error': 'Faltan parámetros (encrypted_message, private_key).'}), 400

        decrypted_blocks = decrypt_blocks(encrypted_message, private_key)
        decrypted_message = ''.join(
            chr(val) for block in decrypted_blocks for val in block.flatten() if val != 0
        )
        return jsonify({'decrypted_message': decrypted_message}), 200
    except Exception as e:
        return jsonify({'error': f'Error al descifrar el mensaje: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)