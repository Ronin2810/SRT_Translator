import re
import streamlit as st
from googletrans import Translator
from io import StringIO

def translate_text(text, source_language='hi', target_language='mr'):
    translator = Translator()
    translated = translator.translate(text, src=source_language, dest=target_language)
    return translated.text

def translate_srt_content(content, source_language='hi', target_language='mr'):
    lines = content.split('\n')
    translated_lines = []
    subtitle_block = []
    total_blocks = sum(1 for line in lines if re.match(r'^\d+$', line.strip()))
    current_block = 0

    progress_bar = st.progress(0)  # Initialize progress bar

    for line in lines:
        if line.strip() == "":
            # End of a subtitle block
            if subtitle_block:
                current_block += 1
                index, timestamp, subtitle_text = subtitle_block
                translated_text = translate_text(subtitle_text.strip(), source_language, target_language)
                translated_lines.append(index)
                translated_lines.append(timestamp)
                translated_lines.append(translated_text + "\n\n")
                subtitle_block = []

                # Update progress bar
                progress_bar.progress(current_block / total_blocks)
                st.write(f"Translated {current_block}/{total_blocks} subtitle blocks")

        else:
            if re.match(r'^\d+$', line.strip()):  # Index line
                if subtitle_block:
                    current_block += 1
                    index, timestamp, subtitle_text = subtitle_block
                    translated_text = translate_text(subtitle_text.strip(), source_language, target_language)
                    translated_lines.append(index)
                    translated_lines.append(timestamp)
                    translated_lines.append(translated_text + "\n\n")
                subtitle_block = [line, "", ""]
            elif re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line.strip()):  # Timestamp line
                subtitle_block[1] = line
            else:  # Subtitle text
                subtitle_block[2] += line

    # Handle the last subtitle block if any
    if subtitle_block:
        current_block += 1
        index, timestamp, subtitle_text = subtitle_block
        translated_text = translate_text(subtitle_text.strip(), source_language, target_language)
        translated_lines.append(index)
        translated_lines.append(timestamp)
        translated_lines.append(translated_text + "\n\n")
        progress_bar.progress(current_block / total_blocks)
        st.write(f"Translated {current_block}/{total_blocks} subtitle blocks")

    progress_bar.progress(1.0)  # Ensure the progress bar is 100% when done

    return ''.join(translated_lines)

st.title('SRT File Translator')
st.write('Upload an SRT file to translate it from Hindi to Marathi.')

uploaded_file = st.file_uploader("Choose an SRT file...", type="srt")

if uploaded_file is not None:
    content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    st.write('File uploaded successfully.')

    if st.button('Translate to Marathi'):
        translated_content = translate_srt_content(content)
        st.write('Translation completed.')

        # Provide a download link
        st.download_button(
            label="Download Translated SRT",
            data=translated_content,
            file_name='Marathi_Translation.srt',
            mime='text/plain',
        )
