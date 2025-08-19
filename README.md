# 🏠 Arduino Home Automation with Python GUI & Bluetooth

This project is a simple **home automation system** that allows you to control multiple electrical outlets (via relays) using an **Arduino + Bluetooth module (HC-05/HC-06)** and a **Python desktop GUI**.  

It includes:
- Arduino sketch (`Automation_4.ino`) to control relays.
- Python GUI (`gui_send.py`) built with Tkinter to send commands over serial/Bluetooth.
- Support for 4 relay-controlled outlets and additional devices.

---

## 🚀 Features
- Control up to **4 outlets** (e.g., lights, fan, appliances).
- Wireless communication via **HC-05 / HC-06 Bluetooth module**.
- Cross-platform **Python GUI** with ON/OFF buttons.
- Manual serial commands supported for debugging.
- Real-time logging of communication.

---

## 🛠 Hardware Setup

### Components
- Arduino Uno (or compatible)
- 4-channel relay module
- HC-05 or HC-06 Bluetooth module
- Jumper wires, breadboard
- Electrical loads (lamps, fan, etc.)

### Arduino Pin Wiring
| Device       | Arduino Pin | Relay Channel |
|--------------|-------------|---------------|
| Relay 1      | D2          | Outlet 1      |
| Relay 2      | D3          | Outlet 2      |
| Relay 3      | D7          | Outlet 3      |
| Relay 4      | D8          | Outlet 4      |

### Bluetooth Module Wiring
| HC-05/HC-06 | Arduino Pin |
|-------------|-------------|
| TX          | RX (D0)     |
| RX          | TX (D1)     |
| GND         | GND         |
| VCC (+5V)   | +5V         |

⚠️ **Note:** Use a **voltage divider** (or logic level converter) for Arduino TX → HC-05 RX, since Arduino works at 5V and HC-05 at 3.3V on RX.

---

## 🔌 Circuit Diagram (ASCII Style)

```
        +-------------------+
        |   Arduino UNO     |
        |                   |
 D2 ----| Relay1            |
 D3 ----| Relay2            |
 D7 ----| Relay3            |
 D8 ----| Relay4            |
        |                   |
 TX ----| HC-05 RX          |
 RX ----| HC-05 TX          |
 5V ----| HC-05 VCC         |
 GND ---| HC-05 GND         |
        +-------------------+
```

---

## 💻 Software Setup

### Arduino
1. Open `Automation_4.ino` in Arduino IDE.
2. Select your board & COM port.
3. Upload the sketch.

### Python GUI
1. Install dependencies:
   ```bash
   pip install pyserial
   ```
2. Run the GUI:
   ```bash
   python gui_send.py
   ```
3. Select the correct COM port (Bluetooth serial port) and connect.
4. Use ON/OFF buttons to control devices.

---

## 🔑 Commands
The Arduino expects single-character commands ending with `#`.  

| Command | Action          |
|---------|-----------------|
| `A#`    | Switch ON       |
| `a#`    | Switch OFF      |
| `B#`    | Light ON        |
| `b#`    | Light OFF       |
| `C#`    | Light ON        |
| `c#`    | Light OFF       |
| `D#`    | Light ON        |
| `d#`    | Light OFF       |
| `E#`    | Fan ON          |
| `e#`    | Fan OFF         |

---

## 📷 Future Improvements
- Add a mobile app for control.
- Add MQTT/IoT cloud support.
- Secure authentication for commands.

---

## 📝 License
This project is open-source under the MIT License.
