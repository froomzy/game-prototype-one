import random

import pytmx
from lxml import etree

import arcade
from arcade import load_textures

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        super().__init__(width, height)
        self.all_sprites_list = None
        self.sprite_sheet = None
        self.tile_set = None
        self.viewport_bottom = 0.0

    def load_layer(self, layer):
        for tile in layer.tiles():
            tile_sprite = arcade.Sprite()
            tile_texture_positions = tile[2][1]
            x, y = tile_texture_positions[0] / 64, tile_texture_positions[1] / 64
            offset = y * 16 + x
            tile_sprite.append_texture(self.tile_set[int(offset)])
            print(tile[0], tile[1])
            tile_sprite.set_position(center_x=32 + tile[0]* 64, center_y=32 + (70 - tile[1]) * 64)
            tile_sprite.set_texture(0)
            self.all_sprites_list.append(tile_sprite)

    def setup(self):
        self.all_sprites_list = arcade.SpriteList()
        # Need to load the sprite sheet, then get the texture region out of the sprite sheet
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
                tile_coordinates.append([x * 64, y * 64, 64, 64])
        self.tile_set = load_textures(
            file_name='../assets/sprites/tiles_sheet.png',
            image_location_list=tile_coordinates
        )
        level = pytmx.TiledMap('../assets/levels/pim-test-3.tmx')

        self.load_layer(layer=level.get_layer_by_name('water'))
        self.load_layer(layer=level.get_layer_by_name('overlay'))
        self.load_layer(layer=level.get_layer_by_name('land'))
        self.load_layer(layer=level.get_layer_by_name('props'))



        # for layer in level.layers:
        #     for tile in layer
        # Then make a sprite, and then give it the texture
        sprite = arcade.Sprite()
        sprite.append_texture(self.sprite_sheet[85])
        sprite.set_position(center_x=400, center_y=300)
        sprite.set_texture(0)
        sprite.angle = 180
        self.all_sprites_list.append(sprite)
        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def animate(self, delta_time):
        """ Movement and game logic """
        sprite = self.all_sprites_list[-1]
        delta_angle = 36.0 * delta_time
        self.viewport_bottom += 64 * delta_time
        if self.viewport_bottom > ((70 * 64) - 600):
            self.viewport_bottom = ((70 * 64) - 600)

        if sprite.position[1] < self.viewport_bottom + 55:
            sprite.set_position(center_x=sprite.position[0], center_y=self.viewport_bottom + 55)
        arcade.set_viewport(left=0, right=800, bottom=int(self.viewport_bottom), top=int(self.viewport_bottom) + 600)
        # sprite.angle += delta_angle
        sprite.update()

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.all_sprites_list.draw()


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
window.setup()

arcade.run()
