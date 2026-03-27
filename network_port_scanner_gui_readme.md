# Network Port Scanner GUI

A lightweight and user-friendly TCP port scanner built using Python and Tkinter. This tool allows users to scan a range of ports on a target system and identify open ports along with common services.

---

## 🚀 Features

- Simple GUI with only 3 inputs (Target, Start Port, End Port)
- Multi-threaded scanning for faster results
- Real-time progress bar and status updates
- Service identification for common ports (HTTP, SSH, etc.)
- Ability to stop scanning anytime
- Save results to a `.txt` file
- Cross-platform (Windows, macOS, Linux)

---

## 🛠️ Technologies Used

- Python
- Tkinter (GUI)
- Socket Programming
- Multithreading

---

## 📦 Installation

1. Make sure Python is installed (Python 3.x recommended)
2. Download or clone this repository
3. Navigate to the project folder

---

## ▶️ How to Run

```bash
python portscanergui.py
```

---

## 📌 Usage

1. Enter the target IP address or hostname
2. Enter the start port (e.g., 1)
3. Enter the end port (e.g., 1024)
4. Click **Start Scan**
5. View results in real-time
6. Click **Stop** to cancel scan anytime
7. Save results using **Save Results** button

---

## 📊 Example Output

```
[+] Port 80 (HTTP) open
[+] Port 443 (HTTPS) open
Scan complete.
Open ports found: 2
```

---

## ⚠️ Limitations

- Only supports TCP connect scan
- Service detection is based on common port mapping (not deep inspection)
- High thread counts may affect system performance

---

## 🔮 Future Improvements

- Add banner grabbing for better service detection
- Export results in CSV/JSON format
- Dark mode UI
- Scan speed statistics

---


