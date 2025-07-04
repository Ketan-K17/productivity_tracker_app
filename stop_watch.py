import tkinter as tk
from datetime import datetime
import pandas as pd
import os

class SimpleStopwatch:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Focus Timer")

        self.running = False
        self.start_time = None
        self.total_seconds_today = self.load_today_total()

        self.label = tk.Label(root, text=self.format_time(self.total_seconds_today), font=("Helvetica", 48))
        self.label.pack(pady=20)

        frame = tk.Frame(root)
        frame.pack()

        self.start_btn = tk.Button(frame, text="Start", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.pause_btn = tk.Button(frame, text="Pause", command=self.pause)
        self.pause_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(frame, text="Stop", command=self.stop)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.update_timer()

    def update_timer(self):
        if self.running:
            current_seconds = (datetime.now() - self.start_time).total_seconds()
            display_seconds = self.total_seconds_today + current_seconds
            self.label.config(text=self.format_time(display_seconds))
        else:
            self.label.config(text=self.format_time(self.total_seconds_today))
        self.root.after(100, self.update_timer)

    def format_time(self, seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hrs:02}:{mins:02}:{secs:02}"

    def start(self):
        if not self.running:
            self.start_time = datetime.now()
            self.running = True
            print(f"🟢 Started at {self.start_time.strftime('%H:%M:%S')}")

    def pause(self):
        if self.running:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            self.total_seconds_today += duration
            self.save_session(self.start_time, end_time)
            self.running = False
            self.start_time = None
            print(f"⏸️ Paused at {end_time.strftime('%H:%M:%S')} — session saved")

    def stop(self):
        if self.running:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            self.total_seconds_today += duration
            self.save_session(self.start_time, end_time)
        self.running = False
        self.start_time = None
        self.total_seconds_today = 0
        self.label.config(text="00:00:00")
        print("🛑 Stopped and reset")

    def save_session(self, start_dt, end_dt):
        filename = "stopwatch_sessions.csv"
        new_row = pd.DataFrame([[start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                                 end_dt.strftime("%Y-%m-%d %H:%M:%S")]],
                               columns=["session_start", "session_end"])

        if os.path.isfile(filename):
            df = pd.read_csv(filename)
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row

        df.to_csv(filename, index=False)
        print(f"💾 Saved session: {start_dt.strftime('%H:%M:%S')} — {end_dt.strftime('%H:%M:%S')}")

    def load_today_total(self):
        filename = "stopwatch_sessions.csv"
        if not os.path.isfile(filename):
            return 0
        df = pd.read_csv(filename)
        today = datetime.now().date()
        total = 0
        for _, row in df.iterrows():
            try:
                start = datetime.strptime(row["session_start"], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(row["session_end"], "%Y-%m-%d %H:%M:%S")
                if start.date() == today:
                    total += (end - start).total_seconds()
            except:
                pass
        return total

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleStopwatch(root)
    root.mainloop()
