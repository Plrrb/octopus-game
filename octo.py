# KISS:
# keep it simple, stupid
# OR:
# keep it separate, stupid

# A Base Class should only only share the similarities between the sub classes

# functions should only do one thing
#   classes should only be one thing


import socket
import sys
import time
import timeit
import arcade
import arcade.gui

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1000
GRAVITY = 9.8 / 40
DAMAGE = 10


from network import Network


def func_timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter() - start

        print(func.__name__, end)

        return result

    return wrapper


class Framerate:
    def __init__(self):
        # --- Variables for our statistics

        # Time for on_update
        self.processing_time = 0

        # Time for on_draw
        self.draw_time = 0

        # Variables used to calculate frames per second
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None

    def start_frame(self):
        # Start timing how long this takes
        self.start_time = timeit.default_timer()

        # --- Calculate FPS

        fps_calculation_freq = 60
        # Once every 60 frames, calculate our FPS
        if self.frame_count % fps_calculation_freq == 0:
            # Do we have a start time?
            if self.fps_start_timer is not None:
                # Calculate FPS
                total_time = timeit.default_timer() - self.fps_start_timer
                self.fps = fps_calculation_freq / total_time
            # Reset the timer
            self.fps_start_timer = timeit.default_timer()
        # Add one to our frame count
        self.frame_count += 1

    def end_frame(self):
        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, WINDOW_HEIGHT - 25, arcade.color.BLACK, 18)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, WINDOW_HEIGHT - 50, arcade.color.BLACK, 18)

        if self.fps is not None:
            output = f"FPS: {self.fps:.0f}"
            arcade.draw_text(output, 20, WINDOW_HEIGHT - 75, arcade.color.BLACK, 18)

        # Stop the draw timer, and calculate total on_draw time.
        self.draw_time = timeit.default_timer() - self.start_time

    def start_update(self):
        self.start_time = timeit.default_timer()

    def end_update(self):
        self.processing_time = timeit.default_timer() - self.start_time

    def draw(self):
        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, WINDOW_HEIGHT - 25, arcade.color.BLACK, 18)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, WINDOW_HEIGHT - 50, arcade.color.BLACK, 18)

        if self.fps is not None:
            output = f"FPS: {self.fps:.0f}"
            arcade.draw_text(output, 20, WINDOW_HEIGHT - 75, arcade.color.BLACK, 18)

        # Stop the draw timer, and calculate total on_draw time.
        self.draw_time = timeit.default_timer() - self.start_time


class Character_Chooser(arcade.View):
    def __init__(self, socket):
        super().__init__()
        self.characters = (
            ":resources:images/animated_characters/male_adventurer/maleAdventurer_",
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_",
            ":resources:images/animated_characters/female_person/femalePerson_",
            ":resources:images/animated_characters/male_person/malePerson_",
            ":resources:images/animated_characters/robot/robot_",
            ":resources:images/animated_characters/zombie/zombie_",
        )

        self.char = None

        self.buttons = []
        self.make_buttons()

        self.network = Network(socket, self.on_recv, self.on_send)

    def choose_character(self, char):
        self.char = char
        self.network.run()

    def on_send(self):
        return {"character": self.char}

    def on_recv(self, database):

        if 0 in database and "character" in database[0]:
            character = database[0]["character"]

        elif 1 in database and "character" in database[1]:
            character = database[1]["character"]
        else:
            return

        game = Online_Game(self.char, character, self.network.socket)

        self.network.stop()
        self.window.show_view(game)

    def make_buttons(self):
        self.ui_manager = arcade.gui.UIManager(self.window)

        box = arcade.gui.UIBoxLayout(vertical=False)

        for i in self.characters:
            t = arcade.load_texture(i + "idle.png")
            b = arcade.gui.UITextureButton(texture=t)
            b.on_click = lambda *x, key=i: self.choose_character(key)
            box.add(b)

        self.ui_manager.add(arcade.gui.UIAnchorWidget(child=box))

    def on_show_view(self):
        """Called when switching to this view"""
        arcade.set_background_color(arcade.color.ORANGE_PEEL)
        self.ui_manager.enable()

    def on_hide_view(self):
        # This unregisters the manager's UI handlers,
        # Handlers respond to GUI button clicks, etc.
        self.ui_manager.disable()
        print("charicter chooser over")

    def on_draw(self):
        self.ui_manager.draw()


class Base_Game(arcade.View):
    def __init__(self, character_url):
        super().__init__()
        arcade.set_background_color(arcade.color.ORANGE_PEEL)

        self.controls = Boolean_Input()
        self.wall_list = arcade.SpriteList()

        self.player = Controllable_Player(character_url)
        self.time_since_last_shot = 0

        self.load_map("map.txt")
        self.make_physics_engine()
        self.fps_counter = Framerate()

    def on_draw(self):
        # self.fps_counter.start_frame()
        arcade.start_render()
        # self.fps_counter.draw()

        self.wall_list.draw()
        self.draw_health_bar(50, WINDOW_HEIGHT - 15, self.player.health)
        self.player.draw()

        # self.fps_counter.end_frame()

    def draw_health_bar(self, x, y, health):
        arcade.draw_rectangle_filled(x, y, 100, 30, arcade.color.RED)

        arcade.draw_rectangle_filled(
            x - (100 - health), y, health - (100 - health), 30, arcade.color.GREEN
        )

    def on_update(self, delta_time):
        self.fps_counter.start_update()
        self.physics_engine.update()
        self.update_player_contols()

        self.player.bullet_collision_check(self.wall_list)

        self.player.update()
        self.player.update_texture(self.cached_player_can_jump)
        self.player_can_jump_was_cached = False
        self.time_since_last_shot += delta_time
        self.fps_counter.end_update()

    def cached_player_can_jump(self):
        if not self.player_can_jump_was_cached:
            self.player_can_jump_was_cached = True
            return self.physics_engine.can_jump()

    def update_player_contols(self):

        if self.controls.get(arcade.key.C):
            self.try_shoot()

        right = self.controls.get(arcade.key.D) or self.controls.get(arcade.key.RIGHT)
        left = self.controls.get(arcade.key.A) or self.controls.get(arcade.key.LEFT)

        if right and not left:
            self.player.move_right()

        elif left and not right:
            self.player.move_left()

        else:
            self.player.stop_moving()

        if self.controls.get(arcade.key.SPACE) and self.cached_player_can_jump():
            self.player.jump()

    def on_key_press(self, key, modifiers):
        self.controls.press(key)

    def on_key_release(self, key, modifiers):
        self.controls.release(key)

    def on_mouse_press(self, x, y, button, modifiers):
        self.try_shoot()

    def try_shoot(self):
        if self.time_since_last_shot > 1:
            self.player.shoot()
            self.time_since_last_shot = 0

    def make_physics_engine(self):
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list, GRAVITY
        )

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
            self.sprite_height = WINDOW_HEIGHT / self.map_height

            self.map_width = biggest - 1
            self.sprite_width = WINDOW_WIDTH / self.map_width

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


class Online_Game(Base_Game):
    def __init__(self, player1, player2, socket):
        super().__init__(player1)
        self.player2 = Online_Player(player2)

        self.network = Network(socket, self.on_recv, self.on_send)
        self.network.run()

    def on_send(self):
        return {
            "player_data": (
                self.player.center_x,
                self.player.center_y,
                self.player.texture_number,
                self.player.get_bullet_positions(),
            ),
            "other_player_data": (self.player2.health,),
        }

    def on_recv(self, database):
        for key in database:
            if "player_data" not in database[key]:
                return
            else:
                player_data = database[key]["player_data"]
                self.player2.set_data(*player_data)

                if self.player.health > database[key]["other_player_data"][0]:

                    self.player.sub_health(
                        self.player.health - database[key]["other_player_data"][0]
                    )

        # set_data() could kinda animate the player2 over to the new pos so it doesnt look choppy

    def on_update(self, delta_time):
        super().on_update(delta_time)

        # check for collsion with the online player and remove OUR Bullet

        for hit in self.player2.check_for_hit_with_bullets(self.player.bullets):
            self.player.bullets.remove(hit)

        self.player2.update()
        # print("player1: ", self.player.health)
        # print("player2: ", self.player2.health)

    def on_draw(self):
        super().on_draw()
        self.draw_health_bar(WINDOW_WIDTH - 50, WINDOW_HEIGHT - 15, self.player2.health)
        self.player2.draw()


class Boolean_Input:
    __slots__ = ("inputs",)

    def __init__(self):
        self.inputs = {None: None}

    def get(self, input_name):
        return self.inputs.get(input_name, None)

    def press(self, input_name):
        self.inputs[input_name] = True

    def release(self, input_name):
        self.inputs[input_name] = False


class Base_Player(arcade.Sprite):
    def __init__(self, character_url):
        super().__init__()
        self.dead = False
        self.texturess = self.make_players_textures(character_url)
        self.change_texture(0, 0, 0)
        self.bullets = arcade.SpriteList()
        self.health = 100
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")
        self.death_sound = arcade.load_sound(":resources:sounds/gameover4.wav")

    def draw(self):
        super().draw()
        self.bullets.draw()

    def update(self):
        self.bullets.update()

    def change_texture(self, is_walk, index, direction):
        self.texture_number = is_walk, index, direction
        self.texture = self.texturess[is_walk][index][direction]

    def make_players_textures(self, url):
        return (
            (
                (arcade.load_texture_pair(url + "idle.png")),
                (arcade.load_texture_pair(url + "jump.png")),
                (arcade.load_texture_pair(url + "fall.png")),
            ),
            (
                (arcade.load_texture_pair(url + "walk0.png")),
                (arcade.load_texture_pair(url + "walk2.png")),
                (arcade.load_texture_pair(url + "walk3.png")),
                (arcade.load_texture_pair(url + "walk4.png")),
                (arcade.load_texture_pair(url + "walk5.png")),
                (arcade.load_texture_pair(url + "walk6.png")),
                (arcade.load_texture_pair(url + "walk7.png")),
            ),
            (arcade.load_texture_pair(f"images/{url.split('/')[-1]}dead.png"),),
        )

    def get_bullet_positions(self):
        return [bullet.get_position() for bullet in self.bullets]

    def sub_health(self, value):
        print(self.health)
        self.health -= value

        if self.health <= 0:
            self.die()
            return
        self.hit_sound.play()

    def die(self):
        print("im dead")
        if self.dead:
            return

        self.dead = True
        self.death_sound.play()

    def check_for_hit_with_bullets(self, bullets):
        hits = arcade.check_for_collision_with_list(self, bullets)

        if len(hits) > 0:
            self.sub_health(DAMAGE * len(hits))

        return hits

    def bullet_collision_check(self, sprite_list):
        bullet_hits = []

        for bullet in self.bullets:
            if arcade.check_for_collision_with_list(
                bullet, sprite_list
            ) or not bullet.inbounds(WINDOW_WIDTH, WINDOW_HEIGHT):
                bullet_hits.append(bullet)

        for hit in bullet_hits:
            self.bullets.remove(hit)


class Bullet(arcade.Sprite):
    def __init__(self, start_x, start_y, vel_x, vel_y):
        super().__init__(":resources:images/enemies/saw.png", scale=0.5)
        self.center_x = start_x
        self.center_y = start_y

        self.change_x = vel_x
        self.change_y = vel_y

    def get_position(self):
        return self.center_x, self.center_y

    def inbounds(self, width, height):
        return (
            self.center_x >= 0
            and self.center_y >= 0
            and self.center_x <= width
            and self.center_y <= height
        )


class Controllable_Player(Base_Player):
    def __init__(self, character_url):
        super().__init__(character_url)

        # left = 0, right = 1
        self.direction = 0
        self.max_speed = 5
        self.animation_speed_reducer = 10
        self.walk_index = 0
        self.friction = 0.5
        self.acceleration_reducer = 2
        self.jump_power = 10

        self.center_x = 500
        self.center_y = 500

        self.change_texture(0, 0, 0)
        self.load_sounds()

    def shoot(self):
        if self.direction == 0:
            vel_y = 10
        else:
            vel_y = -10

        b = Bullet(self.center_x, self.center_y, vel_y, 0)
        self.bullets.append(b)

    # def draw(self):
    #     super().draw()

    # def update(self):
    #     super().update()
    def load_sounds(self):
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def update_texture(self, on_ground):
        if self.dead:
            self.change_texture(2, 0, self.direction)
            return

        self.update_direction()

        # update 0 = idle, 1 = jump, 2 =fall
        if self.change_y > 0:
            self.change_texture(0, 1, self.direction)

        elif self.change_y < 0:
            self.change_texture(0, 2, self.direction)

        elif 0.01 > self.change_x > -0.01 and on_ground():
            self.change_texture(0, 0, self.direction)
            self.reset_walk()

        else:
            self.update_walk()

    def update_walk(self):
        self.walk_index += 1

        if self.walk_index > len(self.texturess[1]) * self.animation_speed_reducer - 1:
            self.reset_walk()

        frame = self.walk_index // self.animation_speed_reducer

        self.change_texture(1, frame, self.direction)

    def update_direction(self):
        if self.change_x == 0:
            return
        elif self.change_x > 0:
            self.direction = 0
        else:
            self.direction = 1

    def reset_walk(self):
        self.walk_index = 0

    def jump(self):
        self.change_y += self.jump_power
        arcade.play_sound(self.jump_sound)

    def movement_math(self):
        return (abs(self.change_x) - self.max_speed) / self.acceleration_reducer

    def move_left(self):
        self.change_x += self.movement_math()

    def move_right(self):
        self.change_x -= self.movement_math()

    def stop_moving(self):
        self.change_x *= self.friction


class Online_Player(Base_Player):
    def update(self):
        super().update()
        self.change_texture(*self.texture_number)

    def set_data(self, x, y, texture_number, bullets_pos):
        self.center_x = x
        self.center_y = y

        self.texture_number = texture_number

        self.bullets = arcade.SpriteList()

        for pos in bullets_pos:
            self.bullets.append(
                Bullet(pos[0], pos[1], 0, 0),
            )


def main():
    # player2_ip = "162.196.90.150"
    ip = sys.argv[1]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Trying to connect...")
    server_socket.connect((ip, 5555))
    print("Connected!")

    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Octopus Game")
    screen = Character_Chooser(server_socket)

    window.show_view(screen)
    arcade.run()


def game_with_no_networking():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Octopus Game")
    g = Base_Game(
        ":resources:images/animated_characters/male_adventurer/maleAdventurer_"
    )

    window.show_view(g)
    arcade.run()


if __name__ == "__main__":
    main()
    # game_with_no_networking()
