import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGroupBox, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QTextEdit, QSpinBox,
                             QDoubleSpinBox, QGridLayout)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
import serial
import serial.tools.list_ports

class SerialThread(QThread):
    """Thread for reading serial data without blocking GUI"""
    received = pyqtSignal(str)
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True
    
    def run(self):
        while self.running:
            if self.serial_port and self.serial_port.is_open:
                try:
                    if self.serial_port.in_waiting:
                        data = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                        if data:
                            self.received.emit(data)
                except Exception as e:
                    self.received.emit(f"Error reading: {str(e)}")
            self.msleep(10)
    
    def stop(self):
        self.running = False

class StepperControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.serial_thread = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Stepper Motor Controller - TB6600')
        # Increased height for better initial view of the new layout
        self.setGeometry(100, 100, 1000, 800) 
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Change to QGridLayout for two-column layout
        main_layout = QGridLayout(central_widget)
        
        # Left Column Layout (Groups stacked vertically)
        left_column_layout = QVBoxLayout()
        
        # Connection Group (Row 0, Col 0 - Left Column)
        conn_group = self.create_connection_group()
        left_column_layout.addWidget(conn_group)
        
        # Configuration Group (Row 1, Col 0 - Left Column)
        config_group = self.create_config_group()
        left_column_layout.addWidget(config_group)
        
        # Movement Control Group (Row 2, Col 0 - Left Column)
        movement_group = self.create_movement_group()
        left_column_layout.addWidget(movement_group)
        
        # Control Buttons Group (Row 3, Col 0 - Left Column)
        control_group = self.create_control_group()
        left_column_layout.addWidget(control_group)
        
        left_column_layout.addStretch() # Push all widgets to the top of the left column
        
        # Add the left column layout to the main grid
        main_layout.addLayout(left_column_layout, 0, 0, 1, 1) # Row 0, Col 0, span 1 row, 1 col
        
        # Serial Monitor (Row 0, Col 1 - Right Column, spanning all rows)
        monitor_group = self.create_monitor_group()
        # Set monitor to occupy the entire right column (Row 0, Col 1, span 4 rows)
        main_layout.addWidget(monitor_group, 0, 1, 4, 1) 
        
        # Status Bar
        self.statusBar().showMessage('Disconnected')
    
    def create_connection_group(self):
        group = QGroupBox("Serial Connection")
        layout = QHBoxLayout()
        
        # COM Port selection
        layout.addWidget(QLabel("COM Port:"))
        self.port_combo = QComboBox()
        self.refresh_ports()
        layout.addWidget(self.port_combo)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(refresh_btn)
        
        # Baud rate
        layout.addWidget(QLabel("Baud:"))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '115200', '230400'])
        self.baud_combo.setCurrentText('115200')
        layout.addWidget(self.baud_combo)
        
        # Connect/Disconnect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def create_config_group(self):
        group = QGroupBox("Motor Configuration")
        layout = QGridLayout()
        
        # Steps per revolution
        layout.addWidget(QLabel("Steps/Rev:"), 0, 0)
        self.spr_input = QSpinBox()
        self.spr_input.setRange(200, 100000)
        self.spr_input.setValue(1600)
        self.spr_input.setSingleStep(200)
        layout.addWidget(self.spr_input, 0, 1)
        
        spr_btn = QPushButton("Set")
        spr_btn.clicked.connect(lambda: self.send_command(f"P{self.spr_input.value()}"))
        layout.addWidget(spr_btn, 0, 2)
        
        # Max speed
        layout.addWidget(QLabel("Max Speed (steps/s):"), 1, 0)
        self.speed_input = QSpinBox()
        self.speed_input.setRange(100, 100000)
        self.speed_input.setValue(20000)
        self.speed_input.setSingleStep(1000)
        layout.addWidget(self.speed_input, 1, 1)
        
        speed_btn = QPushButton("Set")
        speed_btn.clicked.connect(lambda: self.send_command(f"V{self.speed_input.value()}"))
        layout.addWidget(speed_btn, 1, 2)
        
        # Acceleration
        layout.addWidget(QLabel("Acceleration (steps/s²):"), 2, 0)
        self.accel_input = QSpinBox()
        self.accel_input.setRange(100, 100000)
        self.accel_input.setValue(1500)
        self.accel_input.setSingleStep(500)
        layout.addWidget(self.accel_input, 2, 1)
        
        accel_btn = QPushButton("Set")
        accel_btn.clicked.connect(lambda: self.send_command(f"A{self.accel_input.value()}"))
        layout.addWidget(accel_btn, 2, 2)
        
        # Apply all button
        apply_all_btn = QPushButton("Apply All Configuration")
        apply_all_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        apply_all_btn.clicked.connect(self.apply_all_config)
        layout.addWidget(apply_all_btn, 3, 0, 1, 3)
        
        group.setLayout(layout)
        return group
    
    def create_movement_group(self):
        group = QGroupBox("Movement Control")
        layout = QGridLayout()
        
        # Move by revolutions
        layout.addWidget(QLabel("Revolutions:"), 0, 0)
        self.rev_input = QDoubleSpinBox()
        self.rev_input.setRange(-1000, 1000)
        self.rev_input.setValue(1.0)
        self.rev_input.setSingleStep(0.5)
        self.rev_input.setDecimals(2)
        layout.addWidget(self.rev_input, 0, 1)
        
        rev_btn = QPushButton("Move")
        rev_btn.clicked.connect(lambda: self.send_command(f"R{self.rev_input.value()}"))
        layout.addWidget(rev_btn, 0, 2)
        
        # Quick revolution buttons
        quick_layout = QHBoxLayout()
        quick_revs = [("← 10", -10), ("← 1", -1), ("→ 1", 1), ("→ 10", 10)]
        for text, value in quick_revs:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, v=value: self.send_command(f"R{v}"))
            quick_layout.addWidget(btn)
        layout.addLayout(quick_layout, 1, 0, 1, 3)
        
        # Move to absolute position
        layout.addWidget(QLabel("Absolute Pos (steps):"), 2, 0)
        self.pos_input = QSpinBox()
        self.pos_input.setRange(-1000000, 1000000)
        self.pos_input.setValue(0)
        self.pos_input.setSingleStep(100)
        layout.addWidget(self.pos_input, 2, 1)
        
        pos_btn = QPushButton("Move To")
        pos_btn.clicked.connect(lambda: self.send_command(f"M{self.pos_input.value()}"))
        layout.addWidget(pos_btn, 2, 2)
        
        # Continuous run
        layout.addWidget(QLabel("Continuous Speed:"), 3, 0)
        self.cont_speed_input = QSpinBox()
        self.cont_speed_input.setRange(-100000, 100000)
        self.cont_speed_input.setValue(5000)
        self.cont_speed_input.setSingleStep(1000)
        layout.addWidget(self.cont_speed_input, 3, 1)
        
        cont_btn = QPushButton("Run Continuous")
        cont_btn.clicked.connect(lambda: self.send_command(f"C{self.cont_speed_input.value()}"))
        layout.addWidget(cont_btn, 3, 2)
        
        group.setLayout(layout)
        return group
    
    def create_control_group(self):
        group = QGroupBox("Motor Control")
        layout = QHBoxLayout()
        
        # Stop button
        stop_btn = QPushButton("⏸ STOP")
        stop_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px;")
        stop_btn.clicked.connect(lambda: self.send_command("X"))
        layout.addWidget(stop_btn)
        
        # Emergency stop
        estop_btn = QPushButton("🛑 E-STOP")
        estop_btn.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 10px;")
        estop_btn.clicked.connect(lambda: self.send_command("E"))
        layout.addWidget(estop_btn)
        
        # Home
        home_btn = QPushButton("🏠 Home")
        home_btn.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 10px;")
        home_btn.clicked.connect(lambda: self.send_command("G"))
        layout.addWidget(home_btn)
        
        # Zero position
        zero_btn = QPushButton("⭕ Zero")
        zero_btn.setStyleSheet("background-color: #607D8B; color: white; font-weight: bold; padding: 10px;")
        zero_btn.clicked.connect(lambda: self.send_command("Z"))
        layout.addWidget(zero_btn)
        
        # Status
        status_btn = QPushButton("📊 Status")
        status_btn.setStyleSheet("background-color: #009688; color: white; font-weight: bold; padding: 10px;")
        status_btn.clicked.connect(lambda: self.send_command("S"))
        layout.addWidget(status_btn)
        
        # Help
        help_btn = QPushButton("❓ Help")
        help_btn.setStyleSheet("background-color: #3F51B5; color: white; font-weight: bold; padding: 10px;")
        help_btn.clicked.connect(lambda: self.send_command("H"))
        layout.addWidget(help_btn)
        
        group.setLayout(layout)
        return group
    
    def create_monitor_group(self):
        group = QGroupBox("Serial Monitor")
        layout = QVBoxLayout()
        
        self.monitor = QTextEdit()
        self.monitor.setReadOnly(True)
        self.monitor.setFont(QFont("Courier", 9))
        # Removed setMaximumHeight(200) to allow it to expand
        layout.addWidget(self.monitor)
        
        # Command input
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(QLabel("Send:"))
        self.cmd_input = QLineEdit()
        self.cmd_input.returnPressed.connect(self.send_custom_command)
        cmd_layout.addWidget(self.cmd_input)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_custom_command)
        cmd_layout.addWidget(send_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.monitor.clear)
        cmd_layout.addWidget(clear_btn)
        
        layout.addLayout(cmd_layout)
        group.setLayout(layout)
        return group
    
    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")
    
    def toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def connect_serial(self):
        try:
            port = self.port_combo.currentText().split(' - ')[0]
            baud = int(self.baud_combo.currentText())
            
            self.serial_port = serial.Serial(port, baud, timeout=1)
            self.log_monitor(f"Connected to {port} at {baud} baud")
            
            # Start reading thread
            self.serial_thread = SerialThread(self.serial_port)
            self.serial_thread.received.connect(self.log_monitor)
            self.serial_thread.start()
            
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet("background-color: #F44336; color: white; font-weight: bold;")
            self.statusBar().showMessage(f'Connected to {port}')
            
        except Exception as e:
            self.log_monitor(f"Connection failed: {str(e)}")
            self.statusBar().showMessage('Connection failed')
    
    def disconnect_serial(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.wait()
        
        if self.serial_port:
            self.serial_port.close()
            self.log_monitor("Disconnected")
        
        self.connect_btn.setText("Connect")
        self.connect_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.statusBar().showMessage('Disconnected')
    
    def send_command(self, command):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(f"{command}\n".encode())
                self.log_monitor(f"SENT: {command}", color="blue")
            except Exception as e:
                self.log_monitor(f"Send error: {str(e)}", color="red")
        else:
            self.log_monitor("Not connected!", color="red")
    
    def send_custom_command(self):
        command = self.cmd_input.text().strip()
        if command:
            self.send_command(command)
            self.cmd_input.clear()
    
    def apply_all_config(self):
        self.send_command(f"P{self.spr_input.value()}")
        self.send_command(f"V{self.speed_input.value()}")
        self.send_command(f"A{self.accel_input.value()}")
        self.log_monitor("Configuration applied", color="green")
    
    def log_monitor(self, message, color="black"):
        if color == "blue":
            self.monitor.append(f'<span style="color: blue;"><b>{message}</b></span>')
        elif color == "red":
            self.monitor.append(f'<span style="color: red;"><b>{message}</b></span>')
        elif color == "green":
            self.monitor.append(f'<span style="color: green;"><b>{message}</b></span>')
        else:
            self.monitor.append(message)
        
        # Auto-scroll to bottom
        self.monitor.verticalScrollBar().setValue(
            self.monitor.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        self.disconnect_serial()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    gui = StepperControlGUI()
    gui.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()