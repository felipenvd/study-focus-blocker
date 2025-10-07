import time
import os
import sys

# Caminho do arquivo hosts dependendo do sistema operacional
if os.name == 'nt':  # Windows
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
else:  # Linux/Mac
    hosts_path = "/etc/hosts"

# Redirecionamento para localhost
redirect = "127.0.0.1"

# Sites que você quer bloquear
sites_bloqueados = [
    "www.youtube.com",
    "youtube.com",
    "www.instagram.com",
    "instagram.com",
    "m.youtube.com",
    "m.instagram.com",
    "www.facebook.com",
    "facebook.com",
    "web.whatsapp.com",
    "www.whatsapp.com",
    "whatsapp.com",
    "x.com",
    "www.x.com",
    "twitter.com",
    "www.twitter.com",
    "mobile.twitter.com",
    "m.twitter.com"
]

def bloquear_sites():
    """Adiciona os sites bloqueados ao arquivo hosts"""
    try:
        with open(hosts_path, 'r+') as arquivo:
            conteudo = arquivo.read()
            
            # Adiciona os sites se ainda não estiverem bloqueados
            for site in sites_bloqueados:
                if site not in conteudo:
                    arquivo.write(f"\n{redirect} {site}")
        
        print("✅ Sites bloqueados com sucesso!")
        print("📚 Foco total nos estudos!")
        
    except PermissionError:
        print("❌ ERRO: Execute este programa como administrador!")
        print("   Windows: Clique com botão direito e 'Executar como administrador'")
        print("   Linux/Mac: Use 'sudo python bloqueador.py'")
        sys.exit(1)

def desbloquear_sites():
    """Remove os sites bloqueados do arquivo hosts"""
    try:
        with open(hosts_path, 'r+') as arquivo:
            linhas = arquivo.readlines()
            arquivo.seek(0)
            
            # Remove as linhas que contêm os sites bloqueados
            for linha in linhas:
                if not any(site in linha for site in sites_bloqueados):
                    arquivo.write(linha)
            
            arquivo.truncate()
        
        print("✅ Sites desbloqueados!")
        
    except PermissionError:
        print("❌ ERRO: Execute este programa como administrador!")
        sys.exit(1)

def main():
    print("=" * 50)
    print("🎯 BLOQUEADOR DE SITES PARA ESTUDOS")
    print("=" * 50)
    
    # Bloqueia os sites
    bloquear_sites()
    
    print("\n⏰ Quanto tempo você quer estudar?")
    try:
        minutos = int(input("Digite os minutos (ex: 60): "))
        
        print(f"\n⏳ Sites bloqueados por {minutos} minutos")
        print("💡 Pressione Ctrl+C para desbloquear antes se necessário\n")
        
        # Aguarda o tempo definido
        time.sleep(minutos * 60)
        
        print("\n⏰ Tempo de estudo finalizado!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Bloqueio interrompido pelo usuário")
    except ValueError:
        print("\n❌ Valor inválido! Digite apenas números.")
    finally:
        # Sempre desbloqueia os sites ao finalizar
        desbloquear_sites()
        print("👋 Até a próxima sessão de estudos!")

if __name__ == "__main__":
    main()