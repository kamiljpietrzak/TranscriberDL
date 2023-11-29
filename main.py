import os
import csv
from tkinter import Tk, filedialog, Button, Label
import openai
from config import API_KEY #Create config.py with your api key inside
from pydub.utils import mediainfo
from PIL import Image, ImageTk
import time
import re

def choose_directory():
    folder_path = filedialog.askdirectory()
    return folder_path


def clean_transcription(text):
    return re.sub(r'.*?(swoimi słowami\?|Internet Światłowodowy\?|jej usługi\?|nie poleciałaby Pani usługę Orange\?|Swoimi słowami proszę powiedzieć.)\s*', '', text)


def transcribe_audio(file_path):
    openai.api_key=API_KEY
    with open(file_path, "rb") as audio_file:
        response = openai.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="text",
            language="pl"
        )
    print(response)
    return response


def save_to_csv(data, output_folder, mode='w'):
    output_path = os.path.join(output_folder, "nagrania.csv")
    with open(output_path, mode, newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        if mode == 'w':  # If it's a new file, write the header
            writer.writerow(['File Name', 'Transcription'])
        for row in data:
            writer.writerow(row)


def show_completion_message(processed_files_count, total_duration):
    completion_window = Tk()
    completion_window.title("Transkrypcja zakończona")

    message = f"Transkrypcja zakończona sukcesem!\n\nLiczba przetworzonych plików: {processed_files_count}\nŁączny czas trwania: {total_duration:.2f} sekund"
    completion_label = Label(completion_window, text=message)
    completion_label.pack(pady=20)

    close_button = Button(completion_window, text="Zamknij", command=completion_window.quit)
    close_button.pack(pady=20)

    completion_window.mainloop()


def main():
    folder_path = choose_directory()
    data = []
    processed_files_count = 0
    total_duration = 0

    # First loop for counting and getting total duration
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.wav'):
            full_path = os.path.join(folder_path, file_name)
            processed_files_count += 1
            file_info = mediainfo(full_path)
            try:
                total_duration += float(file_info['duration'])
            except KeyError:
                print(f"No duration information for {file_name}. Skipping...")

    # Second loop for transcribing
    transcribed_files_count = 0
    failed_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.wav'):
            full_path = os.path.join(folder_path, file_name)
            try:
                transcription = transcribe_audio(full_path)
                transcription = clean_transcription(transcription)
                data.append((file_name, transcription))
            except Exception as e:
                print(f"Error processing file {file_name}. Error message: {e}. Skipping...")
                failed_files.append(file_name)
            transcribed_files_count += 1
            # Zapisz nazwy plików z błędem do pliku
            with open(os.path.join(folder_path, "zepsute_pliki_sprawdz.txt"), "w") as f:
                 for file_name in failed_files:
                    f.write(file_name + "\n")

            # jeżeli liczba podzielna przez 3
            if transcribed_files_count % 3 == 0:
                save_mode = 'a' if transcribed_files_count > 3 else 'w'  # Append if not the first batch of 3
                save_to_csv(data, folder_path, mode=save_mode)
                data = []  # Clear the data list for the next batch
                print("czekam 5")
                time.sleep(5)  # Sleep +5sec for whisper

    # In case there are less than 3 files left at the end
    if data:
        save_to_csv(data, folder_path, mode='a')

    show_completion_message(processed_files_count, total_duration)


if __name__ == "__main__":
    window = Tk()
    # LOGO
    image = Image.open("images/DataLabLogo.png")
    image = image.resize((250, 250))
    logo = ImageTk.PhotoImage(image)
    logo_label = Label(window, image=logo)
    logo_label.pack(pady=20)
    window.title("Speech to Text")
    label = Label(window, text="Kliknij przycisk i wybierz folder gdzie umieszczone są nagrania!")
    label.pack(pady=20)
    btn = Button(window, text="Wybierz folder", command=main)
    btn.pack(pady=20)
    window.mainloop()
