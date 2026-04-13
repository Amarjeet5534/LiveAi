"""
Desktop Application for Live AI Assistant
PyQt6-based cross-platform desktop app with voice integration
"""

import sys
import json
import requests
import threading
import time
import subprocess
import webbrowser
import pyperclip
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional
from PIL import ImageGrab

import pyaudio
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTextEdit, QListWidget, QListWidgetItem, 
    QComboBox, QMessageBox, QLineEdit, QTabWidget, QDialog, QFormLayout,
    QProgressBar, QStatusBar, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QTextCursor
from PyQt6.QtMultimedia import QAudioDecoder

# Try to import whisper (may fail on Windows due to torch)
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception as e:
    print(f"Warning: Whisper not available ({e}). Will use backend for transcription.")
    WHISPER_AVAILABLE = False

from pydub import AudioSegment
from pydub.playback import play
import io

# Configuration
API_BASE_URL = "http://localhost:8000"
CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000

def find_working_microphone():
    """Find a working microphone device and compatible sample rate"""
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    
    # Try to find a microphone that works
    for i in range(device_count):
        try:
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # Is an input device
                # Try common sample rates
                for rate in [16000, 44100, 48000, 22050]:
                    try:
                        stream = p.open(
                            format=FORMAT,
                            channels=CHANNELS,
                            rate=rate,
                            input=True,
                            input_device_index=i,
                            frames_per_buffer=CHUNK,
                            input_host_api=None
                        )
                        stream.close()
                        print(f"✅ Found working microphone: {info['name']} (device {i}, rate {rate}Hz)")
                        p.terminate()
                        return i, rate
                    except Exception:
                        continue
        except Exception:
            continue
    
    p.terminate()
    print("⚠️ No specific microphone found, using default")
    return None, RATE  # Use default device and rate

def speak_text(text: str, voice: str = "en-US-AriaNeural"):
    """Speak text - simple version, optional"""
    try:
        import edge_tts
        from pydub import AudioSegment
        from pydub.playback import play
        
        def tts_worker():
            try:
                # Generate and play audio
                async def generate():
                    communicate = edge_tts.Communicate(text=text, voice=voice)
                    await communicate.save("response.mp3")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(generate())
                loop.close()
                
                sound = AudioSegment.from_mp3("response.mp3")
                play(sound)
                    
            except Exception as e:
                print(f"Audio error: {e}")
        
        tts_thread = threading.Thread(target=tts_worker, daemon=True)
        tts_thread.start()
        
    except Exception as e:
        pass  # Silently fail if TTS not available

class VoiceRecorder(QThread):
    """Background thread for recording voice input"""
    recording_finished = pyqtSignal(str)  # Emits transcribed text
    error_occurred = pyqtSignal(str)  # Emits error message
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.audio_data = []
        self.device_index, self.sample_rate = find_working_microphone()
        
    def run(self):
        try:
            self.recording_started.emit()
            p = pyaudio.PyAudio()
            
            try:
                if self.device_index is not None:
                    stream = p.open(
                        format=FORMAT,
                        channels=CHANNELS,
                        rate=self.sample_rate,
                        input=True,
                        input_device_index=self.device_index,
                        frames_per_buffer=CHUNK
                    )
                else:
                    # Use default device
                    stream = p.open(
                        format=FORMAT,
                        channels=CHANNELS,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=CHUNK
                    )
            except Exception as e:
                self.error_occurred.emit(f"Microphone error: {str(e)}")
                p.terminate()
                return
            
            self.is_recording = True
            self.audio_data = []
            
            # Record for 5 seconds
            record_duration = 5
            frames_to_record = int(self.sample_rate / CHUNK * record_duration)
            
            for i in range(frames_to_record):
                if not self.is_recording:
                    break
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    self.audio_data.append(np.frombuffer(data, dtype=np.float32))
                except Exception as e:
                    print(f"Frame read error: {e}")
                    continue
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if not self.audio_data or len(self.audio_data) == 0:
                self.error_occurred.emit("No audio recorded - check microphone")
                return
            
            print(f"✅ Recorded {len(self.audio_data)} frames at {self.sample_rate}Hz")
            
            # Convert to byte data
            audio_array = np.concatenate(self.audio_data)
            audio_bytes = (audio_array * 32767).astype(np.int16).tobytes()
            
            # Save and send to backend for transcription
            try:
                # Use unique filename with timestamp to avoid conflicts
                import time
                timestamp = int(time.time() * 1000000) % 1000000
                temp_path = Path(f"temp_audio_{timestamp}.wav")
                
                # Create WAV file with proper header
                audio_segment = AudioSegment(
                    data=audio_bytes,
                    sample_width=2,
                    frame_rate=self.sample_rate,
                    channels=CHANNELS
                )
                
                print(f"📁 Saving audio: {audio_segment.frame_count()} frames")
                audio_segment.export(str(temp_path), format="wav")
                
                # Verify file was created
                if not temp_path.exists():
                    self.error_occurred.emit("Failed to save audio file")
                    return
                
                print(f"📤 Sending audio ({temp_path.stat().st_size} bytes) to backend...")
                
                # IMPORTANT: Read the file and close immediately before sending
                with open(temp_path, "rb") as f:
                    file_data = f.read()  # Read entire file into memory
                
                # Now send the data
                files = {"file": ("audio.wav", file_data, "audio/wav")}
                response = requests.post(
                    f"{API_BASE_URL}/api/transcribe",
                    files=files,
                    timeout=60  # Increased to 60s - backend may load large ML model first time
                )
                
                print(f"Backend response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("text", "").strip()
                    error_msg = data.get("error", "")
                    
                    if text:
                        print(f"✅ Transcribed: {text}")
                        self.recording_finished.emit(text)
                    else:
                        error = error_msg or "Could not understand speech - try speaking louder"
                        print(f"❌ {error}")
                        self.error_occurred.emit(error)
                else:
                    print(f"❌ Backend error: {response.status_code}")
                    self.error_occurred.emit(f"Backend error: {response.status_code}")
                
                # Clean up temp file
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            except Exception as e:
                print(f"❌ Transcription error: {str(e)}")
                self.error_occurred.emit(f"Transcription failed: {str(e)}")
            
            self.recording_stopped.emit()
        except Exception as e:
            print(f"❌ Recording error: {str(e)}")
            self.error_occurred.emit(f"Recording error: {str(e)}")

class SystemCommandExecutor:
    """Execute system commands locally"""
    
    @staticmethod
    def execute(command: str) -> tuple[bool, str]:
        """
        Execute a system command if recognized
        Returns: (executed: bool, result: str)
        """
        cmd_lower = command.lower().strip()
        
        # Chrome/Browser commands
        if any(x in cmd_lower for x in ["open chrome", "launch chrome", "start chrome"]):
            try:
                subprocess.Popen(["chrome", "--no-first-run"])
                return True, "✅ Chrome opened successfully"
            except:
                try:
                    webbrowser.open("about:blank")
                    return True, "✅ Browser opened successfully"
                except:
                    return False, "Could not open browser"
        
        # Screenshot commands
        if any(x in cmd_lower for x in ["screenshot", "take screenshot", "snap screen"]):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = Path("screenshots") / f"screenshot_{timestamp}.png"
                path.parent.mkdir(exist_ok=True)
                
                img = ImageGrab.grab()
                img.save(path)
                return True, f"📸 Screenshot saved to {path}"
            except Exception as e:
                return False, f"Screenshot failed: {str(e)}"
        
        # Calculator commands
        if "calculator" in cmd_lower or "calc" in cmd_lower:
            try:
                subprocess.Popen("calc.exe")
                return True, "🧮 Calculator opened"
            except:
                return False, "Could not open calculator"
        
        # Notepad commands
        if "notepad" in cmd_lower or "text editor" in cmd_lower:
            try:
                subprocess.Popen("notepad.exe")
                return True, "📝 Notepad opened"
            except:
                return False, "Could not open Notepad"
        
        # Shutdown/Lock commands
        if "shutdown" in cmd_lower or "shut down" in cmd_lower:
            try:
                response = QMessageBox.warning(
                    None, "Confirm", 
                    "Are you sure you want to shut down?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if response == QMessageBox.StandardButton.Yes:
                    subprocess.run(["shutdown", "/s", "/t", "30"])
                    return True, "💻 Shutting down in 30 seconds..."
                else:
                    return True, "Shutdown cancelled"
            except:
                return False, "Could not initiate shutdown"
        
        # Lock computer
        if "lock" in cmd_lower and "computer" in cmd_lower or "lock screen" in cmd_lower:
            try:
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
                return True, "🔒 Computer locked"
            except:
                return False, "Could not lock computer"
        
        # Volume control
        if "volume up" in cmd_lower or "increase volume" in cmd_lower:
            try:
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from ctypes import cast, POINTER
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(min(current + 0.1, 1.0), None)
                return True, "🔊 Volume increased"
            except:
                return False, "Could not adjust volume"
        
        if "volume down" in cmd_lower or "decrease volume" in cmd_lower:
            try:
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from ctypes import cast, POINTER
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(max(current - 0.1, 0.0), None)
                return True, "🔉 Volume decreased"
            except:
                return False, "Could not adjust volume"
        
        # Search commands
        if "search" in cmd_lower and ("google" in cmd_lower or "web" in cmd_lower):
            query = cmd_lower.replace("search for", "").replace("search", "").replace("google", "").strip()
            if query:
                try:
                    webbrowser.open(f"https://www.google.com/search?q={query}")
                    return True, f"🔍 Searching for '{query}'"
                except:
                    return False, "Could not open search"
        
        # File commands
        if "open file explorer" in cmd_lower or "open files" in cmd_lower:
            try:
                subprocess.Popen("explorer.exe")
                return True, "📁 File Explorer opened"
            except:
                return False, "Could not open File Explorer"
        
        if "open downloads" in cmd_lower:
            try:
                downloads = Path.home() / "Downloads"
                subprocess.Popen(f"explorer.exe {downloads}")
                return True, "📥 Downloads folder opened"
            except:
                return False, "Could not open Downloads"
        
        # App launcher
        if "open" in cmd_lower and any(app in cmd_lower for app in ["word", "excel", "powerpoint", "outlook"]):
            try:
                if "word" in cmd_lower:
                    subprocess.Popen("winword.exe")
                    return True, "📄 Word opened"
                elif "excel" in cmd_lower:
                    subprocess.Popen("excel.exe")
                    return True, "📊 Excel opened"
                elif "powerpoint" in cmd_lower:
                    subprocess.Popen("powerpnt.exe")
                    return True, "🎯 PowerPoint opened"
                elif "outlook" in cmd_lower:
                    subprocess.Popen("outlook.exe")
                    return True, "📧 Outlook opened"
            except:
                return False, "Could not open application"
        
        # Not a system command
        return False, None


class CommandExecutor(QThread):
    """Background thread for executing commands"""
    command_executed = pyqtSignal(str)  # Response text
    error_occurred = pyqtSignal(str)
    
    def __init__(self, session_token: str, command: str):
        super().__init__()
        self.session_token = session_token
        self.command = command
    
    def run(self):
        try:
            # Try to execute as system command first
            executed, result = SystemCommandExecutor.execute(self.command)
            
            if executed:
                # System command was handled
                self.command_executed.emit(result)
                return
            
            # If not a system command, send to AI backend
            headers = {"Authorization": f"Bearer {self.session_token}"}
            response = requests.post(
                f"{API_BASE_URL}/api/commands/execute",
                json={"command": self.command},
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result = data.get("response", data.get("result", "Command executed"))
                    if result:
                        self.command_executed.emit(result)
                    else:
                        self.error_occurred.emit("No response received")
                except:
                    self.error_occurred.emit("Invalid response from server")
            else:
                self.error_occurred.emit(f"Server error: {response.status_code}")
        except Exception as e:
            self.error_occurred.emit(f"Execution error: {str(e)}")

class LoginDialog(QDialog):
    """Login/Register dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.token = None
        self.username = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Live AI Assistant - Authentication")
        self.setGeometry(100, 100, 400, 250)
        
        layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(register_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def login(self):
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/auth/login",
                json={
                    "username": self.username_input.text(),
                    "password": self.password_input.text()
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")  # Backend returns 'token', not 'access_token'
                self.username = self.username_input.text()
                self.accept()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def register(self):
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/auth/register",
                json={
                    "username": self.username_input.text(),
                    "password": self.password_input.text()
                }
            )
            
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Registration successful! Please login.")
                self.login()
            else:
                QMessageBox.warning(self, "Registration Failed", "User already exists or invalid input")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class DesktopAssistant(QMainWindow):
    """Main desktop application window"""
    
    def __init__(self):
        super().__init__()
        self.session_token = None
        self.username = None
        self.init_login()
        
    def init_login(self):
        """Show login dialog"""
        login_dialog = LoginDialog(self)
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            self.session_token = login_dialog.token
            self.username = login_dialog.username
            self.init_ui()
        else:
            sys.exit()
    
    def init_ui(self):
        """Initialize main UI"""
        self.setWindowTitle(f"Live AI Assistant - {self.username}")
        self.setGeometry(100, 100, 1200, 700)
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create layout
        layout = QHBoxLayout()
        
        # Left panel - Chat
        left_panel = QVBoxLayout()
        
        # Chat display
        chat_label = QLabel("Chat History")
        chat_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        left_panel.addWidget(chat_label)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Courier", 10))
        left_panel.addWidget(self.chat_display)
        
        # Input area
        input_label = QLabel("Your Command")
        input_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_panel.addWidget(input_label)
        
        input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type a command or use voice...")
        self.command_input.returnPressed.connect(self.execute_command)
        input_layout.addWidget(self.command_input)
        
        # Send button
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.execute_command)
        send_btn.setMaximumWidth(100)
        input_layout.addWidget(send_btn)
        
        left_panel.addLayout(input_layout)
        
        # Voice recording button
        voice_layout = QHBoxLayout()
        self.voice_btn = QPushButton("🎤 Record Voice (5s)")
        self.voice_btn.clicked.connect(self.start_voice_recording)
        self.voice_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        voice_layout.addWidget(self.voice_btn)
        
        # Quick commands
        chrome_btn = QPushButton("Open Chrome")
        chrome_btn.clicked.connect(lambda: self.execute_quick_command("open chrome"))
        voice_layout.addWidget(chrome_btn)
        
        weather_btn = QPushButton("Weather")
        weather_btn.clicked.connect(lambda: self.execute_quick_command("what is the weather"))
        voice_layout.addWidget(weather_btn)
        
        screenshot_btn = QPushButton("Screenshot")
        screenshot_btn.clicked.connect(lambda: self.execute_quick_command("take screenshot"))
        voice_layout.addWidget(screenshot_btn)
        
        left_panel.addLayout(voice_layout)
        
        # Right panel - History and status
        right_panel = QVBoxLayout()
        
        # Tabs
        tabs = QTabWidget()
        
        # History tab
        history_layout = QVBoxLayout()
        history_label = QLabel("Command History")
        history_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        history_layout.addWidget(history_label)
        
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        
        history_widget = QWidget()
        history_widget.setLayout(history_layout)
        tabs.addTab(history_widget, "History")
        
        # Stats tab
        stats_layout = QVBoxLayout()
        stats_label = QLabel("Session Statistics")
        stats_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        stats_layout.addWidget(stats_label)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        tabs.addTab(stats_widget, "Stats")
        
        # Settings tab
        settings_layout = QVBoxLayout()
        settings_label = QLabel("Settings")
        settings_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        settings_layout.addWidget(settings_label)
        
        device_index, sample_rate = find_working_microphone()
        device_name = f"Device {device_index}, {sample_rate}Hz" if device_index is not None else "Default Device"
        device_label = QLabel(f"Microphone: {device_name}")
        settings_layout.addWidget(device_label)
        
        api_label = QLabel(f"API URL: {API_BASE_URL}")
        settings_layout.addWidget(api_label)
        
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        settings_layout.addWidget(logout_btn)
        
        settings_layout.addStretch()
        
        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)
        tabs.addTab(settings_widget, "Settings")
        
        right_panel.addWidget(tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(20)
        self.status_bar.addPermanentWidget(self.progress)
        self.progress.setVisible(False)
        
        # Add panels to main layout
        layout.addLayout(left_panel, 2)
        layout.addLayout(right_panel, 1)
        main_widget.setLayout(layout)
        
        # Threads
        self.recorder = None
        self.executor = None
        
        # Load history
        self.load_history()
        
        # Add styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
    
    def start_voice_recording(self):
        """Start voice recording"""
        self.voice_btn.setEnabled(False)
        self.voice_btn.setText("🎤 Recording...")
        self.status_bar.showMessage("Recording for 5 seconds... Speak CLEARLY and LOUDLY into the microphone!")
        self.progress.setVisible(True)
        self.progress.setMaximum(0)  # Indeterminate progress
        
        print("🎙️ Starting voice recording - speak clearly and loudly for 5 seconds")
        
        self.recorder = VoiceRecorder()
        self.recorder.recording_finished.connect(self.on_voice_recorded)
        self.recorder.error_occurred.connect(self.on_recording_error)
        self.recorder.recording_stopped.connect(self.on_recording_stopped)
        self.recorder.start()
    
    def on_voice_recorded(self, text: str):
        """Handle recorded voice"""
        self.command_input.setText(text)
        self.add_to_chat(f"You (voice): {text}", "#1976D2")
        self.execute_command()
    
    def on_recording_error(self, error: str):
        """Handle recording error"""
        QMessageBox.warning(self, "Recording Error", error)
        self.status_bar.showMessage(f"Error: {error}")
    
    def on_recording_stopped(self):
        """Handle recording stopped"""
        self.voice_btn.setEnabled(True)
        self.voice_btn.setText("🎤 Record Voice (5s)")
        self.progress.setVisible(False)
    
    def execute_quick_command(self, command: str):
        """Execute a quick command"""
        self.command_input.setText(command)
        self.execute_command()
    
    def execute_command(self):
        """Execute command"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        self.command_input.clear()
        self.add_to_chat(f"You: {command}", "#1976D2")
        
        self.status_bar.showMessage("Executing command...")
        self.progress.setVisible(True)
        self.progress.setMaximum(0)
        
        self.executor = CommandExecutor(self.session_token, command)
        self.executor.command_executed.connect(self.on_command_executed)
        self.executor.error_occurred.connect(self.on_command_error)
        self.executor.start()
    
    def on_command_executed(self, result: str):
        """Handle command execution result"""
        try:
            # Truncate very long results for display
            display_result = result[:500] + "..." if len(result) > 500 else result
            self.add_to_chat(f"Assistant: {display_result}", "#4CAF50")
            self.status_bar.showMessage("Ready")
            self.progress.setVisible(False)
            
            # Try to speak (but don't crash if it fails)
            try:
                speak_text(result[:300])
            except:
                pass
            
            self.load_history()
        except Exception as e:
            print(f"Result error: {e}")
    
    def on_command_error(self, error: str):
        """Handle command execution error"""
        self.add_to_chat(f"Error: {error}", "#F44336")
        self.status_bar.showMessage(f"Error: {error}")
        self.progress.setVisible(False)
    
    def add_to_chat(self, message: str, color: str = "#333"):
        """Add message to chat display"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insertHtml(f"<span style='color: #999; font-size: 9px;'>[{timestamp}]</span> ")
        
        # Add message
        self.chat_display.insertHtml(f"<span style='color: {color};'>{message}</span><br>")
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def load_history(self):
        """Load command history from API"""
        try:
            headers = {"Authorization": f"Bearer {self.session_token}"}
            response = requests.get(
                f"{API_BASE_URL}/api/commands/history",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                commands = data.get("commands", [])
                
                self.history_list.clear()
                for cmd in commands[-10:]:  # Last 10 commands
                    item = QListWidgetItem(f"{cmd['command']} - {cmd['timestamp']}")
                    self.history_list.addItem(item)
        except Exception as e:
            pass  # Silently fail for history loading
    
    def logout(self):
        """Logout and exit"""
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            sys.exit()

def main():
    app = QApplication(sys.argv)
    window = DesktopAssistant()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
