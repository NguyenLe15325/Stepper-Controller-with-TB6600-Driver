#include <AccelStepper.h>

// Define the two control pins on the left side of the ESP32
#define DIR_PIN 14 // Direction Pin (DIR+)
#define PUL_PIN 13 // Step/Pulse Pin (PUL+)

// Define the steps per revolution for 1/8 microstepping: 200 * 8 = 1600
const long STEPS_PER_REV = 1600;
const long REVOLUTIONS_TO_MOVE = 40;
const long FORWARD_TARGET = REVOLUTIONS_TO_MOVE * STEPS_PER_REV; // e.g., 16000 steps

// IMPORTANT: Using constant '1' (AccelStepper::DRIVER) is the most standard setting.
// The previous constant '4' was experimental. Reverting to '1' often resolves direction issues.
AccelStepper stepper(1, PUL_PIN, DIR_PIN); 

void setup() {
  Serial.begin(115200);
  
  // Set faster motor parameters
  stepper.setMaxSpeed(20000.0);       // Max speed in steps/second
  stepper.setAcceleration(1500.0);   // Acceleration rate in steps/second/second
  
  // Set the current position to 0
  stepper.setCurrentPosition(0); 

  // OPTIONAL: Invert the DIR pin logic if the motor doesn't reverse direction.
  // Format: setPinsInverted(enable_pin, direction_pin, step_pin)
  // Setting the direction_pin parameter (the second one) to true inverts its logic.
  stepper.setPinsInverted(false, true, false); 
  
  Serial.println("Stepper initialized. Starting movement test (10 revs FWD/REV).");
}

void loop() {
  // MUST be called as often as possible to generate steps and manage acceleration.
  stepper.run(); 

  // Check if the motor has reached its target position
  if (stepper.distanceToGo() == 0) {
    
    // Check the current position to decide the next target
    if (stepper.currentPosition() == 0) {
      // If at 0, move FORWARD to the target position
      stepper.moveTo(FORWARD_TARGET); 
      Serial.print("Moving FORWARD to position: ");
      Serial.println(FORWARD_TARGET);
      
    } else {
      // If at the forward target, move REVERSE back to 0
      stepper.moveTo(0); 
      Serial.println("Moving REVERSE back to position: 0");
    }
    
    // Pause briefly (0.5 seconds) at the end of the movement cycle
    delay(500); 
  }
}