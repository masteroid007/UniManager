import uuid
import pandas as pd
import datetime

class Student:
    def __init__(self, name, surname, studentId=None):
        self.name = name
        self.surname = surname
        self.studentId = studentId if studentId else str(uuid.uuid4())
        self.courses = []
        self.grades = {}

    def studentInfo(self):
        return f"""
INFORMAZIONI STUDENTE

Nome: {self.name}
Cognome: {self.surname}
ID Univoco: {self.studentId}
Corsi frequentati: {self.courses if self.courses else "Nessun corso frequentato"}
Voti: {self.grades if self.grades else "Nessun voto registrato"}
"""

    def enroll(self, course):
        if course.courseName not in self.courses:
            self.courses.append(course.courseName)

        if self.studentId not in course.students:
            course.students.append(self.studentId)

        return f"Studente {self.name} iscritto a {course.courseName}"

    def addGrade(self, course, grade):
        if course.courseName not in self.courses:
            return "Studente non iscritto al corso"

        if course.courseName in self.grades:
            self.grades[course.courseName].append(grade)
        else:
            self.grades[course.courseName] = [grade]

        return f"Voto {grade} aggiunto a {course.courseName}"

    def averageGrade(self):
        voti = []
        for lista in self.grades.values():
            voti.extend(lista)

        if not voti:
            return 0

        return sum(voti) / len(voti)

    def isExcellent(self):
        return self.averageGrade() >= 28


class Course:
    def __init__(self, courseName, teacher, maxStudents):
        self.courseName = courseName
        self.teacher = teacher
        self.maxStudents = maxStudents
        self.students = []

    def courseInfo(self):
        return f"""
INFORMAZIONI CORSO
Nome: {self.courseName}
Docente: {self.teacher}
Max studenti: {self.maxStudents}
Studenti: {self.students if self.students else "Nessuno"}
"""

    def isFull(self):
        return len(self.students) >= self.maxStudents

    def addStudent(self, studentId):
        if studentId not in self.students and not self.isFull():
            self.students.append(studentId)


class University:
    def __init__(self):
        self.students = []
        self.courses = []

    def writeLog(self, message):
        with open("logs.txt", "a") as file:
            file.write(message + "\n")

    def registerStudent(self, student):
        for s in self.students:
            if s.studentId == student.studentId:
                self.writeLog("[ERROR] Studente già registrato")
                return "Studente già registrato"

        self.students.append(student)
        self.writeLog(f"[INFO] Studente registrato {student.name} {student.surname} con ID studente {student.studentId}")
        return f"Studente registrato con ID {student.studentId}"

    def createCourse(self, course):
        for c in self.courses:
            if c.courseName == course.courseName:
                self.writeLog("[ERROR] Corso già esistente")
                return "Corso già esistente"

        self.courses.append(course)
        self.writeLog(f"[INFO] Corso creato {course.courseName}")
        return "Corso creato"

    def findStudent(self, info, typeFind="id"):
        results = []

        for student in self.students:
            if typeFind == "id":
                if student.studentId == info:
                    return student

            elif typeFind == "nome":
                if student.name.lower() == info.lower():
                    results.append(student)

            elif typeFind == "cognome":
                if student.surname.lower() == info.lower():
                    results.append(student)

        return None if typeFind == "id" else results
                

    def findCourse(self, courseName):
        for course in self.courses:
            if course.courseName == courseName:
                return course
        return None

    def showTopStudents(self):
        valid_students = [s for s in self.students if s.grades]

        sorted_students = sorted(
            valid_students,
            key=lambda s: s.averageGrade(),
            reverse=True
        )

        return [
            f"{s.name} {s.surname} - Media: {s.averageGrade()}"
            for s in sorted_students
        ]

    def saveData(self):
        students = []
        courses = []
        enrollments = []
        grades = []

        
        for s in self.students:
            students.append({
                "StudentID": s.studentId,
                "Name": s.name,
                "Surname": s.surname
            })

        pd.DataFrame(students).to_csv("students.csv", index=False)


        for c in self.courses:
            courses.append({
                "CourseName": c.courseName,
                "Teacher": c.teacher,
                "MaxStudents": c.maxStudents
            })

        pd.DataFrame(courses).to_csv("courses.csv", index=False)

        
        for s in self.students:
            for course in s.courses:
                enrollments.append({
                    "StudentID": s.studentId,
                    "Course": course
                })

        pd.DataFrame(enrollments).to_csv("enrollments.csv", index=False)

        
        for s in self.students:
            for course, grade_list in s.grades.items():
                for g in grade_list:
                    grades.append({
                        "StudentID": s.studentId,
                        "Course": course,
                        "Grade": g
                    })

        pd.DataFrame(grades).to_csv("grades.csv", index=False)

        self.writeLog(f"[SYSTEM]  Dati salvati")
        return "Dati salvati"

    def loadData(self):
        self.students = []
        self.courses = []

        
        try:
            df = pd.read_csv("students.csv")

            for _, row in df.iterrows():
                self.students.append(
                    Student(row["Name"], row["Surname"], row["StudentID"])
                )

        except FileNotFoundError:
            pass

        
        try:
            df = pd.read_csv("courses.csv")

            for _, row in df.iterrows():
                self.courses.append(
                    Course(
                        row["CourseName"],
                        row["Teacher"],
                        int(row["MaxStudents"])
                    )
                )

        except FileNotFoundError:
            pass

        
        try:
            df = pd.read_csv("enrollments.csv")

            for _, row in df.iterrows():
                student = self.findStudent(row["StudentID"])
                course = self.findCourse(row["Course"])

                if student and course:

                    if row["Course"] not in student.courses:
                        student.courses.append(row["Course"])

                    if student.studentId not in course.students:
                        course.students.append(student.studentId)

        except FileNotFoundError:
            pass

        
        try:
            df = pd.read_csv("grades.csv")

            for _, row in df.iterrows():
                student = self.findStudent(row["StudentID"])

                if student:

                    if row["Course"] not in student.grades:
                        student.grades[row["Course"]] = []

                    student.grades[row["Course"]].append(float(row["Grade"]))

        except FileNotFoundError:
            pass


        for s in self.students:
            for courseName in s.courses:
                course = self.findCourse(courseName)

                if course and s.studentId not in course.students:
                    course.students.append(s.studentId)

        self.writeLog("[SYSTEM] Dati caricati")
        return "Dati caricati"
    
    def listCourses(self):
        if len(self.courses) == 0:
            return "Nessun corso registrato"

        result = ""
        for c in self.courses:
            result += c.courseName + "\n"

        return result.strip()


    def listStudents(self):
        if len(self.students) == 0:
            return "Nessuno studente registrato"

        result = ""
        for s in self.students:
            result += f"{s.name} {s.surname} - Id Univoco: {s.studentId}\n"

        return result.strip()


def main():
    uni = University()
    uni.loadData()

    while True:
        print("""
MENU PRINCIPALE

1. Registra studente
2. Crea corso
3. Iscrivi studente
4. Aggiungi voto
5. Mostra studente
6. Mostra corso
7. Mostra lista studenti
8. Mostra lista corsi
9. Classifica studenti
10. Salva dati
11. Carica dati
12. Mostra log
0. Esci
""")
        try:
            choice = int(input("Scelta: "))

            match choice:
                case 1:
                    name = input("Nome: ")
                    surname = input("Cognome: ")
                    student = Student(name, surname)
                    print(uni.registerStudent(student))

                case 2:
                    name = input("Nome corso: ")
                    teacher = input("Docente: ")

                    try:
                        max_students = int(input("Max studenti: "))
                    except ValueError:
                        print("Numero non valido")
                        continue

                    course = Course(name, teacher, max_students)
                    print(uni.createCourse(course))

                case 3:
                    sid = input("ID studente: ")
                    cname = input("Nome corso: ")

                    student = uni.findStudent(sid)
                    course = uni.findCourse(cname)

                    if student is None or course is None:
                        print("Errore: studente o corso non trovato")
                    else:
                        print(student.enroll(course))
                        uni.writeLog(f"[ENROLL] {student.studentId} -> {course.courseName}")

                case 4:
                    sid = input("ID studente: ")
                    cname = input("Corso: ")

                    try:
                        grade = float(input("Voto: "))
                    except ValueError:
                        print("Voto non valido")
                        continue

                    student = uni.findStudent(sid)
                    course = uni.findCourse(cname)

                    if student is None or course is None:
                        print("Errore")
                    else:
                        print(student.addGrade(course, grade))
                        uni.writeLog(f"[GRADE] {student.studentId} | {course.courseName} | {grade}")

                case 5:
                    scelta = input("Che tipo di ricerca? (nome/cognome/id): ").lower().strip()

                    while scelta not in ["nome", "cognome", "id"]:
                        print("Scelta non valida")
                        scelta = input("Che tipo di ricerca? (nome/cognome/id): ").lower().strip()

                    info = input("Info studente da cercare: ")

                    result = uni.findStudent(info, scelta)

                    if not result:
                        print("Studente non trovato")
                    else:
                        try:
                            for s in result:
                                print(s.studentInfo())
                        except TypeError:
                            print(result.studentInfo())

                case 6:
                    cname = input("Nome corso: ")
                    course = uni.findCourse(cname)

                    if course is None:
                        print("Corso non trovato")
                    else:
                        print(course.courseInfo())

                case 7:
                    print(uni.listStudents())

                case 8:
                    print(uni.listCourses())

                case 9:
                    for s in uni.showTopStudents():
                        print(s)

                case 10:
                    print(uni.saveData())

                case 11:
                    print(uni.loadData())

                case 12:
                    try:
                        with open("logs.txt", "r") as file:
                            print(file.read())
                    except FileNotFoundError:
                        print("Nessun log disponibile")

                case 0:
                    break

                case _:
                    print("Scelta non valida")
        
        except ValueError:
            print("Scelta non valida")
        
        except Exception as e:
            print("Errore:", e)


if __name__ == "__main__":
    main()