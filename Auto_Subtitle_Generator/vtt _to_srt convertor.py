def vtt_to_srt(vtt_file, srt_file):
    with open(vtt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    srt_lines = []
    counter = 1

    for line in lines:
        line = line.strip()

        # Skip the WEBVTT header or metadata
        if line.startswith("WEBVTT") or line == "" or line.startswith("NOTE"):
            continue

        # Convert time format from "00:01:03.120 --> 00:01:44.704" to "00:01:03,120 --> 00:01:44,704"
        if "-->" in line:
            line = line.replace('.', ',')
            srt_lines.append(str(counter))
            counter += 1
            srt_lines.append(line)
        else:
            srt_lines.append(line)

        # Add newline spacing
        if line == "":
            srt_lines.append("")

    # Ensure blank lines between subtitle blocks
    srt_output = "\n".join(srt_lines).replace("\n\n\n", "\n\n")

    with open(srt_file, 'w', encoding='utf-8') as f:
        f.write(srt_output)

    print(f"✅ Converted '{vtt_file}' → '{srt_file}' successfully!")


# Example usage:
vtt_to_srt("Watch Demon Slayer- Kimetsu no Yaiba Infinity Castle English.vtt", "output.srt")
