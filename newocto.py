# KISS:
# keep it simple, stupid
# OR:
# keep it separate, stupid


# functions should only do one thing
#   classes should only be one thing

import threading
import arcade
import socket
import sys

GRAVITY = 9.8 / 20


class Character_Texture_System:
    def __init__(self, url):
        self.textures_tuple = self.load_textures(url)
        self.walk_textures = self.load_walk_textures(url)

        self.texture = self.textures_tuple[0][0]

    def set_texture_state(self, texture_num):
        self.texture = self.textures_tuple[texture_num][self.direction]

    def update_texture(self, on_ground):
        self.update_direction()

        # update 0 = idle, 1 = jump, 2 =fall
        if self.change_y > 0:
            self.set_texture_state(1)

        elif self.change_y < 0:
            self.set_texture_state(2)

        elif 0.01 > self.change_x > -0.01 and on_ground:
            self.set_texture_state(0)
            self.reset_walk()

        else:
            self.update_walk()

    def update_walk(self):
        self.walk_index += 1

        if self.walk_index > len(self.walk_textures) * self.animation_speed_reducer - 1:
            self.reset_walk()

        frame = self.walk_index // self.animation_speed_reducer

        self.texture = self.walk_textures[frame][self.direction]

    def update_direction(self):
        if self.change_x == 0:
            pass
        elif self.change_x > 0:
            self.direction = 0
        else:
            self.direction = 1

    def reset_walk(self):
        self.walk_index = 0

    @staticmethod
    def load_textures(url):
        return (
            (arcade.load_texture_pair(url + "idle.png")),
            (arcade.load_texture_pair(url + "jump.png")),
            (arcade.load_texture_pair(url + "fall.png")),
        )

    @staticmethod
    def load_walk_textures(url):
        return (
            (arcade.load_texture_pair(url + "walk0.png")),
            (arcade.load_texture_pair(url + "walk2.png")),
            (arcade.load_texture_pair(url + "walk3.png")),
            (arcade.load_texture_pair(url + "walk4.png")),
            (arcade.load_texture_pair(url + "walk5.png")),
            (arcade.load_texture_pair(url + "walk6.png")),
            (arcade.load_texture_pair(url + "walk7.png")),
        )


class Controls:
    def __init__(self):
        self.inputs = {None: None}

    def get(self, input_name):
        return self.inputs.get(input_name, None)

    def press(self, input_name, value):
        self.inputs[input_name] = value


class Player(arcade.Sprite, Character_Texture_System):
    def __init__(self, url):
        arcade.Sprite.__init__(self)
        Character_Texture_System.__init__(self, url)

        # left = 0, right = 1
        self.direction = 0
        self.max_speed = 3
        self.animation_speed_reducer = 10
        self.walk_index = 0
        self.friction = 0.5
        self.acceleration_reducer = 2
        self.jump_power = 10

        self.center_x = 500
        self.center_y = 500

        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

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


class Main_View(arcade.View):
    def __init__(self, character_url):
        super().__init__()

        self.controls = Controls()

        self.make_walls()
        self.player = Player(character_url)
        self.make_physics_engine()

        self.left_pressed_before_right = False
        self.right_pressed_before_left = False

    def on_draw(self):
        arcade.start_render()

        self.player.draw()
        self.wall_list.draw()

    def on_update(self, delta_time):
        self.cached_player_can_jump = self.physics_engine.can_jump()

        self.update_player_contols()

        self.player.update()

        self.player.update_texture(self.cached_player_can_jump)

        self.physics_engine.update()

    def update_player_contols(self):
        right = self.controls.get(arcade.key.D)
        left = self.controls.get(arcade.key.A)

        if right and not left:
            self.player.move_right()

        elif left and not right:
            self.player.move_left()

        else:
            self.player.stop_moving()

        if self.controls.get(arcade.key.SPACE) and self.cached_player_can_jump:
            self.player.jump()

    def on_key_press(self, key, modifiers):
        self.controls.press(key, True)

    def on_key_release(self, key, modifiers):
        self.controls.press(key, False)

    def on_mouse_press(self, x, y, button, modifiers):
        self.player.set_position(x, y)

    def make_walls(self):
        wall = arcade.Sprite(
            ":resources:images/tiles/grassMid.png",
        )

        wall.width = 1000
        wall.center_x = 1000 / 2
        wall.center_y = 0

        self.wall_list = arcade.SpriteList()
        self.wall_list.append(wall)

    def make_physics_engine(self):
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list, GRAVITY
        )


class Online_Game(Main_View):
    def __init__(self, character_url, socket):
        super().__init__(character_url)
        self.socket = socket

        self.player2 = arcade.Sprite(
            ":resources:images/animated_characters/robot/robot_idle.png"
        )

        t = threading.Thread(target=self.recv_other_players_pos, daemon=True)
        t.start()

    def on_draw(self):
        super().on_draw()

        self.player2.draw()

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.player2.update()

    def send_our_pos(self):
        self.socket.send(f"{self.player.center_x},{self.player.center_y}".encode())

    def recv_other_players_pos(self):
        try:
            while True:
                self.send_our_pos()
                data = self.socket.recv(512)
                data = data.decode()
                data = eval(data)
                self.player2.center_x, self.player2.center_y = data

        except ConnectionResetError:
            print("Server Error!")
            self.socket.close()
            arcade.exit()
            return


def make_connection(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # player2_ip = "162.196.90.150"

    print("Trying to connect...")
    client_socket.connect((ip, port))
    print("Connected!")

    return client_socket


def main():
    client_socket = make_connection(sys.argv[1], 5555)

    window = arcade.Window(1000, 1000, "Octopus Game")
    screen = Online_Game(
        ":resources:images/animated_characters/male_adventurer/maleAdventurer_",
        client_socket,
    )

    window.show_view(screen)
    arcade.run()


if __name__ == "__main__":
    main()
