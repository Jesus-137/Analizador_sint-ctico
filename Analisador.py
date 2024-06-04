from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# Palabras clave y símbolos
KEYWORDS = {"for", "int", "System.out.println"}
SYMBOLS = {"(", ")", "{", "}", "=", "<=", ";", "+", "."}

def tokenize(code):
    # Dividir el código en tokens utilizando expresiones regulares
    tokens = re.findall(r'[A-Za-z_]\w*|==|<=|>=|!=|[{}();=+.]', code)
    return tokens

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze_lexical', methods=['POST'])
def analyze_lexical():
    code = request.form['code']
    tokens = tokenize(code)
    lexical_result = "\n".join([f"Token: {token}" for token in tokens])
    return jsonify(lexical_result=lexical_result)

@app.route('/analyze_syntactic', methods=['POST'])
def analyze_syntactic():
    code = request.form['code']
    lines = code.splitlines()
    errors = []

    # Verificar estructura básica del bucle for
    for_found = False
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith("for "):  # Espacio después de "for" para evitar palabras similares
            for_found = True
            # Verificar que la estructura del for es correcta
            if not stripped_line.endswith("{"):
                errors.append(f"Error en la línea {i + 1}: La declaración del 'for' debe terminar con '{{'.")
            # Verificar que tiene los paréntesis correctos
            if stripped_line.count('(') != 1 or stripped_line.count(')') != 1:
                errors.append(f"Error en la línea {i + 1}: La declaración del 'for' debe tener paréntesis correctos.")
            # Verificar que contiene los punto y coma correctos
            for_parts = stripped_line[stripped_line.find('(') + 1:stripped_line.find(')')].split(';')
            if len(for_parts) != 3:
                errors.append(f"Error en la línea {i + 1}: La declaración del 'for' debe contener dos punto y coma.")
            else:
                # Verificar la primera parte de la declaración del for
                for_part_1 = for_parts[0].strip()
                if not for_part_1.startswith("int "):
                    errors.append(f"Error en la línea {i + 1}: La declaración del 'for' debe comenzar con 'int'. Encontrado: {for_part_1}")
                else:
                    # Verificar que hay una variable después de 'int'
                    variable_declaration = for_part_1.split(" ")
                    if len(variable_declaration) < 2 or not variable_declaration[1].replace("=", "").strip().isidentifier():
                        errors.append(f"Error en la línea {i + 1}: Se esperaba una variable después de 'int'. Encontrado: {for_part_1}")
                # Verificar la segunda parte de la declaración del for
                for_part_2 = for_parts[1].strip()
                if not for_part_2 or not re.match(r'^[a-zA-Z_]\w*\s*[<=>!]+\s*\w*$', for_part_2):
                    errors.append(f"Error en la línea {i + 1}: La condición del 'for' es incorrecta o falta un valor. Encontrado: {for_part_2}")
                # Verificar la tercera parte de la declaración del for
                for_part_3 = for_parts[2].strip()
                if not any(op in for_part_3 for op in ["++", "--", "+=", "-="]):
                    errors.append(f"Error en la línea {i + 1}: La actualización del 'for' es incorrecta. Encontrado: {for_part_3}")

    if not for_found:
        errors.append("Error: Falta la declaración del bucle 'for'.")

    # Verificar que las llaves y paréntesis estén balanceados
    if code.count("{") != code.count("}") or code.count("(") != code.count(")"):
        errors.append("Error: Llaves o paréntesis desbalanceados.")

    # Verificar punto y coma al final de las líneas (excepto líneas con '{', '}', 'for', 'if', etc.)
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line and not stripped_line.endswith(";") and not stripped_line.endswith("{") and not stripped_line.endswith("}") and not stripped_line.startswith("for"):
            errors.append(f"Error en la línea {i + 1}: Falta punto y coma al final de la línea.")

    # Verificar la sintaxis de System.out.println
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if "system.out.println" in stripped_line:
            # Verificar que la llamada a System.out.println siga el formato exacto
            if not re.match(r'system\.out\.println\s*\(.*\)\s*;', stripped_line):
                errors.append(f"Error en la línea {i + 1}: Sintaxis incorrecta en 'System.out.println'. Se esperaba 'System.out.println(...)'. Encontrado: {stripped_line}")
            else:
                print(stripped_line)
                print(not re.match(r'"[^"]*"\s*\+\s*[a-zA-Z_]\w*', stripped_line))
                if re.match(r'"[^"]*"\s*\+\s*[a-zA-Z_]\w*', stripped_line):
                    errors.append(f"Error en la linea {i+1}: Sistaxis incorrecta en la imprecion se encontro: {stripped_line}")
        # Verificar que no haya errores tipográficos en System.out.println
        if "system.out.print" in stripped_line and not "system.out.println" in stripped_line:
            errors.append(f"Error en la línea {i + 1}: Sintaxis incorrecta. Se esperaba 'system.out.println'. Encontrado: {stripped_line}")
    
    syntactic_result = "Sintaxis Correcta" if not errors else "\n".join(errors)
    
    return jsonify(syntactic_result=syntactic_result)

if __name__ == '__main__':
    app.run(debug=True)
