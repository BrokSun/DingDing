import easyocr

class Recognizer:
    def __init__(self, use_gpu=False):
        self.model = easyocr.Reader(["ch_sim", "en"], gpu=use_gpu)
    
    def read_text(self, img_path, detail=0):
        return self.model.readtext(img_path, detail=detail)
    
    def verify_content(self, texts, s):
        for text in texts:
            if s in text:
                return True
        
        return False


if __name__ == "__main__":
    ocr = Recognizer()

    # path = "/home/fdse/result_failed.png"
    # texts = ocr.read_text(path)
    # print(texts)

    path = "/home/fdse/AndroidAutomation/sign_in_page.png"
    texts = ocr.read_text(path)
    print(texts)

    print(ocr.verify_content(texts, "上班打卡"))