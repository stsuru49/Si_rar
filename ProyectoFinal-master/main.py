import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtCore import QTime, QTimer
from datetime import datetime
from ui_interfaz_grafica import Ui_MainWindow
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

class Horario:
    def __init__(self):
        self.horarios = [["" for _ in range(3)] for _ in range(7)]

    def guardar_horario(self, dia, columna, hora):
        self.horarios[dia][columna] = hora

    def obtener_horario_extremo(self):
        horas_planificadas = [
            QTime.fromString(hora, "hh:mm")
            for fila in self.horarios
            for hora in fila
            if hora
        ]
        if not horas_planificadas:
            return None, None

        horas_planificadas = sorted(horas_planificadas)
        return horas_planificadas[0].toString("hh:mm"), horas_planificadas[-1].toString("hh:mm")
    def buscar_dias_por_hora(self, hora_buscada):
        # Lista de días de la semana en español
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        # Convertir hora buscada al formato correcto
        hora_buscada = QTime.fromString(hora_buscada, "hh:mm").toString("hh:mm")
        
        dias_encontrados = []
        for i, fila in enumerate(self.horarios):
            if hora_buscada in [hora.strip() for hora in fila if hora]:
                dias_encontrados.append(dias_semana[i])
        
        return dias_encontrados
    
class Usuario:
    def __init__(self):
        self.nombre = ""
        self.correos = []

    def guardar_usuario(self, nombre):
        self.nombre = nombre

    def guardar_correos(self, lista_correos):
        self.correos = lista_correos


class Persistencia:
    def __init__(self, archivo="datos.json"):
        self.archivo = archivo

    def guardar_datos(self, datos):
        with open(self.archivo, "w") as file:
            json.dump(datos, file, indent=4)

    def cargar_datos(self):
        try:
            with open(self.archivo, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"usuario": "", "correos": [], "horarios": [["" for _ in range(3)] for _ in range(7)]}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Inicializar clases
        self.usuario = Usuario()
        self.horario = Horario()
        self.persistencia = Persistencia()
        # Configurar interfaz
        self.ui.scheduleTableWidget.setHorizontalHeaderLabels(["Horario 1", "Horario 2", "Horario 3"])
        self.ui.scheduleTableWidget.setVerticalHeaderLabels(
            ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        )
        
        self.ui.buscarButton.clicked.connect(self.buscar_dias)
        # Temporizador para comparación de horarios
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.comparar_horarios)
        self.timer.start(60000)
        # Cargar datos iniciales
        self.cargar_datos()
        # Conectar botones
        self.ui.guardarHorariosButton.clicked.connect(self.guardar_horarios)
        self.ui.guardarCorreosButton.clicked.connect(self.guardar_correos)
        self.ui.buscarExtremosButton.clicked.connect(self.mostrar_extremos)
        self.ui.resultadosLabel2.setWordWrap(True)


    def cargar_datos(self):
        datos = self.persistencia.cargar_datos()
        self.usuario.guardar_usuario(datos["usuario"])
        self.usuario.guardar_correos(datos["correos"])
        self.horario.horarios = datos["horarios"]
        # Mostrar datos en la interfaz
        self.ui.nombreUsuarioLineEdit.setText(self.usuario.nombre)
        self.ui.correosTextEdit.setText(", ".join(self.usuario.correos))
        for i, fila in enumerate(self.horario.horarios):
            for j, hora in enumerate(fila):
                self.ui.scheduleTableWidget.setItem(i, j, QTableWidgetItem(hora))

    def buscar_dias(self):
    
        hora_buscada = self.ui.buscarHorarioInput.text()
        
        if not QTime.fromString(hora_buscada, "hh:mm").isValid():
            self.ui.resultadosLabel2.setText("Formato de hora inválido. Usa 'hh:mm'.")
            return
        dias_encontrados = self.horario.buscar_dias_por_hora(hora_buscada)
        
        if dias_encontrados:
            self.ui.resultadosLabel2.setText(f"La hora {hora_buscada} está registrada en: {', '.join(dias_encontrados)}.")
        else:
            self.ui.resultadosLabel2.setText(f"La hora {hora_buscada} no está registrada en ningún día.")

    def guardar_horarios(self):
        for i in range(7):
            for j in range(3):
                item = self.ui.scheduleTableWidget.item(i, j)
                hora = item.text() if item else ""
                self.horario.guardar_horario(i, j, hora)

        self.guardar_datos()

    def guardar_correos(self):
        correos = self.ui.correosTextEdit.toPlainText().split(",")
        self.usuario.guardar_correos([correo.strip() for correo in correos if correo.strip()])
        self.guardar_datos()

    def guardar_datos(self):
        datos = {
            "usuario": self.usuario.nombre,
            "correos": self.usuario.correos,
            "horarios": self.horario.horarios,
        }
        self.persistencia.guardar_datos(datos)

    def mostrar_extremos(self):
        temprano, tardio = self.horario.obtener_horario_extremo()
        if temprano and tardio:
            self.ui.resultadosLabel.setText(f"Más temprano: {temprano}, Más tardío: {tardio}")
        else:
            self.ui.resultadosLabel.setText("No hay horarios registrados.")

    def comparar_horarios(self):
        dia_actual = datetime.now().strftime("%A").lower()  # Día actual en minúsculas
        hora_actual = datetime.now().strftime("%H:%M")  # Hora actual en formato hh:mm
        
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        if dia_actual not in dias_semana:
            print(f"Día no reconocido: {dia_actual}")
            return
        
        indice_dia = dias_semana.index(dia_actual)  # Encuentra el índice del día actual
        horarios_dia_actual = self.horario.horarios[indice_dia]  # Horarios del día actual
        
        print(f"Horarios del día {dia_actual}: {horarios_dia_actual}")  # Para depuración
        
        for horario in horarios_dia_actual:
            if hora_actual == horario.strip():  # Compara después de eliminar espacios adicionales
                print("Hora encontrada en la tabla, enviando alerta...")
                self.enviar_alerta_arduino()
                break
            
            
    def enviar_alerta_arduino(self):
        import serial
        import time

        arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

        try:
            while True:
                arduino.write("AS\n".encode())
                print("Se envió la señal ACTIVAR al Arduino")

                time.sleep(0.5)
                respuesta = arduino.readline().decode("ascii").strip()
                print(f"Respuesta del Arduino: {respuesta}")
                if respuesta == "r":
                    print("El Arduino confirmó la acción.")
                    break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            arduino.close()

if __name__ == "__main__":
    app = QApplication([])
    ventana = MainWindow()
    ventana.show()
    app.exec_()