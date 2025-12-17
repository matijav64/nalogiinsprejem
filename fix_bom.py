import os
import chardet

def remove_bom_if_any(root_path):
    for dirpath, dirs, files in os.walk(root_path):
        for fname in files:
            if fname.lower().endswith('.py'):
                full = os.path.join(dirpath, fname)
                with open(full,'rb') as f:
                    data = f.read()
                enc = chardet.detect(data)['encoding']
                # BOM check:
                has_bom = data.startswith(b'\xef\xbb\xbf')
                if has_bom or (enc and enc.lower() not in ['utf-8','ascii']):
                    try:
                        text = data.decode(enc or 'utf-8','replace')
                    except:
                        text = data.decode('utf-8','replace')
                    with open(full,'wb') as fw:
                        fw.write(text.encode('utf-8'))

if __name__=='__main__':
    remove_bom_if_any(os.getcwd())
