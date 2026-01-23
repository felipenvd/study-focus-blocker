import flet as ft
import time
import os
import json
import asyncio
import subprocess
import atexit

# --- Configurações Padrão ---
if os.name == 'nt':  # Windows
    HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
else:  # Linux/Mac
    HOSTS_PATH = "/etc/hosts"

REDIRECT = "127.0.0.1"
SITES_FILE = os.path.join(os.path.dirname(__file__), "sites.json")

def with_opacity(opacity: float, color: str) -> str:
    """
    Helper to apply opacity to a color. 
    Assumes color is a hex string (e.g. #RRGGBB) or simple name (white, black).
    Returns #AARRGGBB format which Flet expects.
    """
    if color == ft.Colors.WHITE: color = "#FFFFFF"
    if color == ft.Colors.BLACK: color = "#000000"
    
    color = color.lstrip("#")
    
    # Handle partial hex or names not covered (simplify for this app)
    if len(color) not in (6, 8):
        # Fallback for named colors if not white/black - assuming they are full opaque initially
        # primitive check, for this app we only use white, black and some valid hexes
        if color.lower() == "white": color = "FFFFFF"
        elif color.lower() == "black": color = "000000"
        else: return color # Can't handle others easily without map
        
    if len(color) == 6:
        # RRGGBB -> AARRGGBB
        alpha = int(opacity * 255)
        return f"#{alpha:02x}{color}"
    return f"#{color}"


DEFAULT_SITES = [
    "www.youtube.com", "youtube.com", "m.youtube.com", "youtu.be",
    "www.instagram.com", "instagram.com", "m.instagram.com",
    "www.facebook.com", "facebook.com", "m.facebook.com", "web.facebook.com",
    "web.whatsapp.com", "www.whatsapp.com", "whatsapp.com",
    "x.com", "www.x.com", "twitter.com", "www.twitter.com"
]

def load_sites():
    try:
        with open(SITES_FILE, 'r') as f:
            data = json.load(f)
            return data.get("sites", DEFAULT_SITES)
    except (FileNotFoundError, json.JSONDecodeError):
        save_sites(DEFAULT_SITES)
        return DEFAULT_SITES

def save_sites(sites):
    with open(SITES_FILE, 'w') as f:
        json.dump({"sites": sites}, f, indent=2)

class FocusBlockerApp:
    def __init__(self):
        self.bloqueado = False
        self.timer_rodando = False
        self.tempo_restante = 0
        self.page = None
        self.sites = load_sites()
        
        atexit.register(self.limpeza_final)

    def limpeza_final(self):
        if self.bloqueado:
            print("Encerrando e desbloqueando sites...")
            self.desbloquear_sites()

    async def main(self, page: ft.Page):
        self.page = page
        self.page.title = "Focus Blocker Pro"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 450
        self.page.window_height = 850
        self.page.window_resizable = False
        self.page.padding = 0
        self.page.bgcolor = "#0f172a"
        
        self.page.window.on_event = self.window_event

        self.main_container = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#0f172a", "#1e1b4b", "#000000"], 
            ),
            padding=30,
            expand=True,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    self._build_header(),
                    self._build_timer_section(),
                    self._build_controls(),
                    self._build_action_button(),
                    ft.Divider(height=20, color=ft.Colors.WHITE10),
                    self._build_sites_manager()
                ]
            )
        )

        self.page.add(self.main_container)
        self.page.overlay.append(self._build_warning_dialog())
        await self.verificar_permissoes()

    def window_event(self, e):
        if e.data == "close":
            self.limpeza_final()
            self.page.window.destroy()

    def _build_warning_dialog(self):
        self.warning_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Atenção Necessária", color=ft.Colors.ORANGE_400),
            content=ft.Text(
                "Para o bloqueio funcionar 100%, você precisa FECHAR E REABRIR seu navegador agora.\n\nIsso limpa conexões antigas.",
                size=16
            ),
            actions=[
                ft.TextButton("Entendi, vou reiniciar!", on_click=self.close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor="#1e293b",
        )
        return self.warning_dialog

    async def close_dialog(self, e):
        self.warning_dialog.open = False
        self.page.update()

    def _glass_container(self, content, padding=20, margin=None, width=None, on_click=None):
        return ft.Container(
            content=content,
            padding=padding,
            margin=margin,
            width=width,
            bgcolor=with_opacity(0.1, ft.Colors.WHITE),
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            border_radius=20,
            border=ft.Border.all(1, with_opacity(0.2, ft.Colors.WHITE)),
            on_click=on_click,
            ink=True if on_click else False
        )

    def _build_header(self):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(ft.Icons.LOCK_CLOCK, size=40, color="#818cf8"),
                    bgcolor=with_opacity(0.1, ft.Colors.WHITE),
                    blur=ft.Blur(5, 5),
                    padding=15,
                    border_radius=50,
                    margin=ft.Margin(0, 0, 0, 10),
                    border=ft.Border.all(1, with_opacity(0.2, ft.Colors.WHITE))
                ),
                ft.Text("Focus Mode", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            margin=ft.Margin(0, 20, 0, 10)
        )

    def _build_timer_section(self):
        self.timer_text = ft.Text(
            "00:00:00", 
            size=32, 
            weight=ft.FontWeight.W_900, 
            color="#ffffff",
            font_family="monospace"
        )
        self.status_text = ft.Text("Pronto para focar?", color=ft.Colors.WHITE70, size=14)
        
        self.progress_ring = ft.ProgressRing(
            width=200, 
            height=200, 
            stroke_width=8, 
            color=ft.Colors.CYAN_400,
            bgcolor=with_opacity(0.1, ft.Colors.WHITE),
            value=0
        )

        return self._glass_container(
            content=ft.Stack(
                controls=[
                    self.progress_ring,
                    ft.Column([
                        self.timer_text,
                        self.status_text
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ],
                alignment=ft.Alignment(0, 0)
            ),
            width=300,
            padding=20
        )

    def _build_controls(self):
        def criar_input(label, ref, valor):
            return ft.TextField(
                label=label,
                value=valor,
                width=90,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                border_color=with_opacity(0.5, "#6366f1"),
                text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                label_style=ft.TextStyle(color="#818cf8"),
                bgcolor=with_opacity(0.1, ft.Colors.BLACK),
                ref=ref
            )

        self.horas_input = ft.Ref[ft.TextField]()
        self.minutos_input = ft.Ref[ft.TextField]()

        inputs = ft.Row(
            [
                criar_input("Horas", self.horas_input, "0"),
                criar_input("Minutos", self.minutos_input, "25")
            ], 
            alignment=ft.MainAxisAlignment.CENTER
        )

        tempos = [("15m", 15), ("25m", 25), ("45m", 45), ("1h", 60), ("2h", 120)]
        chips = []
        for label, mins in tempos:
            chips.append(
                ft.Container(
                    content=ft.Text(label, color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                    bgcolor=with_opacity(0.2, "#4f46e5"),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    border_radius=20,
                    on_click=lambda e, m=mins: asyncio.create_task(self.set_time(0 if m < 60 else m // 60, m % 60)),
                    ink=True,
                    border=ft.Border.all(1, with_opacity(0.3, "#818cf8"))
                )
            )

        return ft.Column([
            inputs,
            ft.Row(chips, alignment=ft.MainAxisAlignment.CENTER, wrap=True)
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _build_action_button(self):
        self.action_btn = ft.Container(
            content=ft.Text("INICIAR FOCO 🚀", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            width=280,
            height=60,
            gradient=ft.LinearGradient(colors=["#4f46e5", "#7c3aed"]),
            border_radius=15,
            alignment=ft.Alignment(0, 0),
            on_click=self.toggle_bloqueio, 
            ink=True,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=20,
                color=with_opacity(0.5, "#4f46e5"),
                offset=ft.Offset(0, 5),
            ),
            border=ft.Border.all(1, with_opacity(0.3, ft.Colors.WHITE))
        )
        return self.action_btn

    def _build_sites_manager(self):
        self.new_site_input = ft.TextField(
            hint_text="Ex: reddit.com",
            width=200,
            border_color="#6366f1",
            text_style=ft.TextStyle(size=14, color=ft.Colors.WHITE),
            bgcolor=with_opacity(0.1, ft.Colors.BLACK),
            on_submit=self.add_site
        )
        
        add_btn = ft.Container(
            content=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=20),
            bgcolor=with_opacity(0.8, "#0ea5e9"), # Sky 500
            border_radius=10,
            padding=10,
            on_click=self.add_site,
            ink=True
        )

        self.sites_list_column = ft.Column(
            controls=self._build_site_rows(),
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            height=150
        )

        return self._glass_container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BLOCK, color=ft.Colors.RED_400, size=20),
                    ft.Text("Sites Bloqueados", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                ]),
                ft.Row([
                    self.new_site_input,
                    add_btn
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=self.sites_list_column,
                    bgcolor=with_opacity(0.3, ft.Colors.BLACK),
                    border_radius=10,
                    padding=10,
                    margin=ft.Margin(0, 10, 0, 0)
                )
            ], spacing=10),
            padding=15,
            width=380
        )

    def _build_site_rows(self):
        rows = []
        for site in sorted(set(self.sites)):
            rows.append(
                ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.RED_400),
                    ft.Text(site, color=ft.Colors.WHITE70, size=12, expand=True),
                    ft.Container(
                        content=ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_300),
                        on_click=lambda e, s=site: asyncio.create_task(self.remove_site(s)),
                        ink=True,
                        border_radius=5,
                        padding=5
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        return rows

    async def add_site(self, e):
        new_site = self.new_site_input.value.strip().lower()
        if new_site and new_site not in self.sites:
            new_site = new_site.replace("https://", "").replace("http://", "").rstrip("/")
            self.sites.append(new_site)
            save_sites(self.sites)
            self.new_site_input.value = ""
            self.sites_list_column.controls = self._build_site_rows()
            self.page.update()

    async def remove_site(self, site):
        if site in self.sites:
            self.sites.remove(site)
            save_sites(self.sites)
            self.sites_list_column.controls = self._build_site_rows()
            self.page.update()

    async def set_time(self, h, m):
        self.horas_input.current.value = str(h)
        self.minutos_input.current.value = str(m)
        self.page.update()

    async def verificar_permissoes(self):
        try:
            with open(HOSTS_PATH, 'r+') as f:
                pass
        except PermissionError:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("⚠️ Execute como Administrador para funcionar!"), 
                bgcolor=ft.Colors.RED_900
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            self.action_btn.content.value = "SEM PERMISSÃO 🔒"
            self.action_btn.gradient = ft.LinearGradient(colors=[ft.Colors.GREY_700, ft.Colors.GREY_800])
            self.action_btn.on_click = None
            self.page.update()

    def limpar_dns(self):
        try:
            if os.name == 'nt':
                subprocess.run(['ipconfig', '/flushdns'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.run(['sudo', 'systemd-resolve', '--flush-caches'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

    def bloquear_sites(self):
        try:
            with open(HOSTS_PATH, 'r+') as arquivo:
                conteudo = arquivo.read()
                for site in self.sites:
                    if site not in conteudo:
                        arquivo.write(f"\n{REDIRECT} {site}")
            self.limpar_dns()
            return True
        except Exception as e:
            print(f"Erro: {e}")
            return False

    def desbloquear_sites(self):
        try:
            with open(HOSTS_PATH, 'r+') as arquivo:
                linhas = arquivo.readlines()
                arquivo.seek(0)
                for linha in linhas:
                    if not any(site in linha for site in self.sites):
                        arquivo.write(linha)
                arquivo.truncate()
            return True
        except Exception as e:
            print(f"Erro: {e}")
            return False

    async def toggle_bloqueio(self, e):
        if not self.bloqueado:
            try:
                h = int(self.horas_input.current.value)
                m = int(self.minutos_input.current.value)
                self.total_segundos = (h * 3600) + (m * 60)
                
                if self.total_segundos <= 0:
                    return

                if self.bloquear_sites():
                    self.bloqueado = True
                    self.tempo_restante = self.total_segundos
                    self.timer_rodando = True
                    
                    self.action_btn.content.value = "PARAR FOCO ⏹️"
                    self.action_btn.gradient = ft.LinearGradient(colors=["#be123c", "#9f1239"]) # Rose Gradients
                    self.action_btn.shadow.color = with_opacity(0.5, "#be123c")
                    
                    self.status_text.value = "Modo Foco Ativo 🔥"
                    self.status_text.color = "#fb7185"
                    self.status_text.weight = ft.FontWeight.BOLD
                    self.horas_input.current.disabled = True
                    self.minutos_input.current.disabled = True
                    
                    self.progress_ring.value = 1.0
                    
                    self.page.update()
                    
                    self.warning_dialog.open = True
                    self.page.update()
                    
                    asyncio.create_task(self.executar_timer())
            except ValueError:
                pass
        else:
            await self.parar_bloqueio()

    async def executar_timer(self):
        end_time = time.time() + self.tempo_restante
        last_remaining = -1
        
        while self.timer_rodando:
            remaining = int(end_time - time.time())
            
            if remaining <= 0:
                break
            
            if remaining != last_remaining:
                last_remaining = remaining
                m, s = divmod(remaining, 60)
                h, m = divmod(m, 60)
                
                # Update progress ring
                progress = remaining / self.total_segundos
                self.progress_ring.value = progress

                try:
                    self.timer_text.value = "{:02d}:{:02d}:{:02d}".format(h, m, s)
                    self.timer_text.update()
                    self.progress_ring.update()
                except:
                    break 
            
            await asyncio.sleep(0.1)

        if self.timer_rodando: 
            await self.parar_bloqueio()

    async def parar_bloqueio(self):
        self.timer_rodando = False
        self.desbloquear_sites()
        self.bloqueado = False
        
        try:
            self.timer_text.value = "00:00:00"
            self.progress_ring.value = 0
            
            self.action_btn.content.value = "INICIAR FOCO 🚀"
            self.action_btn.gradient = ft.LinearGradient(colors=["#4f46e5", "#7c3aed"])
            self.action_btn.shadow.color = with_opacity(0.5, "#4f46e5")
            
            self.status_text.value = "Pronto para focar?"
            self.status_text.color = ft.Colors.WHITE54
            self.status_text.weight = ft.FontWeight.NORMAL
            self.horas_input.current.disabled = False
            self.minutos_input.current.disabled = False
            self.page.update()
        except:
            pass

if __name__ == "__main__":
    app = FocusBlockerApp()
    ft.run(app.main)
