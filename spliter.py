import os
import sys
import multiprocessing
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QToolButton,
)

from image_processing import split_image


class ImageSpliter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Spliter")
        self.initUI()
        self.connect_event()
        self.init_config()

    def initUI(self):
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QGridLayout()
        main_widget.setLayout(main_layout)

        input_dir_label = QLabel("Input Directory:")
        self.input_dir_lineedit = QLineEdit()
        self.input_dir_button = QToolButton()
        self.input_dir_button.setText("...")
        main_layout.addWidget(input_dir_label, 0, 0)
        main_layout.addWidget(self.input_dir_lineedit, 0, 1)
        main_layout.addWidget(self.input_dir_button, 0, 2)

        output_dir_label = QLabel("Output Directory:")
        self.output_dir_lineedit = QLineEdit()
        self.output_dir_button = QToolButton()
        self.output_dir_button.setText("...")
        main_layout.addWidget(output_dir_label, 1, 0)
        main_layout.addWidget(self.output_dir_lineedit, 1, 1)
        main_layout.addWidget(self.output_dir_button, 1, 2)

        image_size_label = QLabel("Square Image Width:")
        self.image_size_lineedit = QLineEdit()
        self.image_size_lineedit.setFixedWidth(80)
        main_layout.addWidget(image_size_label, 2, 0)
        main_layout.addWidget(self.image_size_lineedit, 2, 1)

        self.split_button = QPushButton("Split")
        main_layout.addWidget(self.split_button, 3, 2)

    def connect_event(self):
        self.input_dir_button.clicked.connect(lambda: self.browse_dir(self.input_dir_lineedit))
        self.output_dir_button.clicked.connect(lambda: self.browse_dir(self.output_dir_lineedit))
        self.split_button.clicked.connect(self.split_images)

    def init_config(self):
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        if not os.path.isfile("config.ini"):
            self.settings.setValue("input_dir", "")
            self.settings.setValue("output_dir", "")
            self.settings.setValue("image_size", 1024)
            self.image_size_lineedit.setText(str(1024))
        else:
            self.load_config()

    def load_config(self):
        self.input_dir = self.settings.value("input_dir", defaultValue="", type=str)
        self.output_dir = self.settings.value("output_dir", defaultValue="", type=str)
        self.image_size = self.settings.value("image_size", defaultValue=1024, type=int)
        self.input_dir_lineedit.setText(self.input_dir)
        self.output_dir_lineedit.setText(self.output_dir)
        self.image_size_lineedit.setText(str(self.image_size))

    def get_config(self):
        self.input_dir = self.input_dir_lineedit.text()
        self.output_dir = self.output_dir_lineedit.text()
        self.image_size = int(self.image_size_lineedit.text())

    def save_config(self):
        self.settings.setValue("input_dir", self.input_dir_lineedit.text())
        self.settings.setValue("output_dir", self.output_dir_lineedit.text())
        self.settings.setValue("image_size", self.image_size_lineedit.text())

    def browse_dir(self, lineedit: QLineEdit):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            lineedit.setText(directory)

    def split_images(self):
        self.get_config()
        self.save_config()

        print("################Start Split################")
        print("Input Directory:", self.input_dir)
        print("Output Directory:", self.output_dir)
        print("Image Size:", self.image_size)

        input_dir = Path(self.input_dir)
        output_dir = Path(self.output_dir)
        output_dir.mkdir(exist_ok=True)
        image_paths = list(input_dir.glob("*.jpg"))
        if not image_paths:
            print(f"{self.input_dir} has no jpg format image file.")
            return

        _input = [(image_path, self.image_size, output_dir) for image_path in image_paths]
        use_cpus = multiprocessing.cpu_count() >> 1
        with multiprocessing.Pool(use_cpus) as p:
            p.starmap(split_image, _input)
        print("Finish!")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = ImageSpliter()
    window.resize(400, 200)
    window.show()
    sys.exit(app.exec())
