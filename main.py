import pyglet
from networktables import NetworkTables

FIELD_WIDTH = 16.46
FIELD_HEIGHT = 8.23
FIELD_PIXEL_WIDTH = 100
FIELD_PIXEL_HEIGHT = FIELD_HEIGHT*FIELD_PIXEL_WIDTH/FIELD_WIDTH

ROBORIO_IP = "10.47.74.2"

STANDBY_STATUS_STRING = f"No connection, waiting for {ROBORIO_IP}"

GRAY = (127, 127, 127)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

dashboard = NetworkTables.getTable("SmartDashboard")
components = NetworkTables.getTable("components")
field = dashboard.getSubTable("Field")
indexer = components.getSubTable("indexer")

window = pyglet.window.Window(caption="Drop Bears Dashboard", resizable=True)

is_running = False
uptime = 0.0

batch = pyglet.graphics.Batch()

status_padding = 10
status_label = pyglet.text.Label(STANDBY_STATUS_STRING, font_size=72, anchor_y="top", x=100, y=window.height-status_padding, width=window.width, batch=batch)

ball_rad = 100
ball_y = 400
ball_outlines = [
    pyglet.shapes.Circle(150, window.height - ball_y, ball_rad, batch=batch, color=GRAY), # tunnel
    pyglet.shapes.Circle(400, window.height - ball_y, ball_rad, batch=batch, color=GRAY), # chimney
    pyglet.shapes.Circle(750, window.height - ball_y, ball_rad, batch=batch, color=GRAY), # trap
]
ball_indicators = [
    pyglet.shapes.Circle(150, window.height - ball_y, ball_rad-5, batch=batch, color=BLACK), # tunnel
    pyglet.shapes.Circle(400, window.height - ball_y, ball_rad-5, batch=batch, color=BLACK), # chimney
    pyglet.shapes.Circle(750, window.height - ball_y, ball_rad-5, batch=batch, color=BLACK), # trap
]
balls_seperator = pyglet.shapes.Rectangle(572.5, window.height-ball_y-ball_rad, 5, 200, color=GRAY, batch=batch)

robot = pyglet.shapes.Rectangle(0, 0, 40, 40, batch=batch)
robot.anchor_position = 20, 20
robot_facing = pyglet.shapes.Rectangle(0, 0, 20, 10, color=RED, batch=batch)
robot_facing.anchor_position = 0, 5

goal = pyglet.shapes.Circle(window.width / 2, window.height / 2, 60, batch=batch)
effective_goal = pyglet.shapes.Circle(window.width / 2, window.height / 2, 60, color=YELLOW, batch=batch)

@window.event
def on_key_press(symbol, mods):
    print(f"key pressed {symbol}")

@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_resize(width, height):
    print('The window was resized to %dx%d' % (width, height))
    status_label.update(0, window.height-status_padding)
    ball_indicators[0].y = window.height-ball_y
    ball_indicators[1].y = window.height-ball_y
    ball_indicators[2].y = window.height-ball_y
    ball_outlines[0].y = window.height-ball_y
    ball_outlines[1].y = window.height-ball_y
    ball_outlines[2].y = window.height-ball_y
    balls_seperator.y = window.height-ball_y-ball_rad

def update(dt):
    global is_running, status_label, uptime
    if is_running:
        if not NetworkTables.isConnected():
            status_label.text = STANDBY_STATUS_STRING
            is_running = False
        uptime += dt
        pos = field.getValue("estimator_pose", None)
        if pos is not None:
            robot.x = robot_facing.x = pos[0] * FIELD_TO_WINDOW
            robot.y = robot_facing.y = pos[1] * FIELD_TO_WINDOW
            robot.rotation = robot_facing.rotation = -pos[2]
        pos = field.getValue("effective_goal", None)
        if pos is not None:
            effective_goal.x = pos[0] * FIELD_TO_WINDOW
            effective_goal.y = pos[1] * FIELD_TO_WINDOW

        status_label.text = f"Uptime: {int(uptime)} s"
        ball_indicators[0].color = YELLOW if indexer.getBoolean("has_cargo_in_tunnel", False) else BLACK
        ball_indicators[1].color = YELLOW if indexer.getBoolean("has_cargo_in_chimney", False) else BLACK
        ball_indicators[2].color = RED if indexer.getBoolean("has_trapped_cargo", False) else BLACK
    else:
        NetworkTables.startClient(ROBORIO_IP)
        if NetworkTables.isConnected():
            is_running = True
            uptime = 0.0

pyglet.clock.schedule_interval(update, 1/24.0)
pyglet.app.run()
