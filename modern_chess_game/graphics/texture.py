"""Modern Chess Game - Texture Management with ModernGL"""
from pathlib import Path
from PIL import Image
import moderngl
import pygame

class TextureManager:
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx
        self.textures: dict[str, moderngl.Texture] = {}
        self.surface_textures: dict[str, moderngl.Texture] = {}

    def load_piece_texture(self, name: str, filepath: Path) -> moderngl.Texture:
        """Load an RGBA PNG image and create a filtered ModernGL texture with mipmaps."""
        if name in self.textures:
            return self.textures[name]

        img = Image.open(filepath).convert("RGBA")
        size = img.size
        data = img.tobytes()

        tex = self.ctx.texture(size, 4, data)
        tex.build_mipmaps()
        tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        self.textures[name] = tex
        return tex

    def texture_from_surface(self, key: str, surface: pygame.Surface) -> moderngl.Texture:
        """Create or update a ModernGL texture from a Pygame surface (useful for text rendering)."""
        w, h = surface.get_size()
        data = pygame.image.tobytes(surface, "RGBA", False)

        if key in self.surface_textures:
            tex = self.surface_textures[key]
            if tex.size != (w, h):
                tex.release()
                tex = self.ctx.texture((w, h), 4, data)
                self.surface_textures[key] = tex
            else:
                tex.write(data)
        else:
            tex = self.ctx.texture((w, h), 4, data)
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self.surface_textures[key] = tex

        return self.surface_textures[key]

    def get(self, name: str) -> moderngl.Texture | None:
        return self.textures.get(name)

    def release_all(self):
        for tex in self.textures.values():
            tex.release()
        for tex in self.surface_textures.values():
            tex.release()
        self.textures.clear()
        self.surface_textures.clear()
