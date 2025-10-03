#!/usr/bin/env python3
"""
1D Fitts' Law Experiment in Pygame using raw mouse input from libpointing
"""

import pygame
import json
import time
import random
from pathlib import Path
from datetime import datetime
import sys
import threading


# --- libpointing imports ---
sys.path.insert(0, str(Path(__file__).parent / "libpointing/bindings/Python/cython"))
try:
    from libpointing.libpointing import PointingDevice
except ImportError as e:
    print(f"Error: {e}. Make sure libpointing Python bindings are built.")
    sys.exit(1)

# ==========================
# Experiment States
# ==========================
START_SCREEN = 0
TRIAL = 1
TRANSITION = 2
EXPERIMENT = 3
BREAK_SCREEN = 4
END = 5

EXPERIMENT_SEED = 42
random.seed(EXPERIMENT_SEED)

state = START_SCREEN

# Target properties
targetX = 0
targetY = 0
targetSize = 50
targetOnLeft = True
formerTargetX = 0
formerTargetY = 0
formerTargetSize = 0

# Trial / Experiment settings
trialCount = 0
totalTrialTargets = 3
experimentCount = 0
totalExperimentTargets = 100
breakInterval = 20

# Timing
targetShownTime = 0
enteredEdgeTime = -1
hasEnteredEdge = False
reactionTimes = []

# Mouse / click tracking
mouseX, mouseY = 0, 0
clicked = False
hit = False
insideEdgeLastFrame = False
overshootCount = 0

# Logging
logData = "trialNumber,time(ms),mouseX,mouseY,targetX,targetY,targetSize,formerTargetX,formerTargetY,formerTargetSize,distanceCenter,distanceEdge,timeSinceTarget,timeSinceEdge,clicked,hit,overshootCount\n"
logSaved = False
logFileName = f"./mouse_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

# Screen config
WIDTH, HEIGHT = 800, 400

# Thread-safe raw mouse position
class RawPointer:
    def __init__(self, width, height):
        self.x = width // 2
        self.y = height // 2
        self.lock = threading.Lock()

    def update(self, dx, dy):
        with self.lock:
            self.x = max(0, min(WIDTH, self.x + dx))
            self.y = max(0, min(HEIGHT, self.y + dy))

    def get_pos(self):
        with self.lock:
            return int(self.x), int(self.y)

pointer = RawPointer(WIDTH, HEIGHT)

# ==========================
# libpointing device callback
# ==========================
def pointing_callback(timestamp, dx, dy, buttons):
    pointer.update(dx, dy)

# ==========================
# Target logic
# ==========================
def pickNewTarget():
    global targetX, targetY, targetSize, targetOnLeft
    global formerTargetX, formerTargetY, formerTargetSize
    global targetShownTime, enteredEdgeTime, hasEnteredEdge, insideEdgeLastFrame, overshootCount

    formerTargetX, formerTargetY, formerTargetSize = targetX, targetY, targetSize
    targetSize = random.randint(30, 100)
    if targetOnLeft:
        targetX = random.randint(targetSize//2, WIDTH//2 - targetSize//2)
    else:
        targetX = random.randint(WIDTH//2 + targetSize//2, WIDTH - targetSize//2)
    targetOnLeft = not targetOnLeft
    targetY = HEIGHT // 2

    targetShownTime = pygame.time.get_ticks()
    enteredEdgeTime = -1
    hasEnteredEdge = False
    insideEdgeLastFrame = False
    overshootCount = 0

# ==========================
# Logging
# ==========================
def logMouseData():
    global logData, clicked, hit, insideEdgeLastFrame, overshootCount
    x, y = pointer.get_pos()
    distanceCenter = ((x - targetX)**2 + (y - targetY)**2)**0.5
    distanceEdge = max(0, distanceCenter - targetSize/2)

    global enteredEdgeTime, hasEnteredEdge
    if not hasEnteredEdge and distanceEdge == 0:
        enteredEdgeTime = pygame.time.get_ticks()
        hasEnteredEdge = True

    insideEdge = distanceEdge == 0
    if insideEdgeLastFrame and not insideEdge:
        overshootCount += 1
    insideEdgeLastFrame = insideEdge

    timeSinceTarget = pygame.time.get_ticks() - targetShownTime
    timeSinceEdge = pygame.time.get_ticks() - enteredEdgeTime if hasEnteredEdge else -1

    currentTrialNumber = 0
    if state == TRIAL:
        currentTrialNumber = trialCount + 1
    elif state == EXPERIMENT:
        currentTrialNumber = experimentCount + 1

    logData += f"{currentTrialNumber},{pygame.time.get_ticks()},{x},{y},{targetX},{targetY},{targetSize},{formerTargetX},{formerTargetY},{formerTargetSize},{distanceCenter},{distanceEdge},{timeSinceTarget},{timeSinceEdge},{int(clicked)},{int(hit)},{overshootCount}\n"
    clicked = False
    hit = False


# --- Pointer drawing ---
def drawPointer(surface):
    x, y = pointer.get_pos()
    pointer_size = 10  # half-length of crosshair
    color = (0, 100, 255)

    # Crosshair lines
    pygame.draw.line(surface, color, (x - pointer_size, y), (x + pointer_size, y), 2)
    pygame.draw.line(surface, color, (x, y - pointer_size), (x, y + pointer_size), 2)

    # Center dot
    pygame.draw.circle(surface, color, (x, y), 3)


def saveLog():
    global logSaved
    Path("./tests").mkdir(parents=True, exist_ok=True)
    with open('./tests/' + logFileName, "w") as f:
        f.write(logData)
    print(f"Log saved to: {logFileName}")
    logSaved = True

# ==========================
# Pygame Initialization
# ==========================
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)  # fullscreen
WIDTH, HEIGHT = screen.get_size()  # get actual screen resolution
pygame.display.set_caption("1D Fitts' Law Experiment")
font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()


# Initialize libpointing
device_uri = b"any:?debugLevel=2"
pointing_device = PointingDevice(device_uri)
pointing_device.setCallback(pointing_callback)
pygame.mouse.set_visible(False)

# Start first target
pickNewTarget()

# ==========================
# Main Loop
# ==========================
running = True
while running:
    screen.fill((240, 240, 240))
    pygame.draw.line(screen, (180, 180, 180), (0, HEIGHT//2), (WIDTH, HEIGHT//2), 2)

    x, y = pointer.get_pos()

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_s:
                saveLog()
            if state == TRANSITION:
                if event.key == pygame.K_r:
                    trialCount = 0
                    state = TRIAL
                    pickNewTarget()
                elif event.key == pygame.K_c:
                    experimentCount = 0
                    reactionTimes.clear()
                    state = EXPERIMENT
                    pickNewTarget()
            elif state == BREAK_SCREEN and event.key == pygame.K_c:
                state = EXPERIMENT
                pickNewTarget()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            distance = ((x - targetX)**2 + (y - targetY)**2)**0.5
            if state == START_SCREEN:
                state = TRIAL
                trialCount = 0
                pickNewTarget()
            elif state == TRIAL:
                if distance <= targetSize/2:
                    hit = True
                    trialCount += 1
                    if trialCount >= totalTrialTargets:
                        state = TRANSITION
                    else:
                        pickNewTarget()
                else:
                    hit = False
            elif state == EXPERIMENT:
                if distance <= targetSize/2:
                    hit = True
                    reactionTimes.append(pygame.time.get_ticks() - targetShownTime)
                    experimentCount += 1
                    if experimentCount >= totalExperimentTargets:
                        state = END
                    elif experimentCount % breakInterval == 0:
                        state = BREAK_SCREEN
                    else:
                        pickNewTarget()
                else:
                    hit = False

    # State Screens
    def drawText(text, y, size=24):
        t = pygame.font.Font(None, size).render(text, True, (0,0,0))
        rect = t.get_rect(center=(WIDTH//2, y))
        screen.blit(t, rect)

    if state == START_SCREEN:
        drawText("Fitts' Law Experiment", HEIGHT//2 - 40)
        drawText("Click to begin a short trial session.", HEIGHT//2 + 10, 18)
        drawText("Try clicking the targets as fast and accurately as you can.", HEIGHT//2 + 40, 18)
    elif state == TRIAL:
        drawText("Trial Session", 30)
        drawText(f"Trial {trialCount+1} of {totalTrialTargets}", HEIGHT - 30, 14)
    elif state == TRANSITION:
        drawText("Trial Session Complete!", HEIGHT//2 - 60)
        drawText("Press 'C' to continue or 'R' to repeat the trial.", HEIGHT//2 - 20, 18)
    elif state == EXPERIMENT:
        drawText("Main Experiment", 30)
        drawText(f"Trial {experimentCount+1} of {totalExperimentTargets}", HEIGHT - 30, 14)
    elif state == BREAK_SCREEN:
        drawText("Take a short break!", HEIGHT//2 - 30)
        drawText(f"You've completed {experimentCount} out of {totalExperimentTargets} trials.", HEIGHT//2, 18)
        drawText("Press 'C' to continue when ready.", HEIGHT//2 + 40, 18)
    elif state == END:
        drawText("Experiment Complete!", HEIGHT//2 - 40)
        avgTime = sum(reactionTimes)/len(reactionTimes) if reactionTimes else 0
        drawText(f"Average Reaction Time: {avgTime:.2f} ms", HEIGHT//2)
        if not logSaved:
            saveLog()

    # Draw target during TRIAL/EXPERIMENT
    if state in (TRIAL, EXPERIMENT):
        pygame.draw.circle(screen, (200,0,0), (int(targetX), int(targetY)), targetSize//2)
        logMouseData()
    drawPointer(screen)
    pygame.display.flip()
    clock.tick(60)
    PointingDevice.idle(1)  # process libpointing events

# Cleanup
saveLog()
del pointing_device
pygame.quit()
