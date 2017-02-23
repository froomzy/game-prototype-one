import random

import pytmx
from lxml import etree

import arcade
from arcade import load_textures

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1200


class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        super().__init__(width, height)
        self.all_sprites_list = None
        self.player_sprite = None
        self.sprite_sheet = None
        self.tile_set = None
        self.viewport_bottom = 128.0

    def load_layer(self, layer):
        for tile in layer.tiles():
            tile_sprite = arcade.Sprite()
            tile_texture_positions = tile[2][1]
            x, y = int(tile_texture_positions[0] / 64), int(tile_texture_positions[1] / 64)
            offset = y * 16 + x
            tile_sprite.append_texture(self.tile_set[int(offset)])
            tile_sprite.set_position(center_x=32 + tile[0] * 64, center_y=32 + (70 - tile[1]) * 64)
            tile_sprite.set_texture(0)
            self.all_sprites_list.append(tile_sprite)

    def load_tiles(self):
        tile_set = []
        for idx in range(1, 97):
            texture = arcade.load_texture('../assets/sprites/tiles/tile_{:0>2}.png'.format(idx))
            tile_set.append(texture)
        return tile_set

    def setup(self):
        self.all_sprites_list = arcade.SpriteList()
        sprite_coordinates = []
        with open('../assets/sprites/shipsMiscellaneous_sheet.xml') as texture_atlas:
            tree = etree.parse(texture_atlas)
            for child in list(tree.getroot()):
                sprite_coordinates.append([
                    int(child.get('x')),
                    int(child.get('y')),
                    int(child.get('width')),
                    int(child.get('height'))
                ])
        self.sprite_sheet = load_textures(
            file_name='../assets/sprites/shipsMiscellaneous_sheet.png',
            image_location_list=sprite_coordinates
        )
        tile_coordinates = []
        for y in range(0, 6):
            for x in range(0, 16):
                tile_coordinates.append([int(x * 64), int(y * 64), 64, 64])
        self.tile_set = load_textures(
            file_name='../assets/sprites/tiles_sheet.png',
            image_location_list=tile_coordinates
        )
        level = pytmx.TiledMap('../assets/levels/pim-test-3.tmx')

        self.load_layer(layer=level.get_layer_by_name('water'))
        self.load_layer(layer=level.get_layer_by_name('overlay'))
        self.load_layer(layer=level.get_layer_by_name('land'))
        self.load_layer(layer=level.get_layer_by_name('props'))

        for sprite in self.all_sprites_list:
            x = sprite.position[0]
            y = int(sprite.position[1] - self.viewport_bottom)
            sprite.set_position(center_x=x, center_y=y)
            sprite.update()

        self.player_sprite = arcade.Sprite()
        self.player_sprite.append_texture(self.sprite_sheet[85])
        self.player_sprite.set_position(center_x=400, center_y=300)
        self.player_sprite.set_texture(0)
        self.player_sprite.angle = 180

        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.AMARANTH)

    def own_scrolling(self, viewport_delta):
        for sprite in self.all_sprites_list:
            x = sprite.position[0]
            y = int(sprite.position[1] - viewport_delta)
            sprite.set_position(center_x=x, center_y=y)
            sprite.update()

    def animate(self, delta_time):
        """ Movement and game logic """

        viewport_delta = 64 * delta_time
        self.viewport_bottom = int(self.viewport_bottom + viewport_delta)

        if self.viewport_bottom > ((70 * 64) - SCREEN_HEIGHT):
            self.viewport_bottom = ((70 * 64) - SCREEN_HEIGHT)

        self.own_scrolling(viewport_delta)
        self.player_sprite.update()

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.all_sprites_list.draw()
        self.player_sprite.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE and not (modifiers & ~(arcade.key.MOD_NUMLOCK |
                                                              arcade.key.MOD_CAPSLOCK |
                                                              arcade.key.MOD_SCROLLLOCK)):
            self.dispatch_event('on_close')


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
window.set_fullscreen()

window.setup()

arcade.run()
