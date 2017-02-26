import random
from collections import defaultdict
from typing import List

import pytmx
from lxml import etree

import arcade
from arcade import load_textures

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


class Collider:
    def __init__(self, tmxObject: pytmx.TiledObject, total_height: int) -> None:
        self.center_x = tmxObject.x
        self.center_y = tmxObject.y
        self.radius = 10
        if hasattr(tmxObject, 'points'):
            self.center_x = tmxObject.x
            self.center_y = tmxObject.y
            self.is_polygon = True
            self.points = []
            for point in tmxObject.points:
                self.points.append((point[0], total_height - point[1]))
        else:
            self.is_polygon = False
            self.width = tmxObject.width
            self.height = tmxObject.height
            self.radius = tmxObject.width * 0.5
            self.center_x = tmxObject.x + self.width * 0.5
            self.center_y = tmxObject.y + self.height * 0.5

        self.center_y = total_height - self.center_y
        self.type = tmxObject.type
        self.name = tmxObject.name


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
        self.viewport_bottom = 64.0
        self.input_map = defaultdict(lambda: 0.0)
        self.input_map['ACCELERATION'] = (0.0, 0.0)
        self.collisions = []

    def load_layer(self, layer: pytmx.TiledTileLayer) -> None:
        for tile in layer.tiles():
            tile_sprite = arcade.Sprite()
            tile_texture_positions = tile[2][1]
            x, y = int(tile_texture_positions[0] / 64), int(tile_texture_positions[1] / 64)
            offset = y * 16 + x
            tile_sprite.append_texture(self.tile_set[int(offset)])
            tile_sprite.set_position(center_x=32 + tile[0] * 64, center_y=32 + (70 - tile[1]) * 64)
            tile_sprite.set_texture(0)
            self.all_sprites_list.append(tile_sprite)

    def load_tiles(self) -> List[arcade.Texture]:
        tile_set = []
        for idx in range(1, 97):
            texture = arcade.load_texture('../assets/sprites/tiles/tile_{:0>2}.png'.format(idx))
            tile_set.append(texture)
        return tile_set

    def setup(self) -> None:
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

        for collision in level.get_layer_by_name('collisions'):
            total_height = 70 * 64
            collider = Collider(tmxObject=collision, total_height=total_height)
            self.collisions.append(collider)

        for sprite in self.all_sprites_list:
            x = sprite.position[0]
            y = int(sprite.position[1] - self.viewport_bottom)
            sprite.set_position(center_x=x, center_y=y)
            sprite.update()

        self.player_sprite = arcade.Sprite()
        self.player_sprite.append_texture(self.sprite_sheet[85])
        self.player_sprite.set_position(center_x=SCREEN_WIDTH * 0.5, center_y=self.viewport_bottom + 55)
        self.player_sprite.set_texture(0)
        self.player_sprite.angle = 180

        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.AMARANTH)

    def own_scrolling(self, viewport_delta: float) -> None:
        for sprite in self.all_sprites_list:
            x = sprite.position[0]
            y = int(sprite.position[1] - viewport_delta)
            sprite.set_position(center_x=x, center_y=y)
            sprite.update()

        for collider in self.collisions:
            if collider.is_polygon:
                points = []
                for point in collider.points:
                    x = point[0]
                    y = int(point[1] - viewport_delta)
                    points.append((x, y))
                collider.points = points
            else:
                x = collider.center_x
                y = int(collider.center_y - viewport_delta)
                collider.center_x = x
                collider.center_y = y

    def animate(self, delta_time: float) -> None:
        """ Movement and game logic """
        if self.input_map['USER_BREAK']:
            self.dispatch_event('on_close')
        viewport_delta = 64 * delta_time
        self.viewport_bottom = int(self.viewport_bottom + viewport_delta)

        if self.viewport_bottom > ((70 * 64) - SCREEN_HEIGHT):
            self.viewport_bottom = ((70 * 64) - SCREEN_HEIGHT)
            viewport_delta = 0.0

        self.own_scrolling(viewport_delta)

        self.player_sprite.position[0] += self.input_map['ACCELERATION'][0] * viewport_delta
        self.player_sprite.position[1] += self.input_map['ACCELERATION'][1] * viewport_delta

        if self.player_sprite.position[1] - 55 < 0:
            self.player_sprite.position[1] = 55

        if self.player_sprite.position[1] + 55 > SCREEN_HEIGHT:
            self.player_sprite.position[1] = SCREEN_HEIGHT - 55

        if self.player_sprite.position[0] + 28 > SCREEN_WIDTH:
            self.player_sprite.position[0] = SCREEN_WIDTH - 28

        if self.player_sprite.position[0] - 28 < 0:
            self.player_sprite.position[0] = 28

        self.player_sprite.update()

        player_bounds = [(self.player_sprite.position[0] - 28, self.player_sprite.position[1] - 55),
                         (self.player_sprite.position[0] - 28, self.player_sprite.position[1] + 55),
                         (self.player_sprite.position[0] + 28, self.player_sprite.position[1] + 55),
                         (self.player_sprite.position[0] + 28, self.player_sprite.position[1] - 55)]

        for collider in self.collisions:
            if self.test_collision(player_bounds, collider):
                print('Collision @', self.player_sprite.position)

    def test_collision(self, bounding_box, collider: Collider):
        if collider.is_polygon:
            return arcade.are_polygons_intersecting(bounding_box, collider.points)
        return False

    def on_draw(self) -> None:
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.all_sprites_list.draw()
        if __debug__:
            for collision in self.collisions:
                if collision.is_polygon:
                    for point in collision.points:
                        arcade.draw_points(collision.points, arcade.color.AMARANTH, 3)
                    arcade.draw_polygon_outline(collision.points, arcade.color.AMARANTH, 3)
                else:
                    arcade.draw_point(collision.center_x, collision.center_y, arcade.color.AMARANTH, 3)
                    arcade.draw_circle_outline(collision.center_x, collision.center_y, collision.radius, arcade.color.AMARANTH, 3)
        self.player_sprite.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        is_modified = (modifiers & ~(arcade.key.MOD_NUMLOCK | arcade.key.MOD_CAPSLOCK | arcade.key.MOD_SCROLLLOCK))
        if symbol == arcade.key.ESCAPE and not is_modified:
            self.input_map['USER_BREAK'] = True

        if symbol == arcade.key.W and not is_modified:
            self.input_map['ACCELERATION'] = (self.input_map['ACCELERATION'][0], 1.0)
        if symbol == arcade.key.S and not is_modified:
            self.input_map['ACCELERATION'] = (self.input_map['ACCELERATION'][0], -1.0)
        if symbol == arcade.key.A and not is_modified:
            self.input_map['ACCELERATION'] = (-1.0, self.input_map['ACCELERATION'][1])
        if symbol == arcade.key.D and not is_modified:
            self.input_map['ACCELERATION'] = (1.0, self.input_map['ACCELERATION'][1])

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        is_modified = (modifiers & ~(arcade.key.MOD_NUMLOCK | arcade.key.MOD_CAPSLOCK | arcade.key.MOD_SCROLLLOCK))
        if symbol == arcade.key.W and not is_modified:
            self.input_map['ACCELERATION'] = (self.input_map['ACCELERATION'][0], 0.0)
        if symbol == arcade.key.S and not is_modified:
            self.input_map['ACCELERATION'] = (self.input_map['ACCELERATION'][0], 0.0)
        if symbol == arcade.key.A and not is_modified:
            self.input_map['ACCELERATION'] = (0.0, self.input_map['ACCELERATION'][1])
        if symbol == arcade.key.D and not is_modified:
            self.input_map['ACCELERATION'] = (0.0, self.input_map['ACCELERATION'][1])


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
window.set_fullscreen()
SCREEN_WIDTH, SCREEN_HEIGHT = window.get_size()
window.setup()

arcade.run()
