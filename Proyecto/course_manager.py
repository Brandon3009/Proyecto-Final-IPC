import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass

class Course:
    def __init__(self, nombre_curso, costo, horario, codigo, cupo, catedratico):
        self.nombre_curso = nombre_curso
        self.costo = costo
        self.horario = horario
        self.codigo = codigo
        self.cupo = cupo
        self.catedratico = catedratico
        self.estudiantes = []  # Lista de estudiantes inscritos
        self.pagos = {}  # Diccionario para rastrear los pagos de los estudiantes

    def inscribir_estudiante(self, estudiante):
        if len(self.estudiantes) < self.cupo and estudiante.username not in self.estudiantes:
            self.estudiantes.append(estudiante.username)
            self.pagos[estudiante.username] = False  # Inicialmente, el estudiante no ha pagado
            return True
        return False

class Student:
    def __init__(self, username):
        self.username = username
        self.inscrito_cursos = []

    def inscribir_curso(self, nombre_curso):
        self.inscrito_cursos.append(nombre_curso)

    def verificar_inscripcion(self, nombre_curso):
        return nombre_curso in self.inscrito_cursos

    def pagar_curso(self, nombre_curso, monto, course_manager):
        if nombre_curso in self.inscrito_cursos:
            curso = course_manager.get_curso_por_nombre(nombre_curso)
            if not curso.pagos.get(self.username, False):
                if abs(monto - curso.costo) < 0.001:  # Comparación de números en coma flotante
                    curso.pagos[self.username] = True
                    self.inscrito_cursos.remove(nombre_curso)
                    guardar_informacion_estudiantes(course_manager, self.username, nombre_curso)
                    curso.cupo -= 1
                    guardar_informacion_cursos(course_manager)
                    return True
                else:
                    messagebox.showerror("Error de Pago", "El monto ingresado no coincide con el costo del curso.")
        return False

class CourseManager:
    def __init__(self):
        self.cursos = {}  # Un diccionario donde la clave es el código del curso y el valor es la instancia del curso
    
    def crear_curso(self, nombre_curso, costo, horario, codigo, cupo, catedratico):
        if nombre_curso not in self.cursos:
            curso = Course(nombre_curso, costo, horario, codigo, cupo, catedratico)
            self.cursos[nombre_curso] = curso
            return curso
    
    def listar_cursos(self):
        return self.cursos.values()

    def crear_curso(self, nombre_curso, costo, horario, codigo, cupo, catedratico):
        if nombre_curso not in self.cursos:
            curso = Course(nombre_curso, costo, horario, codigo, cupo, catedratico)
            self.cursos[nombre_curso] = curso
            return curso
    
    def listar_cursos(self):
        return self.cursos.values()

    def inscribir_estudiante(self, nombre_curso, estudiante):
        if nombre_curso in self.cursos:
            curso = self.cursos[nombre_curso]
            return curso.inscribir_estudiante(estudiante)
        else:
            return False

    def get_curso_por_nombre(self, nombre_curso):
        return self.cursos.get(nombre_curso)

def guardar_informacion_estudiantes(course_manager, student_username, nombre_curso):
    with open("usuarios_inscritos.txt", "a") as file:
        file.write(f"{nombre_curso},{student_username}\n")

def cargar_informacion_estudiantes(course_manager):
    try:
        with open("usuarios_inscritos.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                nombre_curso, username = line.strip().split(',')
                if nombre_curso in course_manager.cursos:
                    curso_manager = course_manager.cursos[nombre_curso]
                    curso_manager.estudiantes.append(username)
                    curso_manager.pagos[username] = False  # Inicialmente, no se ha realizado el pago
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los estudiantes: {str(e)}")

def cargar_cursos_desde_archivo(course_manager):
    try:
        with open("cursos.json", "r", encoding="utf-8") as file:
            cursos_data = json.load(file)
            for curso_data in cursos_data:
                nombre_curso = curso_data["nombre_curso"]
                costo = float(curso_data["costo"])
                horario = curso_data["horario"]
                codigo = curso_data["codigo"]
                cupo = int(curso_data["cupo"])
                catedratico = curso_data["catedratico"]
                course_manager.crear_curso(nombre_curso, costo, horario, codigo, cupo, catedratico)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los cursos: {str(e)}")

# Crear instancias de CourseManager y cargar cursos desde el archivo
course_manager = CourseManager()
cargar_cursos_desde_archivo(course_manager)
cargar_informacion_estudiantes(course_manager)

# Función para buscar la existencia del usuario en la lista de usuarios
def buscar_usuario(username):
    try:
        with open("usuarios.txt", "r") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) >= 6 and parts[3] == username:
                    # Retorna el correo del usuario si se encuentra
                    return parts[7]
        return None  # El usuario no se encontró en el archivo
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los usuarios: {str(e)}")
        return None

# Crear una instancia de estudiante
student_username = simpledialog.askstring("Nombre de Usuario", "Ingresa tu nombre de usuario:")

if student_username is None:
    # Se presionó Cancelar, por lo que se cierra el programa
    exit()

if buscar_usuario(student_username):
    student = Student(student_username)
else:
    messagebox.showerror("Error", "El usuario no existe. Por favor, ingrese un usuario válido.")
    # No se cierra el programa, puedes mostrar un mensaje y permitir que el usuario ingrese un nuevo nombre de usuario

# Crear la ventana principal de Cursos
root = tk.Tk()
root.title("Cursos")
root.geometry("500x300")
root.config(bd=10, bg="lavender")

cursos_listbox = tk.Listbox(root, height=10, width=60)
cursos_listbox.pack()

# Función para mostrar los cursos disponibles
def mostrar_cursos_disponibles():
    cursos_listbox.delete(0, tk.END)
    for curso in course_manager.listar_cursos():
        if curso.cupo > 0:
            cursos_listbox.insert(tk.END, f"Nombre: {curso.nombre_curso}, Cupo: {curso.cupo}")
mostrar_cursos_disponibles()  # Llamar a la función al abrir la ventana

# Crear un botón "Inscribirse en el Curso" en la ventana principal
button_inscribirse = tk.Button(root, text="Inscribirse en el Curso")
button_inscribirse.pack()

def mostrar_informacion_curso():
    selected_index = cursos_listbox.curselection()
    if not selected_index:
        messagebox.showinfo("Error", "Por favor, seleccione un curso antes de inscribirse.")
        return

    selected_course = cursos_listbox.get(selected_index)
    nombre_curso = selected_course.split(" ")[1].split(',')[0]
    if nombre_curso in course_manager.cursos:
        curso = course_manager.cursos[nombre_curso]
        descripcion_curso = f"Nombre del Curso: {curso.nombre_curso}\n" \
                           f"Costo: {curso.costo}\n" \
                           f"Horario: {curso.horario}\n" \
                           f"Código del Curso: {curso.codigo}\n" \
                           f"Cupo Disponible: {curso.cupo}\n" \
                           f"Catedrático: {curso.catedratico}\n" \
                           f"Nombre de Usuario: {student.username}"

        if curso.cupo == 0:
            messagebox.showinfo("Error", "No hay cupo disponible en este curso.")
        elif student.verificar_inscripcion(nombre_curso):
            messagebox.showinfo("Mensaje", "Ya estás inscrito en este curso.")
        else:
            mostrar_ventana_inscripcion(curso, nombre_curso, descripcion_curso)

def enviar_correo_confirmacion(user_email, nombre_curso, curso):
    # Configura las credenciales de Gmail
    sender_email = 'unicursos31@gmail.com'
    sender_password = 'ptco lxts jwep gebn'

    # Crea un mensaje de correo
    subject = "Confirmación de Inscripción en el Curso"
    body = f"¡Gracias por inscribirte en el curso {curso.nombre_curso}!\n\n" \
           f"Detalles del curso:\n" \
           f"Costo: {curso.costo}\n" \
           f"Horario: {curso.horario}\n" \
           f"Código del Curso: {curso.codigo}\n" \
           f"Catedrático: {curso.catedratico}\n\n" \
           f"¡Esperamos verte en el aula!"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = user_email  # Utiliza la dirección de correo del usuario
    message["Subject"] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, message.as_string())
        server.quit()

        messagebox.showinfo("Mensaje", "Correo de confirmación enviado exitosamente.")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo enviar el correo: {str(e)}")

def mostrar_ventana_inscripcion(curso, nombre_curso, descripcion_curso):
    if student.verificar_inscripcion(nombre_curso):
        messagebox.showinfo("Mensaje", "Ya estás inscrito en este curso.")
    else:
        inscribirse_window = tk.Toplevel(root)
        inscribirse_window.title("Inscribirse en el Curso")
        inscribirse_window.geometry("400x300")
        inscribirse_window.config(bd=5)

        label = tk.Label(inscribirse_window, text=f"Inscribirse en el curso: {curso.nombre_curso}")
        label.pack()

        info_curso_label = tk.Label(inscribirse_window, text=descripcion_curso)
        info_curso_label.pack()

        def pagar_curso():
            if verificar_pago_previo(student.username, nombre_curso):
                messagebox.showerror("Error", "Ya has pagado este curso anteriormente.")
            elif not curso.pagos.get(student.username, False):
                monto_pago = simpledialog.askfloat("Pago del Curso", f"Ingresa el monto a pagar para el curso {curso.nombre_curso}:")
                if monto_pago is not None:
                    if abs(monto_pago - curso.costo) < 0.001:
                        curso.pagos[student.username] = True
                        curso.cupo -= 1
                        guardar_informacion_cursos(course_manager)
                        mostrar_cursos_disponibles()
                        guardar_informacion_estudiantes(course_manager, student.username, nombre_curso)
                        # Obtiene la dirección de correo del usuario
                        user_email = buscar_usuario(student.username)
                        if user_email:
                            enviar_correo_confirmacion(user_email, nombre_curso, curso)
                        messagebox.showinfo("Mensaje", "Pago exitoso del curso.")
                        inscribirse_window.destroy()
                    else:
                        messagebox.showerror("Error", "El monto ingresado no coincide con el costo del curso.")
                else:
                    messagebox.showerror("Error", "El monto ingresado no es válido.")
            else:
                messagebox.showinfo("Mensaje", "Ya has pagado este curso.")
        pagar_button = tk.Button(inscribirse_window, text="Pagar el Curso", command=pagar_curso)
        pagar_button.pack()

def verificar_pago_previo(username, nombre_curso):
    # Cargar información de inscripción desde el archivo "usuarios_inscritos.txt"
    inscripciones = cargar_informacion_inscripciones()

    # Verificar si el par (nombre_curso, username) existe en las inscripciones
    return (nombre_curso, username) in inscripciones

def cargar_informacion_inscripciones():
    inscripciones = set()
    try:
        with open("usuarios_inscritos.txt", "r") as file:
            for line in file:
                nombre_curso, username = line.strip().split(',')
                inscripciones.add((nombre_curso, username))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar las inscripciones: {str(e)}")
    return inscripciones

# Conectar la función "mostrar_informacion_curso" al botón "Inscribirse en el Curso"
button_inscribirse.config(command=mostrar_informacion_curso)

# Función para cerrar la ventana de Cursos
def cerrar_ventana():
    root.destroy()

# Cambia el texto del botón "Regresar a Estudiante" a "Cerrar"
boton_cerrar = tk.Button(root, text="Cerrar", command=cerrar_ventana)
boton_cerrar.pack()

# Función para guardar información de cursos en el archivo "cursos.json"
def guardar_informacion_cursos(course_manager):
    cursos_data = []

    # Actualizar los datos de los cursos en cursos_data
    for curso in course_manager.listar_cursos():
        curso_data = {
            "nombre_curso": curso.nombre_curso,
            "costo": curso.costo,
            "horario": curso.horario,
            "codigo": curso.codigo,
            "cupo": curso.cupo,
            "catedratico": curso.catedratico
        }
        cursos_data.append(curso_data)

    # Guardar la información actualizada en el archivo
    with open("cursos.json", "w", encoding="utf-8") as file:
        json.dump(cursos_data, file, ensure_ascii=False, indent=4)

# Iniciar la ventana principal
root.mainloop()
