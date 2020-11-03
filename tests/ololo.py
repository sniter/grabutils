import abc
import io
import logging
import multiprocessing as mp
from pathlib import Path

from PIL import Image, ImageOps
from tqdm import tqdm


class CompressorAbc(abc.ABC):
    @abc.abstractmethod
    def params(self) -> dict:
        """Save with compression settings"""


class ImageConverter:
    transparent_color = 255, 255, 255

    def __init__(self, img: Image):
        self.img = img

    @classmethod
    def from_bytes(cls, raw: bytes) -> "ImageConverter":
        return cls(Image.open(io.BytesIO(raw)))

    def scale(self, min_size: int, inplace: bool = False, resample: int = Image.LANCZOS) -> "ImageConverter":
        img = self.img
        if min(img.size) > min_size:
            img = ImageOps.scale(img, min_size / min(img.size), resample=resample)
        if inplace:
            self.img = img
            return self
        return self.__class__(img)

    def to_rgb(self, inplace: bool = False) -> "ImageConverter":
        img = self.img
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, self.transparent_color)
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            # img.mode == "P":
            img = self.img.convert("RGB")

        if inplace:
            self.img = img
            return self
        return self.__class__(img)

    def to_bytes(self, compressor: CompressorAbc) -> bytes:
        raw = io.BytesIO()
        self.img.save(raw, **compressor.params())
        return raw.getvalue()

    def to_file(self, file: str or io.BufferedIOBase, compressor: CompressorAbc):
        self.img.save(file, **compressor.params())


class JpegCompressor(CompressorAbc):

    def __init__(self, **kwargs):
        self.format = kwargs.get('format', "JPEG")
        self.dpi = kwargs.get("dpi", (72, 72))
        self.progression = kwargs.get("progression", True)
        self.quality = kwargs.get("quality", 70)
        self.optimize = kwargs.get("optimize", True)
        self.progressive = kwargs.get("progressive", True)

    def params(self) -> dict:
        return dict(
            format=self.format,
            dpi=self.dpi,
            progression=self.progression,
            quality=self.quality,
            optimize=self.optimize,
            progressive=self.progressive
        )


def compare_images(img_file: Path, min_size: int = 700, quality: int = 70) -> tuple:
    try:
        jpeg = JpegCompressor(quality=quality)
        initial_length = Path(img_file).stat().st_size

        im = Image.open(io.BytesIO(img_file.read_bytes()))
        print(f'MODE: {im.mode}')
        # print(f'{im.split()}')

        ib = ImageConverter(im) \
            .scale(min_size=min_size, inplace=True) \
            .to_rgb(inplace=True) \
            .to_bytes(compressor=jpeg)

        return initial_length, len(ib)
    except Exception as exc:
        logging.error(f'{img_file}: {exc}')


def scan_folder(folder: Path):
    for obj in folder.iterdir():
        if obj.is_dir():
            continue
        if obj.name in ('.DS_Store', ):
            continue

        old_size, new_size = compare_images(obj)
        compression = (old_size - new_size) / old_size * 100
        print(f"{obj.relative_to(folder)} {old_size} --> {new_size} / {compression:.2f}%")

scan_folder(Path('/Users/ilya/Downloads/ttttttt'))


def convert_images(img_file: Path, min_size: int = 700, quality: int = 70) -> Path:
    try:
        jpeg = JpegCompressor(quality=quality)
        with Image.open(img_file) as img:
            imb = ImageConverter(img)

        imb.scale(min_size=min_size, inplace=True) \
            .to_rgb(inplace=True) \
            .to_file(img_file, compressor=jpeg)

        return img_file
    except Exception as exc:
        raise Exception(f"{img_file} error {exc}") from exc


def convert_images_master(logfile: str, base_path: Path, processes=None):
    with mp.Pool(processes=processes) as pool:
        with open(logfile, 'r') as files:
            fn_args = (
                base_path.joinpath(file.strip())
                for file in files
            )
            it = pool.imap_unordered(convert_images, fn_args)
            with open(logfile + '.progress', 'w') as log:
                for result in tqdm(it, desc='Converting images'):
                    log.write(str(result) + "\n")
