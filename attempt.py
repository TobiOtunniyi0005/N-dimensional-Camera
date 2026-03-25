import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
from PIL import Image, ImageTk


def normalize(v):
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n


def project_and_rotate(points, change_code, angle):
    change_code = np.asarray(change_code)
    x_idx = np.nonzero(change_code == 1)[0]
    y_idx = np.nonzero(change_code == 2)[0]

    if len(x_idx) == 0 or len(y_idx) == 0:
        return points.copy()

    c = np.cos(angle)
    s = np.sin(angle)
    out = points.copy()

    for xi in x_idx:
        for yi in y_idx:
            x = out[:, xi].copy()
            y = out[:, yi].copy()
            out[:, xi] = x * c - y * s
            out[:, yi] = x * s + y * c

    return out


class Camera:
    def __init__(self, ndim, center, pos, neg):
        self.ndimensions = ndim
        self.center = np.array(center, dtype=float)
        self.screen_x = normalize(np.array(pos[0], dtype=float))
        self.screen_y = normalize(np.array(neg[0], dtype=float))

    def move_camera(self, delta):
        self.center += np.array(delta, dtype=float)

    def scale_camera(self, factor):
        self.screen_x *= factor
        self.screen_y *= factor

    def project_and_rotate_camera(self, change_code, angle):
        basis = np.vstack([self.screen_x, self.screen_y])
        rotated = project_and_rotate(basis, change_code, angle)
        self.screen_x = normalize(rotated[0])
        self.screen_y = normalize(rotated[1])

    def project_points(self, points):
        pts = np.asarray(points, dtype=float)
        rel = pts - self.center
        xs = rel @ self.screen_x
        ys = rel @ self.screen_y
        return xs, ys


class CameraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("N-D Camera Viewer")

        self.camera = None
        self.data_points = np.empty((0, 0))

        self.canvas_width = 900
        self.canvas_height = 600
        self.scale = 40

        self._build_ui()

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.canvas.bind("<Configure>", self._on_resize)

    def _build_ui(self):
        main = ttk.Frame(self.root)
        main.grid(row=0, column=0, sticky="nsew")

        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)   # canvas expands
        main.columnconfigure(1, weight=0)   # sidebar fixed width

        # ---------------- canvas ----------------
        self.canvas = tk.Canvas(main, bg="black")
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # ---------------- sidebar ----------------
        SIDEBAR_WIDTH = 230   # <<< middle ground width

        sidebar = ttk.Frame(main, width=SIDEBAR_WIDTH)
        sidebar.grid(row=0, column=1, sticky="ns", padx=4, pady=4)

        # stop auto-expansion
        sidebar.grid_propagate(False)

        # ---------------- controls ----------------
        controls = ttk.LabelFrame(sidebar, text="Controls")
        controls.pack(fill="x", pady=4)

        entry_width = 8

        ttk.Label(controls, text="Dimensions").grid(row=0, column=0, sticky="w")
        self.dim_entry = ttk.Entry(controls, width=entry_width)
        self.dim_entry.insert(0, "6")
        self.dim_entry.grid(row=0, column=1)

        ttk.Button(controls, text="Create Camera", command=self.create_camera)\
            .grid(row=1, column=0, columnspan=2, pady=2)

        ttk.Button(controls, text="Load Data File", command=self.load_file)\
            .grid(row=2, column=0, columnspan=2, pady=2)

        ttk.Label(controls, text="Move (comma list)").grid(row=3, column=0, sticky="w")
        self.move_entry = ttk.Entry(controls, width=entry_width)
        self.move_entry.insert(0, "0,0,0,0,0,0")
        self.move_entry.grid(row=3, column=1)

        ttk.Button(controls, text="Move", command=self.move_camera)\
            .grid(row=4, column=0, columnspan=2, pady=2)

        ttk.Label(controls, text="Scale factor").grid(row=5, column=0, sticky="w")
        self.scale_entry = ttk.Entry(controls, width=entry_width)
        self.scale_entry.insert(0, "1.1")
        self.scale_entry.grid(row=5, column=1)

        ttk.Button(controls, text="Scale Camera", command=self.scale_camera)\
            .grid(row=6, column=0, columnspan=2, pady=2)

        ttk.Label(controls, text="Rotate X dims").grid(row=7, column=0, sticky="w")
        self.rot_x_entry = ttk.Entry(controls, width=entry_width)
        self.rot_x_entry.insert(0, "0,1")
        self.rot_x_entry.grid(row=7, column=1)

        ttk.Label(controls, text="Rotate Y dims").grid(row=8, column=0, sticky="w")
        self.rot_y_entry = ttk.Entry(controls, width=entry_width)
        self.rot_y_entry.insert(0, "2,3")
        self.rot_y_entry.grid(row=8, column=1)

        ttk.Label(controls, text="Angle (radians)").grid(row=9, column=0, sticky="w")
        self.rot_angle_entry = ttk.Entry(controls, width=entry_width)
        self.rot_angle_entry.insert(0, "0.05")
        self.rot_angle_entry.grid(row=9, column=1)

        ttk.Button(controls, text="Rotate Camera", command=self.rotate_camera)\
            .grid(row=10, column=0, columnspan=2, pady=4)

        # ---------------- camera state panel ----------------
        state_frame = ttk.LabelFrame(sidebar, text="Camera State")
        state_frame.pack(fill="both", expand=True)

        self.state_text = tk.Text(
            state_frame,
            wrap="word",          # <<< wrap instead of forcing width
            bg="#111",
            fg="#00ffcc",
            font=("Consolas", 9),
            width=24,             # readable within 230px
            height=14
        )
        self.state_text.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(
            state_frame,
            orient="vertical",
            command=self.state_text.yview
        )
        scroll.pack(side="right", fill="y")
        self.state_text.configure(yscrollcommand=scroll.set)
        self.state_text.configure(state="disabled")

    # ---------------- resize ----------------
    def _on_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.update_canvas()

    # ---------------- camera ops ----------------
    def create_camera(self):
        D = int(self.dim_entry.get())
        center = np.zeros(D)
        pos = np.eye(D)[0]
        neg = np.eye(D)[1]
        self.camera = Camera(D, center, [pos], [neg])
        self.data_points = np.random.uniform(-5, 5, size=(600000, D))
        self.update_canvas()
        self.update_camera_state()

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
        self.camera = Camera(D, np.zeros(D), [np.eye(D)[0]], [np.eye(D)[1]])
        self.data_points = data
        self.dim_entry.delete(0, tk.END)
        self.dim_entry.insert(0, str(D))
        self.update_canvas()
        self.update_camera_state()

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

    # ---------------- rendering ----------------
    def update_canvas(self):
        if self.camera is None or self.data_points.size == 0:
            return

        xs, ys = self.camera.project_points(self.data_points)

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
        pts = self.data_points[mask]

        d = np.linalg.norm(pts - self.camera.center, axis=1)
        t = np.clip(d / 10.0, 0, 1)

        r = (255*(1-t)+60*t).astype(np.uint8)
        g = (220*(1-t)+80*t).astype(np.uint8)
        b = (80*(1-t)+255*t).astype(np.uint8)

        img = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        img[sy, sx] = np.stack([r, g, b], axis=1)

        pil = Image.fromarray(img, mode="RGB")
        self.photo = ImageTk.PhotoImage(pil)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

    def update_camera_state(self):
        if self.camera is None:
            return

        self.state_text.configure(state="normal")
        self.state_text.delete("1.0", tk.END)

        def fmt(v):
            return "[" + ", ".join(f"{x:.4f}" for x in v) + "]"

        self.state_text.insert(tk.END, "Center:\n" + fmt(self.camera.center) + "\n\n")
        self.state_text.insert(tk.END, "Screen X:\n" + fmt(self.camera.screen_x) + "\n\n")
        self.state_text.insert(tk.END, "Screen Y:\n" + fmt(self.camera.screen_y) + "\n\n")
        self.state_text.insert(tk.END, f"Dimensions: {self.camera.ndimensions}\n")

        self.state_text.configure(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    CameraGUI(root)
    root.mainloop()
