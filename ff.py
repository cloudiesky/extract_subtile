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

    pattern = r'Stream #(\d+):(\d+)\((\w+)\): Subtitle: subrip.*?title\s+: (.*?)\s+'
    map_lines_0 = re.findall(pattern, output, re.DOTALL)

    pattern = r'Stream #(\d+):(\d+)\((\w+)\): Subtitle: subrip(.*?)\n'
    map_lines_1 = re.findall(pattern, output)
    if map_lines_0 != []:
        map_lines = map_lines_0
    elif map_lines_1 != []:
        map_lines = map_lines_1
    else:
        print("no match lines")
    print(map_lines)

    first_stream_id = int(map_lines[0][1]) 

    for vid, stream_id, lang, title in map_lines:
        if map_lines == map_lines_1:
            title = "dump"
        if lang in ["eng", "chi"]:  # 只有当lang为"eng"或"chi"时才执行下面的代码
             # 根据 unkown 内容进一步确定 lang 的取值
            if lang == "chi":
                #if title in ['Simplified',"简体中文"] :
                if "Simplified" in title or "简" in title:
                    lang = "chs"
                else:
                    lang = "cht"

            # 根据第一个字幕流的stream_id调整后续的stream_id
            adjusted_stream_id = int(stream_id) - first_stream_id  

            # 设置输出字幕文件的名称
            output_subtitle_file = f"{os.path.splitext(video_file)[0]}.{lang}.srt"
            ass = f"{os.path.splitext(video_file)[0]}.{lang}.ass"

            print(f"Extracting subtitle stream {stream_id} to {ass}")

            # 提取字幕
            #result = subprocess.run([ffmpeg, "-i", video_file, "-map", f"0:s:{adjusted_stream_id}", "-c:s", "srt", "-n", output_subtitle_file, "-loglevel", "quiet"])
            result = subprocess.run([ffmpeg, "-i", video_file, "-map", f"0:s:{adjusted_stream_id}", "-c:s", "ass", "-n", ass, "-loglevel", "quiet"])
        
            #subprocess.run([ffmpeg, "-i", output_subtitle_file, "-n", ass])

            # 提示用户
            print(f"Extracted subtitle stream {stream_id} to {ass}")

def find_and_extract_subtitles(directory):
    if os.path.isdir(directory):  # 检查输入路径是否为目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith((".mp4", ".mkv", ".avi")):  # 检查文件扩展名
                    video_file = os.path.join(root, file)  # 获取视频文件的完整路径
                    extract_subtitles(video_file)  # 调用extract_subtitles函数提取字幕
    else:
        print(f"{directory} is not a valid directory.")

if __name__ == "__main__":
    video_path = sys.argv[1]
    find_and_extract_subtitles(video_path)
