import re
from datetime import timedelta

def parse_timestamp(ts: str) -> timedelta:

    ts = ts.replace('.', ',')  # unify separator
    parts = ts.split(',')
    if len(parts) != 2:
        raise ValueError(f"Invalid timestamp format: {ts}")
    ms = int(parts[1])
    time_part = parts[0].split(':')
    time_part = [int(x) for x in time_part]
    if len(time_part) == 3:  # HH:MM:SS
        hh, mm, ss = time_part
    elif len(time_part) == 2:  # MM:SS
        hh = 0
        mm, ss = time_part
    elif len(time_part) == 1:  # SS
        hh = 0
        mm = 0
        ss = time_part[0]
    else:
        raise ValueError(f"Unsupported timestamp: {ts}")
    return timedelta(hours=hh, minutes=mm, seconds=ss, milliseconds=ms)

def format_timestamp(td: timedelta, use_vtt=False) -> str:
    total_seconds = int(td.total_seconds())
    ms = td.microseconds // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if use_vtt:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"

def shift_subtitles(file_in, file_out, shift_minutes=0, shift_seconds=0, shift_milliseconds=0, direction="later"):

    total_shift = timedelta(minutes=shift_minutes, seconds=shift_seconds, milliseconds=shift_milliseconds)
    if direction == "earlier":
        total_shift = -total_shift

    use_vtt = file_in.lower().endswith('.vtt')

    # Regex to match timestamps like 00:16.880 or 00:16,880
    ts_pattern = re.compile(r'\d{1,2}(?::\d{2}){0,2}[.,]\d{1,3}')

    with open(file_in, 'r', encoding='utf-8') as f:
        content = f.read()

    def repl(m):
        td = parse_timestamp(m.group(0))
        td_new = td + total_shift
        if td_new.total_seconds() < 0:
            td_new = timedelta(0)
        return format_timestamp(td_new, use_vtt)

    new_content = ts_pattern.sub(repl, content)

    with open(file_out, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Subtitles shifted {direction} by {shift_minutes} min, {shift_seconds} sec, {shift_milliseconds} ms.")
    print(f"Output saved to: {file_out}")


# ---------------- Example Usage ----------------
# Shift VTT 10 seconds and 250 milliseconds later
shift_subtitles('Watch Demon Slayer- Kimetsu no Yaiba Infinity Castle English.srt', 'output.srt', shift_seconds=10, shift_milliseconds=00, direction='earlier')

# Shift SRT 5 seconds and 500 milliseconds earlier
# shift_subtitles('example.srt', 'output.srt', shift_seconds=5, shift_milliseconds=500, direction='earlier')
