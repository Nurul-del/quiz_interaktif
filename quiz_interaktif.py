import json
import os
import random
import tkinter as tk
from tkinter import messagebox, ttk

# KONSTANTA
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz_state.json")
TIME_PER_QUESTION = 30      # timer soal
POINTS_PER_QUESTION = 10    # poin 1 jawaban benar
FEEDBACK_DELAY = 2000       # jeda sebelum soal berikutnya

CARD = "#ffffff"
BLUE = "#00bfff"
PRIMARY = "#800080"        # header (orchid terang)
GREEN = "#27ae60"
YELLOW = "#ffd700"
SCORE_GREEN = "#7fff00"
ORANGE = "#e67e22"
RED = "#ff0000"
TEXT = "#2c3e50"
MUTED = "#7f8c8d"
SELECTED_BG = "#f6dff4"
CORRECT_BG = "#c8f7d4"
WRONG_BG = "#f8c9c9"

# warna tema (mengikuti referensi desain)
BG_APP = "#8b4789"          # latar utama (ungu tua)
OPTION_BG = "#ffffff"       # latar opsi jawaban (polos putih)
OPTION_EDGE = "#d9dde3"     # garis tepi tipis pembeda antar opsi
SELECTED_EDGE = "#8b4789"   # garis tepi opsi yang dipilih
SUBMIT_BG = "#ff9800"       # tombol Submit / Ulangi Quiz (oranye)
SUBMIT_ACTIVE = "#e08600"
SKIP_BG = "#8b93b3"         # tombol Skip (abu kebiruan)
SKIP_ACTIVE = "#767e9e"
SCORE_BG = "#ffb347"        # label skor (oranye muda)
SCORE_FG = "#4a2c00"
HEADER_FG = "#ffffff"       # teks judul di header (ungu gelap, kontras tinggi)

# warna notifikasi tenang: (teks, latar)
NOTIF_COLORS = {
    "success": ("#1e7e45", "#e6f6ec"),
    "error": ("#a93226", "#fdecea"),
    "warning": ("#8a5a00", "#fff4e0"),
}


def blend(c1, c2, t):
    """Campur dua warna hex (#rrggbb); t=0 -> c1, t=1 -> c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


class QuizApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Quiz Interaktif")
        self.window.geometry("700x700")
        self.window.resizable(True, True)
        self.window.minsize(700, 700)
        self.window.configure(bg=BG_APP)

        # Data quiz. wrong_reasons[i] = alasan kenapa opsi i salah (None untuk opsi benar)
        self.questions = [
            {
                "question": "Apa itu event-driven programming?",
                "options": ["Program yang berjalan berurutan", "Program yang merespons kejadian",
                            "Program tanpa GUI", "Program berbasis web"],
                "correct": 1,
                "explanation": "Pada event-driven programming, program menunggu event (klik, penekanan "
                               "tombol, timer) lalu menjalankan handler yang sesuai.",
                "wrong_reasons": [
                    "Itu ciri program sekuensial/prosedural. Pada event-driven, alur ditentukan oleh kejadian, bukan urutan baris kode.",
                    None,
                    "Event-driven tidak ditentukan ada atau tidaknya GUI. Aplikasi GUI justru umumnya event-driven.",
                    "Event-driven bukan khusus web. Konsep ini juga dipakai pada aplikasi desktop seperti Tkinter.",
                ],
            },
            {
                "question": "Method Tkinter apa yang dipakai untuk menjalankan event loop?",
                "options": ["mainloop()", "run()", "start()", "loop()"],
                "correct": 0,
                "explanation": "window.mainloop() membuat jendela terus menunggu dan memproses event "
                               "sampai jendela ditutup.",
                "wrong_reasons": [
                    None,
                    "Window Tkinter tidak punya method run(). Event loop dijalankan lewat mainloop().",
                    "start() bukan method event loop Tkinter (start() lazim pada Thread).",
                    "loop() tidak ada di Tkinter. Namanya mainloop().",
                ],
            },
            {
                "question": "Agar hanya satu Radiobutton dalam satu grup yang bisa terpilih, "
                            "apa yang harus dibagikan bersama?",
                "options": ["Nilai value setiap tombol", "Teks (text) tombol",
                            "Variabel (variable) yang sama", "Warna tombol"],
                "correct": 2,
                "explanation": "Radiobutton dalam satu grup memakai variable yang sama (misalnya IntVar), "
                               "sedangkan value-nya harus berbeda agar pilihan bisa dibedakan.",
                "wrong_reasons": [
                    "value justru harus berbeda tiap tombol supaya Tkinter tahu tombol mana yang terpilih.",
                    "text hanya label tampilan dan tidak memengaruhi pengelompokan.",
                    None,
                    "Warna hanya soal tampilan, tidak berpengaruh pada pengelompokan.",
                ],
            },
            {
                "question": "Method apa yang dipakai untuk menjadwalkan fungsi berjalan setelah jeda waktu "
                            "tanpa membekukan GUI?",
                "options": ["sleep()", "after()", "wait()", "delay()"],
                "correct": 1,
                "explanation": "widget.after(ms, fungsi) menjadwalkan pemanggilan fungsi tanpa memblokir "
                               "event loop. Teknik ini dipakai untuk timer countdown.",
                "wrong_reasons": [
                    "time.sleep() memblokir event loop sehingga GUI membeku selama jeda.",
                    None,
                    "Tkinter tidak punya wait() untuk menjadwalkan fungsi (yang ada wait_variable/wait_window dengan tujuan lain).",
                    "Tkinter tidak memiliki method delay().",
                ],
            },
            {
                "question": "Apa fungsi method bind() pada widget/window Tkinter?",
                "options": ["Menghapus widget", "Mengubah warna widget", "Menutup jendela",
                            "Menghubungkan event dengan fungsi handler"],
                "correct": 3,
                "explanation": "bind(event, handler) mengaitkan sebuah event (mis. <Return>, <Escape>) "
                               "dengan fungsi yang akan dipanggil saat event terjadi.",
                "wrong_reasons": [
                    "Widget dihapus dengan destroy(), bukan bind().",
                    "Warna diubah lewat config() atau opsi bg/fg, bukan bind().",
                    "Jendela ditutup dengan destroy() atau quit().",
                    None,
                ],
            },
            {
                "question": "String event Tkinter mana untuk menangkap penekanan tombol Enter?",
                "options": ["<Enter>", "<Submit>", "<Return>", "<Go>"],
                "correct": 2,
                "explanation": "Tombol Enter ditangkap dengan <Return>. Event <Enter> artinya kursor "
                               "mouse masuk ke area widget.",
                "wrong_reasons": [
                    "<Enter> adalah event mouse masuk ke area widget, bukan tombol Enter di keyboard.",
                    "<Submit> bukan event bawaan Tkinter.",
                    None,
                    "<Go> bukan event bawaan Tkinter.",
                ],
            },
            {
                "question": "Apa fungsi IntVar pada Radiobutton?",
                "options": ["Menyimpan nilai opsi terpilih dan otomatis sinkron dengan widget",
                            "Mengatur ukuran font", "Menjadwalkan timer", "Menutup aplikasi"],
                "correct": 0,
                "explanation": "IntVar adalah control variable: nilainya terhubung dua arah dengan widget, "
                               "jadi memilih opsi mengubah isi IntVar, dan sebaliknya.",
                "wrong_reasons": [
                    None,
                    "Ukuran font diatur lewat opsi font pada widget, bukan IntVar.",
                    "Timer dijadwalkan dengan after(), bukan IntVar.",
                    "Aplikasi ditutup dengan destroy() atau quit().",
                ],
            },
            {
                "question": "Bagaimana cara memperbarui nilai ttk.Progressbar lewat kode?",
                "options": ["bar.value = 50", "bar.set_value(50)", "bar['value'] = 50", "bar.update(50)"],
                "correct": 2,
                "explanation": "Opsi widget Tkinter diubah dengan notasi bar['value'] = nilai atau "
                               "bar.config(value=nilai). Batas maksimum diatur lewat opsi maximum.",
                "wrong_reasons": [
                    "Itu hanya membuat atribut Python baru, tampilan widget tidak berubah.",
                    "ttk.Progressbar tidak punya method set_value().",
                    None,
                    "update() dipakai memproses event tertunda dan tidak menerima nilai progres.",
                ],
            },
            {
                "question": "Mengapa time.sleep() sebaiknya dihindari di aplikasi GUI?",
                "options": ["Memblokir event loop sehingga GUI tidak merespons (freeze)",
                            "Mempercepat jalannya program", "Menambah penggunaan memori",
                            "Tidak ada masalah di aplikasi GUI"],
                "correct": 0,
                "explanation": "sleep() menghentikan thread utama, padahal thread itu yang menjalankan "
                               "event loop. Akibatnya tombol dan jendela tidak merespons. Gunakan after().",
                "wrong_reasons": [
                    None,
                    "sleep() justru menahan program, bukan mempercepat.",
                    "Masalah sleep() bukan memori, melainkan GUI yang membeku.",
                    "Ada masalah: jendela membeku selama sleep() berjalan.",
                ],
            },
            {
                "question": "Apa yang dimaksud dengan state management pada aplikasi?",
                "options": ["Mengatur warna tema aplikasi", "Menghapus data saat aplikasi ditutup",
                            "Mempercepat render widget",
                            "Menyimpan dan mengelola kondisi aplikasi (soal ke berapa, skor, dll)"],
                "correct": 3,
                "explanation": "State management adalah pengelolaan data kondisi aplikasi agar konsisten "
                               "dan bisa disimpan/dipulihkan, misalnya progress kuis yang disimpan ke file.",
                "wrong_reasons": [
                    "Tema warna hanya soal tampilan, bukan pengelolaan state.",
                    "State management justru menyimpan kondisi, bukan menghapusnya.",
                    "Kecepatan render tidak terkait dengan state management.",
                    None,
                ],
            },
        ]
        self.total = len(self.questions)

        # State management
        self.current_question = 0
        self.score = 0
        self.time_left = TIME_PER_QUESTION
        self.selected_answer = tk.IntVar(value=-1)
        self.order = random.sample(range(self.total), self.total)
        self.answers = []
        self.restored_time = None
        self.finished = False
        self.locked = False
        self.timer_id = None
        self.next_id = None
        self._notif_token = 0

        self.buat_interface()
        self.muat_state_jika_ada()
        self.update_score_display(animated=False)
        self.load_question()
        self.start_timer()

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    # INTERFACE
    def buat_interface(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        for name, color in (("Quiz", BLUE), ("Score", SCORE_GREEN), ("Timer", YELLOW)):
            self.style.configure(f"{name}.Horizontal.TProgressbar", troughcolor="#dfe6ee",
                                 background=color, bordercolor="#dfe6ee",
                                 lightcolor=color, darkcolor=color, thickness=14)

        self.main_frame = tk.Frame(self.window, bg=BG_APP)
        self.main_frame.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(self.main_frame, bg=PRIMARY, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="QUIZ INTERAKTIF", font=("Arial", 16, "bold"),
                 bg=PRIMARY, fg=HEADER_FG).place(relx=0.5, rely=0.5, anchor="center")
        self.score_label = tk.Label(header, text="Skor: 0", font=("Arial", 13, "bold"),
                                    bg=SCORE_BG, fg=SCORE_FG, padx=10, pady=2,
                                    highlightthickness=2, highlightbackground=BG_APP)
        self.score_label.place(relx=1.0, x=-20, rely=0.5, anchor="e")

        # Area progress
        prog = tk.Frame(self.main_frame, bg=BG_APP)
        prog.pack(fill="x", padx=20, pady=(12, 0))

        self.counter_label = tk.Label(prog, text="", font=("Arial", 10, "bold"),
                                      bg=BG_APP, fg="white", anchor="w")
        self.counter_label.pack(fill="x")
        self.quiz_bar = ttk.Progressbar(prog, style="Quiz.Horizontal.TProgressbar",
                                        maximum=self.total, value=0)
        self.quiz_bar.pack(fill="x", pady=(2, 8))

        tk.Label(prog, text="Skor real-time", font=("Arial", 10, "bold"),
                 bg=BG_APP, fg="white", anchor="w").pack(fill="x")
        self.score_bar = ttk.Progressbar(prog, style="Score.Horizontal.TProgressbar",
                                         maximum=self.total * POINTS_PER_QUESTION, value=0)
        self.score_bar.pack(fill="x", pady=(2, 8))

        self.timer_label = tk.Label(prog, text="", font=("Arial", 12, "bold"),
                                    bg=BG_APP, fg=GREEN, anchor="e")
        self.timer_label.pack(fill="x")
        self.timer_bar = ttk.Progressbar(prog, style="Timer.Horizontal.TProgressbar",
                                         maximum=TIME_PER_QUESTION, value=TIME_PER_QUESTION)
        self.timer_bar.pack(fill="x", pady=(2, 0))

        # Kartu soal
        card = tk.Frame(self.main_frame, bg=CARD, highlightbackground="#d0d7de", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=12)

        self.question_label = tk.Label(card, text="", font=("Arial", 14, "bold"), bg=CARD, fg=TEXT,
                                       wraplength=620, justify="left", anchor="w")
        self.question_label.pack(fill="x", padx=20, pady=(16, 8))

        self.options_frame = tk.Frame(card, bg=CARD)
        self.options_frame.pack(fill="x", padx=20)
        self.option_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.options_frame, variable=self.selected_answer, value=i,
                                font=("Arial", 12), anchor="w", justify="left", bg=OPTION_BG,
                                highlightthickness=1, highlightbackground=OPTION_EDGE,
                                highlightcolor=OPTION_EDGE,
                                activebackground=SELECTED_BG, fg=TEXT, disabledforeground=TEXT,
                                wraplength=600, padx=10, pady=8, cursor="hand2",
                                command=self.on_select)
            rb.pack(fill="x", pady=3)
            self.option_buttons.append(rb)

        # Bar notifikasi (tinggi tetap supaya layout tidak bergeser)
        self.notif_label = tk.Label(card, text="", font=("Arial", 11), bg=CARD, fg=CARD,
                                    wraplength=600, justify="center", height=3, padx=10)
        self.notif_label.pack(fill="x", padx=20, pady=(10, 4))

        btn_frame = tk.Frame(card, bg=CARD)
        btn_frame.pack(pady=(0, 14))
        self.submit_btn = tk.Button(btn_frame, text="Submit  (Enter)", font=("Arial", 11, "bold"),
                                    bg=SUBMIT_BG, fg="white", activebackground=SUBMIT_ACTIVE,
                                    activeforeground="white", relief="flat", padx=18, pady=6,
                                    cursor="hand2", command=self.submit_answer)
        self.submit_btn.pack(side="left", padx=8)
        self.skip_btn = tk.Button(btn_frame, text="Skip  (Esc)", font=("Arial", 11, "bold"),
                                  bg=SKIP_BG, fg="white", activebackground=SKIP_ACTIVE,
                                  activeforeground="white", relief="flat", padx=18, pady=6,
                                  cursor="hand2", command=self.skip_question)
        self.skip_btn.pack(side="left", padx=8)

        tk.Label(self.main_frame,
                 text="Tips: tekan 1-4 untuk memilih opsi, Enter untuk submit, Esc untuk skip",
                 font=("Arial", 9), bg=BG_APP, fg="white").pack(pady=(0, 8))

        # Keyboard shortcuts (event handling)
        self.window.bind("<Return>", lambda e: self.submit_answer())
        self.window.bind("<KP_Enter>", lambda e: self.submit_answer())
        self.window.bind("<Escape>", lambda e: self.skip_question())
        for n in range(4):
            self.window.bind(str(n + 1), lambda e, n=n: self.select_option(n))

    # LOAD SOAL
    def current_q(self):
        return self.questions[self.order[self.current_question]]

    def load_question(self):
        if self.current_question >= self.total:
            self.show_result()
            return

        q = self.current_q()
        self.locked = False
        self.selected_answer.set(-1)
        self.question_label.config(text=q["question"])
        self.counter_label.config(text=f"Soal {self.current_question + 1} dari {self.total}")
        self.quiz_bar["value"] = self.current_question
        for i, rb in enumerate(self.option_buttons):
            rb.config(text=f"{chr(65 + i)}.  {q['options'][i]}", bg=OPTION_BG,
                      highlightbackground=OPTION_EDGE, highlightcolor=OPTION_EDGE, state="normal")
        self.clear_notification()
        self.submit_btn.config(state="normal")
        self.skip_btn.config(state="normal")

        if self.restored_time is not None:      # sisa waktu hanya untuk soal pertama setelah resume
            self.time_left = self.restored_time
            self.restored_time = None
        else:
            self.time_left = TIME_PER_QUESTION
        self.update_timer_display()

    def next_question(self):
        self.load_question()
        self.start_timer()

    # TIMER
    def start_timer(self):
        if self.finished:
            return
        self.stop_timer()
        self._tick()

    def stop_timer(self):
        if self.timer_id is not None:
            self.window.after_cancel(self.timer_id)
            self.timer_id = None

    def _tick(self):
        self.update_timer_display()
        if self.time_left <= 0:
            self.timer_id = None
            if not self.locked and not self.finished:
                self.process_answer(None, status="waktu habis")
            return
        self.time_left -= 1
        self.timer_id = self.window.after(1000, self._tick)

    def update_timer_display(self):
        t = self.time_left
        color = YELLOW if t > 10 else ORANGE if t > 5 else RED
        self.timer_label.config(text=f"Sisa waktu: {t:02d} detik", fg=color)
        self.timer_bar["value"] = t
        self.style.configure("Timer.Horizontal.TProgressbar", background=color,
                             lightcolor=color, darkcolor=color)

    # INPUT HANDLER
    def on_select(self):
        self.update_option_highlight()

    def select_option(self, idx):
        if self.locked or self.finished:
            return
        self.selected_answer.set(idx)
        self.update_option_highlight()

    def update_option_highlight(self):
        sel = self.selected_answer.get()
        for i, rb in enumerate(self.option_buttons):
            bg, edge = (SELECTED_BG, SELECTED_EDGE) if i == sel else (OPTION_BG, OPTION_EDGE)
            rb.config(bg=bg, highlightbackground=edge, highlightcolor=edge)

    # SUBMIT
    def submit_answer(self):
        if self.locked or self.finished:
            return
        choice = self.selected_answer.get()
        # Validasi: wajib memilih jawaban dulu (notifikasi tenang, tanpa getar)
        if choice == -1:
            self.notify("Pilih salah satu jawaban dulu, lalu tekan Enter.", "warning", duration=2500)
            return
        self.process_answer(choice)

    def skip_question(self):
        if self.locked or self.finished:
            return
        self.process_answer(None, status="skip")

    def process_answer(self, choice, status=None):
        self.locked = True
        self.stop_timer()
        self.submit_btn.config(state="disabled")
        self.skip_btn.config(state="disabled")
        for rb in self.option_buttons:
            rb.config(state="disabled")

        q = self.current_q()
        correct = q["correct"]
        correct_text = f"{chr(65 + correct)}. {q['options'][correct]}"
        if choice is not None:
            status = "benar" if choice == correct else "salah"

        # Jawaban benar hanya ditampilkan saat menjawab (benar/salah).
        # Soal dilewati atau waktu habis: tidak menampilkan jawaban benar.
        if status == "benar":
            self.score += POINTS_PER_QUESTION
            self.notify(f"Benar. +{POINTS_PER_QUESTION} poin", "success")
        elif status == "salah":
            self.fade_bg(self.option_buttons[choice], WRONG_BG)
            self.notify(f"Belum tepat. Jawaban yang benar: {correct_text}", "error")
        elif status == "waktu habis":
            self.notify("Waktu habis. Soal tidak dijawab.", "warning")
        else:
            self.notify("Soal dilewati.", "warning")

        self.answers.append({"pilihan": choice, "status": status})
        self.current_question += 1
        self.quiz_bar["value"] = self.current_question
        self.update_score_display(animated=True)
        self.save_state()

        self.next_id = self.window.after(FEEDBACK_DELAY, self.next_question)

    # SKOR
    def update_score_display(self, animated=True):
        self.score_label.config(text=f"Skor: {self.score}")
        if animated:
            self._animate_score_bar()
        else:
            self.score_bar["value"] = self.score

    def _animate_score_bar(self):
        cur = float(self.score_bar["value"])
        if cur < self.score:
            self.score_bar["value"] = min(cur + 1, self.score)
            self.window.after(20, self._animate_score_bar)

    # NOTIFIKASI & ANIMASI HALUS
    def notify(self, text, kind="warning", duration=None):
        """Notifikasi tenang: fade-in warna lembut, tanpa getar/ukuran berubah."""
        fg, bg = NOTIF_COLORS[kind]
        self._notif_token += 1
        token = self._notif_token
        self.notif_label.config(text=text, fg=CARD, bg=CARD)
        steps = 10

        def step(i=0):
            if token != self._notif_token:
                return
            t = i / steps
            self.notif_label.config(bg=blend(CARD, bg, t), fg=blend(CARD, fg, t))
            if i < steps:
                self.window.after(25, step, i + 1)
            elif duration:
                self.window.after(duration, lambda: self.clear_notification(token))

        step()

    def clear_notification(self, token=None):
        if token is not None and token != self._notif_token:
            return
        self._notif_token += 1
        self.notif_label.config(text="", bg=CARD, fg=CARD)

    def fade_bg(self, widget, end, steps=10, delay=30):
        """Transisi warna latar widget secara halus."""
        start = widget.cget("bg")

        def step(i=0):
            widget.config(bg=blend(start, end, i / steps))
            if i < steps:
                self.window.after(delay, step, i + 1)

        step()

    # STATE MANAGEMENT
    def save_state(self):
        if self.finished:
            return
        data = {
            "current_question": self.current_question,
            "score": self.score,
            "time_left": TIME_PER_QUESTION if self.locked else self.time_left,
            "order": self.order,
            "answers": self.answers,
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def clear_state(self):
        try:
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
        except OSError:
            pass

    def muat_state_jika_ada(self):
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            order = data["order"]
            cur = int(data["current_question"])
            score = int(data["score"])
            answers = data["answers"]
            time_left = int(data["time_left"])
            assert sorted(order) == list(range(self.total))
            assert 0 < cur < self.total and len(answers) == cur
            assert all("pilihan" in a and "status" in a for a in answers)
        except (OSError, ValueError, KeyError, TypeError, AssertionError):
            self.clear_state()
            return

        self.window.update_idletasks()
        if messagebox.askyesno("Lanjutkan Quiz?",
                               f"Ditemukan progress quiz sebelumnya (soal {cur + 1}, skor {score}).\n"
                               "Lanjutkan dari sana?"):
            self.order = order
            self.current_question = cur
            self.score = score
            self.answers = answers
            self.restored_time = max(1, min(time_left, TIME_PER_QUESTION))
        else:
            self.clear_state()

    def on_close(self):
        if not self.finished:
            self.save_state()
        self.window.destroy()

    # HASIL
    def show_result(self):
        self.finished = True
        self.stop_timer()
        self.clear_state()
        self.main_frame.pack_forget()

        self.result_frame = tk.Frame(self.window, bg=BG_APP)
        self.result_frame.pack(fill="both", expand=True)

        benar = sum(1 for a in self.answers if a["status"] == "benar")
        salah = sum(1 for a in self.answers if a["status"] == "salah")
        lewat = self.total - benar - salah
        persen = round(benar / self.total * 100)
        if persen >= 80:
            pesan, warna = "Luar biasa!", GREEN
        elif persen >= 60:
            pesan, warna = "Bagus, terus belajar!", PRIMARY
        else:
            pesan, warna = "Ayo coba lagi, pelajari pembahasan di bawah.", ORANGE

        # Ringkasan (tetap di atas)
        header = tk.Frame(self.result_frame, bg=PRIMARY, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="HASIL QUIZ", font=("Arial", 16, "bold"),
                 bg=PRIMARY, fg=HEADER_FG).place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(header, text=f"Skor Akhir: {self.score}/{self.total * POINTS_PER_QUESTION}",
                 font=("Arial", 13, "bold"), bg=SCORE_BG, fg=SCORE_FG, padx=10, pady=2,
                 highlightthickness=2, highlightbackground=BG_APP
                 ).place(relx=1.0, x=-20, rely=0.5, anchor="e")
        tk.Label(self.result_frame, text=pesan, font=("Arial", 12), bg=BG_APP,
                 fg="white").pack(pady=(10, 2))
        tk.Label(self.result_frame,
                 text=f"Benar: {benar}    Salah: {salah}    Dilewati/Waktu habis: {lewat}    ({persen}%)",
                 font=("Arial", 11), bg=BG_APP, fg="white").pack(pady=(0, 6))

        # Tombol (dipasang dulu di bawah agar selalu terlihat)
        btns = tk.Frame(self.result_frame, bg=BG_APP)
        btns.pack(side="bottom", pady=10)
        tk.Button(btns, text="Ulangi Quiz", font=("Arial", 11, "bold"), bg=SUBMIT_BG, fg="white",
                  relief="flat", padx=18, pady=6, cursor="hand2",
                  command=self.restart_quiz).pack(side="left", padx=8)
        tk.Button(btns, text="Keluar", font=("Arial", 11, "bold"), bg=RED, fg="white",
                  relief="flat", padx=18, pady=6, cursor="hand2",
                  command=self.window.destroy).pack(side="left", padx=8)

        # Area daftar soal yang bisa di-scroll
        container = tk.Frame(self.result_frame, bg=BG_APP)
        container.pack(fill="both", expand=True, padx=(16, 8), pady=(0, 4))
        self.result_canvas = tk.Canvas(container, bg=BG_APP, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.result_canvas.yview)
        self.result_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.result_canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(self.result_canvas, bg=BG_APP)
        inner_id = self.result_canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))
        self.result_canvas.bind("<Configure>",
                                lambda e: self.result_canvas.itemconfig(inner_id, width=e.width))

        # Mouse wheel (Windows/macOS: MouseWheel, Linux: Button-4/5)
        self.window.bind_all("<MouseWheel>", self._on_mousewheel)
        self.window.bind_all("<Button-4>", self._on_mousewheel)
        self.window.bind_all("<Button-5>", self._on_mousewheel)

        for n, a in enumerate(self.answers):
            self._buat_kartu_hasil(inner, n + 1, self.questions[self.order[n]], a)

    def _on_mousewheel(self, event):
        if event.num == 4:
            d = -1
        elif event.num == 5:
            d = 1
        else:
            d = -1 if event.delta > 0 else 1
        self.result_canvas.yview_scroll(d, "units")

    def _buat_kartu_hasil(self, parent, nomor, q, a):
        status, choice, correct = a["status"], a["pilihan"], q["correct"]
        color, label = {
            "benar": (GREEN, "BENAR"),
            "salah": (RED, "SALAH"),
            "skip": (ORANGE, "DILEWATI"),
            "waktu habis": (ORANGE, "WAKTU HABIS"),
        }[status]

        outer = tk.Frame(parent, bg=color)
        outer.pack(fill="x", pady=6, padx=(0, 6))
        card = tk.Frame(outer, bg=CARD)
        card.pack(fill="both", expand=True, padx=(5, 0))

        head = tk.Frame(card, bg=CARD)
        head.pack(fill="x", padx=12, pady=(10, 2))
        tk.Label(head, text=f"Soal {nomor}", font=("Arial", 10, "bold"), bg=CARD, fg=MUTED).pack(side="left")
        tk.Label(head, text=label, font=("Arial", 9, "bold"), bg=color, fg="white",
                 padx=8, pady=2).pack(side="right")

        tk.Label(card, text=q["question"], font=("Arial", 12, "bold"), bg=CARD, fg=TEXT,
                 wraplength=570, justify="left", anchor="w").pack(fill="x", padx=12, pady=(0, 6))

        for i, opt in enumerate(q["options"]):
            bg, suffix = OPTION_BG, ""
            if i == correct and i == choice:
                bg, suffix = CORRECT_BG, "   ✔ jawabanmu (benar)"
            elif i == correct:
                bg, suffix = CORRECT_BG, "   ✔ jawaban benar"
            elif i == choice:
                bg, suffix = WRONG_BG, "   ✘ jawabanmu"
            tk.Label(card, text=f"{chr(65 + i)}. {opt}{suffix}", font=("Arial", 11), bg=bg, fg=TEXT,
                     wraplength=560, justify="left", anchor="w", padx=8, pady=4,
                     highlightthickness=1, highlightbackground=OPTION_EDGE
                     ).pack(fill="x", padx=12, pady=1)

        correct_text = f"{chr(65 + correct)}. {q['options'][correct]}"
        if status == "benar":
            penjelasan = f"Pembahasan:\n{q['explanation']}"
        elif status == "salah":
            penjelasan = (f"Kenapa jawabanmu salah:\n{q['wrong_reasons'][choice]}\n\n"
                          f"Yang benar: {correct_text}\n{q['explanation']}")
        else:
            penjelasan = (f"Soal ini tidak dijawab.\n\n"
                          f"Yang benar: {correct_text}\n{q['explanation']}")
        tk.Label(card, text=penjelasan, font=("Arial", 10), bg="#f6f8fa", fg=TEXT,
                 wraplength=560, justify="left", anchor="w", padx=10, pady=8
                 ).pack(fill="x", padx=12, pady=(8, 12))

    def restart_quiz(self):
        self.window.unbind_all("<MouseWheel>")
        self.window.unbind_all("<Button-4>")
        self.window.unbind_all("<Button-5>")
        self.result_frame.destroy()
        self.main_frame.pack(fill="both", expand=True)
        self.current_question = 0
        self.score = 0
        self.answers = []
        self.order = random.sample(range(self.total), self.total)
        self.restored_time = None
        self.finished = False
        self.score_bar["value"] = 0
        self.update_score_display(animated=False)
        self.next_question()

    # JALANKAN
    def jalankan(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = QuizApp()
    app.jalankan()