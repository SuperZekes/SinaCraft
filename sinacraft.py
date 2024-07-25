from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

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

for z in range(20):
    for x in range(20):
        voxel = Voxel(position=(x, 0, z))

player = FirstPersonController()
player.speed = 5

window.fullscreen = False
mouse.locked = True

def update():
    global selected_color_index
    
    if held_keys['escape']:
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

app.run()
