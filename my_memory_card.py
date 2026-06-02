import sys
import json
import os
import random
import math
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect, 
    QSize, pyqtProperty, QPointF, QObject, QRectF
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsWidget, QGraphicsLinearLayout, QGraphicsItem, QGraphicsTextItem,
    QGraphicsDropShadowEffect, QGraphicsBlurEffect, QPushButton, QLabel, 
    QMessageBox, QCheckBox, QProgressBar, QStackedWidget, QVBoxLayout, 
    QHBoxLayout, QFrame, QGridLayout, QGraphicsRectItem, QSlider, QDialog
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QBrush, QPen, QLinearGradient, QRadialGradient, 
    QPainter, QPainterPath, QTransform, QIcon, QCursor, QSurfaceFormat
)

# ==========================================
# 1. 3D ENGINE, GLOWS, & CYBER UTILITIES
# ==========================================

class CyberGlowEffect(QGraphicsDropShadowEffect):
    """Custom dynamic glow effect mimicking high-tech HUD systems"""
    def __init__(self, color_hex="#00ffcc", blur_radius=25, parent=None):
        super().__init__(parent)
        self.setColor(QColor(color_hex))
        self.setBlurRadius(blur_radius)
        self.setOffset(0, 0)


class FloatingParticle(QGraphicsItem):
    """A floating ambient node reacting with varying alpha depths"""
    def __init__(self, scene_rect):
        super().__init__()
        self.scene_rect = scene_rect
        self.reset()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pos)
        self.timer.start(16)  # ~60 FPS Smooth Rendering

    def reset(self):
        self.x = random.uniform(0, self.scene_rect.width())
        self.y = random.uniform(0, self.scene_rect.height())
        self.z = random.uniform(1, 100)
        self.speed = random.uniform(0.3, 1.5)
        # Sci-fi Palette: Cyber Mint, Neon Magenta, Stark White
        self.base_color = QColor(random.choice(["#00ffcc", "#ff007f", "#ffffff"]))
        self.size = random.uniform(2, 6)
        self.setZValue(1)

    def update_pos(self):
        self.y -= self.speed
        self.x += math.sin(self.y * 0.02) * 0.4
        if self.y < 0:
            self.y = self.scene_rect.height()
            self.x = random.uniform(0, self.scene_rect.width())
        self.update()

    def boundingRect(self):
        return QRectF(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        
        # Simulating distance via scale-based opacity mapping
        alpha = int(50 + (self.z / 100.0) * 205)
        color = QColor(self.base_color)
        color.setAlpha(alpha)
        
        painter.setBrush(color)
        painter.drawEllipse(QPointF(self.x, self.y), self.size, self.size)


class HolographicCard(QGraphicsWidget):
    """Interactive card generating 3D microtransformations upon user focus"""
    def __init__(self, text, width, height, color_start="#0d1b2a", color_end="#1b263b"):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.width = width
        self.height = height
        self.resize(width, height)
        
        self.grad = QLinearGradient(0, 0, width, height)
        self.grad.setColorAt(0, QColor(color_start))
        self.grad.setColorAt(1, QColor(color_end))
        
        self.label = QGraphicsTextItem(text, self)
        self.label.setFont(QFont("Orbitron", 14, QFont.Bold))
        self.label.setDefaultTextColor(QColor("#00ffcc"))
        
        br = self.label.boundingRect()
        self.label.setPos((width - br.width()) / 2, (height - br.height()) / 2)
        self.setGraphicsEffect(CyberGlowEffect("#00ffcc", 20))

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.grad))
        painter.setPen(QPen(QColor("#00ffcc"), 1.5, Qt.SolidLine))
        painter.drawRoundedRect(0, 0, self.width, self.height, 12, 12)
        
        # Tech geometric accents on borders
        painter.setPen(QPen(QColor("#ff007f"), 2))
        painter.drawLine(0, 0, 15, 0)
        painter.drawLine(0, 0, 0, 15)

    def hoverMoveEvent(self, event):
        center = self.boundingRect().center()
        delta = event.pos() - center
        max_tilt = 12
        dx = delta.x() / (self.width / 2)
        dy = delta.y() / (self.height / 2)
        
        self.setTransform(QTransform().translate(center.x(), center.y())
                          .rotate(dx * max_tilt, Qt.YAxis)
                          .rotate(-dy * max_tilt, Qt.XAxis)
                          .translate(-center.x(), -center.y()))

    def hoverLeaveEvent(self, event):
        self.setTransform(QTransform())


# ==========================================
# 2. DATA MANAGEMENT & PROFILE CONTROL
# ==========================================

SAVE_FILE = "quiz_legend_3d_save.json"

class PlayerProfile:
    def __init__(self):
        self.coins = 9999  # Elite Starter Value
        self.gems = 50
        self.xp = 0
        self.level = 1
        self.rank_title = "Cyber Novice"
        self.stats = {"wins": 0, "games": 0, "high_score": 0}
        self.inventory = {"5050": 5, "freeze": 5, "skip": 5}
        self.settings = {"vr_mode": False, "music": True}

    def save(self):
        with open(SAVE_FILE, 'w') as f:
            json.dump(self.__dict__, f)

    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.__dict__.update(data)
            except:
                pass

    def add_reward(self, coins, xp):
        self.coins += coins
        self.xp += xp
        req_xp = self.level * 150
        leveled_up = False
        if self.xp >= req_xp:
            self.xp -= req_xp
            self.level += 1
            leveled_up = True
            self.update_rank()
        self.save()
        return leveled_up

    def update_rank(self):
        ranks = {1: "Netrunner", 3: "Data Spectre", 5: "Quantum Elite", 8: "Grid Sovereign"}
        self.rank_title = ranks.get(self.level, self.rank_title)

player = PlayerProfile()
player.load()

# ==========================================
# 3. COMPREHENSIVE ENGINE QUESTION DICTIONARY
# ==========================================

def get_questions():
    return [
        {'q': 'What is the powerhouse of the cell?', 'a': 'Mitochondria', 'w': ['Nucleus', 'Ribosome', 'Golgi'], 'cat': 'Biology'},
        {'q': 'Which planet spins the fastest?', 'a': 'Jupiter', 'w': ['Saturn', 'Mars', 'Earth'], 'cat': 'Space'},
        {'q': 'Code name for the atomic bomb dropped on Nagasaki?', 'a': 'Fat Man', 'w': ['Little Boy', 'Big Boy', 'Trinity'], 'cat': 'History'},
        {'q': 'Who painted The Starry Night?', 'a': 'Van Gogh', 'w': ['Monet', 'Picasso', 'Da Vinci'], 'cat': 'Art'},
        {'q': 'What is the hardest natural substance on Earth?', 'a': 'Diamond', 'w': ['Graphene', 'Steel', 'Quartz'], 'cat': 'Chemistry'},
        {'q': 'In binary code, what does "1010" represent?', 'a': '10', 'w': ['2', '4', '8'], 'cat': 'Coding'},
        {'q': 'Which gas makes up the majority of Earth\'s atmosphere?', 'a': 'Nitrogen', 'w': ['Oxygen', 'Carbon Dioxide', 'Hydrogen'], 'cat': 'Science'},
        {'q': 'BOSS: What is the speed of light approx?', 'a': '299,792 km/s', 'w': ['150,000 km/s', '1,000,000 km/s', 'Sound speed'], 'cat': 'Physics'},
        {'q': 'What year was the first iPhone released?', 'a': '2007', 'w': ['2005', '2008', '2010'], 'cat': 'Tech'},
        {'q': 'What represents the "K" in CMYK printing?', 'a': 'Key (Black)', 'w': ['Khol', 'Kelvin', 'Kerning'], 'cat': 'Design'},
    ]

# ==========================================
# 4. PRIMARY UI FRAMEWORK (STYLING ENGINE)
# ==========================================

class OPQuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QUIZ LEGEND: CYBERPUNK EDITION")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #030712; border: none;")
        
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- UI Scene Setup ---
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setSceneRect(0, 0, 1200, 800)
        
        self.view.setMouseTracking(True)
        self.view.viewport().setMouseTracking(True)
        
        self.init_particles()
        
        # Overlay Layout Framework
        self.overlay_container = QWidget(self.view)
        self.overlay_container.setGeometry(0, 0, 1200, 800)
        self.overlay_container.setAttribute(Qt.WA_TranslucentBackground)
        
        self.stack = QStackedWidget(self.overlay_container)
        self.stack.setGeometry(0, 0, 1200, 800)
        
        self.init_3d_menu()
        self.init_hud_game()
        self.init_shop()
        
        self.main_layout.addWidget(self.view)

    def init_particles(self):
        self.particles = []
        for _ in range(65):
            p = FloatingParticle(self.view.sceneRect())
            self.scene.addItem(p)
            self.particles.append(p)

    # --- MAIN HUD STYLING DEF & CREATION ---
    def init_3d_menu(self):
        self.menu_widget = QWidget()
        self.menu_widget.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self.menu_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("CYBER QUIZ RESISTANCE")
        title.setFont(QFont("Orbitron", 52, QFont.Bold))
        title.setStyleSheet("""
            color: #00ffcc; 
            letter-spacing: 4px;
            font-weight: 900;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Add dynamic drop glow manually using framework attributes
        title_effect = CyberGlowEffect("#00ffcc", 35)
        title.setGraphicsEffect(title_effect)
        
        self.lbl_stats = QLabel(f"GRID LEVEL: {player.level}  //  CREDITS: {player.coins} CC")
        self.lbl_stats.setFont(QFont("Share Tech Mono", 16))
        self.lbl_stats.setStyleSheet("color: #ff007f; letter-spacing: 5px;")
        self.lbl_stats.setAlignment(Qt.AlignCenter)
        
        # Advanced Neo CSS Overrides
        btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f172a, stop:1 #1e1b4b);
                color: #ffffff; 
                border: 2px solid #00ffcc; 
                border-radius: 6px;
                padding: 18px; 
                font-family: 'Orbitron';
                font-size: 18px; 
                font-weight: bold;
                min-width: 340px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e1b4b, stop:1 #ff007f);
                border: 2px solid #ffffff;
                color: #ffffff;
            }
            QPushButton:pressed {
                padding-top: 21px; 
                padding-bottom: 15px;
            }
        """
        
        self.btn_campaign = QPushButton("⚡ INITIALIZE CAMPAIGN")
        self.btn_campaign.setStyleSheet(btn_style)
        self.btn_campaign.clicked.connect(lambda: self.start_game("campaign"))
        
        self.btn_survival = QPushButton("☠️ SURVIVAL MATRIX")
        self.btn_survival.setStyleSheet(btn_style)
        self.btn_survival.clicked.connect(lambda: self.start_game("survival"))
        
        self.btn_time = QPushButton("⏱️ OVERCLOCK PROTOCOL")
        self.btn_time.setStyleSheet(btn_style)
        self.btn_time.clicked.connect(lambda: self.start_game("time"))
        
        self.btn_shop = QPushButton("💎 BLACK MARKET ARSENAL")
        self.btn_shop.setStyleSheet(btn_style)
        self.btn_shop.clicked.connect(lambda: self.stack.setCurrentWidget(self.shop_widget))
        
        self.btn_settings = QPushButton("⚙️ VR NEURAL CONFIG")
        self.btn_settings.setStyleSheet(btn_style)
        self.btn_settings.clicked.connect(self.open_settings)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(self.lbl_stats)
        layout.addSpacing(40)
        layout.addWidget(self.btn_campaign)
        layout.addWidget(self.btn_survival)
        layout.addWidget(self.btn_time)
        layout.addWidget(self.btn_shop)
        layout.addWidget(self.btn_settings)
        layout.addStretch()
        
        self.stack.addWidget(self.menu_widget)

    def init_hud_game(self):
        self.game_widget = QWidget()
        self.game_widget.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self.game_widget)
        
        top_bar = QHBoxLayout()
        self.lbl_score = QLabel("NET DATA SCORE: 0000")
        self.lbl_score.setStyleSheet("color: #00ffcc; font-family: 'Share Tech Mono'; font-size: 22px; font-weight: bold; letter-spacing: 2px;")
        
        self.lbl_lives = QLabel("❤️❤️❤️")
        self.lbl_lives.setStyleSheet("font-size: 24px;")
        
        self.lbl_time = QLabel("00")
        self.lbl_time.setStyleSheet("""
            color: #ff007f; 
            font-family: 'Orbitron';
            font-size: 30px; 
            font-weight: bold; 
            border: 2px solid #ff007f; 
            border-radius: 8px; 
            padding: 4px 18px;
            background-color: #090514;
        """)
        
        top_bar.addWidget(self.lbl_score)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_time)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_lives)
        
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        
        q_card = QFrame()
        q_card.setStyleSheet("""
            background-color: rgba(10, 15, 30, 0.9); 
            border: 2px solid #00ffcc; 
            border-radius: 16px;
        """)
        q_card.setGraphicsEffect(CyberGlowEffect("#00ffcc", 25))
        
        q_layout = QVBoxLayout(q_card)
        q_layout.setContentsMargins(35, 35, 35, 35)
        
        self.lbl_q_category = QLabel("// SECTION: HARDWARE")
        self.lbl_q_category.setStyleSheet("color: #ff007f; font-family: 'Share Tech Mono'; font-size: 14px; letter-spacing: 4px; font-weight: bold;")
        
        self.lbl_q_text = QLabel("Decrypting mainframe questions...")
        self.lbl_q_text.setWordWrap(True)
        self.lbl_q_text.setStyleSheet("color: #ffffff; font-family: 'Orbitron'; font-size: 26px; font-weight: bold;")
        self.lbl_q_text.setAlignment(Qt.AlignCenter)
        
        q_layout.addWidget(self.lbl_q_category, 0, Qt.AlignCenter)
        q_layout.addSpacing(25)
        q_layout.addWidget(self.lbl_q_text)
        
        self.options_layout = QGridLayout()
        self.option_btns = []
        for i in range(4):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setMinimumHeight(75)
            btn.setStyleSheet("""
                QPushButton { 
                    background: rgba(255, 255, 255, 0.03); 
                    color: #e2e8f0; 
                    border: 1px solid #334155; 
                    border-radius: 8px; 
                    font-family: 'Orbitron';
                    font-size: 16px; 
                    text-align: left; 
                    padding-left: 25px;
                }
                QPushButton:checked { 
                    background: rgba(0, 255, 204, 0.15); 
                    border: 2px solid #00ffcc; 
                    color: #00ffcc; 
                }
                QPushButton:hover { 
                    background: rgba(255, 255, 255, 0.08); 
                    border-color: #64748b;
                }
            """)
            btn.clicked.connect(self.check_selection)
            self.options_layout.addWidget(btn, i // 2, i % 2)
            self.option_btns.append(btn)
            
        q_layout.addLayout(self.options_layout)
        
        p_layout = QHBoxLayout()
        self.btn_5050 = QPushButton("✂️ INTEGRITY WIPER")
        self.btn_freeze = QPushButton("❄️ CHRONO FREEZE")
        self.btn_skip = QPushButton("🌌 QUANTUM WARP")
        
        for btn in [self.btn_5050, self.btn_freeze, self.btn_skip]:
            btn.setStyleSheet("""
                QPushButton { 
                    background: #0f172a; 
                    color: #e2e8f0; 
                    border: 1px solid #ff007f;
                    border-radius: 6px; 
                    padding: 10px; 
                    font-family: 'Share Tech Mono';
                    font-weight: bold; 
                    font-size: 13px;
                }
                QPushButton:hover { 
                    background: #ff007f; 
                    color: white;
                }
                QPushButton:disabled { 
                    color: #475569; 
                    border-color: #334155; 
                    background: #020617;
                }
            """)
            p_layout.addWidget(btn)
            
        q_layout.addSpacing(20)
        q_layout.addLayout(p_layout)
        
        self.btn_submit = QPushButton("SUBMIT SELECTION VECTOR")
        self.btn_submit.setFixedHeight(55)
        self.btn_submit.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff007f, stop:1 #7e22ce); 
                color: white; 
                font-family: 'Orbitron';
                font-size: 18px; 
                font-weight: bold; 
                border-radius: 8px;
                letter-spacing: 2px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7e22ce, stop:1 #ff007f); 
            }
        """)
        self.btn_submit.clicked.connect(self.submit_answer)
        
        q_layout.addSpacing(20)
        q_layout.addWidget(self.btn_submit)
        
        center_layout.addWidget(q_card)
        
        layout.addLayout(top_bar)
        layout.addStretch()
        layout.addLayout(center_layout)
        layout.addStretch()
        
        self.stack.addWidget(self.game_widget)
        
        self.btn_5050.clicked.connect(lambda: self.use_powerup("5050"))
        self.btn_freeze.clicked.connect(lambda: self.use_powerup("freeze"))
        self.btn_skip.clicked.connect(lambda: self.use_powerup("skip"))

    def init_shop(self):
        self.shop_widget = QWidget()
        self.shop_widget.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self.shop_widget)
        
        header = QLabel("DEEP WEB MARKET ARSENAL")
        header.setFont(QFont("Orbitron", 28, QFont.Bold))
        header.setStyleSheet("color: #ff007f; letter-spacing: 4px;")
        header.setAlignment(Qt.AlignCenter)
        header.setGraphicsEffect(CyberGlowEffect("#ff007f", 20))
        
        grid = QGridLayout()
        self.shop_items = [
            {"id": "5050", "name": "Logic Eraser", "cost": 100, "icon": "✂️"},
            {"id": "freeze", "name": "Cryo Stasis", "cost": 150, "icon": "❄️"},
            {"id": "skip", "name": "Quantum Leap", "cost": 200, "icon": "🌌"},
            {"id": "hint", "name": "Oracle Hint", "cost": 500, "icon": "👁️"},
        ]
        
        for idx, item in enumerate(self.shop_items):
            frame = QFrame()
            frame.setStyleSheet("background-color: rgba(15, 23, 42, 0.85); border-radius: 12px; border: 1px solid #334155;")
            f_layout = QVBoxLayout(frame)
            
            lbl_icon = QLabel(item["icon"])
            lbl_icon.setFont(QFont("Arial", 32))
            lbl_icon.setAlignment(Qt.AlignCenter)
            
            lbl_name = QLabel(item["name"])
            lbl_name.setStyleSheet("color: white; font-family: 'Orbitron'; font-weight: bold; font-size: 16px;")
            lbl_name.setAlignment(Qt.AlignCenter)
            
            lbl_cost = QLabel(f"{item['cost']} CREDITS")
            lbl_cost.setStyleSheet("color: #00ffcc; font-family: 'Share Tech Mono'; font-size: 14px;")
            lbl_cost.setAlignment(Qt.AlignCenter)
            
            btn_buy = QPushButton("EXECUTE ACQUISITION")
            btn_buy.setProperty("index", idx)
            btn_buy.clicked.connect(self.buy_item)
            btn_buy.setStyleSheet("""
                QPushButton { 
                    background: #ff007f; 
                    color: white; 
                    font-family: 'Share Tech Mono';
                    font-weight: bold; 
                    border: none; 
                    border-radius: 4px; 
                    padding: 8px;
                }
                QPushButton:hover { background: #ffffff; color: #000000; }
            """)
            
            f_layout.addWidget(lbl_icon)
            f_layout.addWidget(lbl_name)
            f_layout.addWidget(lbl_cost)
            f_layout.addWidget(btn_buy)
            
            grid.addWidget(frame, idx // 2, idx % 2)
            
        btn_back = QPushButton("DISCONNECT FROM MARKET")
        btn_back.setStyleSheet("""
            QPushButton {
                background: transparent; 
                color: white; 
                border: 2px solid white; 
                border-radius: 6px;
                padding: 12px 30px; 
                font-family: 'Orbitron';
                font-size: 15px;
            }
            QPushButton:hover {
                background: white;
                color: black;
            }
        """)
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.menu_widget))
        
        layout.addSpacing(20)
        layout.addWidget(header)
        layout.addSpacing(20)
        layout.addLayout(grid)
        layout.addSpacing(20)
        layout.addWidget(btn_back, 0, Qt.AlignCenter)
        self.stack.addWidget(self.shop_widget)

    # --- SIMULATED LOGIC PROCESSING ---
    def open_settings(self):
        reply = QMessageBox.question(self, 'NEURAL INTERFACE', 
                                     "Sync interface with 4D holographic optics layer?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            player.settings["vr_mode"] = not player.settings["vr_mode"]
            state = "SYNCHRONIZED" if player.settings["vr_mode"] else "TERMINATED"
            QMessageBox.information(self, "System Core", f"Optics Layer State: {state}")
            player.save()

    def start_game(self, mode):
        self.game_mode = mode
        self.score = 0
        self.questions = get_questions()
        random.shuffle(self.questions)
        self.q_index = 0
        
        if mode == "survival":
            self.lives = 1
            self.time_limit = 15
        elif mode == "time":
            self.lives = 3
            self.time_limit = 8
        else:
            self.lives = 3
            self.time_limit = 20
            
        self.stack.setCurrentWidget(self.game_widget)
        self.load_question()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.current_time = self.time_limit
        self.frozen = False
        
        self.update_powerups()

    def update_powerups(self):
        inv = player.inventory
        self.btn_5050.setText(f"✂️ WIPER ({inv.get('5050', 0)})")
        self.btn_freeze.setText(f"❄️ FREEZE ({inv.get('freeze', 0)})")
        self.btn_skip.setText(f"🌌 WARP ({inv.get('skip', 0)})")

    def load_question(self):
        if self.q_index >= len(self.questions):
            self.game_over(win=True)
            return
            
        q = self.questions[self.q_index]
        self.lbl_q_category.setText(f"// ACCESSING DATABANK PATHNAME: [ {q['cat'].upper()} ]")
        self.lbl_q_text.setText(q['q'])
        self.lbl_score.setText(f"NET DATA SCORE: {self.score:04d}")
        
        self.lbl_lives.setText("⚡" * self.lives)
        
        self.current_time = self.time_limit
        self.frozen = False
        self.lbl_time.setStyleSheet("""
            color: #00ffcc; font-family: 'Orbitron'; font-size: 30px; font-weight: bold; 
            border: 2px solid #00ffcc; border-radius: 8px; padding: 4px 18px; background-color: #020617;
        """)
        
        opts = q['w'] + [q['a']]
        random.shuffle(opts)
        
        for i, btn in enumerate(self.option_btns):
            btn.setText(opts[i])
            btn.setChecked(False)
            btn.setEnabled(True)
            btn.setProperty("is_correct", opts[i] == q['a'])
            btn.setStyleSheet("""
                QPushButton { 
                    background: rgba(255, 255, 255, 0.03); color: #e2e8f0; border: 1px solid #334155; 
                    border-radius: 8px; font-family: 'Orbitron'; font-size: 16px; text-align: left; padding-left: 25px;
                }
                QPushButton:checked { 
                    background: rgba(0, 255, 204, 0.2); border: 2px solid #00ffcc; color: #00ffcc; 
                }
                QPushButton:hover { background: rgba(255, 255, 255, 0.08); }
            """)

    def tick(self):
        if self.frozen: return
        
        self.current_time -= 1
        self.lbl_time.setText(f"{self.current_time:02d}")
        
        if self.current_time <= 5:
            self.lbl_time.setStyleSheet("""
                color: #ff007f; font-family: 'Orbitron'; font-size: 30px; font-weight: bold; 
                border: 2px solid #ff007f; border-radius: 8px; padding: 4px 18px; background-color: #090514;
            """)
            # Overclock mechanical shake sequence
            if self.current_time % 2 == 0:
                self.lbl_time.move(self.lbl_time.x() + 3, self.lbl_time.y())
            else:
                self.lbl_time.move(self.lbl_time.x() - 3, self.lbl_time.y())
        
        if self.current_time <= 0:
            self.handle_timeout()

    def handle_timeout(self):
        self.lives -= 1
        self.lbl_lives.setText("⚡" * self.lives)
        if self.lives <= 0:
            self.game_over(win=False)
        else:
            self.q_index += 1
            self.load_question()

    def check_selection(self):
        pass

    def use_powerup(self, pid):
        if player.inventory.get(pid, 0) > 0:
            if pid == "5050":
                wrongs = [b for b in self.option_btns if not b.property("is_correct") and b.isEnabled()]
                if len(wrongs) >= 2:
                    to_hide = random.sample(wrongs, 2)
                    for b in to_hide: 
                        b.setEnabled(False)
                        b.setText("[ DATA CORRUPTED ]")
            elif pid == "freeze":
                self.frozen = True
                self.lbl_time.setText("❄️")
                QTimer.singleShot(8000, lambda: setattr(self, 'frozen', False))
            elif pid == "skip":
                self.q_index += 1
                self.load_question()
            
            player.inventory[pid] -= 1
            player.save()
            self.update_powerups()

    def buy_item(self):
        sender = self.sender()
        idx = sender.property("index")
        item = self.shop_items[idx]
        
        if player.coins >= item['cost']:
            player.coins -= item['cost']
            player.inventory[item['id']] = player.inventory.get(item['id'], 0) + 1
            player.save()
            QMessageBox.information(self, "SECURE CHANNEL", f"Successfully extracted: {item['name']}")
        else:
            QMessageBox.warning(self, "TRANSACTION DENIED", "Insufficient digital assets.")

    def submit_answer(self):
        selected = [b for b in self.option_btns if b.isChecked()]
        if not selected:
            return
            
        btn = selected[0]
        is_correct = btn.property("is_correct")
        
        if is_correct:
            self.score += 100
            player.add_reward(60, 30)
            btn.setStyleSheet("""
                QPushButton { background: #00ffcc; color: #020617; border: 2px solid #ffffff; 
                border-radius: 8px; font-family: 'Orbitron'; font-size: 16px; font-weight: bold; padding-left: 25px;}
            """)
            QTimer.singleShot(800, self.next_q)
        else:
            self.lives -= 1
            self.lbl_lives.setText("⚡" * self.lives)
            btn.setStyleSheet("""
                QPushButton { background: #ff007f; color: #ffffff; border: 2px solid #ffffff; 
                border-radius: 8px; font-family: 'Orbitron'; font-size: 16px; font-weight: bold; padding-left: 25px;}
            """)
            
            # Dynamic grid structural jitter response
            self.game_widget.move(self.game_widget.x() + 8, self.game_widget.y())
            QTimer.singleShot(70, lambda: self.game_widget.move(self.game_widget.x() - 16, self.game_widget.y()))
            QTimer.singleShot(140, lambda: self.game_widget.move(self.game_widget.x() + 8, self.game_widget.y()))
            
            if self.lives <= 0:
                QTimer.singleShot(800, lambda: self.game_over(win=False))
            else:
                QTimer.singleShot(800, self.next_q)

    def next_q(self):
        self.q_index += 1
        self.load_question()

    def game_over(self, win):
        self.timer.stop()
        msg = QMessageBox(self)
        msg.setStyleSheet("background-color: #0b0f19; color: #ffffff; font-family: 'Orbitron'; font-size: 16px;")
        
        if win:
            player.stats["wins"] += 1
            if self.score > player.stats["high_score"]:
                player.stats["high_score"] = self.score
            player.save()
            msg.setWindowTitle("MAINFRAME BREACHED")
            msg.setText("🏆 UPLINK SUCCESSFUL 🏆")
            msg.setInformativeText(f"System Yield Score: {self.score}\nIdentity Status: {player.rank_title}")
        else:
            msg.setWindowTitle("CONNECTION LOSS")
            msg.setText("💀 SYNAPSE COLLAPSE 💀")
            msg.setInformativeText(f"Final Manifested Score: {self.score}")
            
        msg.exec_()
        self.stack.setCurrentWidget(self.menu_widget)
        self.lbl_stats.setText(f"GRID LEVEL: {player.level}  //  CREDITS: {player.coins} CC")


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Modern Material High-Contrast Deep Dark Palette Configuration
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(3, 7, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(15, 23, 42))
    palette.setColor(QPalette.AlternateBase, QColor(30, 41, 59))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(15, 23, 42))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, QColor(255, 0, 127))
    palette.setColor(QPalette.Highlight, QColor(0, 255, 204))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = OPQuizApp()
    window.show()
    sys.exit(app.exec_())