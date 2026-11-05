"""Ekspor akhir: python tools/export.py out/video.mp4 <folder_tujuan> <NamaVideo>
SATU file <NamaVideo>_1080x1920.mp4 (potret, IG/TikTok/FB) atau <NamaVideo>_1920x1080.mp4 (lanskap, YouTube/FB): H.264 high, 30 fps, maks 12 Mbps, AAC 48 kHz, -14 LUFS, faststart."""
import sys, os, subprocess
src, dst, name = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(dst, exist_ok=True)
w, h = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src]).decode().split(',')[:2]
out = os.path.join(dst, f'{name}_{w.strip()}x{h.strip()}.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-profile:v', 'high', '-level', '4.1',
                '-pix_fmt', 'yuv420p', '-r', '30', '-maxrate', '12M', '-bufsize', '24M', '-movflags', '+faststart',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', out], check=True)
print('selesai ->', out)
