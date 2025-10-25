import sys
from pathlib import Path
import os # Добавим модуль os для работы с путями

# Используем pdfminer.six — отлично тянет именно текстовые PDF
try:
    from pdfminer.high_level import extract_text
except ImportError:
    print("Требуется пакет pdfminer.six. Установите: pip install pdfminer.six")
    sys.exit(1)

def pdf_to_txt(pdf_path: Path, txt_path: Path) -> None:
    # extract_text вернёт Unicode-строку; пишем в UTF-8 с BOM для корректного
    # отображения в Блокноте (Windows Notepad)
    text = extract_text(str(pdf_path))
    # Если текста нет (например, скан без OCR), сохраняем пустой файл с пометкой
    if not text.strip():
        text = ("[Hinweis] Die PDF-Datei scheint keinen extrahierbaren Text zu enthalten "
                "(möglicherweise ein gescanntes Bild ohne OCR).\n")
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(txt_path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(text)

def main():
    if len(sys.argv) < 2:
        print("Использование: python pdf_to_txt.py <входная_папка_или_файл.pdf> [выходная_папка]")
        sys.exit(1)

    input_arg = Path(sys.argv[1]).expanduser().resolve()
    output_dir = None

    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2]).expanduser().resolve()
        if not output_dir.is_dir():
            print(f"Ошибка: '{output_dir}' не является папкой.")
            sys.exit(1)

    if input_arg.is_dir():
        # Если указана папка, итерируемся по всем PDF-файлам в ней
        print(f"Обработка PDF-файлов из папки: {input_arg}")
        for pdf_file in input_arg.glob("*.pdf"):
            # Определяем путь для сохранения txt файла
            if output_dir:
                txt_path = output_dir / pdf_file.with_suffix(".txt").name
            else:
                txt_path = pdf_file.with_suffix(".txt")

            try:
                pdf_to_txt(pdf_file, txt_path)
                print(f"Готово: {txt_path}")
            except Exception as e:
                print(f"Не удалось извлечь текст из {pdf_file}: {e}")

    elif input_arg.is_file() and input_arg.suffix.lower() == ".pdf":
        # Если указан один PDF-файл
        pdf_path = input_arg
        if output_dir:
            txt_path = output_dir / pdf_path.with_suffix(".txt").name
        else:
            txt_path = pdf_path.with_suffix(".txt")

        try:
            pdf_to_txt(pdf_path, txt_path)
            print(f"Готово: {txt_path}")
        except Exception as e:
            print(f"Не удалось извлечь текст из {pdf_path}: {e}")
            sys.exit(1)
    else:
        print("Ошибка: укажите существующий PDF-файл или папку с PDF-файлами.")
        sys.exit(1)

if __name__ == "__main__":
    main()