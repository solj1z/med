import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime
from pathlib import Path
from pdf_generator import PDFReportGenerator


class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color, fg_color, hover_color, width=140, height=45, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_disabled = False

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

        self.draw_button()

    def draw_button(self):
        self.delete("all")
        color = self.hover_color if self.is_hovered and not self.is_disabled else self.bg_color
        if self.is_disabled:
            color = "#CCCCCC"

        self.create_rectangle(2, 2, self.winfo_width()-2, self.winfo_height()-2,
                             fill=color, outline=color, tags="bg")
        self.create_text(self.winfo_width()/2, self.winfo_height()/2,
                        text=self.text, font=("Segoe UI", 10, "bold"),
                        fill=self.fg_color if not self.is_disabled else "#888888",
                        tags="text")

    def on_enter(self, event):
        if not self.is_disabled:
            self.is_hovered = True
            self.draw_button()

    def on_leave(self, event):
        self.is_hovered = False
        self.draw_button()

    def on_click(self, event):
        if not self.is_disabled and self.command:
            self.command()

    def set_disabled(self, disabled):
        self.is_disabled = disabled
        self.draw_button()

    def config(self, **kwargs):
        if 'state' in kwargs:
            self.set_disabled(kwargs['state'] == tk.DISABLED)


class UltraCapturePro:
    def __init__(self, root):
        self.root = root
        self.root.title("UltraCapture Pro - Ultrasound Imaging System")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        self.camera = None
        self.session_active = False
        self.captured_images = []
        self.session_folder = None
        self.current_frame = None

        self.patient_name = tk.StringVar()
        self.patient_id = tk.StringVar()
        self.exam_title = tk.StringVar()

        self.configure_style()
        self.setup_ui()

    def configure_style(self):
        style = ttk.Style()
        style.theme_use('clam')

        bg_color = "#F5F7FA"
        fg_color = "#1E293B"
        accent_color = "#0066CC"
        light_accent = "#E0F2FE"

        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        style.configure('Header.TLabel', font=("Segoe UI", 18, "bold"), foreground="#0F172A")
        style.configure('Subheader.TLabel', font=("Segoe UI", 12, "bold"), foreground="#1E293B")
        style.configure('Info.TLabel', font=("Segoe UI", 9), foreground="#64748B")

        style.configure('TEntry', font=("Segoe UI", 10), padding=5)
        style.configure('TLabelframe', background=bg_color, foreground=fg_color)
        style.configure('TLabelframe.Label', font=("Segoe UI", 11, "bold"))

        self.root.configure(bg=bg_color)

    def setup_ui(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        header_frame = tk.Frame(main_container, bg="#0F172A", height=70)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="UltraCapture Pro", font=("Segoe UI", 24, "bold"),
                              fg="white", bg="#0F172A")
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        subtitle_label = tk.Label(header_frame, text="Professional Ultrasound Imaging System",
                                 font=("Segoe UI", 10), fg="#94A3B8", bg="#0F172A")
        subtitle_label.pack(side=tk.LEFT, padx=20, pady=15)

        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        patient_info_frame = ttk.LabelFrame(left_panel, text="Patient Information", padding=15)
        patient_info_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(patient_info_frame, text="Patient Name", style='Subheader.TLabel').pack(anchor=tk.W, pady=(0, 3))
        patient_name_entry = ttk.Entry(patient_info_frame, textvariable=self.patient_name, width=40)
        patient_name_entry.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(patient_info_frame, text="Patient ID", style='Subheader.TLabel').pack(anchor=tk.W, pady=(0, 3))
        patient_id_entry = ttk.Entry(patient_info_frame, textvariable=self.patient_id, width=40)
        patient_id_entry.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(patient_info_frame, text="Exam Title (Optional)", style='Subheader.TLabel').pack(anchor=tk.W, pady=(0, 3))
        exam_title_entry = ttk.Entry(patient_info_frame, textvariable=self.exam_title, width=40)
        exam_title_entry.pack(fill=tk.X)

        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, pady=(0, 15))

        button_frame = tk.Frame(control_frame, bg="#F5F7FA")
        button_frame.pack(fill=tk.X)

        self.start_btn = ModernButton(button_frame, "Start Session", self.start_session,
                                     bg_color="#10B981", hover_color="#059669", fg_color="white")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10), pady=10)

        self.capture_btn = ModernButton(button_frame, "Capture", self.capture_snapshot,
                                       bg_color="#0066CC", hover_color="#0052A3", fg_color="white")
        self.capture_btn.pack(side=tk.LEFT, padx=(0, 10), pady=10)
        self.capture_btn.set_disabled(True)

        self.finish_btn = ModernButton(button_frame, "Finish Session", self.finish_session,
                                      bg_color="#EF4444", hover_color="#DC2626", fg_color="white")
        self.finish_btn.pack(side=tk.LEFT, padx=0, pady=10)
        self.finish_btn.set_disabled(True)

        session_info_frame = ttk.LabelFrame(left_panel, text="Session Information", padding=15)
        session_info_frame.pack(fill=tk.BOTH, expand=True)

        self.session_status_label = tk.Label(session_info_frame, text="Status: Ready",
                                            font=("Segoe UI", 10), fg="#10B981", bg="#F5F7FA")
        self.session_status_label.pack(anchor=tk.W, pady=(0, 10))

        self.capture_count_label = tk.Label(session_info_frame, text="Captured Images: 0",
                                           font=("Segoe UI", 10), fg="#0066CC", bg="#F5F7FA")
        self.capture_count_label.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(session_info_frame, text="Captured Images List", style='Subheader.TLabel').pack(anchor=tk.W, pady=(10, 5))

        self.capture_list = tk.Listbox(session_info_frame, font=("Segoe UI", 9), height=10,
                                       bg="white", fg="#1E293B", selectmode=tk.SINGLE)
        self.capture_list.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        scrollbar = ttk.Scrollbar(session_info_frame, orient=tk.VERTICAL, command=self.capture_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.capture_list.config(yscrollcommand=scrollbar.set)

        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        video_frame = ttk.LabelFrame(right_panel, text="Live Feed", padding=10)
        video_frame.pack(fill=tk.BOTH, expand=True)

        self.video_label = tk.Label(video_frame, bg="#000000", width=640, height=480)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        placeholder_text = tk.Label(self.video_label, text="Waiting for session...", font=("Segoe UI", 16),
                                   fg="#666666", bg="#000000")
        placeholder_text.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        footer_frame = tk.Frame(main_container, bg="#1E293B", height=40)
        footer_frame.pack(fill=tk.X, padx=0, pady=0)
        footer_frame.pack_propagate(False)

        self.footer_label = tk.Label(footer_frame, text="Ready to start",
                                    font=("Segoe UI", 9), fg="#94A3B8", bg="#1E293B")
        self.footer_label.pack(side=tk.LEFT, padx=20, pady=10)

    def start_session(self):
        if not self.patient_name.get() or not self.patient_id.get():
            messagebox.showerror("Validation Error", "Please enter both Patient Name and Patient ID")
            return

        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            messagebox.showerror("Camera Error", "Could not access the webcam. Please check your camera connection.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{self.patient_name.get()}_{self.patient_id.get()}_{timestamp}"
        self.session_folder = Path("reports") / folder_name
        self.session_folder.mkdir(parents=True, exist_ok=True)

        self.session_active = True
        self.captured_images = []
        self.capture_list.delete(0, tk.END)

        self.start_btn.set_disabled(True)
        self.capture_btn.set_disabled(False)
        self.finish_btn.set_disabled(False)

        self.session_status_label.config(text=f"Status: Active - {self.patient_name.get()}", fg="#10B981")
        self.footer_label.config(text=f"Session started for {self.patient_name.get()} (ID: {self.patient_id.get()})")

        self.update_video_feed()

    def update_video_feed(self):
        if self.session_active and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (640, 480))

                img = Image.fromarray(frame_resized)
                imgtk = ImageTk.PhotoImage(image=img)

                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk, bg="#000000")

                self.current_frame = frame

            self.root.after(30, self.update_video_feed)

    def capture_snapshot(self):
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"snapshot_{len(self.captured_images) + 1}_{timestamp}.jpg"
            filepath = self.session_folder / filename

            cv2.imwrite(str(filepath), self.current_frame)

            self.captured_images.append(str(filepath))
            self.capture_list.insert(tk.END, filename)

            count = len(self.captured_images)
            self.capture_count_label.config(text=f"Captured Images: {count}")
            self.footer_label.config(text=f"Captured: {filename}")
            self.capture_list.see(tk.END)

    def finish_session(self):
        if not self.captured_images:
            result = messagebox.askyesno("No Images Captured",
                                        "No images were captured. Do you still want to finish the session?")
            if not result:
                return

        self.session_active = False
        if self.camera:
            self.camera.release()

        self.video_label.configure(image='')

        pdf_generator = PDFReportGenerator()
        pdf_path = self.session_folder / "report.pdf"

        patient_info = {
            'name': self.patient_name.get(),
            'id': self.patient_id.get(),
            'exam_title': self.exam_title.get() if self.exam_title.get() else "Ultrasound Examination",
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            self.footer_label.config(text="Generating PDF report...")
            self.root.update()

            pdf_generator.generate_report(
                str(pdf_path),
                patient_info,
                self.captured_images
            )

            messagebox.showinfo("Session Completed",
                              f"Report generated successfully!\n\nLocation: {pdf_path}\nImages: {len(self.captured_images)}")

            self.footer_label.config(text="Session completed successfully")
        except Exception as e:
            messagebox.showerror("PDF Generation Error", f"Failed to generate PDF:\n{str(e)}")
            self.footer_label.config(text="Error generating PDF")

        self.start_btn.set_disabled(False)
        self.capture_btn.set_disabled(True)
        self.finish_btn.set_disabled(True)

        self.session_status_label.config(text="Status: Ready", fg="#10B981")
        self.capture_count_label.config(text="Captured Images: 0")
        self.capture_list.delete(0, tk.END)

    def on_closing(self):
        if self.session_active:
            result = messagebox.askyesno("Exit Confirmation",
                                        "An active session is running. Are you sure you want to exit?")
            if not result:
                return

        if self.camera:
            self.camera.release()

        self.root.destroy()


def main():
    root = tk.Tk()
    app = UltraCapturePro(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
