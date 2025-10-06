# 🎯 Bloqueador de Sites para Estudos

Um bloqueador de sites simples e eficaz para te ajudar a manter o foco durante sessões de estudo, bloqueando temporariamente sites que causam distrações como YouTube, Instagram e Facebook.

## 📋 Características

- ✅ **Interface Gráfica Moderna** - Design intuitivo e bonito
- ⏰ Timer visual com contagem regressiva em tempo real
- 🚀 Atalhos rápidos (15, 25, 45, 60 minutos)
- 🔒 Bloqueia automaticamente YouTube, Instagram e Facebook
- 🔓 Desbloqueia automaticamente após o tempo definido
- ⚡ Leve e sem consumo de recursos
- 🖥️ Funciona em Windows, Linux e macOS
- 🎨 Interface responsiva com efeitos visuais

## 🛠️ Como Funciona

O programa modifica temporariamente o arquivo `hosts` do sistema operacional, redirecionando os domínios dos sites bloqueados para `127.0.0.1` (localhost). Isso impede que o navegador acesse esses sites enquanto o bloqueio estiver ativo.

Quando o tempo de estudo termina ou você interrompe o programa (Ctrl+C), os sites são automaticamente desbloqueados.

## 📦 Requisitos

- Python 3.6 ou superior
- Privilégios de administrador/root

## 🚀 Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/bloqueador-sites.git
cd bloqueador-sites
```

2. Não há dependências externas! O programa usa apenas bibliotecas nativas do Python.

## 💻 Como Usar

### 🎨 Interface Gráfica (Recomendado)

#### Windows

1. Clique com o botão direito no arquivo `bloqueador_gui.py`
2. Selecione **"Executar como administrador"**

**Ou via terminal:**
```bash
# Abra o PowerShell como Administrador
python bloqueador_gui.py
```

#### Linux / macOS

```bash
sudo python3 bloqueador_gui.py
```

### Uso da Interface Gráfica

1. **Defina o tempo** - Digite os minutos ou clique nos atalhos rápidos (15, 25, 45, 60 min)
2. **Clique em "Iniciar Bloqueio"** - Os sites serão bloqueados imediatamente
3. **Acompanhe o timer** - Visualize o tempo restante em tempo real
4. **Finalize** - Os sites são desbloqueados automaticamente ou clique em "Parar Bloqueio"

### 📟 Versão Terminal (Alternativa)

Se preferir usar a versão em linha de comando:

#### Windows
```bash
python bloqueador.py
```

#### Linux / macOS
```bash
sudo python3 bloqueador.py
```

Após executar:
1. Digite quantos minutos você quer estudar
2. Os sites serão bloqueados imediatamente
3. Pressione `Ctrl+C` para interromper antes do tempo

## 📸 Screenshots

### Interface Gráfica

A interface moderna oferece:
- 🎯 **Cabeçalho destacado** com o título do app
- ⏰ **Seletor de tempo** com campo personalizável
- 🚀 **Botões de atalho rápido** para tempos predefinidos
- 📊 **Timer visual** mostrando tempo restante em MM:SS
- 🔒 **Status do bloqueio** em tempo real
- 📋 **Lista dos sites bloqueados**

### Versão Terminal

```
==================================================
🎯 BLOQUEADOR DE SITES PARA ESTUDOS
==================================================
✅ Sites bloqueados com sucesso!
📚 Foco total nos estudos!

⏰ Quanto tempo você quer estudar?
Digite os minutos (ex: 60): 60

⏳ Sites bloqueados por 60 minutos
💡 Pressione Ctrl+C para desbloquear antes se necessário
```

## 🎯 Sites Bloqueados por Padrão

- YouTube (www.youtube.com, youtube.com, m.youtube.com)
- Instagram (www.instagram.com, instagram.com, m.instagram.com)
- Facebook (www.facebook.com, facebook.com)

### Personalizando Sites Bloqueados

Para adicionar ou remover sites, edite a lista `sites_bloqueados` no código:

```python
sites_bloqueados = [
    "www.youtube.com",
    "youtube.com",
    "www.instagram.com",
    "instagram.com",
    # Adicione mais sites aqui
    "twitter.com",
    "www.twitter.com"
]
```

## ⚠️ Avisos Importantes

- **Privilégios de Administrador:** O programa precisa de privilégios elevados para modificar o arquivo hosts
- **Antivírus:** Alguns antivírus podem alertar sobre modificação do arquivo hosts - isso é normal
- **Navegadores Abertos:** Feche e reabra o navegador após iniciar o bloqueio para garantir que funcione
- **Cache DNS:** Em alguns casos, pode ser necessário limpar o cache DNS:
  - Windows: `ipconfig /flushdns`
  - Linux: `sudo systemd-resolve --flush-caches`
  - macOS: `sudo dscacheutil -flushcache`

## 🧩 Técnicas de Estudo Recomendadas

### Técnica Pomodoro
Use o bloqueador com sessões de:
- 25 minutos de estudo focado
- 5 minutos de pausa
- Repita 4 vezes
- Pausa longa de 15-30 minutos

### Blocos de Estudo Intenso
- 50-60 minutos de estudo profundo
- 10-15 minutos de pausa

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abrir um Pull Request

## 📝 Ideias para Futuras Melhorias

- [x] Interface gráfica (GUI) ✨
- [ ] Configuração via arquivo JSON
- [ ] Estatísticas de tempo de estudo
- [ ] Lista de sites personalizável via interface
- [ ] Modo "trabalho" vs "estudo"
- [ ] Notificações desktop ao finalizar
- [ ] Som ao terminar sessão
- [ ] Histórico de sessões de estudo
- [ ] Gráficos de produtividade

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

Desenvolvido para estudantes que querem melhorar seu foco e produtividade! 📚✨

---

**Dica:** Use com disciplina! O bloqueador é uma ferramenta, mas a verdadeira mudança vem do seu compromisso com os estudos. 💪