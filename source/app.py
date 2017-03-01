from collections import defaultdict
from typing import List, Tuple

import arcade
import pytmx
from arcade import load_textures
from lxml import etree
import euclid

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


class PlayerShip:
    def __init__(self, x, y, texture):
        self.sprite = arcade.Sprite()
        self.sprite.append_texture(texture)
        self.sprite.set_texture(0)

        y += self.sprite.height * 0.5

        self.sprite.set_position(center_x=x, center_y=y)
        self.sprite.angle = 180
        self.position = euclid.Vector2(x=x, y=y)
        self.x = x
        self.y = y

    def bounds(self) -> Tuple[List[euclid.Point2], List[euclid.LineSegment2]]:
        points = [
            euclid.Point2(self.x - self.width * 0.5, self.y - self.height * 0.5),
            euclid.Point2(self.x - self.width * 0.5, self.y + self.height * 0.5),
            euclid.Point2(self.x + self.width * 0.5, self.y + self.height * 0.5),
            euclid.Point2(self.x + self.width * 0.5, self.y - self.height * 0.5)
        ]

        lines = [euclid.LineSegment2(x[0], x[1]) for x in [(points[0], points[1]), (points[1], points[2]), (points[2], points[3]), (points[3], points[0])]]
        return points, lines

    def draw(self):
        self.sprite.draw()

    def update(self, x: float, y: float):
        self.sprite.position[0] = x
        self.x = x
        self.sprite.position[1] = y
        self.y = y
        self.position = euclid.Vector2(x, y)
        self.sprite.update()

    @property
    def bottom_left(self) -> euclid.Point2:
        return euclid.Point2(x=self.x - self.sprite.width * 0.5, y=self.y - self.sprite.height * 0.5)

    @property
    def top_right(self) -> euclid.Point2:
        return euclid.Point2(x=self.x + self.sprite.width * 0.5, y=self.y + self.sprite.height * 0.5)

    @property
    def width(self) -> float:
        return self.sprite.width

    @property
    def height(self) -> float:
        return self.sprite.height

    def test_collision(self, collider: Collider):
        points, lines = self.bounds()
        if collider.is_polygon:
            bounds = [(point.x, point.y) for point in points]
            return arcade.are_polygons_intersecting(bounds, collider.points)
        else:
            if (self.x - self.width * 0.5 < collider.center_x < self.x - self.width * 0.5 and
                                self.y - self.height * 0.5 < collider.center_y < self.y + self.height * 0.5):
                return True
            circle = euclid.Circle(center=euclid.Point2(collider.center_x, collider.center_y), radius=collider.radius)
            for side in lines:
                if circle.intersect(side):
                    return True
        return False


class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        super().__init__(width, height)
        self.all_sprites_list = None
        self.player = None
        self.sprite_sheet = None
        self.tile_set = None
        self.viewport_bottom = 64.0
        self.input_map = defaultdict(lambda: 0.0)
        self.velocity = euclid.Vector2(0.0, 0.0)
        self.input_map['FORWARD'] = euclid.Vector2(0.0, 0.0)
        self.input_map['BACKWARD'] = euclid.Vector2(0.0, 0.0)
        self.input_map['LEFT'] = euclid.Vector2(0.0, 0.0)
        self.input_map['RIGHT'] = euclid.Vector2(0.0, 0.0)
        self.collisions = []
        self.total_height = 0
        self.tile_height = 0

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
                tile_coordinates.append([int(x * self.tile_height), int(y * self.tile_height), self.tile_height, self.tile_height])
        self.tile_set = load_textures(
            file_name='../assets/sprites/tiles_sheet.png',
            image_location_list=tile_coordinates
        )
        level = pytmx.TiledMap('../assets/levels/pim-test-3.tmx')
        self.total_height = level.height * level.tileheight
        self.tile_height = level.tileheight

        self.load_layer(layer=level.get_layer_by_name('water'))
        self.load_layer(layer=level.get_layer_by_name('overlay'))
        self.load_layer(layer=level.get_layer_by_name('land'))
        self.load_layer(layer=level.get_layer_by_name('props'))

        for collision in level.get_layer_by_name('collisions'):
            collider = Collider(tmxObject=collision, total_height=self.total_height)
            self.collisions.append(collider)

        for sprite in self.all_sprites_list:
            x = sprite.position[0]
            y = int(sprite.position[1] - self.viewport_bottom)
            sprite.set_position(center_x=x, center_y=y)
            sprite.update()

        self.player = PlayerShip(x=SCREEN_WIDTH * 0.5, y=self.viewport_bottom, texture=self.sprite_sheet[85])

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
        viewport_delta = self.tile_height * delta_time
        self.viewport_bottom = int(self.viewport_bottom + viewport_delta)

        if self.viewport_bottom > (self.total_height - SCREEN_HEIGHT):
            self.viewport_bottom = (self.total_height - SCREEN_HEIGHT)
            viewport_delta = 0.0

        self.own_scrolling(viewport_delta)

        acceleration = (self.input_map['FORWARD'] + self.input_map['BACKWARD'] + self.input_map['LEFT'] + self.input_map['RIGHT']) * 100
        centre = self.player.position + (acceleration * delta_time)
        self.player.update(x=centre.x, y=centre.y)

        if self.player.bottom_left.y < 0:
            self.player.update(x=centre.x, y=centre.y + self.player.height * 0.5)  # Plus height

        if self.player.top_right.y > SCREEN_HEIGHT:
            self.player.update(x=centre.x, y=centre.y - self.player.height * 0.5)  # Minus height

        if self.player.bottom_left.x > SCREEN_WIDTH:
            self.player.update(x=centre.x - self.player.width * 0.5, y=centre.y)  # Minus Width

        if self.player.top_right.x < 0:
            self.player.update(x=centre.x + self.player.width, y=centre.y)  # Plus Width

        for collider in self.collisions:
            if self.player.test_collision(collider):
                if collider.type == 'ROCK':
                    sprite = arcade.Sprite()
                    sprite.append_texture(self.sprite_sheet[6])
                    sprite.set_position(center_x=self.player.x, center_y=self.player.y - self.player.height * 0.5)
                    sprite.set_texture(0)
                    sprite.angle = 180
                    self.all_sprites_list.append(sprite)
                    shunt_x = self.player.width * 0.5 - abs(collider.center_x - self.player.x) * 1.1
                    shunt_y = self.player.height * 0.5 - abs(collider.center_y - self.player.y) * 1.1

                    if self.player.x > collider.center_x:
                        shunt_x *= -1
                    if self.player.y > collider.center_y:
                        shunt_y *= -1
                    self.player.update(x=self.player.x + shunt_x, y=self.player.y + shunt_y)
                if collider.type == 'LAND':
                    shunt_x = self.player.width * 0.5 - abs(collider.center_x - self.player.x) * 1.1
                    shunt_y = self.player.height * 0.5 - abs(collider.center_y - self.player.y) * 1.1

                    if self.player.x > collider.center_x:
                        shunt_x *= -1
                    if self.player.y > collider.center_y:
                        shunt_y *= -1
                    self.player.update(x=self.player.x + shunt_x, y=self.player.y + shunt_y)

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
        self.player.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        is_modified = (modifiers & ~(arcade.key.MOD_NUMLOCK | arcade.key.MOD_CAPSLOCK | arcade.key.MOD_SCROLLLOCK))
        if symbol == arcade.key.ESCAPE and not is_modified:
            self.input_map['USER_BREAK'] = True

        if symbol == arcade.key.W and not is_modified:
            self.input_map['FORWARD'] = euclid.Vector2(0, 1.0)
        if symbol == arcade.key.S and not is_modified:
            self.input_map['BACKWARD'] = euclid.Vector2(0, -1.0)
        if symbol == arcade.key.A and not is_modified:
            self.input_map['LEFT'] = euclid.Vector2(-1.0, 0)
        if symbol == arcade.key.D and not is_modified:
            self.input_map['RIGHT'] = euclid.Vector2(1.0, 0)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        is_modified = (modifiers & ~(arcade.key.MOD_NUMLOCK | arcade.key.MOD_CAPSLOCK | arcade.key.MOD_SCROLLLOCK))
        if symbol == arcade.key.W and not is_modified:
            self.input_map['FORWARD'] = euclid.Vector2(0.0, 0.0)
        if symbol == arcade.key.S and not is_modified:
            self.input_map['BACKWARD'] = euclid.Vector2(0.0, 0.0)
        if symbol == arcade.key.A and not is_modified:
            self.input_map['LEFT'] = euclid.Vector2(0.0, 0.0)
        if symbol == arcade.key.D and not is_modified:
            self.input_map['RIGHT'] = euclid.Vector2(0.0, 0.0)


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
window.set_fullscreen()
SCREEN_WIDTH, SCREEN_HEIGHT = window.get_size()
window.setup()

arcade.run()
