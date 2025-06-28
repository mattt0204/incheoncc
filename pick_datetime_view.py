from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pick_datetime_model import ReservationStrategy
from pick_datetime_view_model import DateWithWeekdayDelegate, PickDatetimeViewModel


class PickDatetimeView(QWidget):
    def __init__(self, app, view_model: PickDatetimeViewModel, parent=None):
        super().__init__(parent)
        self.app = app
        self.view_model = view_model
        self.view_model.setParent(self)  # 이 줄 추가!
        self.is_test = False
        self.setup_ui()

    def update_session_button(self, is_active):
        if is_active:
            self.execute_session_cron.setText("예약 완료(클릭시 취소)")
        else:
            self.execute_session_cron.setText("직접 요청/화,목 9시 예약하기")

    def update_dom_button(self, is_active):
        if is_active:
            self.execute_dom_cron.setText("예약 완료(클릭시 취소)")
        else:
            self.execute_dom_cron.setText("DOM 요청/화,목 9시 예약하기")

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
        self.start_minute_combo.setCurrentIndex(0)

    def init_end_time_section(self):
        self.end_hour_label = QLabel("마지막 시간")
        self.end_minute_label = QLabel("마지막 분")
        self.end_minute_combo = QComboBox()
        self.end_hour_combo = QComboBox()
        self.end_hour_combo.addItems([str(i) for i in range(24)])
        self.end_minute_combo.addItems([str(i) for i in range(60)])
        self.end_hour_combo.setCurrentIndex(8)
        self.end_minute_combo.setCurrentIndex(0)

    def init_priority_time_section(self):
        self.priority_hour_label = QLabel("우선순위 시간")
        self.priority_minute_label = QLabel("우선순위 분")
        self.priority_hour_combo = QComboBox()
        self.priority_minute_combo = QComboBox()
        self.priority_hour_combo.addItems([str(i) for i in range(24)])
        self.priority_minute_combo.addItems([str(i) for i in range(60)])
        self.priority_hour_combo.setCurrentIndex(7)
        self.priority_minute_combo.setCurrentIndex(30)

    def init_button_section(self):
        self.is_test_checkbox = QCheckBox("테스트 모드(실제 예약하지 않음)")
        self.cancel_button = QPushButton("취소")
        self.cancel_layout = QHBoxLayout()
        self.cancel_layout.addStretch()
        self.cancel_layout.addWidget(self.cancel_button)
        self.cancel_layout.addStretch()

        self.execute_session_now = QPushButton("직접 요청/지금 실행")
        self.execute_session_cron = QPushButton("직접 요청/화,목 9시 예약하기")
        self.execute_dom_now = QPushButton("DOM 요청/지금 실행")
        self.execute_dom_cron = QPushButton("DOM 요청/화,목 9시 예약하기")

        # 2행: 나머지 버튼
        self.action_layout = QHBoxLayout()
        self.action_layout.addWidget(self.execute_session_now)
        self.action_layout.addWidget(self.execute_session_cron)
        self.action_layout.addWidget(self.execute_dom_now)
        self.action_layout.addWidget(self.execute_dom_cron)

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

        self.main_layout.addWidget(self.is_test_checkbox)
        self.main_layout.addLayout(self.action_layout)
        self.main_layout.addSpacing(10)  # 버튼 사이 여백
        self.main_layout.addLayout(self.cancel_layout)

        self.setLayout(self.main_layout)

    def connect_signals(self):
        self.execute_session_now.clicked.connect(self.on_session_now)
        self.execute_session_cron.clicked.connect(self.on_session_cron)
        self.execute_dom_now.clicked.connect(self.on_dom_now)
        self.execute_dom_cron.clicked.connect(self.on_dom_cron)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

        self.view_model.session_cron_active_changed.connect(self.update_session_button)
        self.view_model.dom_cron_active_changed.connect(self.update_dom_button)

    def __set_selected_info(self):
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
        self.is_test = self.is_test_checkbox.isChecked()
        self.view_model.set_selected_date(selected_yyyy_mm_dd)
        self.view_model.set_start_time(selected_start_hour, selected_start_minute)
        self.view_model.set_end_time(selected_end_hour, selected_end_minute)
        self.view_model.set_priority_time(
            selected_priority_hour, selected_priority_minute
        )

    def on_session_now(self):
        self.__set_selected_info()
        self.view_model.reserve_course(ReservationStrategy.SESSION, self.is_test)

    def on_session_cron(self):
        self.__set_selected_info()
        self.view_model.toggle_session_cron(ReservationStrategy.SESSION, self.is_test)

    def on_dom_now(self):
        self.__set_selected_info()
        self.view_model.reserve_course(ReservationStrategy.DOM, self.is_test)

    def on_dom_cron(self):
        self.__set_selected_info()
        self.view_model.toggle_dom_cron(ReservationStrategy.DOM, self.is_test)

    def on_cancel_clicked(self):
        self.view_model.stop_all_cron()  # ViewModel에서 모든 스케줄러 종료
        self.app.quit()
        self.view_model.scraper.driver.quit()
