import tkinter as tk
from tkinter import ttk, messagebox
import time
import os
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import subprocess

# Caminho do arquivo hosts dependendo do sistema operacional
if os.name == 'nt':  # Windows
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
else:  # Linux/Mac
    hosts_path = "/etc/hosts"

# Redirecionamento para localhost
redirect = "127.0.0.1"

# Sites que você quer bloquear - todas as variações possíveis
sites_bloqueados = [
    # YouTube
    "www.youtube.com",
    "youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",

    # Instagram
    "www.instagram.com",
    "instagram.com",
    "m.instagram.com",

    # Facebook
    "www.facebook.com",
    "facebook.com",
    "m.facebook.com",
    "web.facebook.com",
    "fb.com",
    "www.fb.com"
]

class BloqueadorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Bloqueador de Sites - Foco nos Estudos")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Variáveis de controle
        self.bloqueado = False
        self.timer_rodando = False
        self.tempo_restante = 0
        self.thread_timer = None
        self.servidor_http = None
        self.thread_servidor = None

        # Cores do tema
        self.cor_primaria = "#6366f1"
        self.cor_secundaria = "#4f46e5"
        self.cor_sucesso = "#10b981"
        self.cor_erro = "#ef4444"
        self.cor_fundo = "#f8fafc"
        self.cor_card = "#ffffff"

        self.root.configure(bg=self.cor_fundo)

        self.criar_interface()
        self.verificar_permissoes()

    def criar_interface(self):
        # Cabeçalho
        header_frame = tk.Frame(self.root, bg=self.cor_primaria, height=100)
        header_frame.pack(fill="x", pady=(0, 20))

        titulo = tk.Label(
            header_frame,
            text="🎯 Bloqueador de Sites",
            font=("Arial", 24, "bold"),
            bg=self.cor_primaria,
            fg="white"
        )
        titulo.pack(pady=20)

        # Container principal
        main_container = tk.Frame(self.root, bg=self.cor_fundo)
        main_container.pack(fill="both", expand=True, padx=30)

        # Card de tempo
        tempo_card = tk.Frame(main_container, bg=self.cor_card, relief="flat", bd=0)
        tempo_card.pack(fill="x", pady=(0, 20))

        tempo_label = tk.Label(
            tempo_card,
            text="⏰ Tempo de Estudo",
            font=("Arial", 14, "bold"),
            bg=self.cor_card,
            fg="#1e293b"
        )
        tempo_label.pack(pady=(20, 10))

        # Frame para entrada de tempo
        input_frame = tk.Frame(tempo_card, bg=self.cor_card)
        input_frame.pack(pady=10)

        # Campo de horas
        self.horas_var = tk.StringVar(value="0")
        horas_entry = tk.Entry(
            input_frame,
            textvariable=self.horas_var,
            font=("Arial", 32, "bold"),
            width=3,
            justify="center",
            relief="flat",
            bg="#f1f5f9",
            fg=self.cor_primaria
        )
        horas_entry.pack(side="left", padx=5)

        h_label = tk.Label(
            input_frame,
            text="h",
            font=("Arial", 20, "bold"),
            bg=self.cor_card,
            fg="#64748b"
        )
        h_label.pack(side="left", padx=2)

        # Campo de minutos
        self.minutos_var = tk.StringVar(value="25")
        minutos_entry = tk.Entry(
            input_frame,
            textvariable=self.minutos_var,
            font=("Arial", 32, "bold"),
            width=3,
            justify="center",
            relief="flat",
            bg="#f1f5f9",
            fg=self.cor_primaria
        )
        minutos_entry.pack(side="left", padx=5)

        min_label = tk.Label(
            input_frame,
            text="min",
            font=("Arial", 20, "bold"),
            bg=self.cor_card,
            fg="#64748b"
        )
        min_label.pack(side="left", padx=2)

        # Botões de tempo rápido
        quick_frame = tk.Frame(tempo_card, bg=self.cor_card)
        quick_frame.pack(pady=15)

        tk.Label(
            quick_frame,
            text="Atalhos rápidos:",
            font=("Arial", 10),
            bg=self.cor_card,
            fg="#64748b"
        ).pack()

        buttons_frame = tk.Frame(quick_frame, bg=self.cor_card)
        buttons_frame.pack(pady=5)

        # Botões em minutos
        tempos_min = [15, 25, 45]
        for tempo in tempos_min:
            btn = tk.Button(
                buttons_frame,
                text=f"{tempo}min",
                font=("Arial", 9),
                bg="#e2e8f0",
                fg="#475569",
                relief="flat",
                cursor="hand2",
                padx=10,
                pady=5,
                command=lambda t=tempo: self.definir_tempo(0, t)
            )
            btn.pack(side="left", padx=3)
            self.adicionar_hover(btn, "#cbd5e1", "#e2e8f0")

        # Botões em horas
        tempos_hora = [1, 2, 3, 4]
        for tempo in tempos_hora:
            btn = tk.Button(
                buttons_frame,
                text=f"{tempo}h",
                font=("Arial", 9),
                bg="#ddd6fe",
                fg="#5b21b6",
                relief="flat",
                cursor="hand2",
                padx=10,
                pady=5,
                command=lambda t=tempo: self.definir_tempo(t, 0)
            )
            btn.pack(side="left", padx=3)
            self.adicionar_hover(btn, "#c4b5fd", "#ddd6fe")

        # Status do bloqueio
        self.status_label = tk.Label(
            main_container,
            text="🔓 Sites desbloqueados",
            font=("Arial", 16, "bold"),
            bg=self.cor_fundo,
            fg="#64748b"
        )
        self.status_label.pack(pady=15)

        # Timer display
        self.timer_label = tk.Label(
            main_container,
            text="00:00",
            font=("Arial", 48, "bold"),
            bg=self.cor_fundo,
            fg=self.cor_primaria
        )
        self.timer_label.pack(pady=10)

        # Botão principal
        self.btn_principal = tk.Button(
            main_container,
            text="🚀 Iniciar Bloqueio",
            font=("Arial", 16, "bold"),
            bg=self.cor_primaria,
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=40,
            pady=15,
            command=self.toggle_bloqueio
        )
        self.btn_principal.pack(pady=20)
        self.adicionar_hover(self.btn_principal, self.cor_secundaria, self.cor_primaria)

        # Lista de sites bloqueados
        sites_card = tk.Frame(main_container, bg=self.cor_card, relief="flat")
        sites_card.pack(fill="both", expand=True, pady=(10, 0))

        sites_titulo = tk.Label(
            sites_card,
            text="📋 Sites Bloqueados",
            font=("Arial", 12, "bold"),
            bg=self.cor_card,
            fg="#1e293b"
        )
        sites_titulo.pack(pady=(15, 10))

        # Lista de sites com scroll
        sites_scroll_frame = tk.Frame(sites_card, bg=self.cor_card)
        sites_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Canvas para scroll
        canvas = tk.Canvas(sites_scroll_frame, bg=self.cor_card, highlightthickness=0, height=150)
        scrollbar = tk.Scrollbar(sites_scroll_frame, orient="vertical", command=canvas.yview)
        sites_frame = tk.Frame(canvas, bg=self.cor_card)

        sites_frame.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=sites_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mostra todos os sites da lista sites_bloqueados
        sites_exibidos = set()  # Para evitar duplicatas visuais
        for site in sites_bloqueados:
            # Pega apenas o domínio principal para exibição limpa
            dominio_principal = site.replace("www.", "").replace("m.", "")
            if dominio_principal not in sites_exibidos:
                sites_exibidos.add(dominio_principal)
                site_label = tk.Label(
                    sites_frame,
                    text=f"🚫 {dominio_principal}",
                    font=("Arial", 11),
                    bg=self.cor_card,
                    fg="#475569",
                    anchor="w"
                )
                site_label.pack(fill="x", pady=3)

        canvas.pack(side="left", fill="both", expand=True)
        if len(sites_bloqueados) > 5:  # Só mostra scrollbar se necessário
            scrollbar.pack(side="right", fill="y")

    def adicionar_hover(self, widget, cor_hover, cor_normal):
        """Adiciona efeito hover aos botões"""
        widget.bind("<Enter>", lambda e: widget.config(bg=cor_hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=cor_normal))

    def definir_tempo(self, horas, minutos):
        """Define o tempo nos campos de horas e minutos"""
        self.horas_var.set(str(horas))
        self.minutos_var.set(str(minutos))

    def verificar_permissoes(self):
        """Verifica se tem permissões para modificar o arquivo hosts"""
        try:
            with open(hosts_path, 'r') as f:
                pass
        except PermissionError:
            msg = "⚠️ ATENÇÃO: Execute como administrador!\n\n"
            if os.name == 'nt':
                msg += "Windows: Clique com botão direito e\n'Executar como administrador'"
            else:
                msg += "Linux/Mac: Execute com 'sudo python3 bloqueador_gui.py'"

            messagebox.showerror("Permissão Negada", msg)

    def iniciar_servidor(self):
        """Inicia o servidor HTTP para servir a página de bloqueio"""
        class CustomHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                # Sempre serve a página de bloqueio para qualquer requisição
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                pagina_path = os.path.join(os.path.dirname(__file__), 'pagina_bloqueio.html')
                try:
                    with open(pagina_path, 'rb') as f:
                        self.wfile.write(f.read())
                except:
                    self.wfile.write(b"<h1>Site Bloqueado - Foque nos Estudos!</h1>")

            def log_message(self, format_str, *args):
                pass  # Silencia logs do servidor

        try:
            # Tenta usar a porta 80 primeiro (requer admin), senão usa 8080
            porta = 80
            try:
                self.servidor_http = HTTPServer(('127.0.0.1', porta), CustomHandler)
            except:
                porta = 8080
                self.servidor_http = HTTPServer(('127.0.0.1', porta), CustomHandler)

            # Inicia servidor em thread separada
            self.thread_servidor = threading.Thread(target=self.servidor_http.serve_forever, daemon=True)
            self.thread_servidor.start()
            return porta
        except Exception as e:
            print(f"Erro ao iniciar servidor: {e}")
            return None

    def parar_servidor(self):
        """Para o servidor HTTP"""
        if self.servidor_http:
            self.servidor_http.shutdown()
            self.servidor_http = None

    def limpar_cache_dns(self):
        """Limpa o cache DNS do sistema"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['ipconfig', '/flushdns'],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             check=False)
            else:  # Linux/Mac
                # Tenta diferentes comandos dependendo do sistema
                try:
                    subprocess.run(['sudo', 'systemd-resolve', '--flush-caches'],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,
                                 check=False)
                except:
                    try:
                        subprocess.run(['sudo', 'dscacheutil', '-flushcache'],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL,
                                     check=False)
                    except:
                        pass
        except:
            pass  # Silenciosamente ignora erros

    def bloquear_sites(self):
        """Adiciona os sites bloqueados ao arquivo hosts"""
        try:
            # Inicia o servidor HTTP
            porta = self.iniciar_servidor()
            if not porta:
                messagebox.showwarning("Aviso", "Não foi possível iniciar o servidor de bloqueio")
                return False

            # Define o IP de redirecionamento
            redirect_ip = f"127.0.0.1"

            with open(hosts_path, 'r+') as arquivo:
                conteudo = arquivo.read()

                for site in sites_bloqueados:
                    if site not in conteudo:
                        arquivo.write(f"\n{redirect_ip} {site}")

            self.bloqueado = True
            self.status_label.config(text="🔒 Sites bloqueados!", fg=self.cor_sucesso)

            # Limpa o cache DNS para garantir que o bloqueio funcione imediatamente
            self.limpar_cache_dns()

            # Aviso para fechar o navegador
            messagebox.showinfo(
                "Bloqueio Ativado! 🔒",
                "Sites bloqueados com sucesso!\n\n"
                "⚠️ IMPORTANTE:\n"
                "• Feche COMPLETAMENTE o navegador\n"
                "• Abra novamente para o bloqueio funcionar\n\n"
                "Bons estudos! 📚"
            )

            return True

        except PermissionError:
            messagebox.showerror(
                "Erro de Permissão",
                "Execute o programa como administrador!"
            )
            return False

    def desbloquear_sites(self):
        """Remove os sites bloqueados do arquivo hosts"""
        try:
            with open(hosts_path, 'r+') as arquivo:
                linhas = arquivo.readlines()
                arquivo.seek(0)

                for linha in linhas:
                    if not any(site in linha for site in sites_bloqueados):
                        arquivo.write(linha)

                arquivo.truncate()

            self.bloqueado = False
            self.status_label.config(text="🔓 Sites desbloqueados", fg="#64748b")
            return True

        except PermissionError:
            messagebox.showerror(
                "Erro de Permissão",
                "Execute o programa como administrador!"
            )
            return False

    def toggle_bloqueio(self):
        """Alterna entre bloquear e desbloquear"""
        if not self.bloqueado:
            try:
                horas = int(self.horas_var.get())
                minutos = int(self.minutos_var.get())

                # Validação: não permitir 0h e 0min
                if horas == 0 and minutos == 0:
                    messagebox.showwarning("Aviso", "Digite um tempo maior que zero!")
                    return

                # Validação: valores negativos
                if horas < 0 or minutos < 0:
                    messagebox.showwarning("Aviso", "Digite apenas valores positivos!")
                    return

                # Validação: minutos não podem ser >= 60
                if minutos >= 60:
                    messagebox.showwarning("Aviso", "Minutos devem ser menores que 60!")
                    return

                if self.bloquear_sites():
                    # Calcula tempo total em segundos
                    self.tempo_restante = (horas * 3600) + (minutos * 60)
                    self.timer_rodando = True
                    self.btn_principal.config(
                        text="⏹️ Parar Bloqueio",
                        bg=self.cor_erro
                    )
                    self.adicionar_hover(self.btn_principal, "#dc2626", self.cor_erro)

                    # Inicia o timer em uma thread separada
                    self.thread_timer = threading.Thread(target=self.executar_timer, daemon=True)
                    self.thread_timer.start()

            except ValueError:
                messagebox.showwarning("Aviso", "Digite apenas números!")
        else:
            self.parar_bloqueio()

    def executar_timer(self):
        """Executa o timer de contagem regressiva"""
        while self.timer_rodando and self.tempo_restante > 0:
            horas = self.tempo_restante // 3600
            minutos = (self.tempo_restante % 3600) // 60
            segundos = self.tempo_restante % 60

            if horas > 0:
                self.timer_label.config(text=f"{horas:02d}:{minutos:02d}:{segundos:02d}")
            else:
                self.timer_label.config(text=f"{minutos:02d}:{segundos:02d}")

            time.sleep(1)
            self.tempo_restante -= 1

        if self.tempo_restante <= 0 and self.timer_rodando:
            self.timer_label.config(text="00:00")
            self.parar_bloqueio()
            messagebox.showinfo(
                "Tempo Finalizado! 🎉",
                "Sua sessão de estudos terminou!\nBom trabalho! 📚"
            )

    def parar_bloqueio(self):
        """Para o bloqueio e desbloqueia os sites"""
        self.timer_rodando = False
        if self.desbloquear_sites():
            self.parar_servidor()  # Para o servidor HTTP
            self.timer_label.config(text="00:00")
            self.btn_principal.config(
                text="🚀 Iniciar Bloqueio",
                bg=self.cor_primaria
            )
            self.adicionar_hover(self.btn_principal, self.cor_secundaria, self.cor_primaria)

    def ao_fechar(self):
        """Garante que os sites sejam desbloqueados ao fechar"""
        if self.bloqueado:
            self.desbloquear_sites()
        self.parar_servidor()  # Para o servidor se estiver rodando
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BloqueadorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.ao_fechar)
    root.mainloop()

if __name__ == "__main__":
    main()
