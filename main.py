from flask import Flask, render_template, request, redirect, url_for, session
import subprocess

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':

        code = request.form['code']

        try:
            output = compile_c_code(code)
            return render_template('index.html', code=code, output=output)

        except Exception as e:
            session['error_message'] = str(e)
            return redirect(url_for('error'))


@app.route('/submit/error')
def error():
    error_message = session.pop('error_message', None)
    return render_template('error.html', error_message=error_message)


def compile_c_code(code):

    with open('temp.c', 'w') as f:
        f.write(code)

    result = subprocess.run(['gcc', '-Og', '-masm=intel', '-S', '-o', 'temp.s', 'temp.c'],
                            capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr)

    with open('temp.s', 'r') as f:
        asm_lines = f.readlines()

    # asm indentation handling
    asm_code = []
    is_colon = False

    for line in asm_lines:
        new_line = line.strip()
        if new_line.endswith(':'):
            is_colon = True
            asm_code.append(new_line)
        elif is_colon and new_line:
            if not new_line.startswith('.') or new_line.startswith(('.L', '.ascii')):
                asm_code.append('\t' + new_line)

    return '\n'.join(asm_code)


if __name__ == '__main__':
    app.run(debug=True)
