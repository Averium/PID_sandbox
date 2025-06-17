# 🎯 PID Sandbox

**PID Sandbox** is an interactive, beginner-friendly tool for learning and experimenting with PID (Proportional-Integral-Derivative) controllers.

This sandbox provides a dynamic environment where you can tune PID parameters in real-time and see their effects immediately. Perfect for students, hobbyists, and anyone curious about control systems.

---

## 🚀 Features
- 📈 **Real-time system visualization**: Watch the system respond to your PID settings instantly.
- 🎛️ **Interactive settings**: Adjust `Kp`, `Ki`, and `Kd` on the fly.
- 🧠 **Real-time plotting**:

---

## 🛠 Installation

1. Clone this repository:

```bash
git clone https://github.com/Averium/pid-sandbox.git
cd pid-sandbox
```

2. Install dependencies:

```bash
pip install pygame-ce
pip install numpy
```

3. Run the sandbox:

```bash
python main.py
```

---

## 📚 How It Works

- Set your **Setpoint** (desired target).
- Tune **RED** settings with mouse wheel scrolling for controller settings.
- Tune **BLUE** settings with mouse wheel to set a scenario. 
- Observe how the system behavior changes:
  - `Kp` moves the system faster towards your setopint, but too much of it causes oscillations or overshoot!
  - `Ki` ensures zero control error, but too much of it also causes oscillation, overshoot and *windup*!
  - `Kd` adds damping to the system which stabilizes everything, but too much of it can cause kicking and slow setting times!

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## ❤️ Acknowledgments

Inspired by the need for more hands-on, intuitive learning tools in the control community.  
Special thanks to everyone who loves tinkering, learning, and teaching!
