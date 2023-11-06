import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from openpyxl import Workbook
import json

class ProfessorWindow:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.courses = {}  # Diccionario para almacenar cursos y calificaciones
        self.selected_course = None  # Curso seleccionado
        self.export_course_info()  # Exportar información al crear la ventana
        self.create_professor_window()

    def load_assigned_courses(self):
        try:
            with open("cursos.json", "r") as courses_file:
                all_courses = json.load(courses_file)
                if isinstance(all_courses, list):
                    # Filtrar los cursos en los que el profesor coincide con el nombre de usuario
                    self.courses = {course["course_name"]: course for course in all_courses if course.get("professor") == self.username}
                else:
                    self.courses = {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.courses = {}

        # Exportar nombre del curso y profesor a registro_curso.json
        self.export_course_info()
        # Crear la ventana del profesor después de cargar los cursos
        self.create_professor_window()


    def export_course_info(self):
        course_info = [{"course_name": course_name, "professor": course.get("professor")} for course_name, course in self.courses.items()]
        with open("registro_curso.json", "w") as export_file:
            json.dump(course_info, export_file, indent=4)

    def create_professor_window(self):
        self.root.title(f"Ventana de Profesor - {self.username}")
        self.root.geometry("400x400")

        frame = tk.Frame(self.root)
        frame.pack()

        # Agregar ListBox para mostrar la lista de cursos
        self.course_listbox = tk.Listbox(frame, selectmode=tk.SINGLE)
        self.course_listbox.pack()

        # Cargar la lista de cursos existentes
        for course_name in self.courses.keys():
            self.course_listbox.insert(tk.END, course_name)

        # Botón para editar cursos
        edit_courses_button = tk.Button(frame, text="Editar Cursos", command=self.edit_courses)
        edit_courses_button.pack()

        # Botón para editar calificaciones (deshabilitado inicialmente)
        self.edit_grades_button = tk.Button(frame, text="Editar Calificaciones", command=self.edit_grades)
        self.edit_grades_button.pack()
        self.edit_grades_button["state"] = "disabled"

        # Botón para exportar calificaciones (deshabilitado inicialmente)
        self.export_grades_button = tk.Button(frame, text="Exportar Calificaciones", command=self.export_grades)
        self.export_grades_button.pack()
        self.export_grades_button["state"] = "disabled"

        logout_button = ttk.Button(self.root, text="Cerrar Sesión", command=self.logout)
        logout_button.place(x=300, y=10)

        # Configurar un manejador de eventos para la selección de cursos
        self.course_listbox.bind("<<ListboxSelect>>", self.course_selected)

    def logout(self):
        # Cierra la ventana actual y muestra la ventana de inicio de sesión
        self.root.destroy()
        from login_window import LoginWindow
        login_window = LoginWindow()

    def edit_courses(self):
        # Editar cursos solo si se ha seleccionado un curso de la lista
        selected_courses = self.course_listbox.curselection()
        if not selected_courses:
            messagebox.showerror("Error", "Por favor, seleccione un curso de la lista.")
            return

        course_name = simpledialog.askstring("Editar Cursos", "Ingrese el nombre del curso:")
        if course_name:
            self.courses[course_name] = {"students": [], "notes": {}, "professor": self.username}
            self.save_data()
            # Actualizar la lista de cursos
            self.course_listbox.insert(tk.END, course_name)
            messagebox.showinfo("Editar Cursos", f"Curso '{course_name}' agregado con éxito.")

    def edit_grades(self):
        if self.selected_course:
            # Editar calificaciones aquí
            course_name = self.selected_course
            self.open_course_window(course_name)
        else:
            messagebox.showerror("Error", "Por favor, seleccione un curso para editar calificaciones.")

    def course_selected(self, event):
        # Manejar la selección de cursos
        selected_courses = self.course_listbox.curselection()
        if selected_courses:
            selected_course = self.course_listbox.get(selected_courses[0])
            self.selected_course = selected_course
            # Habilitar los botones de "Editar Calificaciones" y "Exportar Calificaciones"
            self.edit_grades_button["state"] = "normal"
            self.export_grades_button["state"] = "normal"
        else:
            self.selected_course = None
            # Deshabilitar los botones de "Editar Calificaciones" y "Exportar Calificaciones"
            self.edit_grades_button["state"] = "disabled"
            self.export_grades_button["state"] = "disabled"

    def open_course_window(self, course_name):
        course_data = self.courses.get(course_name)
        if course_data:
            students = course_data["students"]
            course_notes = course_data["notes"]
            course_window = ProfessorCourseWindow(tk.Toplevel(self.root), self.username, course_name, students, course_notes)
            course_window.show()

    def export_grades(self):
        if self.selected_course:
            course_name = self.selected_course
            if course_name in self.courses:
                # Exportar calificaciones
                course_data = self.courses[course_name]
                students = course_data["students"]
                notes = course_data["notes"]
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
                if file_path:
                    try:
                        workbook = Workbook()
                        worksheet = workbook.active
                        worksheet.append(["Estudiante", "Nota"])
                        for student in students:
                            note = notes.get(student, "")
                            worksheet.append([student, note])
                        workbook.remove(workbook.active)  # Elimina la hoja en blanco predeterminada
                        workbook.save(file_path)
                        messagebox.showinfo("Exportar Calificaciones", "Calificaciones exportadas con éxito.")
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo exportar calificaciones: {str(e)}")
            else:
                messagebox.showerror("Error", "El curso seleccionado no existe.")
        else:
            messagebox.showerror("Error", "Por favor, seleccione un curso para exportar calificaciones.")

    def show(self):
        self.root.mainloop()

class ProfessorCourseWindow:
    def __init__(self, root, professor_username, course_name, students, course_notes):
        self.root = root
        self.professor_username = professor_username
        self.course_name = course_name
        self.students = students  # Lista de estudiantes inscritos en el curso
        self.course_notes = course_notes
        self.student_listbox = None  # Agregar un atributo para el ListBox
        self.create_course_window()

    def create_course_window(self):
        self.root.title(f"Curso: {self.course_name} - Profesor: {self.professor_username}")
        self.root.geometry("600x400")

        frame = tk.Frame(self.root)
        frame.pack()

        student_list_label = tk.Label(frame, text="Lista de Estudiantes:")
        student_list_label.pack()

        # ListBox para mostrar la lista de estudiantes
        self.student_listbox = tk.Listbox(frame, selectmode=tk.SINGLE)
        for student in self.students:
            self.student_listbox.insert(tk.END, student)
        self.student_listbox.pack()

        edit_note_button = tk.Button(frame, text="Editar Nota", command=self.edit_note)
        edit_note_button.pack()

        export_grades_button = tk.Button(frame, text="Exportar Calificaciones", command=self.export_grades)
        export_grades_button.pack()

        logout_button = ttk.Button(self.root, text="Cerrar Curso", command=self.root.destroy)
        logout_button.place(x=500, y=10)

    def edit_note(self):
        selected_student = self.student_listbox.get(tk.ACTIVE)
        current_note = self.course_notes.get(selected_student, "")
        new_note = simpledialog.askfloat("Editar Nota", f"Ingrese la nueva nota para {selected_student}:", initialvalue=current_note)

        if new_note is not None:
            self.course_notes[selected_student] = new_note

    def export_grades(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            try:
                workbook = Workbook()
                worksheet = workbook.active
                worksheet.append(["Nombre del Estudiante", "Nota"])
                for student, note in self.course_notes.items():
                    worksheet.append([student, note])
                workbook.save(file_path)
                messagebox.showinfo("Exportar Calificaciones", "Calificaciones exportadas con éxito.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar calificaciones: {str(e)}")

    def show(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    professor_window = ProfessorWindow(root, "profesor1")  # Reemplaza "profesor1" con el nombre de usuario del profesor
    professor_window.show()

