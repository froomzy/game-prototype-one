from collections import defaultdict
from typing import List, Tuple, Any

import arcade
import euclid
import pytmx
from arcade import load_textures
from lxml import etree

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

SPAWN_TYPES = {
    'CARGO': 75
}


def process_collisions(colliders: List['Collider'], player: 'Collider', viewport: Tuple[euclid.Vector2, euclid.Vector2]) -> None:
    # TODO (Dylan): This will figure out the collisions, but there is nothing to actually influence the objects in the world

    # Broad Pass: Collect colliders that are colliding with the viewport

    # Narrow Pass: Test each collider in the set against the others using a stepped process

    pass


class SpawnPoint:
    def __init__(self, tmx_object: pytmx.TiledObject, textures: List[arcade.Texture], total_height: int) -> None:
        self.center_x = tmx_object.x
        self.center_y = total_height - tmx_object.y
        self.type = tmx_object.type
        self.spawns = int(tmx_object.properties.get('count', 3))
        self.texture = textures[SPAWN_TYPES.get(self.type)]
        self.has_spawned = False
        self.total_height = total_height

    def spawn(self, enemies_list: List['EnemyShip'], sprites: arcade.SpriteList, colliders: List['Collider']) -> None:
        x_offset = 0
        y_offset = 0
        for idx in range(self.spawns):
            enemy = EnemyShip(x=self.center_x + x_offset, y=self.center_y + y_offset, texture=self.texture, total_height=self.total_height)
            enemies_list.append(enemy)
            sprites.append(enemy.sprite)
            colliders.append(enemy.collider)
            print(enemy.collider.name)
            y_offset += enemy.sprite.height + 10
        self.has_spawned = True


class Collider:
    def __init__(self, tmx_object: pytmx.TiledObject, total_height: int) -> None:
        self.center_x = tmx_object.x
        self.center_y = tmx_object.y
        self.radius = 10
        if hasattr(tmx_object, 'points'):
            self.center_x = tmx_object.x
            self.center_y = tmx_object.y
            self.is_polygon = True
            self.points = []
            for point in tmx_object.points:
                self.points.append((point[0], total_height - point[1]))
        else:
            self.is_polygon = False
            self.width = tmx_object.width
            self.height = tmx_object.height
            self.radius = tmx_object.width * 0.5
            self.center_x = tmx_object.x + self.width * 0.5
            self.center_y = tmx_object.y + self.height * 0.5

        self.center_y = total_height - self.center_y
        self.type = tmx_object.type
        self.name = tmx_object.name


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

    def set_position(self, x: float, y: float):
        self.sprite.position[0] = x
        self.x = x
        self.sprite.position[1] = y
        self.y = y
        self.position = euclid.Vector2(x, y)

    def update(self):
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


class EnemyShip:
    def __init__(self, x: float, y: float, texture: arcade.Texture, total_height: int) -> None:

        self.sprite = arcade.Sprite()
        self.sprite.append_texture(texture)
        self.sprite.set_texture(0)

        y += self.sprite.height * 0.5

        self.sprite.set_position(center_x=x, center_y=y)
        self.position = euclid.Vector2(x=x, y=y)
        self.x = x
        self.y = y

        points = [
            (self.x - self.sprite.width * 0.5, total_height - (self.y - self.sprite.height * 0.5)),
            (self.x - self.sprite.width * 0.5, total_height - (self.y + self.sprite.height * 0.5)),
            (self.x + self.sprite.width * 0.5, total_height - (self.y + self.sprite.height * 0.5)),
            (self.x + self.sprite.width * 0.5, total_height - (self.y - self.sprite.height * 0.5))
        ]

        tmx_object = type('FakeTiledObject', (object,), {})
        tmx_object.x = x
        tmx_object.y = y
        tmx_object.points = points
        tmx_object.type = 'SHIP'
        tmx_object.name = 'SHIP'

        self.collider = Collider(tmx_object=tmx_object, total_height=total_height)

    def set_position(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.position = euclid.Vector2(x, y)

    def update(self, viewport_delta: float) -> None:
        """Update the position of the ship.

        This is the place that we will calculate the movement of the ship when it is doing
        fancy manoeuvres around the screen."""
        y = int(self.x - viewport_delta)
        self.set_position(x=self.x, y=y)


class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        super().__init__(width, height)
        self.all_sprites_list = None
        self.player: PlayerShip = None
        self.enemies = None
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
        self.spawn_points = []
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
        self.enemies = []
        sprite_coordinates = []

        level = pytmx.TiledMap('../assets/levels/pim-test-3.tmx')
        self.total_height = level.height * level.tileheight
        self.tile_height = level.tileheight

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
        self.load_layer(layer=level.get_layer_by_name('water'))
        self.load_layer(layer=level.get_layer_by_name('overlay'))
        self.load_layer(layer=level.get_layer_by_name('land'))
        self.load_layer(layer=level.get_layer_by_name('props'))

        for collision in level.get_layer_by_name('collisions'):
            collider = Collider(tmx_object=collision, total_height=self.total_height)
            self.collisions.append(collider)

        for spawn_point in level.get_layer_by_name('spawns'):
            spawn = SpawnPoint(tmx_object=spawn_point, textures=self.sprite_sheet, total_height=self.total_height)
            self.spawn_points.append(spawn)

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

        for enemy in self.enemies:
            enemy.update(viewport_delta=viewport_delta)

        for collider in self.collisions:
            # print('--- START ---')
            if collider.is_polygon:
                # if collider.name == 'SHIP':
                #     print('BEFORE', collider.points)
                points = []
                for point in collider.points:
                    x = point[0]
                    y = int(point[1] - viewport_delta)
                    points.append((x, y))
                collider.points = points
                # if collider.name == 'SHIP':
                #     print('AFTER', collider.points)
            else:
                x = collider.center_x
                y = int(collider.center_y - viewport_delta)
                collider.center_x = x
                collider.center_y = y
            # print('--- END ---')

        for spawn in self.spawn_points:
            x = spawn.center_x
            y = int(spawn.center_y - viewport_delta)
            spawn.center_x = x
            spawn.center_y = y

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

        spawn_barrier = self.viewport_bottom + SCREEN_HEIGHT + 200

        for spawn_point in self.spawn_points:
            if spawn_point.center_y < spawn_barrier and not spawn_point.has_spawned:
                spawn_point.spawn(enemies_list=self.enemies, sprites=self.all_sprites_list, colliders=self.collisions)

        acceleration = (self.input_map['FORWARD'] + self.input_map['BACKWARD'] + self.input_map['LEFT'] + self.input_map['RIGHT']) * 100
        centre = self.player.position + (acceleration * delta_time)
        self.player.set_position(x=centre.x, y=centre.y)

        if self.player.bottom_left.y < 0:
            self.player.set_position(x=centre.x, y=centre.y + self.player.height * 0.5)  # Plus height

        if self.player.top_right.y > SCREEN_HEIGHT:
            self.player.set_position(x=centre.x, y=centre.y - self.player.height * 0.5)  # Minus height

        if self.player.bottom_left.x > SCREEN_WIDTH:
            self.player.set_position(x=centre.x - self.player.width * 0.5, y=centre.y)  # Minus Width

        if self.player.top_right.x < 0:
            self.player.set_position(x=centre.x + self.player.width, y=centre.y)  # Plus Width

        for collider in self.collisions:
            if self.player.test_collision(collider):
                if collider.type in ['ROCK', 'SHIP']:
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
                    self.player.set_position(x=self.player.x + shunt_x, y=self.player.y + shunt_y)
                if collider.type == 'LAND':
                    shunt_x = self.player.width * 0.5 - abs(collider.center_x - self.player.x) * 1.1
                    shunt_y = self.player.height * 0.5 - abs(collider.center_y - self.player.y) * 1.1

                    if self.player.x > collider.center_x:
                        shunt_x *= -1
                    if self.player.y > collider.center_y:
                        shunt_y *= -1
                    self.player.set_position(x=self.player.x + shunt_x, y=self.player.y + shunt_y)
        self.player.update()

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
