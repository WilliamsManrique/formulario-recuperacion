import os
from flask import Flask, render_template, request, redirect, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave-secreta-temporal'

def get_db_connection():
    """Conectar a MySQL RDS"""
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "database-1.cpcwiiu4yk22.us-east-1.rds.amazonaws.com"),
            database=os.environ.get("DB_NAME", "FormularioWeb"),
            user=os.environ.get("DB_USER", "admin"),
            password=os.environ.get("DB_PASS", "123456789"),
            port=int(os.environ.get("DB_PORT", 3306))
        )
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Error de conexión a MySQL: {e}")
        flash(f'Error de conexión a la base de datos: {e}', 'danger')
        return None

def init_database():
    """Crear tabla si no existe"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo VARCHAR(50) UNIQUE NOT NULL,
            tipo_equipo VARCHAR(100) NOT NULL,
            marca VARCHAR(100) NOT NULL,
            modelo VARCHAR(100),
            sistema_operativo VARCHAR(100),
            almacenamiento_gb INT,
            ram VARCHAR(50),
            estado VARCHAR(50) DEFAULT 'Activo',
            fecha_mantenimiento DATE,
            fecha_registro DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tabla 'equipos' creada/verificada")

@app.route('/')
def index():
    """Mostrar formulario y lista de equipos"""
    hoy = datetime.now().strftime('%Y-%m-%d')
    equipos = []
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM equipos ORDER BY created_at DESC")
        equipos = cursor.fetchall()
        cursor.close()
        conn.close()
    
    return render_template('index.html', equipos=equipos, hoy=hoy)

@app.route('/registrar', methods=['POST'])
def registrar():
    """Registrar un nuevo equipo"""
    try:
        # Obtener datos del formulario
        codigo = request.form['codigo'].strip().upper()
        tipo_equipo = request.form['tipo_equipo']
        marca = request.form['marca'].strip()
        modelo = request.form.get('modelo', '').strip()
        sistema_operativo = request.form.get('sistema_operativo', '')
        
        almacenamiento_gb = request.form.get('almacenamiento_gb')
        if almacenamiento_gb:
            try:
                almacenamiento_gb = int(almacenamiento_gb)
            except ValueError:
                almacenamiento_gb = None
        else:
            almacenamiento_gb = None
        
        ram = request.form.get('ram', '')
        estado = request.form.get('estado', 'Activo')
        fecha_mantenimiento = request.form.get('fecha_mantenimiento', '')
        fecha_registro = request.form.get('fecha_registro', datetime.now().strftime('%Y-%m-%d'))
        
        # Validar campos obligatorios
        if not codigo or not tipo_equipo or not marca:
            flash('Los campos Código, Tipo de Equipo y Marca son obligatorios', 'warning')
            return redirect('/')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Verificar si el código ya existe
            cursor.execute("SELECT id FROM equipos WHERE codigo = %s", (codigo,))
            if cursor.fetchone():
                flash(f'El código {codigo} ya existe', 'danger')
                cursor.close()
                conn.close()
                return redirect('/')
            
            # Insertar nuevo registro
            cursor.execute('''
                INSERT INTO equipos 
                (codigo, tipo_equipo, marca, modelo, sistema_operativo, 
                 almacenamiento_gb, ram, estado, fecha_mantenimiento, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (codigo, tipo_equipo, marca, modelo, sistema_operativo,
                  almacenamiento_gb, ram, estado, fecha_mantenimiento, fecha_registro))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash(f'✅ Equipo {codigo} registrado exitosamente!', 'success')
        else:
            flash('❌ Error de conexión a la base de datos', 'danger')
    
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'danger')
    
    return redirect('/')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    """Eliminar un equipo"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Obtener código antes de eliminar
            cursor.execute("SELECT codigo FROM equipos WHERE id = %s", (id,))
            equipo = cursor.fetchone()
            
            if equipo:
                cursor.execute("DELETE FROM equipos WHERE id = %s", (id,))
                conn.commit()
                flash(f'🗑️ Equipo {equipo["codigo"]} eliminado', 'info')
            else:
                flash('⚠️ Equipo no encontrado', 'warning')
            
            cursor.close()
            conn.close()
    
    except Exception as e:
        flash(f'❌ Error al eliminar: {str(e)}', 'danger')
    
    return redirect('/')

@app.route('/test_db')
def test_db():
    """Ruta para probar la conexión"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM equipos")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return f"✅ Conexión exitosa. Total equipos: {count}"
    else:
        return "❌ Error de conexión a la base de datos"

if __name__ == '__main__':
    init_database()
    print("🚀 Servidor iniciado en http://localhost:5000")
    app.run(debug=True, port=5000)