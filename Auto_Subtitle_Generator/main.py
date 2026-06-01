import os
import subprocess
from vosk import Model, KaldiRecognizer
import wave
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# GUI Setup
root = tk.Tk()
root.title("Auto Subtitle Generator")
root.geometry("500x300")
root.configure(bg="#333333")

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=400)
progress_bar.pack(pady=10)

progress_label = tk.Label(root, text="Progress: 0%", font=("Arial", 12), bg="#333333", fg="white")
progress_label.pack(pady=5)

# Paths
input_file = ""
converted_file = "converted.wav"
model_path = "vosk-model-small-en-us-0.15"
results = []

def select_file():
    global input_file
    input_file = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mkv *.avi")])
    if input_file:
        messagebox.showinfo("File Selected", f"Selected file:\n{input_file}")

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def create_subtitle_chunks(results, max_length=80, min_display_time=1.0):
    subtitles = []
    current_text = []
    start_time = None

    for word in results:
        if start_time is None:
            start_time = word['start']

        current_text.append(word['word'])

        if len(' '.join(current_text)) > max_length or (word['end'] - start_time) >= min_display_time:
            end_time = word['end']
            subtitles.append({
                'start': start_time,
                'end': end_time,
                'text': ' '.join(current_text)
            })
            current_text = []
            start_time = None

    if current_text:
        end_time = results[-1]['end']
        subtitles.append({
            'start': start_time,
            'end': end_time,
            'text': ' '.join(current_text)
        })

    return subtitles

def transcribe():
    global results
    if not input_file:
        messagebox.showwarning("No File", "Please select a file first!")
        return
    
    output_srt = os.path.splitext(input_file)[0] + ".srt"

    # Step 1: Convert video to WAV
    messagebox.showinfo("Converting", f"Converting '{input_file}' to WAV...")
    subprocess.run([
        "ffmpeg", "-i", input_file, 
        "-ac", "1", "-ar", "16000", 
        "-async", "1", "-fflags", "+genpts", 
        "-y", converted_file
    ], check=True)

    # Step 2: Load Vosk Model
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    recognizer.SetWords(True)

    # Step 3: Transcribe Audio and Update Progress Bar
    results = []
    with wave.open(converted_file, "rb") as wf:
        total_frames = wf.getnframes()
        processed_frames = 0
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if 'result' in result:
                    results.extend(result['result'])

            # ✅ Update Progress Bar
            processed_frames += len(data)
            progress = (processed_frames / total_frames) * 100
            progress_var.set(progress)
            progress_label.config(text=f"Progress: {int(progress)}%")
            root.update_idletasks()

    # Step 4: Create Subtitle Chunks
    subtitles = create_subtitle_chunks(results)

    # Step 5: Write to SRT File
    if subtitles:
        with open(output_srt, "w", encoding="utf-8") as srt_file:
            for idx, sub in enumerate(subtitles, 1):
                start_time = format_time(sub['start'])
                end_time = format_time(sub['end'])

                if sub['end'] - sub['start'] < 1.0:
                    sub['end'] = sub['start'] + 1.0
                    end_time = format_time(sub['end'])

                srt_file.write(f"{idx}\n")
                srt_file.write(f"{start_time} --> {end_time}\n")
                srt_file.write(f"{sub['text']}\n\n")

        messagebox.showinfo("Success", f"Transcription saved to:\n{output_srt}")
    else:
        messagebox.showerror("Error", "No transcription generated. Possible audio issue or recognition failure.")
    
    # Step 6: Clean up
    os.remove(converted_file)
    progress_var.set(0)
    progress_label.config(text="Progress: 0%")

def exit_app():
    root.destroy()

# Buttons
btn_select = tk.Button(root, text="Select File", command=select_file, font=("Arial", 14), bg="#4CAF50", fg="black")
btn_select.pack(pady=10)

btn_transcribe = tk.Button(root, text="Transcribe", command=transcribe, font=("Arial", 14), bg="#2196F3", fg="black")
btn_transcribe.pack(pady=10)

btn_exit = tk.Button(root, text="Exit", command=exit_app, font=("Arial", 14), bg="#f44336", fg="black")
btn_exit.pack(pady=10)

# Start GUI
root.mainloop()
