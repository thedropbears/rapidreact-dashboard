#!/bin/env python3
import time
import pyglet
import math
from networktables import NetworkTables

FIELD_WIDTH = 16.46
FIELD_HEIGHT = 8.23
FIELD_TO_WINDOW = 100
WIN_WIDTH = int(FIELD_WIDTH * FIELD_TO_WINDOW)
WIN_HEIGHT = int(FIELD_HEIGHT * FIELD_TO_WINDOW)

ROBORIO_IP = "10.47.74.2"

STANDBY_STATUS_STRING = f"No connection, waiting for {ROBORIO_IP}"

GRAY = (127, 127, 127)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

dashboard = NetworkTables.getTable("SmartDashboard")
components = NetworkTables.getTable("components")
field = dashboard.getSubTable("Field")
indexer = components.getSubTable("indexer")

window = pyglet.window.Window(width=WIN_WIDTH, height=WIN_HEIGHT, caption="TheDropBears Driver Station")

is_running = False
uptime = 0.0

batch = pyglet.graphics.Batch()

status_label = pyglet.text.Label(STANDBY_STATUS_STRING, font_size=48, anchor_y="top", y=WIN_HEIGHT, width=WIN_WIDTH, multiline=True, batch=batch)

ball_indicators = [pyglet.shapes.Circle(30 + 70 * i, WIN_HEIGHT - 120, 30, batch=batch, color=GRAY) for i in range(3)] # Tunnel, chimney, trap

robot = pyglet.shapes.Rectangle(0, 0, 40, 40, batch=batch)
robot.anchor_position = 20, 20
robot_facing = pyglet.shapes.Rectangle(0, 0, 20, 10, color=RED, batch=batch)
robot_facing.anchor_position = 0, 5

goal = pyglet.shapes.Circle(WIN_WIDTH / 2, WIN_HEIGHT / 2, 60, batch=batch)
effective_goal = pyglet.shapes.Circle(WIN_WIDTH / 2, WIN_HEIGHT / 2, 60, color=YELLOW, batch=batch)

@window.event
def on_key_press(symbol, mods):
    print(f"key pressed {symbol}")

@window.event
def on_draw():
    window.clear()
    batch.draw()

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
        ball_indicators[0].color = YELLOW if indexer.getBoolean("has_cargo_in_tunnel", False) else GRAY
        ball_indicators[1].color = YELLOW if indexer.getBoolean("has_cargo_in_chimney", False) else GRAY
        ball_indicators[2].color = RED if indexer.getBoolean("has_trapped_cargo", False) else GRAY
    else:
        NetworkTables.startClient(ROBORIO_IP)
        if NetworkTables.isConnected():
            is_running = True
            uptime = 0.0

pyglet.clock.schedule_interval(update, 1/24.0)
pyglet.app.run()
