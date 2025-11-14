# Stepper Motor Controller with TB6600 Driver

A comprehensive stepper motor control system featuring an ESP32-based controller with serial command interface and a professional desktop GUI application. Perfect for CNC machines, 3D printers, robotics, and automation projects.

![Stepper Motor Controller](https://img.shields.io/badge/Platform-ESP32%2BPython-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Version](https://img.shields.io/badge/Version-1.0-orange)

## ✨ Features

### 🎛️ Hardware Control
- **ESP32 Microcontroller** with TB6600 stepper driver compatibility
- **High Precision Control** with microstepping support (up to 1/32 step)
- **Flexible Configuration** for steps per revolution, speed, and acceleration
- **Safe Operation** with emergency stop and controlled deceleration

### 💻 Desktop GUI Application
- **Cross-Platform** Python/PyQt6 application (Windows, macOS, Linux)
- **Real-time Monitoring** with comprehensive serial monitor
- **Intuitive Controls** for both absolute and relative positioning
- **Professional Interface** with grouped controls and status display

### 🔧 Control Modes
- **Absolute Positioning** - Move to specific step positions
- **Relative Movement** - Move by revolutions with decimal precision
- **Continuous Rotation** - Run at constant speed in either direction
- **Homing & Zeroing** - Return to home position or set current position as zero

## 🛠️ Hardware Setup

### Required Components
- ESP32 Development Board
- TB6600 Stepper Motor Driver
- NEMA 17 or similar stepper motor
- 12-24V Power Supply for motor
- Jumper wires and connectors

### Wiring Diagram
```
ESP32 ↔ TB6600
GPIO13  → PUL+ (Step Pulse)
GPIO14  → DIR+ (Direction)
GND     → PUL- & DIR- (Common Ground)
```

**Motor Power:**
- TB6600 VCC: 12-24V DC
- TB6600 GND: Power supply ground
- A+, A-: Stepper motor coil A
- B+, B-: Stepper motor coil B

## 📋 Software Installation

### ESP32 Firmware
1. Install Arduino IDE with ESP32 support
2. Install required libraries:
   - `AccelStepper` by Mike McCauley
3. Upload `firmware.ino` to your ESP32
4. Open Serial Monitor at 115200 baud to verify operation

### Desktop GUI
```bash
# Install required Python packages
pip install pyserial pyqt6

# Run the application
python gui.py
```

## 🚀 Usage Guide

### Basic Operation
1. **Connect Hardware**: Wire ESP32 to TB6600 and power up
2. **Launch GUI**: Run `gui.py` to start the control application
3. **Establish Connection**: Select COM port and click "Connect"
4. **Configure Motor**: Set steps per revolution (default: 1600 for 1/8 microstepping)
5. **Start Controlling**: Use movement controls to operate the motor

### Movement Controls
- **Revolutions**: Move by exact revolutions (supports decimals)
- **Absolute Position**: Move to specific step count
- **Continuous Run**: Constant speed operation
- **Quick Buttons**: Pre-set movements (1, 10 revolutions)

### Safety Features
- **⏸ STOP**: Controlled stop with deceleration
- **🛑 E-STOP**: Immediate emergency stop
- **🏠 Home**: Return to zero position
- **⭕ Zero**: Set current position as new zero

## 📁 Project Structure

```
Stepper-Controller-with-TB6600-Driver/
│
├── firmware.ino              # ESP32 main controller firmware
├── first_test.ino           # Basic test and verification sketch
├── gui.py                   # Python desktop control application
└── README.md               # This file
```

## 🔌 Serial Protocol

The ESP32 firmware implements a simple text-based protocol:

### Configuration Commands
- `P<steps>` - Set steps per revolution
- `V<speed>` - Set maximum speed (steps/sec)
- `A<accel>` - Set acceleration (steps/sec²)

### Movement Commands
- `M<steps>` - Move to absolute position
- `R<revolutions>` - Move by revolutions
- `C<speed>` - Continuous run at speed

### Control Commands
- `X` - Stop with deceleration
- `E` - Emergency stop
- `G` - Go home (position 0)
- `Z` - Set current position as zero
- `S` - Show status
- `H` or `?` - Show help

## ⚙️ Configuration Examples

### Common Microstepping Settings
- Full step: 200 steps/rev
- 1/2 step: 400 steps/rev
- 1/4 step: 800 steps/rev
- 1/8 step: 1600 steps/rev (default)
- 1/16 step: 3200 steps/rev

### Performance Tuning
- **Max Speed**: 5000-20000 steps/sec (depending on motor)
- **Acceleration**: 1000-5000 steps/sec² for smooth operation
- **Microstepping**: Higher values for smoother movement, lower for more torque

## 🐛 Troubleshooting

### Common Issues
1. **Motor not moving**
   - Check power supply to TB6600
   - Verify DIR/PUL connections
   - Confirm enable pin settings on TB6600

2. **Wrong direction**
   - Use `stepper.setPinsInverted(false, true, false)` to invert direction
   - Swap motor coil wires A+/- or B+/-

3. **Serial connection fails**
   - Check COM port selection
   - Verify baud rate (115200)
   - Ensure no other program is using the serial port

4. **Motor stalling or missing steps**
   - Reduce maximum speed
   - Increase acceleration time
   - Check power supply voltage and current

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- New features
- Documentation improvements
- Performance enhancements

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **AccelStepper Library** by Mike McCauley for robust stepper control
- **PyQt6 Team** for the excellent GUI framework
- **ESP32 Community** for comprehensive documentation and support

---

**⭐ If this project helped you, please consider giving it a star on GitHub!**

For questions and support, please open an issue on the GitHub repository.