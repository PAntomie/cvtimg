#!/bin/python3

import os
import shutil
import zipfile
import argparse
from pathlib import Path
from PIL import Image
import tempfile

def convert_image(input_path, output_path, target_width, target_height):
    try:
        with Image.open(input_path) as img:
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            orig_width, orig_height = img.size
            target_img = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
            paste_x = 0
            paste_y = 0
            if target_width > orig_width and target_height > orig_height:
                target_img.paste(img, (paste_x, paste_y))
            else:
                ratio = min(target_width / orig_width, target_height / orig_height)
                new_width = int(orig_width * ratio)
                new_height = int(orig_height * ratio)
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                target_img.paste(resized_img, (paste_x, paste_y))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            target_img.save(output_path, "PNG")
            print(f"已转换: {input_path} -> {output_path}")
    except Exception as e:
        print(f"无法转换 {input_path}: {str(e)}")


def process_directory(input_dir, output_dir, target_width, target_height):
    for item in input_dir.iterdir():
        relative_path = item.relative_to(input_dir)
        output_path = output_dir / relative_path
        if item.is_dir():
            process_directory(item, output_path, target_width, target_height)
        elif item.is_file():
            if item.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']:
                output_path = output_path.with_suffix('.png')
                convert_image(item, output_path, target_width, target_height)
            elif item.suffix.lower() == '.zip':
                process_zip_file(item, output_path, target_width, target_height)


def process_zip_file(zip_path, output_zip_path, target_width, target_height):
    try:
        with tempfile.TemporaryDirectory() as temp_extract, tempfile.TemporaryDirectory() as temp_output:
            temp_extract_path = Path(temp_extract)
            temp_output_path = Path(temp_output)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_path)
            process_directory(temp_extract_path, temp_output_path, target_width, target_height)
            output_zip_path.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(output_zip_path, 'w') as new_zip:
                for root, _, files in os.walk(temp_output_path):
                    for file in files:
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(temp_output_path)
                        new_zip.write(file_path, arcname=rel_path)
    except Exception as e:
        print(f"无法处理此 ZIP {zip_path}: {str(e)}")


def clear_directory(directory):
    for item in directory.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def main(target_width, target_height):
    base_dir = Path.cwd()
    input_dir = base_dir / "import"
    output_dir = base_dir / "export"
    if not input_dir.exists():
        input_dir.mkdir()
        print(f"创建输入文件夹: {input_dir}")
        return
    output_dir.mkdir(exist_ok=True)
    process_directory(input_dir, output_dir, target_width, target_height)
    clear_directory(input_dir)
    print("完成")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量转换图片到指定分辨率PNG格式")
    parser.add_argument("width", type=int, help="目标宽度（像素）")
    parser.add_argument("height", type=int, help="目标高度（像素）")
    args = parser.parse_args()
    print("开始转换")
    main(args.width, args.height)