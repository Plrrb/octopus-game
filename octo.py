import arcade
import arcade.gui


TILE_SCALING = 1
SPRITE_SCALING = 1
SCREEN_TITLE = "Platformer"
GRAVITY = 0.2

CHARACTERS = {
    "maleAdventurer": ":resources:images/animated_characters/male_adventurer",
    "femaleAdventurer": ":resources:images/animated_characters/female_adventurer",
    "femalePerson": ":resources:images/animated_characters/female_person",
    "malePerson": ":resources:images/animated_characters/male_person",
    "robot": ":resources:images/animated_characters/robot",
    "zombie": ":resources:images/animated_characters/zombie",
}

MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 2


class Start_Screen(arcade.View):
    def __init__(self, my_window, display_width, display_height):
        super().__init__()
        self.display_width = display_width
        self.display_height = display_height
        self.window = my_window

        self.buttons = []
        self.make_buttons()

    def on_draw(self):
        self.ui_manager.draw()

    def choose_characters(self, character):
        octopus_game = Octopus_Game(self.display_width, self.display_height, character)
        octopus_game.setup()
        self.window.show_view(octopus_game)

    def make_buttons(self):
        self.ui_manager = arcade.gui.UIManager(self.window)

        box = arcade.gui.UIBoxLayout(vertical=False)

        for key in CHARACTERS:
            t = arcade.load_texture(f"{CHARACTERS[key]}/{key}_idle.png")
            b = arcade.gui.UITextureButton(texture=t)
            b.on_click = lambda *x, key=key: self.choose_characters(key)
            box.add(b)

        self.ui_manager.add(arcade.gui.UIAnchorWidget(child=box))

        # width = 150
        # height = 150

        # idle_chars = [
        #     arcade.load_texture(f"{CHARACTERS[key]}/{key}_idle.png")
        #     for key in CHARACTERS
        # ]

        # start = (self.display_width / 2) - (width * 3)

        # # draw row
        # rows = (len(CHARACTERS) // 6) + 1

        # counter = len(CHARACTERS)
        # for j in range(rows):
        #     if counter >= 6:
        #         range_num = 6
        #     else:
        #         range_num = counter % 6

        #     for i in range(range_num):
        #         x = (start + i * width) + width / 2
        #         y = self.display_height - (height * j) - 200
        #         # arcade.draw_rectangle_outline(
        #         #     x,
        #         #     y,
        #         #     width,
        #         #     height,
        #         #     arcade.color.RED,
        #         # )
        #         # arcade.draw_scaled_texture_rectangle(x, y, idle_chars[i])
        #         button = arcade.gui.UITextureButton(x, y, width, height, idle_chars[i])
        #         button.on_click(lambda: self.start_game(idle_chars[i]))

        #         self.buttons.append(button)

        #     counter -= 6

    def setup(self):
        """This should set up your game and get it ready to play"""
        # Replace 'pass' with the code to set up your game
        pass

    def on_show_view(self):
        """Called when switching to this view"""
        arcade.set_background_color(arcade.color.ORANGE_PEEL)
        self.ui_manager.enable()

    def on_hide_view(self):
        # This unregisters the manager's UI handlers,
        # Handlers respond to GUI button clicks, etc.
        self.ui_manager.disable()


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """

    return {
        "right": arcade.load_texture(filename),
        "left": arcade.load_texture(filename, flipped_horizontally=True),
    }


class Coin(arcade.Sprite):
    def __init__(self, x, y):
        img = ":resources:images/items/coinGold.png"
        super().__init__(img, SPRITE_SCALING)
        self.center_x = x
        self.center_y = y
        self.value = 1

    def effect(self, player):
        player.give_coin(1)


class Player(arcade.Sprite):
    def __init__(self, x, y, w, h, character):
        print(character)
        url = f"{CHARACTERS[character]}/{character}_"
        super().__init__(url + "idle.png")

        self.textures_dict = {
            "idle": arcade.load_texture(url + "idle.png"),
            "jump_right": arcade.load_texture(url + "jump.png"),
            "jump_left": arcade.load_texture(
                url + "jump.png", flipped_horizontally=True
            ),
            "fall_left": arcade.load_texture(
                url + "fall.png", flipped_horizontally=True
            ),
            "fall_right": arcade.load_texture(url + "fall.png"),
        }

        self.texture = self.textures_dict["idle"]

        self.width = w * 3
        self.height = h * 3

        self.speed_scale = 4
        self.jump_speed = self.height / 20

        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")

        self.direction = "right"
        self.cur_texture = 0

        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]

        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{url}walk{i}.png")
            self.walk_textures.append(texture)

        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.coins = 0

    def update(self):
        super().update()

        if self.change_y <= -1:
            self.texture = self.textures_dict["fall_" + self.direction]

        elif self.change_y >= 1:
            self.texture = self.textures_dict["jump_" + self.direction]

        elif self.change_y == 0:
            self.texture = self.textures_dict["idle"]

    def update_animation(self, delta_time: float):

        if self.change_x != 0 and self.change_y == 0:

            self.cur_texture += 1

            if self.cur_texture > 7 * UPDATES_PER_FRAME:
                self.cur_texture = 0

            frame = self.cur_texture // UPDATES_PER_FRAME
            direction = self.direction
            self.texture = self.walk_textures[frame][direction]

    def get_coins(self):
        return self.coins

    def give_coin(self, ammount):
        self.coins += ammount
        arcade.play_sound(self.collect_coin_sound)

    def stop(self):
        self.change_x = 0

    def move(self, direction):
        if direction == 1:
            self.direction = "right"
        else:
            self.direction = "left"

        self.change_x = direction * self.speed_scale

    def jump(self, can_jump=True):
        if can_jump:
            self.texture = self.textures_dict["jump_" + self.direction]

            arcade.play_sound(self.jump_sound)
            self.change_y = self.jump_speed


class Octopus_Game(arcade.View):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, display_width, display_height, character):
        super().__init__()

        arcade.set_background_color(arcade.color.AMAZON)
        self.display_width = display_width
        self.display_height = display_height

        self.player_list = None
        self.wall_list = None
        self.coin_list = None
        self.player = None
        self.character = character

    def setup(self):
        """Set up the game variables. Call to re-start the game."""
        # Create your sprites and sprite lists here
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.load_map("octopus-game/map.txt")

        # add the floor
        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
        wall.width = self.display_width
        wall.center_x = self.display_height / 2
        wall.center_y = 0
        self.wall_list.append(wall)

        # Set up the player
        self.player = Player(
            50, 50, self.sprite_width, self.sprite_height, self.character
        )

        print("before adding player to list")
        print(self.player)
        self.player_list.append(self.player)
        print("after adding player to list")

        self.sprite_width = None
        self.sprite_height = None

        self.keys_pressed = {
            arcade.key.D: False,
            arcade.key.A: False,
            arcade.key.SPACE: False,
        }

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list, GRAVITY
        )

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame
        arcade.start_render()

        # Call draw() on all your sprite lists below

        arcade.draw_text(
            "coins: " + str(self.player.get_coins()),
            20,
            self.display_height - 40,
            arcade.color.GOLD,
            20,
        )

        self.player_list.draw()
        self.coin_list.draw()
        self.wall_list.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        self.player_list.update()

        self.player_list.update_animation()

        self.physics_engine.update()

        if self.keys_pressed[arcade.key.D] and not self.keys_pressed[arcade.key.A]:
            self.player.move(1)
        elif self.keys_pressed[arcade.key.A] and not self.keys_pressed[arcade.key.D]:
            self.player.move(-1)
        else:
            self.player.stop()

        if self.keys_pressed[arcade.key.SPACE]:
            self.player.jump(self.physics_engine.can_jump())

        coins_hit_list = arcade.check_for_collision_with_list(
            self.player, self.coin_list
        )

        for coin in coins_hit_list:
            coin.effect(self.player)
            coin.remove_from_sprite_lists()

    def on_key_press(self, key, key_modifiers):
        self.keys_pressed[key] = True

    def on_key_release(self, key, key_modifiers):
        self.keys_pressed[key] = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        self.player.center_x = x
        self.player.center_y = y

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass

    def add_sprite(self, sprite, x, y):
        sprite.width = self.sprite_width
        sprite.height = self.sprite_height
        sprite.center_x = x * self.sprite_width
        sprite.center_y = (self.map_height - y) * self.sprite_height
        return sprite

    def load_map(self, map_file):

        # find longest line and how many lines
        with open(map_file) as map:
            biggest = 0

            for i, line in enumerate(map):
                if len(line) > biggest:
                    biggest = len(line)

            self.map_height = i
            self.sprite_height = self.display_height / self.map_height

            self.map_width = biggest - 1
            self.sprite_width = self.display_width / self.map_width

        with open(map_file) as map:

            for y, line in enumerate(map):
                for x, letter in enumerate(line):

                    if letter == "X":
                        self.wall_list.append(
                            self.add_sprite(
                                arcade.Sprite(":resources:images/tiles/grassMid.png"),
                                x,
                                y,
                            )
                        )

                    elif letter == "C":
                        self.coin_list.append(self.add_sprite(Coin(0, 0), x, y))


def main():
    """Main method"""
    display_width, display_height = arcade.window_commands.get_display_size()
    display_width = int(display_width * 0.8)
    display_height = int(display_height * 0.8)

    window = arcade.Window(display_width, display_height, "Octopus Game")
    start_screen = Start_Screen(window, display_width, display_height)
    start_screen.setup()

    # game = Octopus_Game(display_width, display_height, "maleAdventurer")
    # game.setup()
    window.show_view(start_screen)

    arcade.run()


if __name__ == "__main__":
    main()
