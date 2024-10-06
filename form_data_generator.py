from playwright.sync_api import sync_playwright
from faker import Faker
from bs4 import BeautifulSoup
import os

# Inicializar Faker para generación de datos aleatorios
fake = Faker()

# Función para detectar los campos de un formulario en una página web
def detectar_campos_formulario(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Extraer el HTML y buscar los formularios
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        formularios = soup.find_all('form')
        campos = []

        for form in formularios:
            inputs = form.find_all(['input', 'select', 'textarea'])
            for input in inputs:
                tipo = input.get('type', 'text')
                nombre = input.get('name', input.get('id', ''))
                # Solo agregar campos visibles (no hidden)
                if tipo != 'hidden' and nombre:  
                    campos.append({'campo': nombre, 'tipo': tipo})

        browser.close()
    return campos

# Función para generar datos dinámicos en base a los campos detectados
def generar_datos_dinamicos(campos):
    datos_generados = {}
    for campo in campos:
        tipo = campo['tipo']
        if tipo == 'text':
            datos_generados[campo['campo']] = fake.name()
        elif tipo == 'email':
            datos_generados[campo['campo']] = fake.email()
        elif tipo == 'password':
            datos_generados[campo['campo']] = fake.password()
        elif tipo == 'number':
            datos_generados[campo['campo']] = random.randint(1000, 9999)
        elif tipo == 'date':
            datos_generados[campo['campo']] = fake.date_of_birth().isoformat()
        else:
            datos_generados[campo['campo']] = fake.word()  # Fallback para otros tipos
    return datos_generados

# Función para leer columnas de un archivo .sql y obtener el nombre de la base de datos
def leer_columnas_sql(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    columnas = []
    db_name = ""
    for line in lines:
        line = line.strip()
        if line.startswith("CREATE TABLE") or line.startswith("create table"):
            continue  # Ignorar las líneas que crean tablas
        if line.startswith("`") and "`" in line:
            column_name = line.split()[0].strip('`')
            columnas.append(column_name)
        if line.startswith("CREATE DATABASE") or line.startswith("create database"):
            db_name = line.split()[2].strip('`')
    return columnas, db_name

# Función principal para generar y guardar los datos
def generar_y_guardar_datos(url, n_datos=1000, carpeta_datos='datos_generados', columnas_db=None, db_name=None):
    campos_detectados = detectar_campos_formulario(url)
    print(f"Campos detectados: {campos_detectados}")

    # Filtrar campos detectados según las columnas en la base de datos
    if columnas_db:
        campos_detectados = [campo for campo in campos_detectados if campo['campo'] in columnas_db]
        if not campos_detectados:
            print("No hay coincidencias entre los campos del formulario y la base de datos.")
            return

    if not os.path.exists(carpeta_datos):
        os.makedirs(carpeta_datos)

    datos_generados = []
    for i in range(n_datos):
        datos = generar_datos_dinamicos(campos_detectados)
        datos_generados.append(datos)

    # Guardar todos los datos en un archivo .txt con el nombre de la base de datos
    nombre_archivo = os.path.join(carpeta_datos, f'datos_generados_{db_name}.txt' if db_name else 'datos_generados.txt')
    with open(nombre_archivo, 'w') as f:
        for datos in datos_generados:
            f.write(str(datos) + '\n')
    
    print(f"Datos generados y guardados en la carpeta '{carpeta_datos}' como '{os.path.basename(nombre_archivo)}'.")

# Solicitar URL y cantidad de datos al usuario
url = input("Ingrese la URL de la página con el formulario: ")
n_datos = int(input("Ingrese la cantidad de datos a generar: "))
file_path = input("Ingrese la ruta del archivo .sql: ")

# Leer columnas del archivo SQL
columnas_db, db_name = leer_columnas_sql(file_path)

# Ejecutar la generación de datos
generar_y_guardar_datos(url, n_datos, columnas_db=columnas_db, db_name=db_name)
