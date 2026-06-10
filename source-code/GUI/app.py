import customtkinter as ctk
from tkinter import ttk, messagebox
from db import WeatherDatabase
import tkinter as tk
import pandas as pd
import os
from tkinter import filedialog
from datetime import datetime
 
 
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
 
BG_DEEP      = "#D8E4EE"   # nền toàn màn hình
BG_PANEL     = "#C5D5E4"   # sidebar
BG_CARD      = "#E6EFF6"   # card / form
BG_INPUT     = "#EDF3F8"   # ô nhập liệu
BG_TABLE_ODD = "#DDE8F2"   # hàng lẻ
BG_TABLE_EVN = "#E8F0F7"   # hàng chẵn
 
GOLD         = "#2C6E9E"   # xanh dương – accent
GOLD_LIGHT   = "#4A8EB5"   # xanh sáng – hover
GOLD_DIM     = "#93BAD5"   # xanh mờ – viền
SILVER       = "#2E5470"   # chữ phụ
TEXT_MAIN    = "#0D2233"   # chữ chính
TEXT_DIM     = "#8AAFC4"   # chữ mờ
 
RED_BTN      = "#EDE0E0"   # nền nút xóa
RED_HOVER    = "#E2CECE"   # hover nút xóa
 
 
class WeatherGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
 
        self.title("Vietnam Weather Intelligence")
        self.geometry("1420x820")
        self.configure(fg_color=BG_DEEP)
 
        self.db = None
        self.selected_id = None
 
        self._apply_global_style()
        self.create_layout()
        self.connect_database()
 
    def _apply_global_style(self):
        style = ttk.Style()
        style.theme_use("clam")
 
        style.configure(
            "Luxury.Treeview",
            background=BG_TABLE_EVN,
            foreground=TEXT_MAIN,
            fieldbackground=BG_TABLE_EVN,
            bordercolor=GOLD_DIM,
            borderwidth=0,
            rowheight=34,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Luxury.Treeview.Heading",
            background=BG_PANEL,
            foreground=GOLD,
            font=("Segoe UI", 11, "bold"),
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Luxury.Treeview",
            background=[("selected", GOLD_DIM)],
            foreground=[("selected", GOLD_LIGHT)],
        )
        style.map(
            "Luxury.Treeview.Heading",
            background=[("active", BG_CARD)],
        )
        style.configure(
            "Gold.Vertical.TScrollbar",
            background=BG_CARD,
            troughcolor=BG_DEEP,
            arrowcolor=GOLD,
            bordercolor=BG_DEEP,
            width=10,
        )
        style.configure(
            "Gold.Horizontal.TScrollbar",
            background=BG_CARD,
            troughcolor=BG_DEEP,
            arrowcolor=GOLD,
            bordercolor=BG_DEEP,
            width=10,
        )
 
    def create_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self, width=240, fg_color=BG_PANEL, corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
 
        # Main area với scrollable canvas
        main_container = ctk.CTkFrame(self, fg_color=BG_DEEP, corner_radius=0)
        main_container.pack(side="right", fill="both", expand=True)
 
        # Canvas + scrollbar dọc cho toàn bộ main
        self._main_canvas = tk.Canvas(
            main_container, bg=BG_DEEP, highlightthickness=0, bd=0
        )
        self._main_scrollbar = ttk.Scrollbar(
            main_container,
            orient="vertical",
            command=self._main_canvas.yview,
            style="Gold.Vertical.TScrollbar",
        )
        self._main_canvas.configure(yscrollcommand=self._main_scrollbar.set)
 
        self._main_scrollbar.pack(side="right", fill="y")
        self._main_canvas.pack(side="left", fill="both", expand=True)
 
        # Frame thực sự chứa nội dung bên trong canvas
        self.main_frame = tk.Frame(self._main_canvas, bg=BG_DEEP)
        self._canvas_window = self._main_canvas.create_window(
            (0, 0), window=self.main_frame, anchor="nw"
        )
 
        # Cập nhật scroll region khi nội dung thay đổi kích thước
        self.main_frame.bind("<Configure>", self._on_frame_configure)
        self._main_canvas.bind("<Configure>", self._on_canvas_configure)
 
        # Cuộn bằng chuột
        self._main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
 
        self._build_sidebar()
        self._build_main()
 
    def _on_frame_configure(self, event):
        self._main_canvas.configure(
            scrollregion=self._main_canvas.bbox("all")
        )
 
    def _on_canvas_configure(self, event):
        self._main_canvas.itemconfig(self._canvas_window, width=event.width)
 
    def _on_mousewheel(self, event):
        self._main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
 
    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        accent_top = tk.Frame(self.sidebar, bg=GOLD, height=3)
        accent_top.pack(fill="x")
 
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(28, 0), padx=20)
 
        ctk.CTkLabel(logo_frame, text="🌥", font=("Arial", 32), text_color=GOLD).pack()
        ctk.CTkLabel(logo_frame, text="V I E T N A M", font=("Segoe UI", 15, "bold"), text_color=GOLD).pack()
        ctk.CTkLabel(
            logo_frame,
            text="W E A T H E R  I N T E L L I G E N C E",
            font=("Segoe UI", 8),
            text_color=SILVER,
        ).pack(pady=(2, 0))
 
        self._sidebar_divider()
 
        self.status_dot = ctk.CTkLabel(
            self.sidebar, text="● DB: Chưa kết nối",
            font=("Segoe UI", 12), text_color="#9B3A3A",
        )
        self.status_dot.pack(pady=(16, 10))
 
        self._sidebar_divider()
 
        nav_items = [
            ("↺  Tải lại dữ liệu",    self.load_data,       False),
            ("✦  Cập nhật thống kê",   self.load_statistics, False),
            ("✕  Xóa form",            self.clear_form,      False),
        ]
        for label, cmd, is_danger in nav_items:
            self._sidebar_button(label, cmd, danger=is_danger)
 
        ctk.CTkFrame(self.sidebar, fg_color="transparent", height=1).pack(fill="x", expand=True)
        self._sidebar_divider()
        self._sidebar_button("⏻  Thoát", self.destroy, danger=True)
 
        accent_bot = tk.Frame(self.sidebar, bg=GOLD, height=3)
        accent_bot.pack(fill="x", side="bottom")
 
    def _sidebar_divider(self):
        tk.Frame(self.sidebar, bg=GOLD_DIM, height=1).pack(fill="x", padx=20, pady=6)
 
    def _sidebar_button(self, text, command, danger=False):
        fg    = RED_BTN   if danger else BG_CARD
        hover = RED_HOVER if danger else BG_INPUT
        tc    = "#9B3A3A" if danger else TEXT_MAIN
 
        btn = ctk.CTkButton(
            self.sidebar, text=text, command=command,
            fg_color=fg, hover_color=hover, text_color=tc,
            font=("Segoe UI", 13), corner_radius=6,
            border_width=1,
            border_color=GOLD_DIM if not danger else RED_BTN,
            height=40, anchor="w",
        )
        btn.pack(fill="x", padx=18, pady=5)
 
    # ── Main ──────────────────────────────────────────────────────────────────
    def _build_main(self):
        header_frame = tk.Frame(self.main_frame, bg=BG_DEEP)
        header_frame.pack(fill="x", padx=24, pady=(14, 2))
 
        tk.Label(
            header_frame,
            text="QUẢN LÝ DỮ LIỆU THỜI TIẾT",
            font=("Segoe UI", 20, "bold"),
            fg=GOLD, bg=BG_DEEP,
        ).pack(side="left")
 
        tk.Frame(self.main_frame, bg=GOLD_DIM, height=1).pack(fill="x", padx=24, pady=(0, 6))
 
        self.create_statistics_area()
        self.create_filter_area()
        self.create_form_area()
        self.create_button_area()
        self.create_table_area()
 
    def _section_label(self, parent, text):
        f = tk.Frame(parent, bg=BG_DEEP)
        f.pack(fill="x", padx=24, pady=(6, 2))
        tk.Label(f, text=text, font=("Segoe UI", 10), fg=GOLD, bg=BG_DEEP).pack(side="left")
        tk.Frame(f, bg=GOLD_DIM, height=1).pack(side="left", fill="x", expand=True, padx=8)
 
    # ── Thống kê ──────────────────────────────────────────────────────────────
    def create_statistics_area(self):
        self._section_label(self.main_frame, "◆  TỔNG QUAN")
 
        outer = tk.Frame(self.main_frame, bg=BG_DEEP)
        outer.pack(fill="x", padx=24, pady=3)
 
        self.stat_labels = {}
 
        stats = [
            ("total_records",    "Tổng bản ghi",  "📋"),
            ("total_provinces",  "Tỉnh / Thành",  "🗺"),
            ("avg_temperature",  "Nhiệt độ TB",   "🌡"),
            ("avg_humidity",     "Độ ẩm TB",      "💧"),
            ("max_precipitation","Mưa lớn nhất",  "🌧"),
            ("avg_pressure",     "Áp suất TB",    "⏲"),
        ]
 
        for key, label, icon in stats:
            card = tk.Frame(outer, bg=BG_CARD, bd=1, relief="flat")
            card.pack(side="left", fill="x", expand=True, padx=4)
 
            tk.Label(card, text=icon, font=("Arial", 16), bg=BG_CARD).pack(pady=(8, 0))
            tk.Label(card, text=label, font=("Segoe UI", 9, "bold"), fg=SILVER, bg=BG_CARD).pack()
 
            val_lbl = tk.Label(
                card, text="—",
                font=("Segoe UI", 15, "bold"),
                fg=GOLD_LIGHT, bg=BG_CARD,
            )
            val_lbl.pack(pady=(1, 8))
 
            self.stat_labels[key] = val_lbl
 
    # ── Bộ lọc ────────────────────────────────────────────────────────────────
    def create_filter_area(self):
        self._section_label(self.main_frame, "◆  TÌM KIẾM & LỌC")
 
        filter_frame = ctk.CTkFrame(
            self.main_frame, fg_color=BG_CARD,
            corner_radius=8, border_width=1, border_color=GOLD_DIM,
        )
        filter_frame.pack(fill="x", padx=24, pady=3)
 
        entry_style = dict(
            fg_color=BG_INPUT, text_color=TEXT_MAIN,
            border_color=GOLD_DIM, border_width=1,
            font=("Segoe UI", 12), corner_radius=6,
        )
 
        self.filter_province = ctk.CTkEntry(filter_frame, placeholder_text="Tỉnh / Thành phố", **entry_style)
        self.filter_province.pack(side="left", fill="x", expand=True, padx=8, pady=8)
 
        self.filter_region = ctk.CTkEntry(filter_frame, placeholder_text="Vùng miền  (North / South …)", **entry_style)
        self.filter_region.pack(side="left", fill="x", expand=True, padx=8, pady=8)
 
        self.filter_from_date = ctk.CTkEntry(filter_frame, placeholder_text="Từ ngày  yyyy-mm-dd", **entry_style)
        self.filter_from_date.pack(side="left", fill="x", expand=True, padx=8, pady=8)
 
        self.filter_to_date = ctk.CTkEntry(filter_frame, placeholder_text="Đến ngày  yyyy-mm-dd", **entry_style)
        self.filter_to_date.pack(side="left", fill="x", expand=True, padx=8, pady=8)
 
        ctk.CTkButton(
            filter_frame, text="Lọc", width=80, command=self.search_data,
            fg_color=GOLD_DIM, hover_color=GOLD, text_color=BG_DEEP,
            font=("Segoe UI", 12, "bold"), corner_radius=6,
        ).pack(side="left", padx=5, pady=8)
 
        ctk.CTkButton(
            filter_frame, text="Reset", width=80, command=self.reset_filter,
            fg_color=BG_INPUT, hover_color=BG_CARD, text_color=SILVER,
            border_width=1, border_color=GOLD_DIM,
            font=("Segoe UI", 12), corner_radius=6,
        ).pack(side="left", padx=5, pady=8)
 
    # ── Form nhập liệu ────────────────────────────────────────────────────────
    def create_form_area(self):
        self._section_label(self.main_frame, "◆  NHẬP LIỆU")
 
        form_outer = ctk.CTkFrame(
            self.main_frame, fg_color=BG_CARD,
            corner_radius=8, border_width=1, border_color=GOLD_DIM,
        )
        form_outer.pack(fill="x", padx=24, pady=3)
 
        self.entries = {}
 
        fields = [
            ("weather_date",  "Ngày  (yyyy-mm-dd)"),
            ("province",      "Tỉnh / Thành phố"),
            ("region",        "Vùng miền"),
            ("temperature",   "Nhiệt độ (°C)"),
            ("humidity",      "Độ ẩm (%)"),
            ("precipitation", "Lượng mưa (mm)"),
            ("wind_speed",    "Tốc độ gió (km/h)"),
            ("pressure",      "Áp suất (hPa)"),
            ("weather_code",  "Mã thời tiết"),
            ("source",        "Nguồn dữ liệu"),
        ]
 
        for index, (field, label) in enumerate(fields):
            row = index // 3
            col = index % 3
 
            cell = ctk.CTkFrame(form_outer, fg_color="transparent")
            cell.grid(row=row, column=col, padx=10, pady=6, sticky="ew")
 
            ctk.CTkLabel(
                cell, text=label,
                font=("Segoe UI", 11, "bold"), text_color=SILVER, anchor="w",
            ).pack(anchor="w", padx=2)
 
            entry = ctk.CTkEntry(
                cell,
                fg_color=BG_INPUT, text_color=TEXT_MAIN,
                border_color=GOLD_DIM, border_width=1,
                font=("Segoe UI", 12), corner_radius=6, height=32,
            )
            entry.pack(fill="x", pady=(2, 0))
            self.entries[field] = entry
 
        for col in range(3):
            form_outer.grid_columnconfigure(col, weight=1)
 
    # ── Nút hành động ─────────────────────────────────────────────────────────
    def create_button_area(self):
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=5)
 
        btn_cfg = dict(font=("Segoe UI", 13, "bold"), corner_radius=8, height=38, border_width=1)
 
        ctk.CTkButton(
            btn_frame, text="＋  Thêm bản ghi", command=self.add_data,
            fg_color=GOLD_DIM, hover_color=GOLD, text_color=BG_DEEP,
            border_color=GOLD, **btn_cfg,
        ).pack(side="left", padx=(0, 10))
 
        ctk.CTkButton(
            btn_frame, text="✎  Cập nhật", command=self.update_data,
            fg_color=BG_INPUT, hover_color=BG_CARD, text_color=GOLD_LIGHT,
            border_color=GOLD_DIM, **btn_cfg,
        ).pack(side="left", padx=10)
 
        ctk.CTkButton(
            btn_frame, text="✕  Xóa", command=self.delete_data,
            fg_color=RED_BTN, hover_color=RED_HOVER, text_color="#9B3A3A",
            border_color=RED_HOVER, **btn_cfg,
        ).pack(side="left", padx=10)

        # Divider nhỏ giữa 2 nhóm nút
        tk.Frame(btn_frame, bg=GOLD_DIM, width=1).pack(side="left", fill="y", padx=14, pady=6)

        ctk.CTkButton(
            btn_frame, text="⬇  Xuất CSV", command=self.export_csv,
            fg_color=BG_INPUT, hover_color=BG_CARD, text_color=GOLD,
            border_color=GOLD_DIM, **btn_cfg,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="💾  Backup", command=self.backup_data,
            fg_color=BG_INPUT, hover_color=BG_CARD, text_color=GOLD,
            border_color=GOLD_DIM, **btn_cfg,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="⬆  Restore", command=self.restore_data,
            fg_color=BG_INPUT, hover_color=BG_CARD, text_color=GOLD,
            border_color=GOLD_DIM, **btn_cfg,
        ).pack(side="left", padx=10)
 
    # ── Bảng dữ liệu ─────────────────────────────────────────────────────────
    def create_table_area(self):
        self._section_label(self.main_frame, "◆  DỮ LIỆU")
 
        table_outer = tk.Frame(
            self.main_frame, bg=BG_PANEL, bd=1, relief="flat",
        )
        table_outer.pack(fill="both", padx=24, pady=(2, 16))
 
        columns = (
            "id", "weather_date", "province", "region",
            "temperature", "humidity", "precipitation",
            "wind_speed", "pressure", "weather_code", "source",
        )
 
        self.table = ttk.Treeview(
            table_outer, columns=columns, show="headings",
            style="Luxury.Treeview", height=12,
        )
 
        headings = {
            "id": "ID", "weather_date": "Ngày", "province": "Tỉnh / Thành",
            "region": "Vùng", "temperature": "Nhiệt độ", "humidity": "Độ ẩm",
            "precipitation": "Mưa", "wind_speed": "Gió", "pressure": "Áp suất",
            "weather_code": "Mã TT", "source": "Nguồn",
        }
        widths = {
            "id": 55, "weather_date": 110, "province": 145, "region": 115,
            "temperature": 95, "humidity": 90, "precipitation": 90,
            "wind_speed": 90, "pressure": 90, "weather_code": 120, "source": 120,
        }
 
        for col in columns:
            self.table.heading(col, text=headings[col])
            self.table.column(col, width=widths[col], anchor="center", minwidth=55)
 
        self.table.tag_configure("odd",  background=BG_TABLE_ODD)
        self.table.tag_configure("even", background=BG_TABLE_EVN)
 
        scrollbar_y = ttk.Scrollbar(
            table_outer, orient="vertical", command=self.table.yview,
            style="Gold.Vertical.TScrollbar",
        )
        scrollbar_x = ttk.Scrollbar(
            table_outer, orient="horizontal", command=self.table.xview,
            style="Gold.Horizontal.TScrollbar",
        )
 
        self.table.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
 
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.table.pack(side="top", fill="both", expand=True)
 
        self.table.bind("<<TreeviewSelect>>", self.on_row_select)
 
    # ── Logic ─────────────────────────────────────────────────────────────────
    def connect_database(self):
        try:
            self.db = WeatherDatabase()
            self.db.test_connection()
            self.status_dot.configure(text="● DB: Đã kết nối MySQL", text_color="#2E7D4F")
            self.load_data()
            self.load_statistics()
        except Exception as e:
            self.status_dot.configure(text="● DB: Lỗi kết nối", text_color="#9B3A3A")
            messagebox.showerror("Lỗi kết nối MySQL", f"Không thể kết nối MySQL.\n\nChi tiết lỗi:\n{e}")
 
    def load_data(self):
        if not self.db:
            return
        try:
            records = self.db.get_all()
            self.render_table(records)
            self.load_statistics()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tải được dữ liệu:\n{e}")
 
    def load_statistics(self):
        if not self.db:
            return
        try:
            stats = self.db.get_statistics()
            for key, label in self.stat_labels.items():
                value = stats.get(key)
                label.configure(text="—" if value is None else str(value))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tải được thống kê:\n{e}")
 
    def search_data(self):
        province  = self.filter_province.get().strip()
        region    = self.filter_region.get().strip()
        from_date = self.filter_from_date.get().strip()
        to_date   = self.filter_to_date.get().strip()
        try:
            records = self.db.search_weather(
                province=province, region=region,
                from_date=from_date, to_date=to_date,
            )
            self.render_table(records)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lọc dữ liệu thất bại:\n{e}")
 
    def reset_filter(self):
        self.filter_province.delete(0, "end")
        self.filter_region.delete(0, "end")
        self.filter_from_date.delete(0, "end")
        self.filter_to_date.delete(0, "end")
        self.load_data()
 
    def render_table(self, records):
        for item in self.table.get_children():
            self.table.delete(item)
        for i, record in enumerate(records):
            tag = "odd" if i % 2 == 0 else "even"
            self.table.insert(
                "", "end",
                values=(
                    record.get("id", ""),
                    record.get("weather_date", ""),
                    record.get("province", ""),
                    record.get("region", ""),
                    record.get("temperature", ""),
                    record.get("humidity", ""),
                    record.get("precipitation", ""),
                    record.get("wind_speed", ""),
                    record.get("pressure", ""),
                    record.get("weather_code", ""),
                    record.get("source", ""),
                ),
                tags=(tag,),
            )
 
    def get_form_data(self):
        try:
            return {
                "weather_date":  self.entries["weather_date"].get().strip(),
                "province":      self.entries["province"].get().strip(),
                "region":        self.entries["region"].get().strip(),
                "temperature":   float(self.entries["temperature"].get()),
                "humidity":      float(self.entries["humidity"].get()),
                "precipitation": float(self.entries["precipitation"].get()),
                "wind_speed":    float(self.entries["wind_speed"].get()),
                "pressure":      float(self.entries["pressure"].get()),
                "weather_code":  self.entries["weather_code"].get().strip(),
                "source":        self.entries["source"].get().strip(),
            }
        except ValueError:
            messagebox.showerror(
                "Dữ liệu không hợp lệ",
                "Temperature, humidity, precipitation, wind_speed và pressure phải là số.",
            )
            return None
 
    def add_data(self):
        data = self.get_form_data()
        if not data:
            return
        if not data["weather_date"] or not data["province"]:
            messagebox.showwarning("Thiếu dữ liệu", "Weather date và province không được để trống.")
            return
        try:
            self.db.insert_weather(data)
            messagebox.showinfo("Thành công", "Đã thêm bản ghi thời tiết.")
            self.clear_form()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thêm được dữ liệu:\n{e}")
 
    def update_data(self):
        if not self.selected_id:
            messagebox.showwarning("Chưa chọn dòng", "Hãy chọn một dòng để cập nhật.")
            return
        data = self.get_form_data()
        if not data:
            return
        try:
            self.db.update_weather(self.selected_id, data)
            messagebox.showinfo("Thành công", "Đã cập nhật bản ghi.")
            self.clear_form()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không cập nhật được dữ liệu:\n{e}")
 
    def delete_data(self):
        if not self.selected_id:
            messagebox.showwarning("Chưa chọn dòng", "Hãy chọn một dòng để xóa.")
            return
        confirm = messagebox.askyesno("Xác nhận xóa", "Bạn có chắc muốn xóa bản ghi này không?")
        if not confirm:
            return
        try:
            self.db.delete_weather(self.selected_id)
            messagebox.showinfo("Thành công", "Đã xóa bản ghi.")
            self.clear_form()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không xóa được dữ liệu:\n{e}")
 
    def on_row_select(self, event):
        selected = self.table.selection()
        if not selected:
            return
        values = self.table.item(selected[0], "values")
        self.selected_id = values[0]
        fields = [
            "weather_date", "province", "region",
            "temperature", "humidity", "precipitation",
            "wind_speed", "pressure", "weather_code", "source",
        ]
        for index, field in enumerate(fields, start=1):
            self.entries[field].delete(0, "end")
            self.entries[field].insert(0, values[index])
 
    def clear_form(self):
        self.selected_id = None
        for entry in self.entries.values():
            entry.delete(0, "end")
 
 
    def export_csv(self):
        try:
            data = self.db.get_all_for_export()
            if not data:
                messagebox.showwarning("Thông báo", "Không có dữ liệu.")
                return
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")]
            )
            if not file_path:
                return
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            messagebox.showinfo("Thành công", "Xuất CSV thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def backup_data(self):
        try:
            data = self.db.get_all_for_export()
            if not data:
                messagebox.showwarning("Thông báo", "Không có dữ liệu để backup.")
                return
            os.makedirs("backup", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup/weather_backup_{timestamp}.csv"
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            messagebox.showinfo("Backup thành công", filename)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def restore_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return
        confirm = messagebox.askyesno(
            "Xác nhận",
            "Restore sẽ thêm lại dữ liệu từ file CSV.\nTiếp tục?"
        )
        if not confirm:
            return
        try:
            df = pd.read_csv(file_path)
            records = df.to_dict(orient="records")
            self.db.insert_many(records)
            self.load_data()
            messagebox.showinfo("Thành công", "Restore hoàn tất.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


if __name__ == "__main__":
    app = WeatherGUI()
    app.mainloop()