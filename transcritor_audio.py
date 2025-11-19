import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import requests
import urllib3
import os
from pathlib import Path
import json
import tempfile
import subprocess
import sys

# Desabilita warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TranscritorAudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcritor de Áudio - Groq API")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Arquivo de configuração para salvar a API key
        self.config_file = Path.home() / ".transcritor_config.json"
        self.api_key = self.carregar_api_key()
        
        # Variável para qualidade de áudio não é mais necessária
        
        self.criar_interface()
        
    def carregar_api_key(self):
        """Carrega a API key do arquivo de configuração"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key', '')
            except:
                return ''
        return ''
    
    def encontrar_ffmpeg(self):
        """Tenta encontrar o executável do ffmpeg"""
        # Se estiver rodando como executável PyInstaller
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
        
        # Tenta usar ffmpeg do PATH do sistema
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, 
                                  timeout=5)
            if result.returncode == 0:
                return 'ffmpeg'
        except:
            pass
        
        return None
    
    def salvar_api_key(self, api_key):
        """Salva a API key no arquivo de configuração"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'api_key': api_key}, f)
        except Exception as e:
            print(f"Erro ao salvar API key: {e}")
    
    def criar_interface(self):
        # Frame para API Key
        frame_api = tk.LabelFrame(self.root, text="Configuração da API", padx=10, pady=10)
        frame_api.pack(padx=10, pady=10, fill="x")
        
        tk.Label(frame_api, text="API Key Groq:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_api_key = tk.Entry(frame_api, width=50, show="*")
        self.entry_api_key.grid(row=0, column=1, padx=5, pady=5)
        self.entry_api_key.insert(0, self.api_key)
        
        btn_salvar_key = tk.Button(frame_api, text="Salvar Key", command=self.salvar_key)
        btn_salvar_key.grid(row=0, column=2, padx=5)
        
        btn_mostrar = tk.Button(frame_api, text="👁", command=self.toggle_mostrar_key)
        btn_mostrar.grid(row=0, column=3)
        
        # Frame para seleção de arquivo
        frame_arquivo = tk.LabelFrame(self.root, text="Arquivo de Áudio", padx=10, pady=10)
        frame_arquivo.pack(padx=10, pady=10, fill="x")
        
        self.label_arquivo = tk.Label(frame_arquivo, text="Nenhum arquivo selecionado", 
                                      fg="gray", wraplength=600, justify="left")
        self.label_arquivo.pack(pady=5)
        
        btn_selecionar = tk.Button(frame_arquivo, text="📁 Selecionar Arquivo de Áudio", 
                                   command=self.selecionar_arquivo, 
                                   bg="#4CAF50", fg="white", 
                                   font=("Arial", 10, "bold"),
                                   padx=20, pady=10)
        btn_selecionar.pack(pady=5)
        
        # Informação sobre compressão automática
        info_label = tk.Label(frame_arquivo, 
                             text="💡 Arquivos > 25MB são comprimidos automaticamente:\n"
                                  "• WAV/AIFF → FLAC 16KHz (lossless)\n"
                                  "• MP3/M4A/OGG → OPUS 32kbps 16KHz (otimizado para voz)",
                             fg="gray", wraplength=600, justify="left", font=("Arial", 8))
        info_label.pack(pady=5)
        
        # Botão de transcrever
        self.btn_transcrever = tk.Button(self.root, text="🎤 Transcrever Áudio", 
                                        command=self.transcrever,
                                        bg="#2196F3", fg="white",
                                        font=("Arial", 12, "bold"),
                                        padx=30, pady=15,
                                        state="disabled")
        self.btn_transcrever.pack(pady=10)
        
        # Frame para resultado
        frame_resultado = tk.LabelFrame(self.root, text="Transcrição", padx=10, pady=10)
        frame_resultado.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.texto_resultado = scrolledtext.ScrolledText(frame_resultado, 
                                                         wrap=tk.WORD, 
                                                         height=15,
                                                         font=("Arial", 10))
        self.texto_resultado.pack(fill="both", expand=True)
        
        # Botão para copiar resultado
        btn_copiar = tk.Button(frame_resultado, text="📋 Copiar Transcrição", 
                              command=self.copiar_resultado)
        btn_copiar.pack(pady=5)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Pronto", 
                                     bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.arquivo_selecionado = None
    
    def toggle_mostrar_key(self):
        """Alterna entre mostrar e ocultar a API key"""
        if self.entry_api_key.cget('show') == '*':
            self.entry_api_key.config(show='')
        else:
            self.entry_api_key.config(show='*')
    
    def salvar_key(self):
        """Salva a API key digitada"""
        api_key = self.entry_api_key.get().strip()
        if api_key:
            self.salvar_api_key(api_key)
            self.api_key = api_key
            messagebox.showinfo("Sucesso", "API Key salva com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Digite uma API Key válida")
    
    def selecionar_arquivo(self):
        """Abre diálogo para selecionar arquivo de áudio"""
        filetypes = (
            ('Arquivos de áudio', '*.mp3 *.wav *.m4a *.ogg *.flac *.webm'),
            ('Todos os arquivos', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Selecione o arquivo de áudio',
            filetypes=filetypes
        )
        
        if filename:
            self.arquivo_selecionado = filename
            tamanho_mb = os.path.getsize(filename) / (1024 * 1024)
            info_arquivo = f"Arquivo: {os.path.basename(filename)} ({tamanho_mb:.1f} MB)"
            self.label_arquivo.config(text=info_arquivo, fg="black")
            self.btn_transcrever.config(state="normal")
            self.status_label.config(text=f"Arquivo selecionado: {filename}")
    
    def comprimir_audio(self, arquivo_path):
        """Comprime o arquivo de áudio para formato otimizado baseado no tipo original"""
        try:
            self.status_label.config(text="Analisando e comprimindo áudio... Por favor, aguarde...")
            self.root.update()
            
            # Procura ffmpeg
            ffmpeg_cmd = self.encontrar_ffmpeg()
            
            if not ffmpeg_cmd:
                raise Exception(
                    "FFmpeg não encontrado!\n\n"
                    "Para usar a compressão, você precisa:\n"
                    "1. Criar o executável (.exe) que já vem com ffmpeg incluído:\n"
                    "   python criar_executavel.py\n\n"
                    "OU\n\n"
                    "2. Baixar o ffmpeg manualmente de: https://www.gyan.dev/ffmpeg/builds/\n"
                    "3. Adicionar ao PATH do Windows\n"
                    "4. Reiniciar o VSCode"
                )
            
            # Detecta extensão do arquivo
            extensao = os.path.splitext(arquivo_path)[1].lower()
            
            # Define formato de saída e codec baseado no tipo de entrada
            # WAV/FLAC/AIFF (não comprimidos) -> FLAC (lossless)
            # MP3/M4A/OGG/AAC (já comprimidos) -> OPUS (mais eficiente)
            if extensao in ['.wav', '.aiff', '.aif']:
                # Arquivos não comprimidos: usar FLAC
                output_ext = '.flac'
                codec = 'flac'
                extra_params = []
                tipo_compressao = "FLAC 16KHz mono"
            else:
                # Arquivos já comprimidos: usar OPUS
                output_ext = '.opus'
                codec = 'libopus'
                extra_params = ['-b:a', '32k']  # 32kbps é ótimo para voz a 16KHz
                tipo_compressao = "OPUS 32kbps 16KHz mono"
            
            # Cria arquivo temporário
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=output_ext)
            temp_path = temp_file.name
            temp_file.close()
            
            # Comando ffmpeg para comprimir
            # -ar 16000: 16KHz sample rate (otimizado para voz)
            # -ac 1: mono (1 canal)
            cmd = [
                ffmpeg_cmd,
                '-i', arquivo_path,           # Arquivo de entrada
                '-ar', '16000',               # 16KHz sample rate
                '-ac', '1',                   # Mono
                '-map', '0:a',                # Mapear apenas áudio
            ]
            
            # Adiciona codec e parâmetros específicos
            cmd.extend(['-c:a', codec])
            cmd.extend(extra_params)
            cmd.extend(['-y', temp_path])     # Sobrescrever e arquivo de saída
            
            self.status_label.config(text=f"Comprimindo para {tipo_compressao}...")
            self.root.update()
            
            # Executa o comando
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # Timeout de 5 minutos
            )
            
            if result.returncode != 0:
                raise Exception(f"Erro do ffmpeg: {result.stderr}")
            
            # Verifica se o arquivo foi criado
            if not os.path.exists(temp_path):
                raise Exception("Arquivo comprimido não foi criado")
            
            tamanho_original = os.path.getsize(arquivo_path) / (1024 * 1024)
            tamanho_comprimido = os.path.getsize(temp_path) / (1024 * 1024)
            reducao_percent = ((tamanho_original - tamanho_comprimido) / tamanho_original) * 100
            
            self.status_label.config(
                text=f"Compressão concluída: {tamanho_original:.1f}MB → {tamanho_comprimido:.1f}MB ({reducao_percent:.0f}% de redução)"
            )
            
            return temp_path
            
        except subprocess.TimeoutExpired:
            raise Exception("Tempo esgotado durante a compressão. Arquivo muito grande?")
        except Exception as e:
            raise Exception(f"Erro ao comprimir áudio: {str(e)}")
    
    def transcrever(self):
        """Envia o áudio para transcrição"""
        api_key = self.entry_api_key.get().strip()
        
        if not api_key:
            messagebox.showerror("Erro", "Por favor, insira sua API Key do Groq!")
            return
        
        if not self.arquivo_selecionado:
            messagebox.showerror("Erro", "Por favor, selecione um arquivo de áudio!")
            return
        
        # Desabilita botão durante o processamento
        self.btn_transcrever.config(state="disabled")
        self.status_label.config(text="Processando... Por favor, aguarde...")
        self.root.update()
        
        arquivo_para_enviar = self.arquivo_selecionado
        arquivo_temporario = None
        
        try:
            # Verifica tamanho do arquivo
            tamanho_bytes = os.path.getsize(self.arquivo_selecionado)
            tamanho_mb = tamanho_bytes / (1024 * 1024)
            limite_mb = 25  # Limite da API Groq para free tier
            
            # Se arquivo for maior que 25MB, comprime
            if tamanho_mb > limite_mb:
                self.status_label.config(
                    text=f"Arquivo grande ({tamanho_mb:.1f}MB). Comprimindo automaticamente..."
                )
                self.root.update()
                
                arquivo_temporario = self.comprimir_audio(self.arquivo_selecionado)
                arquivo_para_enviar = arquivo_temporario
                
                # Verifica se ainda está muito grande após compressão
                tamanho_comprimido = os.path.getsize(arquivo_para_enviar) / (1024 * 1024)
                if tamanho_comprimido > limite_mb:
                    messagebox.showwarning(
                        "Arquivo ainda grande",
                        f"Mesmo após compressão, o arquivo tem {tamanho_comprimido:.1f}MB.\n"
                        f"O limite da API Groq (free tier) é 25MB.\n\n"
                        f"Sugestões:\n"
                        f"1. Use um arquivo de áudio mais curto\n"
                        f"2. Considere fazer upgrade para dev tier (limite 100MB)\n"
                        f"3. Divida o áudio em partes menores"
                    )
                    return
            
            # Envia para API
            self.status_label.config(text="Enviando para transcrição... Por favor, aguarde...")
            self.root.update()
            
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            with open(arquivo_para_enviar, "rb") as audio_file:
                files = {
                    "file": (os.path.basename(self.arquivo_selecionado), audio_file)
                }
                
                data = {
                    "model": "whisper-large-v3"
                }
                
                # Desabilita verificação SSL (resolve problemas com certificados corporativos)
                response = requests.post(url, headers=headers, files=files, data=data, verify=False)
            
            if response.status_code == 200:
                transcricao = response.json()["text"]
                self.texto_resultado.delete(1.0, tk.END)
                self.texto_resultado.insert(1.0, transcricao)
                self.status_label.config(text="Transcrição concluída com sucesso!")
                messagebox.showinfo("Sucesso", "Áudio transcrito com sucesso!")
            else:
                erro = response.json().get('error', {}).get('message', 'Erro desconhecido')
                messagebox.showerror("Erro na API", f"Erro: {erro}")
                self.status_label.config(text=f"Erro: {response.status_code}")
                
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo não encontrado!")
            self.status_label.config(text="Erro: Arquivo não encontrado")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Erro ao conectar com a API: {str(e)}")
            self.status_label.config(text="Erro de conexão")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
            self.status_label.config(text=f"Erro: {str(e)}")
        finally:
            # Limpa arquivo temporário se foi criado
            if arquivo_temporario and os.path.exists(arquivo_temporario):
                try:
                    os.unlink(arquivo_temporario)
                except:
                    pass
            
            self.btn_transcrever.config(state="normal")
    
    def copiar_resultado(self):
        """Copia o texto da transcrição para a área de transferência"""
        texto = self.texto_resultado.get(1.0, tk.END).strip()
        if texto:
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            messagebox.showinfo("Copiado", "Transcrição copiada para a área de transferência!")
        else:
            messagebox.showwarning("Aviso", "Não há texto para copiar!")

def main():
    root = tk.Tk()
    app = TranscritorAudio(root)
    root.mainloop()

if __name__ == "__main__":
    main()