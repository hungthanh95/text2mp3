import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QLineEdit, QGroupBox, QSlider, QDialog, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
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
        self.setGeometry(150, 150, 800, 600)

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

        # Thêm thanh trượt điều chỉnh tốc độ (chỉ có 2 lựa chọn: Chậm và Bình thường)
        self.label_speed = QLabel("Tốc độ đọc:")
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(0, 1)  # Chỉ có 2 lựa chọn: Chậm (0) và Bình thường (1)
        self.slider_speed.setValue(1)  # Mặc định là đọc với tốc độ bình thường

        # Nhãn hiển thị tốc độ khi kéo thanh trượt
        self.label_current_speed = QLabel("Tốc độ: Bình thường")
        
        # Kết nối sự kiện
        self.btn_toggle_listen.clicked.connect(self.toggle_listen)
        self.btn_text_to_speech.clicked.connect(self.text_to_speech)

        # Kết nối sự kiện thay đổi giá trị thanh trượt
        self.slider_speed.valueChanged.connect(self.update_speed_label)

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

        # Thêm phần điều chỉnh tốc độ đọc
        layout_speed = QHBoxLayout()
        layout_speed.addWidget(self.label_speed)
        layout_speed.addWidget(self.slider_speed)
        layout_main.addLayout(layout_speed)

        # Thêm label hiển thị tốc độ
        layout_main.addWidget(self.label_current_speed)

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

        # Hiển thị cửa sổ chờ
        self.loading_window = LoadingWindow()
        self.loading_window.show()

        # Chạy quá trình lưu file MP3 trong một thread
        self.worker = SaveMP3Worker(text, filename, self.slider_speed.value(), self.loading_window)
        self.worker.finished.connect(self.on_save_finished)
        self.worker.start()

    def on_save_finished(self):
        # Ẩn cửa sổ chờ khi hoàn tất
        self.loading_window.close()
        self.label_status.setText("Đã lưu file giọng nói thành công!")

    def update_speed_label(self):
        """Cập nhật label hiển thị tốc độ khi kéo thanh trượt."""
        speed_value = self.slider_speed.value()
        if speed_value == 0:
            self.label_current_speed.setText("Tốc độ: Chậm")
        else:
            self.label_current_speed.setText("Tốc độ: Bình thường")


class LoadingWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đang lưu file...")
        self.setGeometry(500, 300, 300, 100)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Không có giá trị cụ thể, chỉ là trạng thái đang chờ
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)


class SaveMP3Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, text, filename, speed, loading_window):
        super().__init__()
        self.text = text
        self.filename = filename
        self.speed = speed
        self.loading_window = loading_window

    def run(self):
        try:
            # Xác định tốc độ đọc
            slow = True if self.speed == 0 else False

            # Tạo giọng nói và lưu file MP3
            tts = gTTS(text=self.text, lang="vi", slow=slow)
            tts.save(self.filename)

            # Sau khi hoàn tất lưu file, phát tín hiệu
            self.finished.emit()
        except Exception as e:
            self.loading_window.close()
            print(f"Lỗi khi lưu file mp3: {e}")
            self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = VoiceApp()
    main_window.show()
    sys.exit(app.exec_())
