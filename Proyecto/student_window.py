import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import json

class StudentWindow:
    def cerrar_student(self):
        self.root.destroy()  # Cierra la ventana de estudiante
        # Abre la ventana de inicio de sesión
        from login_window import LoginWindow
        root = tk.Tk()
        login_window = LoginWindow(root, "student")  # Proporciona los argumentos requeridos
        login_window.show()

    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.courses = []  # Lista de cursos inscritos por el estudiante
        self.notes = {}  # Diccionario para almacenar las notas del estudiante
        self.ruta_foto = None  # Ruta de la foto de perfil
        self.label_foto = None  # Definir label_foto como un atributo
        self.foto = None  # Guarda la referencia de la foto
        self.foto_cargada = False  # Rastrear si se ha cargado una foto
        self.load_courses()  
        self.load_courses
      # Agregar esta línea para cargar los cursos al inicio
        self.load_notes()

    def load_courses(self):
        try:
            with open("usuarios_inscritos.txt", "r") as file:
                lines = file.readlines()
                course_list = []

                for line in lines:
                    course, username = line.strip().split(',')
                    if username.strip() == self.username:
                        course_list.append(course)

                self.courses = course_list
                print("Cursos cargados:", self.courses)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los cursos: {str(e)}")

    def create_student_window(self):
        self.root.title(f"Ventana de Estudiante - {self.username}")
        self.root.geometry("400x400")
        self.root.config(bd=10, bg="alice blue")

        frame = tk.Frame(self.root)
        frame.pack()

        view_notes_button = tk.Button(frame, text="Ver Notas", command=self.view_notes, bg="alice blue")
        view_notes_button.pack()

        inscribir_button = tk.Button(frame, text="Inscribir Curso", command=self.inscribir_curso, bg="alice blue")
        inscribir_button.pack()

         # Botón para ver los cursos inscritos
        inscritos_button = tk.Button(frame, text="Ver Cursos Inscritos", command=self.view_courses, bg="alice blue")
        inscritos_button.pack()

        boton_cerrar_sesion = ttk.Button(self.root, text="Cerrar Sesión", command=self.cerrar_student)
        boton_cerrar_sesion.place(x=300, y=10)

        cargar_foto_button = ttk.Button(frame, text="Cargar Foto", command=self.cargar_foto)
        cargar_foto_button.pack()

        eliminar_foto_button = ttk.Button(frame, text="Eliminar Foto", command=self.eliminar_foto)
        eliminar_foto_button.pack()

        self.label_foto = ttk.Label(frame)
        self.label_foto.pack(side="top", padx=10, pady=10)

    def view_courses(self):
        if not self.courses:
            messagebox.showinfo("Cursos Inscritos", "No estás inscrito en ningún curso.")
        else:
            user_courses_inscribed = self.courses

            # Oculta la ventana de cursos inscritos
            self.root.withdraw()

            # Create a window to display the enrolled courses with a larger size
            courses_window = tk.Toplevel()
            courses_window.title("Cursos Inscritos")
            courses_window.geometry("600x400")  # Set the size of the window
            courses_window.configure(bg="lightblue")  # Set the background color

            for course in user_courses_inscribed:
                course_button = tk.Button(courses_window, text=course, command=lambda c=course: self.abrir_curso(c))
                course_button.pack()

            # Agrega un botón para regresar a la ventana de cursos inscritos
            regresar_button = tk.Button(courses_window, text="Regresar a Estudiante", command=self.show_courses_window)
            regresar_button.pack()

    def show_courses_window(self):
    # Muestra la ventana de cursos inscritos nuevamente y cierra la ventana actual
        self.root.deiconify()
        self.root.focus_set()
        self.root.lift()

    def abrir_curso(self, course_name):
        course_window = tk.Toplevel()
        course_window.title(f"Curso: {course_name}")
        course_window.geometry("800x600")
        course_window.configure(bg="lightgreen")

    # Agregar contenido específico del curso aquí

        if course_name in self.notes and self.notes[course_name] >= 61:
            tk.Label(course_window, text="¡Felicitaciones, has aprobado el curso!", fg="green").pack()

        # Botón de regreso
        regresar_button = tk.Button(course_window, text="Regresar", command=self.show_courses_window)
        regresar_button.pack()

    def show_course_window(self):
        course_name = self.selected_course.get()
        if course_name in self.professor_window.course_messages:
            message = self.professor_window.course_messages[course_name].get(self.username, "Mensaje no disponible")
        else:
            message = "Mensaje no disponible"
        
        course_window = tk.Toplevel()
        course_window.title(f"Curso: {course_name}")
        course_window.geometry("800x600")
        course_window.configure(bg="lightgreen")
        
        tk.Label(course_window, text=f"Mensaje del profesor: {message}", font=("Helvetica", 12)).pack()

    def load_notes(self):
        try:
            with open(f"{self.username}_notas.txt", "r") as file:
                self.notes = json.load(file)
        except FileNotFoundError:
            self.notes = {}

    def save_notes(self):
        with open(f"{self.username}_notas.txt", "w") as file:
            json.dump(self.notes, file)

    def view_notes(self):
        if not self.notes:
            messagebox.showinfo("Notas", "No hay notas cargadas.")
        else:
            notes_window = tk.Toplevel()
            notes_window.title("Notas del Estudiante")

            notes_text = tk.Text(notes_window, height=10, width=50)
            notes_text.pack()

            for course, note in self.notes.items():
                notes_text.insert(tk.END, f"Curso: {course}, Nota: {note}\n")

                if note >= 61:
                    notes_text.insert(tk.END, "¡Felicitaciones, has aprobado el curso!\n\n")

    def inscribir_curso(self):
        from course_manager import CourseManager
        # Redirige a la ventana del administrador de cursos en course_manager.py
        root = tk.Tk()  # Crea una nueva instancia de Tk para la ventana del administrador de cursos
        course_manager = CourseManager(root)
        course_manager.show()  # Muestra la ventana del administrador de cursos

    def cargar_foto(self):
        ruta_foto = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if ruta_foto:
            self.ruta_foto = ruta_foto  # Almacena la ruta de la foto
            imagen = Image.open(self.ruta_foto)
            imagen.thumbnail((100, 100))  # Redimensiona la imagen a 100x100
            self.foto = ImageTk.PhotoImage(imagen)  # Carga la imagen redimensionada
            self.mostrar_foto()
            self.foto_cargada = True  # Marca que se ha cargado una foto

    def eliminar_foto(self):
        if not self.foto_cargada:
            messagebox.showinfo("Información", "No hay foto para eliminar.")
        else:
            self.ruta_foto = None
            self.foto = None  # Elimina la referencia a la foto
            self.label_foto.config(image=None)
            self.foto_cargada = False

    def mostrar_foto(self):
        if self.foto:
            self.label_foto.config(image=self.foto)

    def show(self):
        self.create_student_window()
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    student_window = StudentWindow(root, "usuario")
    student_window.show()
