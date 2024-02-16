import os

def compress_file(file_path, output_path=None):
 
  filename, extension = os.path.splitext(file_path)

  if os.name == "nt":
    output_path = output_path or filename + ".zip"
    os.system(f'7z a "{output_path}" "{file_path}"')  
    return output_path

  

file_to_compress = file_to_compress = "C:/Users/AJEES/Documents/labjava1.pdf"
compressed_file_path = compress_file(file_to_compress)
print(f"File compressed successfully: {compressed_file_path}")
