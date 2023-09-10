import time
print("Willkommen beim Videokonverter von Elias")
time.sleep(2)

print("Notwendige Pakete werden installiert und/oder geprüft")
print()
print()
from pip._internal import main as pipmain
pipmain(['install', 'asyncio'])
pipmain(['install', 'ffmpeg'])
pipmain(['install', 'easygui'])

import asyncio
from ffmpeg import Progress
from ffmpeg.asyncio import FFmpeg
import easygui

print()
print()

Codecs = ["libsvtav1", "av1_nvenc", "libx265"]
Codec_Ausgewählt = easygui.choicebox("Bitte wählen sie einen Codec", "Codec wählen", choices=["AV1", "AV1-NVENC", "HEVC"])
print("Sie haben " + Codec_Ausgewählt + " ausgewählt")
if Codec_Ausgewählt == "AV1":
    Codec_Ausgewählt = Codecs[0]
elif Codec_Ausgewählt == "AV1-NVENC":
    Codec_Ausgewählt = Codecs[1]
else:
    Codec_Ausgewählt = Codecs[2]

B_Frames = "7"
Komprimierer = "crf"
Komprimierer_Einstellung = "veryslow"

if Codec_Ausgewählt != "av1_nvenc":
    B_Frames = "16"
    Komprimierer = "crf"
    Komprimierer_Einstellung = "0"

Speicher_Pfad = easygui.diropenbox("Bitte Ordner auswählen, in dem die Videos gespeichert werden sollen") + "\\"
Dateien = easygui.fileopenbox("Bitte ein oder mehrere Videos auswählen",  multiple=True)
Dateien_Anzahl = 0
print()
print()

while Dateien_Anzahl < len(Dateien):
    import subprocess
    print(Dateien[Dateien_Anzahl])
    Datei_Split = str(Dateien[Dateien_Anzahl]).split("\\")


    print("Frameanzahl wird berechnet...")
    Video_Sekunden = float(subprocess.check_output('ffprobe -i "' + Dateien[Dateien_Anzahl] + '" -show_entries format=duration -v quiet -of csv="p=0"'))
    Video_FPS_roh = str(subprocess.check_output('ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate "' + Dateien[Dateien_Anzahl] + '"'))
    Video_FPS_split_str = Video_FPS_roh.split("/")
    Video_FPS_split_Zahl1 = Video_FPS_split_str[0].split("'")
    Video_FPS_split_Zahl2 = Video_FPS_split_str[1].split("\\")
    Video_FPS = float(Video_FPS_split_Zahl1[1]) / float(Video_FPS_split_Zahl2[0])
    Frames = int(Video_Sekunden * Video_FPS)


    async def ffmpeg():
        ffmpeg = (
            FFmpeg()
            .input(Dateien[Dateien_Anzahl])
            .output(
                Speicher_Pfad + Datei_Split[-1],
                {"vcodec": Codec_Ausgewählt, "codec:a": "aac", Komprimierer: Komprimierer_Einstellung, "bf": B_Frames, "rc": "vbr_hq", "b:v": "0", "b:a": "0", "tier": "high"}
                #av1_nvenc kann nur bf=7
            )
            .option("y")
        )

        @ffmpeg.on("progress")
        async def on_progress(progress: Progress):
            await asyncio.sleep(1)
            Prozent = int((int(progress.frame) / Frames) * 100)
            if (int(progress.fps) > 0):
                Sekunden = int((Frames - int(progress.frame)) / int(progress.fps))

                Minuten = 0
                Zwischen = Sekunden / 60
                while True:
                    if 1 < Zwischen:
                        Zwischen = Zwischen - 1
                        Minuten = Minuten + 1
                    else:
                        break

                if progress.size/1024 < 10000:
                    print(str(Prozent) + "%, " + (str(Minuten) + "m " + str(int(Zwischen * 60)) + "s") + ", " + str(progress.bitrate) + "kbit/s", str(int(progress.size / 1024)) + "KB, " + "Wahrscheinliche Größe: " + str(float(round((((Frames / progress.frame) * progress.size) / 1024) / 1024, 1))) + "MB")

                else:
                    print(str(Prozent) + "%, " + (str(Minuten) + "m " + str(int(Zwischen * 60)) + "s") + ", " + str(progress.bitrate) + "kbit/s", str(float(round((progress.size / 1024)/1024, 1))) + "MB, " + "Wahrscheinliche Größe: " + str(float(round((((Frames / progress.frame) * progress.size) / 1024) / 1024, 1))) + "MB")

            else:
                print("Startet...")

        @ffmpeg.on("completed")
        def on_completed():
            print("Fertig")

        await ffmpeg.execute()


    if __name__ == "__main__":
        asyncio.run(ffmpeg())
    Dateien_Anzahl = Dateien_Anzahl + 1