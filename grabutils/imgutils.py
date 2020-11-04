import abc
import io

from PIL import Image, ImageOps


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
