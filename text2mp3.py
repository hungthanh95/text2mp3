import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QLineEdit, QGroupBox
)
from PyQt5.QtCore import Qt
import speech_recognition as sr
from gtts import gTTS


class VoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_listening = False
        self.initUI()

    def initUI(self):
        # Thiết lập giao diện chính
        self.setWindowTitle("Chuyển Giọng Nói và Văn Bản")
        self.setGeometry(100, 100, 600, 400)

        # Tạo các thành phần giao diện
        self.label_instruction = QLabel(
            "1. Bật nhận diện giọng nói và nói nội dung.\n2. Hoặc nhập nội dung vào ô văn bản.\n3. Nhập tên file và lưu.")
        self.label_instruction.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.label_text_box = QLabel("Văn bản:")
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Nội dung văn bản sẽ hiển thị ở đây...")

        self.label_filename = QLabel("Tên file MP3:")
        self.input_filename = QLineEdit()
        self.input_filename.setPlaceholderText("Nhập tên file (vd: my_audio.mp3)")

        self.btn_toggle_listen = QPushButton("Bắt đầu nhận diện giọng nói")
        self.btn_text_to_speech = QPushButton("Lưu thành file MP3")

        # Nhãn trạng thái
        self.label_status = QLabel("")
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setStyleSheet("font-size: 12px; color: blue;")

        # Kết nối sự kiện
        self.btn_toggle_listen.clicked.connect(self.toggle_listen)
        self.btn_text_to_speech.clicked.connect(self.text_to_speech)

        # Sắp xếp giao diện
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.label_instruction)

        group_text = QGroupBox("Nội dung văn bản")
        layout_text = QVBoxLayout()
        layout_text.addWidget(self.label_text_box)
        layout_text.addWidget(self.text_edit)
        group_text.setLayout(layout_text)
        layout_main.addWidget(group_text)

        group_filename = QGroupBox("Thông tin lưu file")
        layout_filename = QHBoxLayout()
        layout_filename.addWidget(self.label_filename)
        layout_filename.addWidget(self.input_filename)
        group_filename.setLayout(layout_filename)
        layout_main.addWidget(group_filename)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.btn_toggle_listen)
        layout_buttons.addWidget(self.btn_text_to_speech)
        layout_main.addLayout(layout_buttons)

        layout_main.addWidget(self.label_status)

        # Thiết lập widget chính
        central_widget = QWidget()
        central_widget.setLayout(layout_main)
        self.setCentralWidget(central_widget)

        # Thêm phong cách cho giao diện
        self.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
            QTextEdit, QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QLabel {
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
            }
        """)

    def toggle_listen(self):
        if not self.is_listening:
            self.is_listening = True
            self.btn_toggle_listen.setText("DỪNG nhận diện giọng nói")
            self.btn_toggle_listen.setStyleSheet("background-color: red; color: white;")
            self.listen_to_speech()
        else:
            self.is_listening = False
            self.btn_toggle_listen.setText("Nhận diện giọng nói")
            self.btn_toggle_listen.setStyleSheet("background-color: #5cb85c; color: white;")

    def listen_to_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.label_status.setText("Đang nghe, vui lòng nói...")
            QApplication.processEvents()
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = recognizer.recognize_google(audio, language="vi-VN")
                self.text_edit.setText(text)
                self.label_status.setText("Đã chuyển giọng nói sang văn bản.")
            except sr.UnknownValueError:
                self.label_status.setText("Không nhận diện được giọng nói.")
            except sr.RequestError as e:
                self.label_status.setText(f"Lỗi từ Google Speech Recognition: {e}")
            except Exception as e:
                self.label_status.setText(f"Lỗi: {e}")

    def text_to_speech(self):
        text = self.text_edit.toPlainText()
        filename = self.input_filename.text().strip()
        if not text:
            self.label_status.setText("Vui lòng nhập hoặc chuyển văn bản trước.")
            return
        if not filename:
            self.label_status.setText("Vui lòng nhập tên file.")
            return
        if not filename.endswith(".mp3"):
            filename += ".mp3"

        try:
            tts = gTTS(text=text, lang="vi", slow=False)
            tts.save(filename)
            self.label_status.setText(f"Đã lưu file giọng nói: {filename}")
            os.system(f"start {filename}" if os.name == "nt" else f"xdg-open {filename}")
        except Exception as e:
            self.label_status.setText(f"Lỗi khi lưu file mp3: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = VoiceApp()
    main_window.show()
    sys.exit(app.exec_())
