import os
import shutil
from pathlib import Path
from pdf2image import convert_from_path


class PdfController:
    __pdf_path = None
    __pdf_file = None
    __POPPLER_PATH = None

    def __init__(self):
        self.__POPPLER_PATH = Path(__file__).parent.absolute() / "poppler/bin"
        os.environ["PATH"] += os.pathsep + str(self.__POPPLER_PATH)

        # tmpが存在しなければ作成
        os.makedirs("./tmp", exist_ok=True)

        pass

    def convertToImage(self, file_path):
        """PDFを読み込んで画像に変換する

        Args:
            file_path(str): 読み込むPDFのパス

        Returns:
            list[str]: 生成した画像のパスのlist

        """
        self.__pdf_path = Path("./" + file_path)
        self.__pdf_file = convert_from_path(str(self.__pdf_path), 150)
        image_dir = Path("./tmp")
        image_path_list = []

        for i, page in enumerate(self.__pdf_file):
            file_name = self.__pdf_path.stem + "_{:02d}".format(i + 1) + ".jpeg"
            image_path = image_dir / file_name
            page.save(str(image_path), "JPEG")
            image_path_list.append(str(image_path))

        return image_path_list

    def __del__(self):
        shutil.rmtree("./tmp")
