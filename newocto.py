# KISS:
# keep it simple, stupid
# OR:
# keep it separate, stupid

# A Base Class should only only share the similarities between the sub classes

# functions should only do one thing
#   classes should only be one thing

import threading
import arcade
import socket
import sys
import pickle

GRAVITY = 9.8 / 20


class Network:
    def __init__(self, on_recv, on_send):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.on_recv = on_recv
        self.on_send = on_send

    def connect(self, ip):
        print("Trying to connect...")
        self.socket.connect((ip, 5555))
        print("Connected!")

    def get_incoming_data(self):
        return self.incoming_data

    def run(self):
        t = threading.Thread(target=self.listen)
        t.start()

    def listen(self):
        try:
            while True:
                data = pickle.dumps(self.on_send())
                self.socket.send(data)

                incoming_data = self.socket.recv(2048)
                incoming_data = pickle.loads(incoming_data)

                if len(incoming_data) != 0 and incoming_data[0] is not None:
                    self.on_recv(incoming_data)

        except socket.error:
            print("Server Error!")
            self.socket.close()
            return

    @staticmethod
    def get_local_ip():
        return socket.gethostbyname(socket.gethostname())


class Base_Game(arcade.View):
    def __init__(self, character_url):
        super().__init__()

        self.controls = Boolean_Input()

        self.make_walls()
        self.player = Controllable_Player(character_url)
        self.make_physics_engine()

    def on_draw(self):
        arcade.start_render()

        self.player.draw()
        self.wall_list.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.update_player_contols()

        self.player.update()
        self.player.update_texture(self.cached_player_can_jump)
        self.player_can_jump_was_cached = False

    def cached_player_can_jump(self):
        if not self.player_can_jump_was_cached:
            self.player_can_jump_was_cached = True
            return self.physics_engine.can_jump()

    def update_player_contols(self):
        right = self.controls.get(arcade.key.D)
        left = self.controls.get(arcade.key.A)

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


class Online_Game(Base_Game):
    def __init__(self, character_url, player2_ip):
        super().__init__(character_url)

        self.network = Network(self.on_recv, self.on_send)
        self.network.connect(player2_ip)

        self.player2 = Online_Player(
            ":resources:images/animated_characters/robot/robot_"
        )

        self.network.run()

    def on_draw(self):
        super().on_draw()
        self.player2.draw()

    def on_send(self):
        return self.player.center_x, self.player.center_y, self.player.texture_number

    def on_recv(self, data):

        data = data[0]
        print(data)
        self.player2.set_data(data[0], data[1], data[2])

    def on_update(self, delta_time):
        super().on_update(delta_time)
        self.player2.update()


class Boolean_Input:
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
        self.texturess = self.make_players_textures(character_url)
        self.change_texture(0, 0, 0)

    def change_texture(self, is_walk, index, direction):
        self.texture_number = is_walk, index, direction
        self.texture = self.texturess[is_walk][index][direction]

    def make_players_textures(self, url):
        return (
            (arcade.load_texture_pair(url + "idle.png")),
            (arcade.load_texture_pair(url + "jump.png")),
            (arcade.load_texture_pair(url + "fall.png")),
        ), (
            (arcade.load_texture_pair(url + "walk0.png")),
            (arcade.load_texture_pair(url + "walk2.png")),
            (arcade.load_texture_pair(url + "walk3.png")),
            (arcade.load_texture_pair(url + "walk4.png")),
            (arcade.load_texture_pair(url + "walk5.png")),
            (arcade.load_texture_pair(url + "walk6.png")),
            (arcade.load_texture_pair(url + "walk7.png")),
        )


class Controllable_Player(Base_Player):
    def __init__(self, character_url):
        super().__init__(character_url)

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

        self.change_texture(0, 0, 0)
        self.load_sounds()

    def load_sounds(self):
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

    def update_texture(self, on_ground):
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

    def set_data(self, x, y, texture_number):
        self.center_x = x
        self.center_y = y

        self.texture_number = texture_number


def main():
    # player2_ip = "162.196.90.150"
    player2_ip = sys.argv[1]

    window = arcade.Window(1000, 1000, "Octopus Game")
    screen = Online_Game(
        ":resources:images/animated_characters/male_adventurer/maleAdventurer_",
        player2_ip,
    )

    window.show_view(screen)
    arcade.run()


if __name__ == "__main__":
    main()
