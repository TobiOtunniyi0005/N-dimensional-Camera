import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
from PIL import Image, ImageTk

from Working_on_fixed_numpy import Camera


class CameraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("N-D Camera Viewer (Optimized CPU Version)")

        self.camera = None
        self.data_points = np.empty((0, 0))

        self.canvas_width = 900
        self.canvas_height = 600
        self.scale = 40

        self.color_mode = "distance"

        self._build_ui()

        self.root.bind("1", lambda e: self.set_color_mode("distance"))
        self.root.bind("2", lambda e: self.set_color_mode("dimension"))
        self.root.bind("3", lambda e: self.set_color_mode("signed"))

    def _build_ui(self):
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            main,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="black"
        )
        self.canvas.grid(row=0, column=0, rowspan=9, sticky="nsew", padx=5, pady=5)

        controls = ttk.Frame(main)
        controls.grid(row=0, column=1, sticky="nw", padx=5)

        ttk.Label(controls, text="Dimensions").grid(row=0, column=0, sticky="w")
        self.dim_entry = ttk.Entry(controls, width=12)
        self.dim_entry.insert(0, "6")
        self.dim_entry.grid(row=0, column=1)

        ttk.Button(controls, text="Create Camera", command=self.create_camera)\
            .grid(row=1, column=0, columnspan=2, pady=4)

        ttk.Button(controls, text="Load File", command=self.load_file)\
            .grid(row=2, column=0, columnspan=2, pady=4)

        ttk.Label(controls, text="Move Camera").grid(row=3, column=0, sticky="w")
        self.move_entry = ttk.Entry(controls, width=12)
        self.move_entry.insert(0, "0,0,0,0,0,0")
        self.move_entry.grid(row=3, column=1)

        ttk.Button(controls, text="Move", command=self.move_camera)\
            .grid(row=4, column=0, columnspan=2, pady=4)

        ttk.Label(controls, text="Scale").grid(row=5, column=0, sticky="w")
        self.scale_entry = ttk.Entry(controls, width=12)
        self.scale_entry.insert(0, "1.1")
        self.scale_entry.grid(row=5, column=1)

        ttk.Button(controls, text="Scale Camera", command=self.scale_camera)\
            .grid(row=6, column=0, columnspan=2, pady=4)

        ttk.Label(controls, text="Rotate X dims").grid(row=7, column=0, sticky="w")
        self.rot_x_entry = ttk.Entry(controls, width=12)
        self.rot_x_entry.insert(0, "0,1")
        self.rot_x_entry.grid(row=7, column=1)

        ttk.Label(controls, text="Rotate Y dims").grid(row=8, column=0, sticky="w")
        self.rot_y_entry = ttk.Entry(controls, width=12)
        self.rot_y_entry.insert(0, "2,3")
        self.rot_y_entry.grid(row=8, column=1)

        ttk.Label(controls, text="Angle (rad)").grid(row=9, column=0, sticky="w")
        self.rot_angle_entry = ttk.Entry(controls, width=12)
        self.rot_angle_entry.insert(0, "0.05")
        self.rot_angle_entry.grid(row=9, column=1)

        ttk.Button(controls, text="Rotate Camera", command=self.rotate_camera)\
            .grid(row=10, column=0, columnspan=2, pady=6)

        state_frame = ttk.Frame(main)
        state_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        ttk.Label(state_frame, text="Camera State").pack(anchor="w")

        self.state_text = tk.Text(
            state_frame,
            width=26,
            height=14,
            wrap="none",
            bg="#111",
            fg="#00ffcc",
            font=("Consolas", 8),
            bd=0,
            highlightthickness=0
        )
        self.state_text.pack(fill="both", expand=True)
        self.state_text.configure(state="disabled")

    # ---------- camera ----------

    def create_camera(self):
        D = int(self.dim_entry.get())

        center = np.zeros(D)
        pos = np.eye(D)[0]
        neg = np.eye(D)[1]

        self.camera = Camera(D, center, [pos], [neg])

        self.data_points = np.random.uniform(-5, 5, size=(600000, D))

        self.update_canvas()
        self.update_camera_state()

    # ---------- fixed loader ----------

    def load_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        with open(path, "r") as f:
            txt = f.read()

        txt = txt.replace(",", " ")

        from io import StringIO
        data = np.loadtxt(StringIO(txt))

        if data.ndim == 1:
            data = data[None, :]

        D = data.shape[1]

        self.camera = Camera(
            D,
            np.zeros(D),
            [np.eye(D)[0]],
            [np.eye(D)[1]],
        )

        self.data_points = data

        self.dim_entry.delete(0, tk.END)
        self.dim_entry.insert(0, str(D))

        self.update_canvas()
        self.update_camera_state()

    # ---------- controls ----------

    def move_camera(self):
        delta = [float(v) for v in self.move_entry.get().split(",")]
        delta += [0.0] * self.camera.ndimensions
        self.camera.move_camera(delta[:self.camera.ndimensions])
        self.update_canvas()
        self.update_camera_state()

    def scale_camera(self):
        factor = float(self.scale_entry.get())
        self.camera.scale_camera(factor)
        self.scale *= factor
        self.update_canvas()
        self.update_camera_state()

    def rotate_camera(self):
        angle = float(self.rot_angle_entry.get())
        x_idx = [int(i) for i in self.rot_x_entry.get().split(",")]
        y_idx = [int(i) for i in self.rot_y_entry.get().split(",")]

        D = self.camera.ndimensions
        change_code = [0] * D

        for i in x_idx:
            if 0 <= i < D:
                change_code[i] = 1

        for i in y_idx:
            if 0 <= i < D:
                change_code[i] = 2

        self.camera.project_and_rotate_camera(change_code, angle)

        self.update_canvas()
        self.update_camera_state()

    def set_color_mode(self, mode):
        self.color_mode = mode
        self.update_canvas()

    # ---------- fast renderer ----------

    def update_canvas(self):
        if self.camera is None or self.data_points.size == 0:
            return

        pts = self.data_points

        # ALWAYS exactly two values here
        xs, ys = self.camera.project_points(pts)

        cx = self.canvas_width // 2
        cy = self.canvas_height // 2

        sx = (cx + xs * self.scale).astype(int)
        sy = (cy - ys * self.scale).astype(int)

        mask = (
            (sx >= 0) & (sx < self.canvas_width) &
            (sy >= 0) & (sy < self.canvas_height)
        )

        sx = sx[mask]
        sy = sy[mask]
        pts = pts[mask]

        if self.color_mode == "distance":
            d = np.linalg.norm(pts - self.camera.center, axis=1)
            t = np.clip(d / 10.0, 0, 1)
            r = (255*(1-t)+60*t).astype(np.uint8)
            g = (220*(1-t)+80*t).astype(np.uint8)
            b = (80*(1-t)+255*t).astype(np.uint8)

        elif self.color_mode == "signed":
            v = self.camera.screen_x + self.camera.screen_y
            s = pts @ v
            r = np.where(s >= 0, 255, 80).astype(np.uint8)
            g = np.where(s >= 0, 80, 80).astype(np.uint8)
            b = np.where(s >= 0, 80, 255).astype(np.uint8)

        else:
            v1 = self.camera.screen_x
            v2 = self.camera.screen_y
            contrib = np.abs(pts * v1) + np.abs(pts * v2)
            idx = np.argsort(-contrib, axis=1)[:, :3]
            rgb = np.zeros((len(pts), 3), dtype=np.uint8)
            rows = np.arange(len(pts))
            for c in range(3):
                j = idx[:, c]
                rgb[rows, c] = np.clip(
                    80 + contrib[rows, j] * 30,
                    0,
                    255
                )
            r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]

        img = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        img[sy, sx] = np.stack([r, g, b], axis=1)

        pil = Image.fromarray(img, mode="RGB")
        self.photo = ImageTk.PhotoImage(pil)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

        self.draw_legend()

    def draw_legend(self):
        x0, y0 = 10, 10
        self.canvas.create_rectangle(x0-5, y0-5, x0+200, y0+80,
                                     fill="#000000", outline="#444")

        if self.color_mode == "distance":
            txt = "Color: Distance\nNear → Yellow\nFar → Blue"
        elif self.color_mode == "dimension":
            txt = "Color: Dimensions\nRGB = top 3 dims"
        else:
            txt = "Color: Sign\nRed = Positive\nBlue = Negative"

        self.canvas.create_text(
            x0, y0,
            anchor="nw",
            text=txt,
            fill="#cccccc",
            font=("Consolas", 9)
        )

    def update_camera_state(self):
        self.state_text.configure(state="normal")
        self.state_text.delete("1.0", tk.END)

        def fmt(v):
            return "[" + ", ".join(f"{x:.4f}" for x in v) + "]"

        self.state_text.insert(tk.END, "Center:\n" + fmt(self.camera.center) + "\n\n")
        self.state_text.insert(tk.END, "Screen X:\n" + fmt(self.camera.screen_x) + "\n\n")
        self.state_text.insert(tk.END, "Screen Y:\n" + fmt(self.camera.screen_y) + "\n\n")
        self.state_text.insert(tk.END, f"Color mode: {self.color_mode}\n")

        self.state_text.configure(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    CameraGUI(root)
    root.mainloop()
