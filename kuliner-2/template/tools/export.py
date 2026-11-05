"""Ekspor akhir: python tools/export.py out/video.mp4 <folder_tujuan> <NamaVideo>
Membuat versi IG 1080p (-14 LUFS, faststart) dan preview 720p."""
import sys, os, subprocess
src, dst, name = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(dst, exist_ok=True)
AF = 'loudnorm=I=-14:TP=-1.5:LRA=11'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-af', AF, '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', os.path.join(dst, f'{name}_final_1080p.mp4')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', 'scale=720:1280', '-c:v', 'libx264', '-preset', 'medium', '-crf', '24', '-movflags', '+faststart', '-af', AF, '-ar', '48000', '-c:a', 'aac', '-b:a', '128k', os.path.join(dst, f'{name}_preview_720p.mp4')], check=True)
print('selesai ->', dst)
