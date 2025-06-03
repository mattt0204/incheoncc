from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pick_datetime_view_model import DateWithWeekdayDelegate, PickDatetimeViewModel


class PickDatetimeView(QWidget):
    def __init__(self, app, view_model: PickDatetimeViewModel, parent=None):
        super().__init__(parent)
        self.app = app
        self.view_model = view_model
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("날짜와 시간 선택")
        self.init_date_section()
        self.init_start_time_section()
        self.init_priority_time_section()
        self.init_end_time_section()
        self.init_button_section()
        self.init_layout()
        self.connect_signals()

    def init_date_section(self):
        self.date_label = QLabel("날짜")
        self.list_view = QListView()
        self.delegate = DateWithWeekdayDelegate(self.view_model)
        self.list_view.setModel(self.view_model.dates_model)
        self.list_view.setItemDelegate(self.delegate)

    def init_start_time_section(self):
        self.start_hour_label = QLabel("시작하는 시간")
        self.start_minute_label = QLabel("시작하는 분")
        self.start_minute_combo = QComboBox()
        self.start_hour_combo = QComboBox()
        self.start_hour_combo.addItems([str(i) for i in range(24)])
        self.start_minute_combo.addItems([str(i) for i in range(60)])
        self.start_hour_combo.setCurrentIndex(7)
        self.start_minute_combo.setCurrentIndex(30)

    def init_end_time_section(self):
        self.end_hour_label = QLabel("마지막 시간")
        self.end_minute_label = QLabel("마지막 분")
        self.end_minute_combo = QComboBox()
        self.end_hour_combo = QComboBox()
        self.end_hour_combo.addItems([str(i) for i in range(24)])
        self.end_minute_combo.addItems([str(i) for i in range(60)])
        self.end_hour_combo.setCurrentIndex(8)
        self.end_minute_combo.setCurrentIndex(30)

    def init_priority_time_section(self):
        self.priority_hour_label = QLabel("우선순위 시간")
        self.priority_minute_label = QLabel("우선순위 분")
        self.priority_hour_combo = QComboBox()
        self.priority_minute_combo = QComboBox()
        self.priority_hour_combo.addItems([str(i) for i in range(24)])
        self.priority_minute_combo.addItems([str(i) for i in range(60)])
        self.priority_hour_combo.setCurrentIndex(8)
        self.priority_minute_combo.setCurrentIndex(00)

    def init_button_section(self):
        self.cancel_button = QPushButton("취소")
        self.ok_button = QPushButton("다음")
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.ok_button)

    def init_layout(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.date_label)
        self.main_layout.addWidget(self.list_view)
        self.main_layout.addWidget(self.start_hour_label)
        self.main_layout.addWidget(self.start_hour_combo)
        self.main_layout.addWidget(self.start_minute_label)
        self.main_layout.addWidget(self.start_minute_combo)
        self.main_layout.addWidget(self.priority_hour_label)
        self.main_layout.addWidget(self.priority_hour_combo)
        self.main_layout.addWidget(self.priority_minute_label)
        self.main_layout.addWidget(self.priority_minute_combo)
        self.main_layout.addWidget(self.end_hour_label)
        self.main_layout.addWidget(self.end_hour_combo)
        self.main_layout.addWidget(self.end_minute_label)
        self.main_layout.addWidget(self.end_minute_combo)

        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

    def connect_signals(self):
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

    def on_ok_clicked(self):
        """선택한 날짜와 TimeRange를 전달하여 예약"""
        selected_indexes = self.list_view.selectedIndexes()
        if not selected_indexes:
            return
        selected_yyyy_mm_dd = self.view_model.dates_model.data(selected_indexes[0], 0)
        if not selected_yyyy_mm_dd:
            return
        selected_start_hour = self.start_hour_combo.currentIndex()
        selected_start_minute = self.start_minute_combo.currentIndex()
        selected_end_hour = self.end_hour_combo.currentIndex()
        selected_end_minute = self.end_minute_combo.currentIndex()
        selected_priority_hour = self.priority_hour_combo.currentIndex()
        selected_priority_minute = self.priority_minute_combo.currentIndex()

        self.view_model.set_selected_date(selected_yyyy_mm_dd)
        self.view_model.set_start_time(selected_start_hour, selected_start_minute)
        self.view_model.set_end_time(selected_end_hour, selected_end_minute)
        self.view_model.set_priority_time(
            selected_priority_hour, selected_priority_minute
        )

        self.view_model.reserve_course()
        # 지금 실행 / cron job 실행
        # DOMAPI 방식 / Session Post 방식
        # TODO: 지금은 Session post / 지금 실행 방식으로 먼저 개발

        # TODO: 예약 확인 페이지에서 예약이 완료되었는지 확인하고 완료되었다면 예약 완료 문구 발생

    def on_cancel_clicked(self):
        self.app.quit()


# TODO: 시간 레인지 view model의 데이터와 연결
# TODO: 화,수,금 테스트 필요
