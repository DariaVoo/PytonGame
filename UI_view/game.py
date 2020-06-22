import arcade
import os

# Число для уменьшения изображения
from UI_view.gameOver import GameOverView
from ability.abilityFactory import ability_factory
from constants import GRAVITY
from enemies.enemyFactory import create_enemies
from level import create_lvl, END_OF_MAP
from player import Player
from position import Position
from scroll_manage import scroll_manage


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__()
        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.time_taken = 0
        # Sprite lists
        self.coin_list: arcade.SpriteList = None
        self.wall_list: arcade.SpriteList = None
        self.player_list: arcade.SpriteList = None
        self.enemy_list: arcade.SpriteList = None
        self.explosions_list = None
        self.ability_list: arcade.SpriteList = None  # -> player

        # Set up the player
        self.player_sprite: Player = None
        self.physics_engine = None

        self.score = 0
        self.game_over = False

        self.level = 1
        self.max_level = 2

        # sсroll (move camera)
        self.view_left = 0
        self.view_bottom = 0

        # Pre-load the animation frames. We don't do this in the __init__
        # of the explosion sprite because it
        # takes too long and would cause the game to pause.
        self.explosion_texture_list = []

        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256
        file_name = ":resources:images/spritesheets/explosion.png"

        # Load the explosions from a sprite sheet
        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, count)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.coin_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()  # Список стен, через которые игрок не может проходить
        self.enemy_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()

        # ДОЛЖНО ГЕНЕРИРОВАТЬСЯ
        pos_ability = [Position(200, 400, 1), Position(700, 300, 2)]

        # Set up the player
        self.player_sprite = Player()
        self.player_list.append(self.player_sprite)
        # Set up the enemies
        self.enemy_list = create_enemies([1, 2, 3])
        self.ability_list = ability_factory(pos_ability)

        # Создаём уровень
        create_lvl(self.wall_list, self.coin_list, self.level)

        # Физический движок для платформера
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        """
        Render the screen.
        """
        # Очищаем окно и начинаем отрисовку
        arcade.start_render()

        # Draw all the sprites.
        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.explosions_list.draw()
        self.ability_list.draw()

        self.player_sprite.ability_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        self.player_sprite.move(key, self.physics_engine.can_jump())
        if key == arcade.key.SPACE:
            self.player_sprite.shot()
        elif key == arcade.key.ESCAPE:
            self.game_over = True
        elif key == arcade.key.ENTER:
            self.player_sprite.next_ability()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        self.player_sprite.stop(key)


    def on_update(self, delta_time):
        """ Movement and game logic """
        self.time_taken += delta_time

        # Обновляем игрока используя физический движок
        self.physics_engine.update()

        # Проверяем перешли ли мы на новый уровень
        if self.player_sprite.right >= END_OF_MAP:
            if self.level < self.max_level:
                self.level += 1
                create_lvl(self.wall_list, self.coin_list, self.level)
                self.player_sprite.center_x = 128
                self.player_sprite.center_y = 64
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
            else:
                self.game_over = True

        self.player_sprite.ability_list.update()
        self.explosions_list.update()

        # Check each enemy
        for enemy in self.enemy_list:
            enemy.move(self.wall_list)

        # Move the enemies
        self.enemy_list.update()

        # See if the player hit a worm. If so, game over.
        if len(arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)) > 0:
            self.game_over = True

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)
        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            self.score += 1
            self.window.total_score += 1

        # Попали ли во врага
        self.score = self.player_sprite.attack(self.enemy_list, self.score,
                                               self.explosion_texture_list, self.explosions_list)

        # Подобрал ли новую способность
        for weapon in self.ability_list:
            if arcade.check_for_collision(weapon, self.player_sprite):
                self.ability_list.remove(weapon)
                self.player_sprite.add_ability(weapon)
                # добавить это свойство в плеера


        # --- Manage Scrolling ---
        # Track if we need to change the view port
        self.view_left, self.view_bottom = scroll_manage(self.player_sprite,
                                                         self.view_left, self.view_bottom)

        # Если игра закончилась - меняем view
        if self.game_over:
            view = GameOverView()
            view.time_taken = self.time_taken
            self.window.show_view(view)
