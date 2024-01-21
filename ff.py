import subprocess
import re
import os
import sys

def extract_subtitles(video_file):
    ffmpeg = "/usr/lib/jellyfin-ffmpeg/ffmpeg"

    # 检查输入参数（视频文件路径）
    if len(sys.argv) != 2:
        print("Usage: {} <video_file>".format(sys.argv[0]))
        sys.exit(1)


    # 获取视频文件信息并过滤出字幕轨信息
    print ([ffmpeg, "-i", video_file])
    result = subprocess.run([ffmpeg, "-i", video_file], capture_output=True, text=True)
    output = result.stderr
    print(output)

    map_lines = re.findall(r'Stream #0:([0-9]+)\((.*)\): Subtitle: subrip (.*?)\n', output)
    print(map_lines)

    first_stream_id = int(map_lines[0][0]) 

    for stream_id, lang, unkown in map_lines:

        # 根据第一个字幕流的stream_id调整后续的stream_id
        adjusted_stream_id = int(stream_id) - first_stream_id  

        # 设置输出字幕文件的名称
        output_subtitle_file = f"{os.path.splitext(video_file)[0]}.{lang}.srt"
        ass = f"{os.path.splitext(video_file)[0]}.{lang}.ass"

        # 提取字幕
        subprocess.run([ffmpeg, "-i", video_file, "-map", f"0:s:{adjusted_stream_id}", "-c:s", "srt", "-n", output_subtitle_file, "-loglevel", "quiet"])
        
        subprocess.run([ffmpeg, "-i", output_subtitle_file, "-n", ass])

        # 提示用户
        print(f"Extracted subtitle stream {stream_id} to {output_subtitle_file}")

if __name__ == "__main__":
    video_file = sys.argv[1]
    extract_subtitles(video_file)
