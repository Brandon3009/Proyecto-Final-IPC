import tkinter as tk
import hashlib
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar
import re  # Agregamos el módulo re (expresiones regulares)
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cv2
import os
import numpy as np

class LoginWindow:
    def __init__(self, root, user_type):
        self.root = root
        self.user_type = user_type

# Crear la ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Inicio de Sesión")
ventana_principal.geometry("300x350")
ventana_principal.resizable(0, 0)
ventana_principal.config(bd=10, bg="lightblue")  # Cambia el color de fondo a lightblue

def read_users_from_file():
    users = []
    with open("usuarios.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(":")
            if len(parts) == 10:
                cui, nombre, apellido, nombre_usuario, genero, edad, fecha_nacimiento, correo, contraseña_encriptada, tipo_usuario = parts
                users.append({
                    "cui": cui,
                    "nombre": nombre,
                    "apellido": apellido,
                    "nombre_usuario": nombre_usuario,
                    "genero": genero,
                    "edad": edad,
                    "fecha_nacimiento": fecha_nacimiento,
                    "correo": correo,
                    "contraseña_encriptada": contraseña_encriptada,
                    "tipo_usuario": tipo_usuario
                })
    return users

# Lee los usuarios desde el archivo al inicio
users = read_users_from_file()

# Campos de entrada para el nombre de usuario y contraseña
label_usuario = tk.Label(ventana_principal, text="Nombre de Usuario:", bg="lightblue")
label_usuario.pack(padx=10, pady=5)
entry_usuario = tk.Entry(ventana_principal)
entry_usuario.pack(padx=10, pady=5)

label_contraseña = tk.Label(ventana_principal, text="Contraseña:", bg="lightblue")
label_contraseña.pack(padx=10, pady=5)

# Crear un contenedor para el campo de contraseña y el botón "Mostrar"
password_container = tk.Frame(ventana_principal)
password_container.pack(padx=10, pady=5)

entry_contraseña = tk.Entry(password_container, show="*")
entry_contraseña.pack(side="left")

# Función para alternar la visibilidad de la contraseña
def toggle_password_visibility(entry, button):
    if entry["show"] == "*":
        entry["show"] = ""
        button["text"] = "Ocultar"
    else:
        entry["show"] = "*"
        button["text"] = "Mostrar"

toggle_password_button = tk.Button(password_container, text="Mostrar", command=lambda: toggle_password_visibility(entry_contraseña, toggle_password_button))
toggle_password_button.pack(side="left")

entry_fecha_nacimiento = None  # Variable para el campo de fecha de nacimiento

def guardar_fecha(fecha):
    entry_fecha_nacimiento.delete(0, tk.END)
    entry_fecha_nacimiento.insert(0, fecha)
    ventana_calendario.destroy()

# Funciones para abrir las ventanas de inicio de sesión
def verificar_contraseña(contraseña, contraseña_encriptada, usuario):
    # Verificar la contraseña encriptada
    hasher = hashlib.sha256()
    hasher.update(contraseña.encode())
    if hasher.hexdigest() == contraseña_encriptada:
        return True
    return False

# Funciones para abrir las ventanas relacionadas con el tipo de usuario
def abrir_ventana_estudiante(usuario):
    ventana_estudiante = tk.Toplevel(ventana_principal)
    ventana_estudiante.title("Ventana de Estudiante")
    label_bienvenida = tk.Label(ventana_estudiante, text=f"¡Bienvenido, Estudiante - {usuario}!")
    label_bienvenida.pack(padx=10, pady=10)
    ventana_principal.withdraw()
    from student_window import StudentWindow
    # Crear una instancia de StudentWindow
    student_window = StudentWindow(ventana_estudiante, usuario)
    student_window.show()  # Oculta la ventana de inicio

def abrir_ventana_profesor(nombre):
    ventana_profesor = tk.Toplevel(ventana_principal)
    ventana_profesor.title("Ventana de Profesor")
    ventana_profesor.geometry("400x200")
    ventana_profesor.config(bd=10, bg="peachpuff")
    label_bienvenida = tk.Label(ventana_profesor, text=f"¡Bienvenido, Profesor- {nombre}!")
    label_bienvenida.pack(padx=10, pady=10)
    from professor_window import ProfessorWindow
    professor_window = ProfessorWindow(ventana_profesor,nombre)
    ventana_principal.withdraw()

def abrir_ventana_admin():
    ventana_admin = tk.Toplevel(ventana_principal)
    ventana_admin.title("Ventana de Administrador")
    ventana_admin.geometry("600x400")
    ventana_admin.config(bd=10, bg="wheat")
    from admin_window import AdminWindow
    # Crea la instancia de AdminWindow
    admin_window = AdminWindow(ventana_admin)
    ventana_principal.withdraw()

def capture_user_images(username):
    # Crear un directorio para almacenar las imágenes del usuario
    user_images_dir = f"user_images/{username}"
    os.makedirs(user_images_dir, exist_ok=True)

    # Inicializar la cámara
    cap = cv2.VideoCapture(0)  # Puedes ajustar el índice si tienes varias cámaras

    # Configurar el clasificador de rostros
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    image_count = 0
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error al capturar el video")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar rostros en el cuadro actual
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            # Dibujar un rectángulo alrededor del rostro detectado
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Guardar la imagen del rostro en el directorio del usuario
            face_image = gray[y:y + h, x:x + w]
            image_filename = os.path.join(user_images_dir, f"face_{image_count}.png")
            cv2.imwrite(image_filename, face_image)
            image_count += 1

        # Mostrar el cuadro de video
        cv2.imshow("Captura de Rostro", frame)

        # Salir cuando se presiona la tecla 'q' y se han capturado suficientes imágenes
        if cv2.waitKey(1) & 0xFF == ord('q') or image_count >= 5:
            break

    # Liberar la cámara y cerrar las ventanas
    cap.release()
    cv2.destroyAllWindows()

    print(f"Se capturaron {image_count} imágenes del rostro.")

# Declarar cal, ventana_registro y ventana_calendario a nivel de ventana principal
cal = None
ventana_registro = None
ventana_calendario = None

# Función para abrir la ventana de registro
def abrir_ventana_registro():
    global entry_fecha_nacimiento, ventana_registro
    ventana_registro = tk.Toplevel(ventana_principal)
    ventana_registro.title("Registro de Usuario")
    ventana_registro.geometry("500x800")
    ventana_registro.resizable(0, 0)
    ventana_registro.config(bd=10, bg="lightgreen")

    # Etiquetas y campos de entrada
    label_cui = tk.Label(ventana_registro, text="CUI:", bg="lightgreen")
    label_cui.pack(padx=10, pady=5)
    entry_cui = tk.Entry(ventana_registro)
    entry_cui.pack(padx=10, pady=5)

    label_nombre = tk.Label(ventana_registro, text="Nombre:",bg="lightgreen")
    label_nombre.pack(padx=10, pady=5)
    entry_nombre = tk.Entry(ventana_registro)
    entry_nombre.pack(padx=10, pady=5)

    label_apellido = tk.Label(ventana_registro, text="Apellido:",bg="lightgreen")
    label_apellido.pack(padx=10, pady=5)
    entry_apellido = tk.Entry(ventana_registro)
    entry_apellido.pack(padx=10, pady=5)

    label_usuario = tk.Label(ventana_registro, text="Nombre de Usuario:",bg="lightgreen")
    label_usuario.pack(padx=10, pady=5)
    entry_usuario = tk.Entry(ventana_registro)
    entry_usuario.pack(padx=10, pady=5)

    label_genero = tk.Label(ventana_registro, text="Género:",bg="lightgreen")
    label_genero.pack(padx=10, pady=5)
    var_genero = tk.StringVar()
    var_genero.set("Masculino")
    radio_masculino = tk.Radiobutton(ventana_registro, text="Masculino", variable=var_genero, value="Masculino",bg="lightgreen")
    radio_femenino = tk.Radiobutton(ventana_registro, text="Femenino", variable=var_genero, value="Femenino",bg="lightgreen")
    radio_masculino.pack(padx=10, pady=5)
    radio_femenino.pack(padx=10, pady=5)

    label_edad = tk.Label(ventana_registro, text="Edad:",bg="lightgreen")
    label_edad.pack(padx=10, pady=5)
    entry_edad = tk.Entry(ventana_registro)
    entry_edad.pack(padx=10, pady=5)

    label_fecha_nacimiento = tk.Label(ventana_registro, text="Fecha de Nacimiento:",bg="lightgreen")
    label_fecha_nacimiento.pack(padx=10, pady=5)
    entry_fecha_nacimiento = tk.Entry(ventana_registro)
    entry_fecha_nacimiento.pack(padx=10, pady=5)
    boton_calendario = tk.Button(ventana_registro, text="Calendario", command=abrir_calendario,bg="lightblue")
    boton_calendario.pack(padx=10, pady=5)

    label_email = tk.Label(ventana_registro, text="Correo Electrónico:",bg="lightgreen")
    label_email.pack(padx=10, pady=5)
    entry_email = tk.Entry(ventana_registro)
    entry_email.pack(padx=10, pady=5)

    label_contraseña = tk.Label(ventana_registro, text="Contraseña:",bg="lightgreen")
    label_contraseña.pack(padx=10, pady=5)
    # contenedor para el campo de contraseña y el botón "Mostrar"
    password_container = tk.Frame(ventana_registro)
    password_container.pack(padx=10, pady=5)

    entry_contraseña = tk.Entry(password_container, show="*")
    entry_contraseña.pack(side="left")

    # Crear un botón para alternar la visibilidad de la contraseña
    toggle_password_button = tk.Button(password_container, text="Mostrar", command=lambda: toggle_password_visibility(entry_contraseña, toggle_password_button))
    toggle_password_button.pack(side="right")

    label_rep_contraseña = tk.Label(ventana_registro, text="Repetir Contraseña:",bg="lightgreen")
    label_rep_contraseña.pack(padx=10, pady=5)
     # Crear un contenedor similar para el campo de repetir contraseña
    repeat_password_container = tk.Frame(ventana_registro)
    repeat_password_container.pack(padx=10, pady=5)

    entry_rep_contraseña = tk.Entry(repeat_password_container, show="*")
    entry_rep_contraseña.pack(side="left")

    # Crear un botón para alternar la visibilidad de la contraseña de repetición
    toggle_repeat_password_button = tk.Button(repeat_password_container, text="Mostrar", command=lambda: toggle_password_visibility(entry_rep_contraseña, toggle_repeat_password_button))
    toggle_repeat_password_button.pack(side="right")

    # Botón para capturar imágenes del rostro del usuario
    boton_capturar_rostro = tk.Button(ventana_registro, text="Capturar Rostro", command=lambda: capture_user_images(entry_usuario.get()))
    boton_capturar_rostro.pack(padx=10, pady=10)

    var_tipo_usuario = tk.StringVar()
    var_tipo_usuario.set("Estudiante")

# Función para verificar si la contraseña cumple con los requisitos
    def validar_contraseña(contraseña):
    # Al menos 8 caracteres, 1 mayúscula, 1 dígito y 1 símbolo
        if len(contraseña) < 8:
            return False
        if not re.search(r'[A-Z]', contraseña):
            return False
        if not re.search(r'\d', contraseña):
            return False
        if not re.search(r'[!@#$%^&*]', contraseña):
            return False
        return True

    # Función para guardar los datos del nuevo usuario
    def guardar_usuario():
        cui = entry_cui.get()
        nombre = entry_nombre.get()
        apellido = entry_apellido.get()
        usuario = entry_usuario.get()
        genero = var_genero.get()
        edad = entry_edad.get()
        fecha_nacimiento = entry_fecha_nacimiento.get()
        email = entry_email.get()
        contraseña = entry_contraseña.get()
        rep_contraseña = entry_rep_contraseña.get()
        tipo_usuario = var_tipo_usuario.get()  # Esto ya es "Estudiante"

        # Verificar si alguno de los campos obligatorios está vacío
        if not cui or not nombre or not apellido or not usuario or not contraseña:
            messagebox.showerror("Error", "Por favor, complete todos los campos obligatorios.")
            return

    # Verificar si la contraseña cumple con los requisitos
        if not validar_contraseña(contraseña):
            messagebox.showerror("Error", "La contraseña no cumple con los requisitos mínimos.")
            return

        # Verificar si las contraseñas coinciden
        if contraseña != rep_contraseña:
            messagebox.showerror("Error", "Las contraseñas no coinciden. Por favor, inténtelo nuevamente.")
            return

        # Encriptar la contraseña usando SHA-256
        hasher = hashlib.sha256()
        hasher.update(contraseña.encode())
        contraseña_encriptada = hasher.hexdigest()

        # Leer usuarios del archivo "usuarios.txt" y verificar la existencia del usuario
        with open("usuarios.txt", "r") as file:
            usuarios = file.read().splitlines()

        for user in usuarios:
            parts = user.split(':')
            if len(parts) >= 4:
                cui_guardado, nombre_usuario_guardado, bloqueado = parts[0], parts[3], "bloqueado" in parts[-1]
                if usuario == nombre_usuario_guardado or cui == cui_guardado:
                    if bloqueado:
                        messagebox.showerror("Usuario Bloqueado", f"El usuario '{usuario}' está bloqueado.")
                    else:
                        messagebox.showerror("Error", "El CUI o el nombre de usuario ya existen. Por favor, elija otro.")
                    return

        # Guardar el nuevo usuario en el archivo usuarios.txt
        with open("usuarios.txt", "a") as file:
            file.write(f"{cui}:{nombre}:{apellido}:{usuario}:{genero}:{edad}:{fecha_nacimiento}:{email}:{contraseña_encriptada}:{tipo_usuario}\n")

        messagebox.showinfo("Registro Exitoso", "El usuario se registró con éxito.")
        ventana_registro.destroy()

    # Botón para registrar el nuevo usuario
    boton_registrar = tk.Button(ventana_registro, text="Registrar", command=guardar_usuario)
    boton_registrar.pack(padx=10, pady=10)

# Función para abrir el calendario
def abrir_calendario():
    global ventana_calendario, cal
    ventana_calendario = tk.Toplevel(ventana_registro)
    ventana_calendario.title("Calendario")
    ventana_calendario.configure(bg="lightgreen")
    cal = Calendar(ventana_calendario, date_pattern="yyyy-mm-dd")
    cal.pack(padx=10, pady=10)
    boton_seleccionar_fecha = tk.Button(ventana_calendario, text="Seleccionar Fecha", command=seleccionar_fecha)
    boton_seleccionar_fecha.pack(padx=10, pady=10)

# Función para seleccionar la fecha del calendario
def seleccionar_fecha():
    global ventana_calendario, entry_fecha_nacimiento
    fecha_seleccionada = cal.get_date()
    entry_fecha_nacimiento.delete(0, "end")
    entry_fecha_nacimiento.insert(0, fecha_seleccionada)
    ventana_calendario.destroy()

# Botón para registrarse
boton_registro = tk.Button(ventana_principal, text="Registrarse", command=abrir_ventana_registro)
boton_registro.pack(padx=10, pady=10)

# Declarar un diccionario para rastrear intentos fallidos
intentos_fallidos = {}

# Definir una función para enviar un correo electrónico
def send_recovery_email(username, user_email, new_password):
    # Correo electrónico del remitente y la contraseña
    sender_email = 'unicursos31@gmail.com'  # Cambia esto con tu dirección de correo
    sender_password = 'ptco lxts jwep gebn'  # Cambia esto con tu contraseña

    # Crear un mensaje MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = 'Recuperación de Contraseña'

    # Cuerpo del mensaje
    message = f"Tu nueva contraseña es: {new_password}"
    msg.attach(MIMEText(message, 'plain'))

    # Configuración del servidor SMTP (para Gmail)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Puerto seguro para TLS

    # Crear una conexión segura con el servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    # Iniciar sesión en tu cuenta de correo
    server.login(sender_email, sender_password)

    # Enviar el correo electrónico
    server.sendmail(sender_email, user_email, msg.as_string())

    # Finalizar la conexión con el servidor SMTP
    server.quit()
# Definir una función para escribir usuarios en el archivo
def write_users_to_file(users):
    with open("usuarios.txt", "w") as file:
        for user in users:
            user_info = ":".join([
                user["cui"], user["nombre"], user["apellido"], user["nombre_usuario"],
                user["genero"], user["edad"], user["fecha_nacimiento"],
                user["correo"], user["contraseña_encriptada"], user["tipo_usuario"]
            ])
            file.write(user_info + '\n')

def recuperar_contraseña():
    # Solicitar al usuario su nombre de usuario y correo electrónico
    username = simpledialog.askstring("Recuperar Contraseña", "Ingrese su nombre de usuario:")
    email = simpledialog.askstring("Recuperar Contraseña", "Ingrese su correo electrónico:")

    if not username or not email:
        messagebox.showerror("Error", "Debe proporcionar un nombre de usuario y un correo electrónico.")
        return

    # Buscar el usuario en la lista de usuarios
    user = None
    for u in users:
        if u["nombre_usuario"] == username and u["correo"] == email:
            user = u
            break

    if user:
        # Generar una nueva contraseña (cambia esta lógica según tus necesidades)
        import random
        import string
        new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

        # Enviar un correo electrónico con la nueva contraseña
        send_recovery_email(username, email, new_password)

        # Actualizar la contraseña del usuario en la lista de usuarios (simulado)
        user["contraseña_encriptada"] = hashlib.sha256(new_password.encode()).hexdigest()

        # Actualiza el archivo de usuarios
        write_users_to_file(users)

        messagebox.showinfo("Contraseña Recuperada", f"Se ha enviado una nueva contraseña a {email}.")
    else:
        messagebox.showerror("Error", "Usuario no encontrado o el correo electrónico no coincide.")

def get_username_by_user_id(user_id):
    with open("usuarios.txt", "r") as file:
        usuarios = file.read().splitlines()

    for user in usuarios:
        parts = user.split(":")
        if len(parts) >= 4:
            cui, nombre, apellido, nombre_usuario = parts[0], parts[1], parts[2], parts[3]
            if cui == str(user_id):
                return nombre_usuario

    # Si no se encuentra un usuario con el ID dado, devuelve None o un valor predeterminado
    return None

def iniciar_sesion_con_reconocimiento_facial():
    # Cargar el modelo de reconocimiento facial previamente entrenado
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    recognizer.read('C:\\Users\\brand\\OneDrive\\Escritorio\\IPC\trained_model.yml')

    # Inicializar la cámara
    cap = cv2.VideoCapture(0)  # ajustar el índice si tienes varias cámaras

    # Configurar el clasificador de rostros
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error al capturar el video")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar rostros en el cuadro actual
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            # Dibujar un rectángulo alrededor del rostro detectado
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Recortar el rostro de la imagen en escala de grises
            face = gray[y:y + h, x:x + w]

            # Realizar el reconocimiento facial
            user_id, confidence = recognizer.predict(face)

            if confidence < 100:  # Puedes ajustar este valor de confianza
                username = get_username_by_user_id(user_id)  # Obtener el nombre de usuario
                print(f"Usuario reconocido: {username}")

        # Mostrar el cuadro de video
        cv2.imshow("Reconocimiento Facial", frame)

        # Salir cuando se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Liberar la cámara y cerrar las ventanas
    cap.release()
    cv2.destroyAllWindows()

def iniciar_sesion():
    usuario_ingresado = entry_usuario.get()
    contraseña = entry_contraseña.get()

    if not usuario_ingresado or not contraseña:
        messagebox.showerror("Error", "Por favor, complete los campos de usuario y contraseña.")
        return

    if usuario_ingresado == "admin" and contraseña == "admin2468":
        abrir_ventana_admin()
        messagebox.showinfo("Inicio de Sesión Exitoso", f"Bienvenido, {usuario_ingresado} (Administrador).")
        return

    # Primero, intenta verificar si el usuario es un profesor
    with open("profesores.txt", "r") as file:
        profesores = file.read().splitlines()

    for profesor in profesores:
        parts = profesor.split(':')
        if len(parts) >= 5:
            nombre_completo, cui, contraseña_encriptada, tipo_usuario = parts[0], parts[2], parts[3], parts[4]
            # El nombre completo incluye nombre y apellido, separados por un espacio
            nombre_usuario_guardado = nombre_completo.split()[0]  # Tomar el primer nombre como nombre de usuario
            if usuario_ingresado == nombre_usuario_guardado:
                if verificar_contraseña(contraseña, contraseña_encriptada, usuario_ingresado):
                    abrir_ventana_profesor(nombre_completo)  # Puedes usar el nombre completo en lugar del primer nombre
                    return

    with open("usuarios.txt", "r") as file:
        usuarios = file.read().splitlines()

    usuario_encontrado = False

    for i, user in enumerate(usuarios):
        parts = user.split(':')

        if len(parts) >= 10:
            cui, nombre, apellido, usuario, genero, edad, fecha_nacimiento, email, contraseña_encriptada, tipo_usuario = parts

            if usuario == usuario_ingresado:
                if usuario_ingresado in intentos_fallidos and intentos_fallidos[usuario_ingresado] >= 3:
                    usuarios[i] += ",bloqueado"
                    with open("usuarios.txt", "w") as file:
                        file.write("\n".join(usuarios))
                    messagebox.showerror("Usuario Bloqueado", f"El usuario '{usuario_ingresado}' está bloqueado.")
                    return

                if verificar_contraseña(contraseña, contraseña_encriptada, usuario_ingresado):
                    if tipo_usuario == "Estudiante":
                        abrir_ventana_estudiante(usuario)
                    elif tipo_usuario == "Profesor":
                        abrir_ventana_profesor(nombre)
                    else:
                        messagebox.showerror("Error", "Tipo de usuario no reconocido.")
                    if usuario_ingresado in intentos_fallidos:
                        del intentos_fallidos[usuario_ingresado]
                    usuario_encontrado = True
                    return
                else:
                    if usuario_ingresado in intentos_fallidos:
                        intentos_fallidos[usuario_ingresado] += 1
                    else:
                        intentos_fallidos[usuario_ingresado] = 1
                    messagebox.showerror("Error", "Contraseña incorrecta. Por favor, inténtelo nuevamente.")
                    return

    if not usuario_encontrado and usuario_ingresado != "admin":
        messagebox.showerror("Usuario no existe", f"El usuario '{usuario_ingresado}' no existe. Por favor, regístrese.")

boton_iniciar_sesion = tk.Button(ventana_principal, text="Iniciar Sesión", command=iniciar_sesion)
boton_iniciar_sesion.pack(padx=10, pady=10)

# Botón para recuperar la contraseña
boton_recuperar_contraseña = tk.Button(ventana_principal, text="Recuperar Contraseña", command=recuperar_contraseña)
boton_recuperar_contraseña.pack(padx=10, pady=10)

boton_iniciar_sesion_facial = tk.Button(ventana_principal, text="Iniciar Sesión con Reconocimiento Facial", command=iniciar_sesion_con_reconocimiento_facial)
boton_iniciar_sesion_facial.pack(padx=10, pady=10)

ventana_principal.mainloop()
