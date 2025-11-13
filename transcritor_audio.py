import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
import os
from pathlib import Path
import json

class TranscritorAudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcritor de Áudio - Groq API")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Arquivo de configuração para salvar a API key
        self.config_file = Path.home() / ".transcritor_config.json"
        self.api_key = self.carregar_api_key()
        
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
            self.label_arquivo.config(text=f"Arquivo: {os.path.basename(filename)}", fg="black")
            self.btn_transcrever.config(state="normal")
            self.status_label.config(text=f"Arquivo selecionado: {filename}")
    
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
        self.status_label.config(text="Transcrevendo... Por favor, aguarde...")
        self.root.update()
        
        try:
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            with open(self.arquivo_selecionado, "rb") as audio_file:
                files = {
                    "file": (os.path.basename(self.arquivo_selecionado), audio_file)
                }
                
                data = {
                    "model": "whisper-large-v3"
                }
                
                response = requests.post(url, headers=headers, files=files, data=data)
            
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
