import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import json

NAVY = "#1F3A5F"
BLUE_FILL = "#EAF1FB"
BLUE_EDGE = "#2C5F8A"
ACCENT_FILL = "#FDEEDC"
ACCENT_EDGE = "#B9770E"
BG = "#0F172A"
WHITE = "#F5F7FA"

W, H = 1280, 720

def new_fig():
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis("off")
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    return fig, ax

def box(ax, cx, cy, w, h, title, fill=BLUE_FILL, edge=BLUE_EDGE, fs=18, sub=None):
    b = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                        boxstyle="round,pad=0.02,rounding_size=10",
                        linewidth=2, edgecolor=edge, facecolor=fill)
    ax.add_patch(b)
    ax.text(cx, cy + (8 if sub else 0), title, ha="center", va="center",
             fontsize=fs, fontweight="bold", color=NAVY)
    if sub:
        ax.text(cx, cy - 20, sub, ha="center", va="center", fontsize=12, color="#555")

def arrow(ax, x1, y1, x2, y2, color=WHITE):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                 mutation_scale=16, linewidth=2, color=color))

# ---------- Scene 1: Title ----------
fig, ax = new_fig()
ax.text(W/2, H/2 + 60, "Food_ordering_WebAPP", ha="center", va="center",
         fontsize=44, fontweight="bold", color=WHITE)
ax.text(W/2, H/2 - 10, "AI-generated repository overview", ha="center", va="center",
         fontsize=18, color="#9CB4D8")
ax.text(W/2, 60, "RepoGenie", ha="center", va="center", fontsize=16, color=ACCENT_EDGE, fontweight="bold")
plt.savefig("scenes/scene1.png", facecolor=BG)
plt.close()

# ---------- Scene 2: Overview ----------
fig, ax = new_fig()
ax.text(W/2, H - 90, "What is this project?", ha="center", va="center",
         fontsize=30, fontweight="bold", color=WHITE)
lines = [
    "A full-stack food ordering platform",
    "Separate experiences for:",
    "  \u2022 Customers  \u2022 Employees  \u2022 Administrators",
]
for i, line in enumerate(lines):
    ax.text(W/2, H - 220 - i*55, line, ha="center", va="center", fontsize=20, color="#D6E2F5")
plt.savefig("scenes/scene2.png", facecolor=BG)
plt.close()

# ---------- Scene 3: Architecture ----------
fig, ax = new_fig()
ax.text(W/2, H - 60, "Architecture", ha="center", va="center", fontsize=28, fontweight="bold", color=WHITE)
box(ax, W/2, H - 180, 420, 80, "Next.js Frontend", sub="client / employee / admin routes", fs=16)
arrow(ax, W/2, H - 220, W/2, H - 300)
box(ax, W/2, H - 360, 420, 80, "Django REST Backend", sub="7 feature modules", fs=16)
arrow(ax, W/2, H - 400, W/2, H - 480)
box(ax, W/2, H - 540, 420, 80, "MongoDB", sub="via pymongo", fill=ACCENT_FILL, edge=ACCENT_EDGE, fs=16)
plt.savefig("scenes/scene3.png", facecolor=BG)
plt.close()

# ---------- Scene 4: Modules ----------
fig, ax = new_fig()
ax.text(W/2, H - 60, "Key Backend Modules", ha="center", va="center", fontsize=28, fontweight="bold", color=WHITE)
modules = ["users", "carts", "orders", "shipments", "inventory", "promotions", "payments"]
cols = 4
bw_, bh_ = 260, 80
start_x = W/2 - (cols/2)*bw_ + bw_/2 - 20
for i, m in enumerate(modules):
    r, c = divmod(i, cols)
    cx = start_x + c*(bw_+20)
    cy = H - 200 - r*110
    box(ax, cx, cy, bw_-20, bh_, m, fs=16)
plt.savefig("scenes/scene4.png", facecolor=BG)
plt.close()

# ---------- Scene 5: Data flow ----------
fig, ax = new_fig()
ax.text(W/2, H - 60, "Request Data Flow", ha="center", va="center", fontsize=28, fontweight="bold", color=WHITE)
steps = ["Frontend", "API", "Django View", "Service", "MongoDB"]
bw2 = 200
total = len(steps)*bw2 + (len(steps)-1)*40
x0 = (W - total)/2 + bw2/2
for i, s in enumerate(steps):
    cx = x0 + i*(bw2+40)
    cy = H/2
    fill, edge = (ACCENT_FILL, ACCENT_EDGE) if s == "MongoDB" else (BLUE_FILL, BLUE_EDGE)
    box(ax, cx, cy, bw2, 70, s, fill=fill, edge=edge, fs=13)
    if i < len(steps)-1:
        arrow(ax, cx + bw2/2 + 5, cy, cx + bw2 + 35, cy)
plt.savefig("scenes/scene5.png", facecolor=BG)
plt.close()

# ---------- Scene 6: code snippet (Pygments) ----------
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter

code = '''class AuthenticationMiddleware(MiddlewareMixin):
    """Custom authentication middleware."""

    PUBLIC_PATHS = [
        '/api/v1/auth/',
        '/api/v1/users/create/',
        '/admin/',
    ]

    def process_request(self, request):
        if any(request.path.startswith(p) for p in self.PUBLIC_PATHS):
            return None
        if request.method == 'OPTIONS':
            return None
        # ...validate token, attach request.user...
'''

formatter = ImageFormatter(style="monokai", line_numbers=True, font_size=22,
                            image_pad=30, line_pad=6)
highlight(code, PythonLexer(), formatter, outfile="scenes/_code_raw.png")

# composite onto the 1280x720 dark canvas with a caption
fig, ax = new_fig()
ax.text(W/2, H - 40, "backend/middleware/auth.py", ha="center", va="center",
         fontsize=18, color=ACCENT_EDGE, fontweight="bold")
img = plt.imread("scenes/_code_raw.png")
ih, iw = img.shape[0], img.shape[1]
disp_w = 1000
disp_h = disp_w * ih / iw
ax.imshow(img, extent=(W/2 - disp_w/2, W/2 + disp_w/2, H/2 - disp_h/2 - 20, H/2 + disp_h/2 - 20))
plt.savefig("scenes/scene6.png", facecolor=BG)
plt.close()

# ---------- Scene 7: closing ----------
fig, ax = new_fig()
ax.text(W/2, H/2 + 30, "That's Food_ordering_WebAPP", ha="center", va="center",
         fontsize=30, fontweight="bold", color=WHITE)
ax.text(W/2, H/2 - 30, "Ask the AI to go deeper into any module", ha="center", va="center",
         fontsize=18, color="#9CB4D8")
ax.text(W/2, 60, "Generated by RepoGenie", ha="center", va="center", fontsize=14, color=ACCENT_EDGE)
plt.savefig("scenes/scene7.png", facecolor=BG)
plt.close()

print("all scenes rendered")
