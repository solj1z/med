import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime
from pathlib import Path
from pdf_generator import PDFReportGenerator


class UltrasoundCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultrasound Image Capture System")
        self.root.geometry("1200x800")

        self.camera = None
        self.session_active = False
        self.captured_images = []
        self.session_folder = None

        self.patient_name = tk.StringVar()
        self.patient_id = tk.StringVar()
        self.exam_title = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        info_frame = ttk.LabelFrame(main_frame, text="Patient Information", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(info_frame, text="Patient Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.patient_name, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(info_frame, text="Patient ID:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.patient_id, width=20).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(info_frame, text="Exam Title (Optional):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.exam_title, width=50).grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(control_frame, text="Start Session", command=self.start_session, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.capture_btn = ttk.Button(control_frame, text="Capture Snapshot", command=self.capture_snapshot,
                                       width=15, state=tk.DISABLED)
        self.capture_btn.pack(side=tk.LEFT, padx=5)

        self.finish_btn = ttk.Button(control_frame, text="Finish Session", command=self.finish_session,
                                      width=15, state=tk.DISABLED)
        self.finish_btn.pack(side=tk.LEFT, padx=5)

        video_frame = ttk.LabelFrame(main_frame, text="Live Feed", padding="10")
        video_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        self.video_label = ttk.Label(video_frame)
        self.video_label.pack()

        capture_frame = ttk.LabelFrame(main_frame, text="Captured Images", padding="10")
        capture_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.capture_list = tk.Listbox(capture_frame, width=40, height=20)
        self.capture_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(capture_frame, orient=tk.VERTICAL, command=self.capture_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.capture_list.config(yscrollcommand=scrollbar.set)

        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.status_label = ttk.Label(status_frame, text="Ready to start", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)

    def start_session(self):
        if not self.patient_name.get() or not self.patient_id.get():
            messagebox.showerror("Error", "Please enter Patient Name and Patient ID")
            return

        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            messagebox.showerror("Error", "Could not open webcam")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{self.patient_name.get()}_{self.patient_id.get()}_{timestamp}"
        self.session_folder = Path("reports") / folder_name
        self.session_folder.mkdir(parents=True, exist_ok=True)

        self.session_active = True
        self.captured_images = []
        self.capture_list.delete(0, tk.END)

        self.start_btn.config(state=tk.DISABLED)
        self.capture_btn.config(state=tk.NORMAL)
        self.finish_btn.config(state=tk.NORMAL)

        self.status_label.config(text=f"Session active - Saving to: {self.session_folder}")

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
                self.video_label.configure(image=imgtk)

                self.current_frame = frame

            self.root.after(10, self.update_video_feed)

    def capture_snapshot(self):
        if hasattr(self, 'current_frame'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"snapshot_{len(self.captured_images) + 1}_{timestamp}.jpg"
            filepath = self.session_folder / filename

            cv2.imwrite(str(filepath), self.current_frame)

            self.captured_images.append(str(filepath))
            self.capture_list.insert(tk.END, filename)

            self.status_label.config(text=f"Captured: {filename} ({len(self.captured_images)} total)")

    def finish_session(self):
        if not self.captured_images:
            result = messagebox.askyesno("No Images",
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
            pdf_generator.generate_report(
                str(pdf_path),
                patient_info,
                self.captured_images
            )

            messagebox.showinfo("Success",
                               f"Session completed!\n\nReport saved to:\n{pdf_path}\n\nTotal images captured: {len(self.captured_images)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

        self.start_btn.config(state=tk.NORMAL)
        self.capture_btn.config(state=tk.DISABLED)
        self.finish_btn.config(state=tk.DISABLED)

        self.status_label.config(text="Session finished - Ready to start new session")

    def on_closing(self):
        if self.session_active:
            result = messagebox.askyesno("Exit", "Session is active. Are you sure you want to exit?")
            if not result:
                return

        if self.camera:
            self.camera.release()

        self.root.destroy()


def main():
    root = tk.Tk()
    app = UltrasoundCaptureApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
