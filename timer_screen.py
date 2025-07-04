from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from datetime import datetime
import pandas as pd
import os

class TimerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.running = False
        self.start_time = None
        self.total_seconds_today = self.load_today_total()
        
        # Create layout
        layout = MDBoxLayout(orientation='vertical', spacing=20, padding=20)
        
        # Timer display
        self.timer_label = MDLabel(
            text=self.format_time(self.total_seconds_today),
            halign='center',
            font_style='H2'
        )
        layout.add_widget(self.timer_label)
        
        # Buttons layout
        button_layout = MDBoxLayout(spacing=10, size_hint_y=None, height=48)
        
        # Create buttons
        self.start_btn = MDRaisedButton(
            text="Start",
            on_release=self.start
        )
        self.pause_btn = MDRaisedButton(
            text="Pause",
            on_release=self.pause
        )
        self.stop_btn = MDRaisedButton(
            text="Stop",
            on_release=self.stop
        )
        
        # Add buttons to layout
        button_layout.add_widget(self.start_btn)
        button_layout.add_widget(self.pause_btn)
        button_layout.add_widget(self.stop_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
    
    def format_time(self, seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hrs:02}:{mins:02}:{secs:02}"
    
    def start(self, *args):
        if not self.running:
            self.start_time = datetime.now()
            self.running = True
            self.update_timer()
    
    def pause(self, *args):
        if self.running:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            self.total_seconds_today += duration
            self.save_session(self.start_time, end_time)
            self.running = False
            self.start_time = None
    
    def stop(self, *args):
        if self.running:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            self.total_seconds_today += duration
            self.save_session(self.start_time, end_time)
        self.running = False
        self.start_time = None
        self.total_seconds_today = 0
        self.timer_label.text = "00:00:00"
    
    def update_timer(self, *args):
        if self.running:
            current_seconds = (datetime.now() - self.start_time).total_seconds()
            display_seconds = self.total_seconds_today + current_seconds
            self.timer_label.text = self.format_time(display_seconds)
            # Schedule next update
            self.timer_event = self.fbind('on_update_timer', self.update_timer)
    
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