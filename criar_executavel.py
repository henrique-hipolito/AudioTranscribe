# Script para criar o executável
# Execute este arquivo para gerar o .exe

import subprocess
import sys
import os
import urllib.request
import zipfile
import shutil

print("=" * 60)
print("CRIADOR DE EXECUTÁVEL - Transcritor de Áudio")
print("=" * 60)
print()

# Verifica se o PyInstaller está instalado
print("Verificando dependências...")
try:
    import PyInstaller
    print("✓ PyInstaller encontrado!")
except ImportError:
    print("✗ PyInstaller não encontrado. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✓ PyInstaller instalado com sucesso!")

# Verifica se o ffmpeg-python está instalado
try:
    import ffmpeg
    print("✓ ffmpeg-python encontrado!")
except ImportError:
    print("✗ ffmpeg-python não encontrado. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ffmpeg-python"])
    print("✓ ffmpeg-python instalado com sucesso!")

print()
print("Baixando ffmpeg...")
print("(Necessário para compressão de áudio)")
print()

# Diretório temporário para ffmpeg
ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg_bin")
os.makedirs(ffmpeg_dir, exist_ok=True)

# URL do ffmpeg (versão essentials do Windows)
ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
ffmpeg_zip = os.path.join(ffmpeg_dir, "ffmpeg.zip")

# Verifica se já existe
ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe.exe")

if not os.path.exists(ffmpeg_exe):
    try:
        print("Baixando ffmpeg... (pode levar alguns minutos)")
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
        print("✓ Download concluído!")
        
        print("Extraindo ffmpeg...")
        with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
            # Encontra os arquivos ffmpeg.exe e ffprobe.exe no zip
            for file in zip_ref.namelist():
                if file.endswith('ffmpeg.exe') or file.endswith('ffprobe.exe'):
                    # Extrai direto para ffmpeg_bin
                    filename = os.path.basename(file)
                    source = zip_ref.open(file)
                    target = open(os.path.join(ffmpeg_dir, filename), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
        
        os.remove(ffmpeg_zip)
        print("✓ ffmpeg extraído com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao baixar ffmpeg: {e}")
        print("Por favor, baixe manualmente de: https://ffmpeg.org/download.html")
        input("\nPressione ENTER para continuar sem ffmpeg (não funcionará para arquivos grandes)...")
        ffmpeg_dir = None
else:
    print("✓ ffmpeg já existe!")

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
]

# Adiciona ffmpeg se foi baixado
if ffmpeg_dir and os.path.exists(ffmpeg_exe):
    comando.extend([
        f"--add-binary={ffmpeg_exe};.",
        f"--add-binary={ffprobe_exe};.",
    ])
    print("✓ ffmpeg será incluído no executável")

comando.append("transcritor_audio.py")

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
    print("RECURSOS INCLUÍDOS:")
    print("✓ Compressão automática de arquivos grandes")
    print("✓ Seletor de qualidade (64kbps / 128kbps)")
    print("✓ ffmpeg embutido (funciona em qualquer PC)")
    print()
    
except subprocess.CalledProcessError as e:
    print(f"✗ Erro ao criar executável: {e}")
    print()
    print("Tente executar manualmente:")
    print("pyinstaller --onefile --windowed --name=TranscritorAudio transcritor_audio.py")

# Limpa pasta temporária do ffmpeg
if ffmpeg_dir and os.path.exists(ffmpeg_dir):
    try:
        shutil.rmtree(ffmpeg_dir)
        print("Arquivos temporários removidos.")
    except:
        pass

input("\nPressione ENTER para fechar...")