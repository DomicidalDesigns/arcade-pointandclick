"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from
the command line with: python -m arcade.examples.starting_template
"""
from math import sqrt
import os
from pathlib import Path
import random

from pyglet import gl

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "POINT AND CLICK TEST"

UPDATES_PER_FRAME = 3

MOVEMENT_SPEED = 300

SPRITE_SCALING = 3

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

DEBUG = False
# DEBUG = True

# Resources path
project_path = Path(os.path.dirname(__file__))
# TODO create 'resource' main directory and 'sound', 'sprite' subdirectories
resource_path = project_path / "img"


def load_texture_pair(filename):
    '''
    Load a texture pair, with the second being a mirror image.
    '''
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, mirrored=True)
    ]


class Player(arcade.Sprite):
    '''
    Player Class
    '''

    def __init__(self):
        # Set up parent class
        super().__init__()

        self.name = 'Player'

        self.goto_x = 0
        self.goto_y = 0

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = SPRITE_SCALING

        self.Z_INDEX = 0

        # --- Load Textures ---
        # Images from Kenney.nl's Asset Pack 3
        # kenney_path = ":resources:images/animated_characters/"
        # main_path = f"{kenney_path}female_adventurer/femaleAdventurer"
        # main_path = f"{kenney_path}female_person/femalePerson"
        # main_path = f"{kenney_path}male_person/malePerson"
        # main_path = f"{kenney_path}male_adventurer/maleAdventurer"
        # main_path = f"{kenney_path}zombie/zombie"
        # main_path = f"{kenney_path}robot/robot"

        # Load textures for idle standing
        self.run_texture_pair = load_texture_pair(resource_path / "6.png")

        # Load textures for walking
        self.run_textures = []
        for i in range(1, 15):
            texture = load_texture_pair(resource_path / f"{i}.png")
            self.run_textures.append(texture)

        # Set the initial texture
        self.texture = self.run_texture_pair[0]

        # Hit box will be set based on the first image used.
        # If you want to specify
        # a different hit box, you can do it like the code below.
        # self.set_hit_box([[-22, -64], [22, -64], [22, 28], [-22, 28]])
        # self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time):
        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING

        elif (self.change_x > 0) and (self.character_face_direction == LEFT_FACING):
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.run_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 13 * UPDATES_PER_FRAME:
            self.cur_texture = 0

        frames = self.cur_texture // UPDATES_PER_FRAME

        self.texture = self.run_textures[frames][self.character_face_direction]

    def on_update(self, delta_time):
        self.center_x += self.change_x*delta_time
        self.center_y += self.change_y*delta_time

        # THIS CODE PREVENTS MOVING OFF SCREEN
        # if self.left < 50:
        #     self.left = 50
        # elif self.right > SCREEN_WIDTH - 50:
        #     self.right = SCREEN_WIDTH - 50

        if self.bottom < 150:
            self.bottom = 150
        # elif self.top > SCREEN_HEIGHT - 50:
        #     self.top = SCREEN_HEIGHT - 50

        pad = 5

        if self.goto_x in range(int(self.center_x-pad), int(self.center_x+pad)) and self.goto_y in range(int(self.bottom-pad), int(self.bottom)+pad):
            self.change_x = 0
            self.change_y = 0

        if DEBUG:
            print(f"goto:{self.goto_x, self.goto_y} center:{int(self.center_x), int(self.center_y)}")
            print(f"x:{self.change_x} y:{self.change_y}")

    def draw(self, **kwargs):
        """ Draw the sprite. """

        if self._sprite_list is None:
            from arcade import SpriteList
            self._sprite_list = SpriteList()
            self._sprite_list.append(self)

        self._sprite_list.draw(**kwargs)


class Item(arcade.Sprite):
    '''
    Item Class
    '''
    def __init__(self, filename, scale,
                 name, description,
                 set_position,
                 CAN_BE_PICKED_UP,
                 level, **kwargs):

        super().__init__(filename, scale)
        self.name = name
        self.description = description
        self.center_x, self.center_y = set_position
        self.CAN_BE_PICKED_UP = CAN_BE_PICKED_UP
        self.IN_INVENTORY = kwargs.get('IN_INVENTORY', None)
        self.Z_INDEX = 1
        self.Z_INDEX = kwargs.get('Z_INDEX', None)
        self.level = level

    def examine(self):
        return self.description

    def use(self):
        pass

    def draw(self, **kwargs):
        """ Draw the sprite. """

        if self._sprite_list is None:
            from arcade import SpriteList
            self._sprite_list = SpriteList()
            self._sprite_list.append(self)

        self._sprite_list.draw(**kwargs)


class Inventory(arcade.SpriteList):
    '''
    Inventory Class
    '''
    def __init__(self):
        super().__init__()

        self.items = []

        self.items_ordered = []

        self.items_visible = []
        self.row_index = 0
        self.visible_rows = [self.row_index, self.row_index + 1]

    def add(self, item):
        self.items.append(item)

    def remove(self, item):
        self.items.remove(item)

    def update(self):
        self.visible_rows = [self.row_index, self.row_index + 1]
        self.items_ordered = [self.items[i*8:(i+1)*8] for i in range(
            0, (len(self.items)//8)+1)]

        if len(self.items) <= 8:
            self.items_visible = self.items_ordered
        else:
            self.items_visible = self.items_ordered[self.visible_rows[0]:self.visible_rows[1]+1]

        for row in range(0, len(self.items_visible)):
            for item in self.items_visible[row]:
                item.center_x, item.center_y = (self.items_visible[row].index(item)*80+50, row*-80+130)

        for row in range(0, len(self.items_ordered)):
            for item in self.items_ordered[row]:
                if row not in self.visible_rows:
                    item.center_x, item.center_y = (-100, -100)

    def arrow(self, direction):
        if direction == 'up' and self.row_index > 0:
            print("Changed the row index (-1)")
            self.row_index -= 1
        elif direction == 'down' and self.row_index < len(self.items_ordered) - 2:
            print("Changed the row index (+1)")
            self.row_index += 1
        print(self.row_index)
        self.update()


class Room():
    '''
    Room Class
    '''
    def __init__(self, name, number, filename, scale):
        self.name = name
        self.number = number
        self.items = arcade.SpriteList()
        self.clickable_area = []

        self.room_dict = {
            'transition_location': (0, 0),
            'move_to_room': None,
            'player_position': (0, 0),
        },

        self.connected_rooms = []

        self.background = arcade.Sprite(filename, scale)
        self.background.bottom = 150
        self.background.left = 0

    def move_to_room(self):
        pass


class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.level_sprites = None
        self.player_sprite = None

        self.cursor_texture_list = None

        self.text_list = None

        self.text = None

        self.text_color = (0, 0, 0, 255)

        self.goto_point = None

        self.text_x = 200
        self.text_y = 200

        self.current_cursor = None

        self.inventory = Inventory()

        self.level_backgrounds = None

        self.point_list = []

        self.inventory_arrows = None

        '''
        ROOMS
        '''
        self.rooms = []

        items = arcade.SpriteList()

        self.rooms.append(
            Room('Start', 0, resource_path / 'level00.png', 0.45))

        self.rooms.append(
            Room('Level 1', 1, resource_path / 'level01.png', 0.45))

        self.room = self.rooms[0]

        self.room.clickable_area = [range(0, 800), range(178, 330)]

    def room(self, level):
        pass
        # TODO load items for current level

    def setup(self):
        # Create your sprites and sprite lists here

        # Sprite lists
        self.level_sprites = arcade.SpriteList()
        self.level_backgrounds = arcade.SpriteList()

        # Sprites

        self.level_backgrounds.append(
            arcade.Sprite(resource_path / 'level00.png', 0.45),
            )
        # self.level_backgrounds[0].width = 800
        self.level_backgrounds[0].bottom = 150
        self.level_backgrounds[0].left = 0

        # Set up the player
        self.player_sprite = Player()
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 300
        self.level_sprites.append(self.player_sprite)

        self.current_cursor = arcade.Sprite(resource_path / 'cursor/default.png', 0.5)
        self.cursor_texture_list = [
            arcade.load_texture(
                resource_path / f"cursor/{i}.png") for i in (
                'examine', 'use', 'use_examine', )]

        for texture in self.cursor_texture_list:
            self.current_cursor.append_texture(texture)

        self.goto_point = [self.player_sprite.goto_x,
                           self.player_sprite.goto_y]

        self.point_list.append(self.goto_point)

        self.text_list = arcade.SpriteList()

        self.text_y = 0
        self.text_x = 0
        self.text_color = (0, 0, 0, 255)

        self.text = ""

        self.set_mouse_visible(False)

        book = Item(
            resource_path / 'book.png', 1, 'book',
            "It's a book. What else can I tell you?",
            [
                random.randint(0, 500),
                random.randint(200, 500)
            ],
            True, 0, IN_INVENTORY=False, Z_INDEX=0)

        self.level_sprites.append(book)

        rand_items = (
            ('book', "It's a book.", resource_path / "book.png", 1),
            ('key', "It's a key. It opens stuff.", resource_path / "key.png", 1),
            ('firearm', "It's a gun. You should probably run.", resource_path / "firearm.png", 2.5),
            ('brick', "It's a block of cocaine. Nifty.", resource_path / "brick.png", 2.5),
            ("Hammer", "It's hammer time.", resource_path / "hammer.png", 2.5),
            ('sword', "It's a sword.", resource_path / "sword.png", 1),
        )

        # for i in range(20):
        #     item = random.choice(rand_items)
        #     self.level_sprites.append(
        #         Item(
        #             item[2], item[3], item[0], item[1],
        #             [random.randint(0, 800), random.randint(200, 600)],
        #             True, 0, IN_INVENTORY=False, Z_INDEX=0))

        self.inventory_arrows = arcade.SpriteList()

        self.inventory_arrows.append(
            arcade.Sprite(resource_path / 'ui/arrow_up.png', 4,
            center_x=725, center_y=125))

        self.inventory_arrows.append(
            arcade.Sprite(resource_path / 'ui/arrow_down.png', 4,
            center_x=725, center_y=50))

        self.level_sprites.append(
            Item(
                resource_path / 'tires.png', 0.45, 'Tires',
                "It's just a pile of tires...weirdo.",
                [700, 300], False, 0)
            )
        self.level_sprites.append(
            Item(
                resource_path / 'hydrant.png', 0.45, 'Fire hydrant',
                "Y'know, for dogs to piss on.",
                [300, 320], False, 0)
            )

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame
        arcade.start_render()

        self.room.background.draw()

        arcade.draw_rectangle_filled(SCREEN_WIDTH/2, 150/2, SCREEN_WIDTH, 200,
                                     arcade.csscolor.BLACK)

        # Draw inventory squares
        for i in range(8):
            for j in range(2):
                arcade.draw_rectangle_filled(
                    i*80+50, j*80+50,
                    64, 64, arcade.csscolor.RED)

        self.inventory_arrows.draw(filter=gl.GL_NEAREST)

        if DEBUG:
            for sprite in self.inventory_arrows:
                sprite.draw_hit_box(color=arcade.csscolor.RED)

        for sprite in self.level_sprites:
            sprite.draw(filter=gl.GL_NEAREST)

        if DEBUG:
            arcade.draw_point(self.player_sprite.center_x,
                              self.player_sprite.center_y,
                              arcade.csscolor.RED, 5)
            arcade.draw_point(self.player_sprite.goto_x,
                              self.player_sprite.goto_y,
                              arcade.csscolor.RED, 5)
            arcade.draw_line(self.player_sprite.center_x,
                             self.player_sprite.center_y,
                             self.player_sprite.goto_x,
                             self.player_sprite.goto_y,
                             arcade.csscolor.RED, 2)

        self.text_list.draw()

        arcade.draw_text(self.text,
                         self.text_x, self.text_y,
                         self.text_color, 18,
                         width=200, align="center",
                         anchor_x="center", anchor_y="center")

        self.current_cursor.draw()

        if DEBUG:
            arcade.draw_circle_outline(self.player_sprite.center_x, self.player_sprite.center_y, 200, arcade.csscolor.RED, 2, 30)

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        for sprite in self.level_sprites:
            sprite.on_update(delta_time)

        self.player_sprite.update_animation(delta_time)

        # self.level_sprites.update()

        self.current_cursor.update()

        for sprite in self.level_sprites:
            if sprite is self.player_sprite:
                pass
            elif sprite.bottom < self.player_sprite.bottom:
                sprite.Z_INDEX = 1
            else:
                sprite.Z_INDEX = -1


        self.level_sprites = sorted(self.level_sprites, key=lambda x: x.Z_INDEX)


        # TODO Move to on_mouse_release
        if self.player_sprite.center_x > 790 and self.player_sprite.center_y < 350:
            self.room = self.rooms[1]
            self.room.clickable_area = [range(0, 800), range(0, 600)]
            self.player_sprite.set_position(60, 300)
            # self.player_sprite.goto_x, self.player_sprite.goto_y = self.player_sprite._get_position()
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.scale = 1.5

            # TODO BUG Items being removed from inventory
            for item in self.level_sprites:
                if item is not self.player_sprite and not item.IN_INVENTORY:
                    self.level_sprites.remove(item)
                    print(self.level_sprites)

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        pass

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        self.current_cursor.center_x = x
        self.current_cursor.center_y = y

        # Set text position to cursor position (floating bit above the cursor)
        # This creates a tooltip feel.
        self.text_x = x
        self.text_y = y+25  # Floating a little above the cursor

        # For loop for each item

        for sprite in self.level_sprites:
            sprite_x_values, sprite_y_values = [], []
            for point in sprite.get_adjusted_hit_box():
                sprite_x_values.append(int(point[0]))
                sprite_y_values.append(int(point[1]))

            sprite_x_values = range(min(sprite_x_values), max(sprite_x_values))
            sprite_y_values = range(min(sprite_y_values), max(sprite_y_values))

        # for item in self.level_sprites:
        #     x_range = range(int(item.center_x)-pad, int(item.center_x)+pad)
        #     y_range = range(int(item.center_y)-pad, int(item.center_y)+pad)

            if x in sprite_x_values and y in sprite_y_values:
                # Change the text to the item name and display it
                self.text = sprite.name
                self.text_color = (255, 255, 255, 255)
                break
            else:
                # Make the text invisible
                self.text = ""
                self.text_color = (0, 0, 0, 0)

        if DEBUG:
            self.text = f"{self.text}\n{x,y}"
            self.text_color = (255, 255, 255, 255)

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pad = 10  # Padding for the item click detection

        self.x = x
        self.y = y

        left_click = button == arcade.MOUSE_BUTTON_LEFT
        right_click = button == arcade.MOUSE_BUTTON_RIGHT
        middle_click = button == arcade.MOUSE_BUTTON_MIDDLE

        move_cursor = self.current_cursor.textures[0]
        use_cursor = self.current_cursor.textures[2]
        examine_cursor = self.current_cursor.textures[1]

        is_move_cursor = self.current_cursor.texture == move_cursor
        is_use_cursor = self.current_cursor.texture == use_cursor
        is_examine_cursor = self.current_cursor.texture == examine_cursor

        # if left_click:
        #     self.current_cursor.set_texture(0)
        #     self.current_cursor.scale = 0.5

        if (right_click and is_examine_cursor) or (middle_click and is_use_cursor):
            self.current_cursor.set_texture(0)
            self.current_cursor.scale = 0.5

        elif right_click:
            self.current_cursor.set_texture(1)
            self.current_cursor.scale = 1

        elif middle_click:
            self.current_cursor.set_texture(2)
            self.current_cursor.scale = 0.5

        # Level items (not picked up)
        for sprite in self.level_sprites:

            sprite_x_values, sprite_y_values = [], []
            for point in sprite.get_adjusted_hit_box():
                sprite_x_values.append(int(point[0]))
                sprite_y_values.append(int(point[1]))

            sprite_x_values = range(min(sprite_x_values), max(sprite_x_values))
            sprite_y_values = range(min(sprite_y_values), max(sprite_y_values))

            pad = 100

            pickup_x_range = range(int(sprite.center_x)-pad, int(sprite.center_x)+pad)
            pickup_y_range = range(int(sprite.center_x)-pad, int(sprite.center_x)+pad)

            distance_x = self.player_sprite.center_x - x
            distance_y = self.player_sprite.bottom - y
            distance = int(sqrt(distance_x**2+distance_y**2))

            if x in sprite_x_values and y in sprite_y_values:
                if DEBUG:
                    print(self.player_sprite.center_y, sprite_y_values)

                if left_click and is_use_cursor and distance < 200:

                    if not sprite.IN_INVENTORY and sprite.CAN_BE_PICKED_UP:
                        self.inventory.add(sprite)
                        self.inventory.update()
                        print(f"You picked up the {sprite.name}.")
                        # sprite.center_x, sprite.center_y = (100, 100)
                        sprite.IN_INVENTORY = True
                        # for sprite in self.level_sprites:
                        #     if sprite is not self.player_sprite:
                        #         sprite.kill()
                    break

                # elif sprite.IN_INVENTORY:
                    # self.current_cursor.set_texture(0)

                if left_click and is_examine_cursor:
                    print(sprite.description)
                    # self.current_cursor.set_texture(1)
                    break
        else:
            if left_click and int(x) in tuple(self.room.clickable_area[0]) and int(y) in tuple(self.room.clickable_area[1]):
                self.current_cursor.set_texture(0)
                self.current_cursor.scale = 0.5
                if DEBUG:
                    print("Moving to mouse position!")

                self.player_sprite.goto_x = x
                self.player_sprite.goto_y = y

                dx = (x - self.player_sprite.center_x)
                dy = (y - self.player_sprite.bottom)
                magnitude = sqrt(dx**2+dy**2)
                self.player_sprite.change_x = MOVEMENT_SPEED*(dx)/magnitude
                self.player_sprite.change_y = MOVEMENT_SPEED*(dy)/magnitude

        arrow_x_values = []
        arrow_y_values = []

        for arrow in range(2):
            for point in self.inventory_arrows[arrow].get_adjusted_hit_box():
                arrow_x_values.append(int(point[0]))
                arrow_y_values.append(int(point[1]))

            arrow_x_range = range(min(arrow_x_values), max(arrow_x_values))
            arrow_y_range = range(min(arrow_y_values), max(arrow_y_values))

            if left_click and x in arrow_x_range and y in arrow_y_range:
                if arrow == 0:
                    print("Clicked the up arrrow!")
                    self.inventory.arrow('up')
                    break
                if arrow == 1:
                    print("Clicked the down arrow!")
                    self.inventory.arrow('down')

        # # Inventory items
        # for item in self.inventory:
        #     x_range = range(item.center_x-pad, item.center_x+pad)
        #     y_range = range(item.center_y-pad, item.center_y+pad)
        #
        #     if x in x_range and y in y_range:
        #         pass
        #
        # else:
        #     if item not in self.level_sprites and button is not arcade.MOUSE_BUTTON_MIDDLE and int(y) > 150:
        #         self.current_cursor.set_texture(0)
        #         if DEBUG:
        #             print("Moving to mouse position!")
        #
        #         self.player_sprite.goto_x = x
        #         self.player_sprite.goto_y = y
        #
        #         dx = (x - self.player_sprite.center_x)
        #         dy = (y - self.player_sprite.bottom)
        #         magnitude = sqrt(dx**2+dy**2)
        #         self.player_sprite.change_x = MOVEMENT_SPEED*(dx)/magnitude
        #         self.player_sprite.change_y = MOVEMENT_SPEED*(dy)/magnitude


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
