#include <AccelStepper.h>

// Define the two control pins on the left side of the ESP32
#define DIR_PIN 14 // Direction Pin (DIR+)
#define PUL_PIN 13 // Step/Pulse Pin (PUL+)

// Default motor parameters
long stepsPerRev = 1600;        // Default: 200 steps * 8 microsteps
float maxSpeed = 20000.0;       // Steps per second
float acceleration = 1500.0;    // Steps per second squared

// Movement control
long targetPosition = 0;
bool motorRunning = false;

AccelStepper stepper(1, PUL_PIN, DIR_PIN);

void setup() {
  Serial.begin(115200);
  
  stepper.setMaxSpeed(maxSpeed);
  stepper.setAcceleration(acceleration);
  stepper.setCurrentPosition(0);
  stepper.setPinsInverted(false, true, false);
  
  Serial.println("========================================");
  Serial.println("Stepper Motor Serial Control v1.0");
  Serial.println("========================================");
  printHelp();
  printStatus();
}

void loop() {
  // Process serial commands
  if (Serial.available() > 0) {
    processSerialCommand();
  }
  
  // Run the stepper motor
  stepper.run();
  
  // Check if movement completed
  if (motorRunning && stepper.distanceToGo() == 0) {
    motorRunning = false;
    Serial.println(">> Movement completed");
    printStatus();
  }
}

void processSerialCommand() {
  String command = Serial.readStringUntil('\n');
  command.trim(); // Remove whitespace
  command.toUpperCase(); // Convert to uppercase for consistency
  
  if (command.length() == 0) return;
  
  Serial.print(">> Received: ");
  Serial.println(command);
  
  // Parse command (first character) and value (rest)
  char cmd = command.charAt(0);
  String valueStr = (command.length() > 1) ? command.substring(1) : "";
  valueStr.trim(); // Remove any spaces
  
  // Execute commands
  if (cmd == 'H' || cmd == '?') {
    // Help
    printHelp();
    
  } else if (cmd == 'S') {
    // Status
    printStatus();
    
  } else if (cmd == 'P') {
    // Set Steps Per Revolution
    if (valueStr.length() > 0) {
      long value = valueStr.toInt();
      if (value > 0 && value <= 100000) {
        stepsPerRev = value;
        Serial.print(">> Steps per revolution set to: ");
        Serial.println(stepsPerRev);
      } else {
        Serial.println(">> ERROR: Invalid value (range: 1-100000)");
      }
    } else {
      Serial.println(">> ERROR: Missing value");
    }
    
  } else if (cmd == 'V') {
    // Set Max Speed
    if (valueStr.length() > 0) {
      float value = valueStr.toFloat();
      if (value > 0 && value <= 100000) {
        maxSpeed = value;
        stepper.setMaxSpeed(maxSpeed);
        Serial.print(">> Max speed set to: ");
        Serial.print(maxSpeed);
        Serial.println(" steps/sec");
      } else {
        Serial.println(">> ERROR: Invalid value (range: 1-100000)");
      }
    } else {
      Serial.println(">> ERROR: Missing value");
    }
    
  } else if (cmd == 'A') {
    // Set Acceleration
    if (valueStr.length() > 0) {
      float value = valueStr.toFloat();
      if (value > 0 && value <= 100000) {
        acceleration = value;
        stepper.setAcceleration(acceleration);
        Serial.print(">> Acceleration set to: ");
        Serial.print(acceleration);
        Serial.println(" steps/sec²");
      } else {
        Serial.println(">> ERROR: Invalid value (range: 1-100000)");
      }
    } else {
      Serial.println(">> ERROR: Missing value");
    }
    
  } else if (cmd == 'M') {
    // Move to absolute position (in steps)
    if (valueStr.length() > 0) {
      long value = valueStr.toInt();
      stepper.moveTo(value);
      motorRunning = true;
      Serial.print(">> Moving to position: ");
      Serial.print(value);
      Serial.println(" steps");
    } else {
      Serial.println(">> ERROR: Missing position value");
    }
    
  } else if (cmd == 'R') {
    // Move in revolutions
    if (valueStr.length() > 0) {
      float revs = valueStr.toFloat();
      long steps = (long)(revs * stepsPerRev);
      stepper.move(steps);
      motorRunning = true;
      Serial.print(">> Moving ");
      Serial.print(revs);
      Serial.print(" revolutions (");
      Serial.print(steps);
      Serial.println(" steps)");
    } else {
      Serial.println(">> ERROR: Missing revolutions value");
    }
    
  } else if (cmd == 'X') {
    // Stop motor (with deceleration)
    stepper.stop();
    Serial.println(">> Stopping motor (decelerating)");
    
  } else if (cmd == 'E') {
    // Emergency stop (immediate)
    stepper.setCurrentPosition(stepper.currentPosition());
    motorRunning = false;
    Serial.println(">> EMERGENCY STOP");
    
  } else if (cmd == 'Z') {
    // Set current position as zero
    stepper.setCurrentPosition(0);
    Serial.println(">> Current position set to ZERO");
    
  } else if (cmd == 'G') {
    // Go to home (position 0)
    stepper.moveTo(0);
    motorRunning = true;
    Serial.println(">> Homing to position 0");
    
  } else if (cmd == 'C') {
    // Continuous run at constant speed
    if (valueStr.length() > 0) {
      float speed = valueStr.toFloat();
      stepper.setSpeed(speed);
      Serial.print(">> Running at constant speed: ");
      Serial.print(speed);
      Serial.println(" steps/sec");
      Serial.println(">> Use X or E to halt");
    } else {
      Serial.println(">> ERROR: Missing speed value");
    }
    
  } else {
    Serial.println(">> ERROR: Unknown command. Type H for help.");
  }
}

void printHelp() {
  Serial.println("\n========== COMMAND REFERENCE ==========");
  Serial.println("Configuration:");
  Serial.println("  P<value>  - Set steps Per revolution (e.g., P1600)");
  Serial.println("  V<value>  - Set max Velocity in steps/sec (e.g., V10000)");
  Serial.println("  A<value>  - Set Acceleration in steps/sec² (e.g., A2000)");
  Serial.println();
  Serial.println("Movement:");
  Serial.println("  M<steps>  - Move to absolute position (e.g., M3200)");
  Serial.println("  R<revs>   - Move in Revolutions (e.g., R2.5 or R-2.5)");
  Serial.println("  C<speed>  - Continuous run at speed (e.g., C5000)");
  Serial.println();
  Serial.println("Control:");
  Serial.println("  X         - Stop with deceleration");
  Serial.println("  E         - Emergency stop (immediate)");
  Serial.println("  G         - Go home (return to position 0)");
  Serial.println("  Z         - Zero current position");
  Serial.println();
  Serial.println("Info:");
  Serial.println("  S         - Show Status");
  Serial.println("  H or ?    - Show this Help");
  Serial.println("========================================\n");
}

void printStatus() {
  Serial.println("\n========== CURRENT STATUS ==========");
  Serial.print("Steps per Revolution: ");
  Serial.println(stepsPerRev);
  Serial.print("Max Speed:            ");
  Serial.print(maxSpeed);
  Serial.println(" steps/sec");
  Serial.print("Acceleration:         ");
  Serial.print(acceleration);
  Serial.println(" steps/sec²");
  Serial.print("Current Position:     ");
  Serial.print(stepper.currentPosition());
  Serial.println(" steps");
  Serial.print("Target Position:      ");
  Serial.print(stepper.targetPosition());
  Serial.println(" steps");
  Serial.print("Distance to Go:       ");
  Serial.print(stepper.distanceToGo());
  Serial.println(" steps");
  Serial.print("Motor Status:         ");
  Serial.println(motorRunning ? "RUNNING" : "STOPPED");
  Serial.println("====================================\n");
}