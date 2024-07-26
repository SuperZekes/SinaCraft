from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import os
import pickle

app = Ursina()

colors = [
    color.red, color.orange, color.yellow, color.green, 
    color.azure, color.blue, color.white, color.pink, color.brown
]

selected_color_index = 0

# Load sound effects
place_sound = Audio('assets/place_sound.mp3', autoplay=False)
break_sound = Audio('assets/break_sound.mp3', autoplay=False)

hotbar = Entity(parent=camera.ui, model='quad', texture='white_cube', 
                scale=(0.9, 0.1), color=color.black, position=(0, -0.45, 0))

hotbar_slots = []
for i, col in enumerate(colors):
    slot = Entity(parent=hotbar, model='quad', texture='white_cube',
                  scale=(0.1, 0.1), position=(i * 0.11 - 0.44, 0, -0.1),
                  color=col)
    hotbar_slots.append(slot)

highlight = Entity(parent=hotbar, model='quad', scale=(0.11, 0.11),
                   color=color.white.tint(-0.5), position=(selected_color_index * 0.11 - 0.44, 0, -0.2))

class Voxel(Button):
    def __init__(self, position=(0, 0, 0), block_color=color.white):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube',
            color=block_color,
            highlight_color=color.lime,
        )

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                # Play place sound
                place_sound.play()
                voxel = Voxel(position=self.position + mouse.normal, block_color=colors[selected_color_index])
            if key == 'left mouse down':
                # Play break sound
                break_sound.play()
                destroy(self)

class Menu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.create_world_button = Button(text='Create World', scale=(0.3, 0.1), position=(0, 0.1), color=color.azure)
        self.load_world_button = Button(text='Load World', scale=(0.3, 0.1), position=(0, -0.1), color=color.green)
        self.exit_button = Button(text='Exit', scale=(0.3, 0.1), position=(0, -0.3), color=color.red)
        
        self.create_world_button.on_click = self.create_world
        self.load_world_button.on_click = self.load_world_menu
        self.exit_button.on_click = application.quit

        self.worlds_list = None
        self.load_panel = None

    def create_world(self):
        self.disable_buttons()
        mouse.locked = True
        generate_world('new_world')
        
    def load_world_menu(self):
        if self.worlds_list:
            for btn in self.worlds_list:
                btn.disable()

        self.worlds_list = []
        save_path = 'saves'
        if not os.path.exists(save_path):
            return
        
        self.load_panel = Entity(parent=camera.ui, model='quad', scale=(0.6, 0.8), color=color.gray, position=(0, 0, -1))

        for i, file_name in enumerate(os.listdir(save_path)):
            if file_name.endswith('.world'):
                button = Button(
                    text=file_name[:-6],
                    parent=self.load_panel,
                    scale=(0.4, 0.08),
                    position=(0, 0.35 - (i * 0.1)),
                    color=color.light_gray
                )
                button.on_click = Func(self.load_world_data, file_name)
                self.worlds_list.append(button)

        close_button = Button(text='Close', parent=self.load_panel, scale=(0.4, 0.08), position=(0, -0.4), color=color.red)
        close_button.on_click = Func(self.close_load_menu)

    def close_load_menu(self):
        if self.load_panel:
            destroy(self.load_panel)

    def load_world_data(self, file_name):
        path = f'saves/{file_name}'
        if os.path.exists(path):
            for e in scene.entities:
                if isinstance(e, Voxel):
                    destroy(e)

            with open(path, 'rb') as file:
                voxels_data = pickle.load(file)
                for pos, col_index in voxels_data:
                    voxel = Voxel(position=pos, block_color=colors[col_index])
        
        self.disable_buttons()
        self.close_load_menu()  # Close the load world menu
        mouse.locked = True
        player.enable()
        player.world_name = file_name

    def disable_buttons(self):
        # Hide the menu buttons
        self.create_world_button.disable()
        self.load_world_button.disable()
        self.exit_button.disable()
        if self.worlds_list:
            for button in self.worlds_list:
                button.disable()

    def enable_buttons(self):
        # Show the menu buttons
        self.create_world_button.enable()
        self.load_world_button.enable()
        self.exit_button.enable()
        if self.worlds_list:
            for button in self.worlds_list:
                button.enable()

def generate_world(world_name):
    global player
    player.enable()
    player.world_name = f'{world_name}.world'
    for z in range(20):
        for x in range(20):
            voxel = Voxel(position=(x, 0, z))

player = FirstPersonController()
player.speed = 5
player.disable()
player.world_name = 'new_world.world'  # Default world name

window.fullscreen = False
mouse.locked = False

def update():
    global selected_color_index
    
    if held_keys['escape']:
        if player.enabled:
            confirm_quit()
        else:
            application.quit()

    if player.y < -30:
        player.position = (10, 10, 10)

    for i in range(9):
        if held_keys[str(i+1)]:
            selected_color_index = i
            break

    if held_keys['scroll up']:
        selected_color_index = (selected_color_index + 1) % len(colors)
    elif held_keys['scroll down']:
        selected_color_index = (selected_color_index - 1) % len(colors)

    highlight.x = selected_color_index * 0.11 - 0.44

def save_world():
    save_path = 'saves'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    voxels_data = [(v.position, colors.index(v.color)) for v in scene.entities if isinstance(v, Voxel)]
    world_file_path = f'saves/{player.world_name}'
    with open(world_file_path, 'wb') as file:
        pickle.dump(voxels_data, file)
    application.quit()

def confirm_quit():
    def yes_action():
        save_world()

    def no_action():
        application.quit()

    # Show the mouse cursor
    mouse.locked = False

    panel = Entity(parent=camera.ui, model='quad', scale=(0.5, 0.3), color=color.black)
    text_entity = Text("Save before quitting?", parent=panel, scale=2, position=(-0.25, 0.1))
    yes_button = Button(text='Yes', parent=panel, scale=(0.2, 0.1), position=(-0.15, -0.1), color=color.azure)
    no_button = Button(text='No', parent=panel, scale=(0.2, 0.1), position=(0.15, -0.1), color=color.orange)

    yes_button.on_click = Func(yes_action)
    no_button.on_click = Func(no_action)

menu = Menu()

app.run()
