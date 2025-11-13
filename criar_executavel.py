# Script para criar o executável
# Execute este arquivo para gerar o .exe

import subprocess
import sys

print("=" * 60)
print("CRIADOR DE EXECUTÁVEL - Transcritor de Áudio")
print("=" * 60)
print()

# Verifica se o PyInstaller está instalado
try:
    import PyInstaller
    print("✓ PyInstaller encontrado!")
except ImportError:
    print("✗ PyInstaller não encontrado. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✓ PyInstaller instalado com sucesso!")

print()
print("Gerando o executável...")
print("Isso pode levar alguns minutos...")
print()

# Comando para criar o executável
comando = [
    "pyinstaller",
    "--onefile",  # Cria um único arquivo executável
    "--windowed",  # Não mostra console (apenas a janela)
    "--name=TranscritorAudio",  # Nome do executável
    "--icon=NONE",  # Você pode adicionar um ícone .ico aqui se quiser
    "transcritor_audio.py"
]

try:
    subprocess.run(comando, check=True)
    print()
    print("=" * 60)
    print("✓ EXECUTÁVEL CRIADO COM SUCESSO!")
    print("=" * 60)
    print()
    print("O arquivo 'TranscritorAudio.exe' está na pasta 'dist'")
    print()
    print("Para criar um atalho na área de trabalho:")
    print("1. Vá até a pasta 'dist'")
    print("2. Clique com botão direito em 'TranscritorAudio.exe'")
    print("3. Selecione 'Criar atalho'")
    print("4. Arraste o atalho para a área de trabalho")
    print()
    
except subprocess.CalledProcessError as e:
    print(f"✗ Erro ao criar executável: {e}")
    print()
    print("Tente executar manualmente:")
    print("pyinstaller --onefile --windowed --name=TranscritorAudio transcritor_audio.py")

input("\nPressione ENTER para fechar...")
