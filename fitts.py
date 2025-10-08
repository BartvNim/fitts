#!/usr/bin/env python3
"""
1D Fitts' Law Experiment in Pygame using raw mouse input from libpointing
Logs summed dx/dy per frame so that mouseX/Y matches movement
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
COUNTDOWN = 6  # new state

EXPERIMENT_SEED = 42
random.seed(EXPERIMENT_SEED)

# Fitts' Law fixed conditions
distances = [200, 400, 600, 800]
widths = [30, 50, 70]             
repetitions = 10          

# Create all combinations
conditions = [(A, W) for A in distances for W in widths]
trial_sequence = conditions * repetitions

random.shuffle(trial_sequence)

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
totalExperimentTargets = len(conditions) * repetitions
breakInterval = 20
currentTrialSequence = []
currentTrialIndex = 0

# Timing
targetShownTime = 0
enteredEdgeTime = -1
hasEnteredEdge = False
reactionTimes = []

# Countdown
countdownStartTime = 0
countdownDuration = 3  # seconds

# Mouse / click tracking
mouseX, mouseY = 0, 0
clicked = False
hit = False
insideEdgeLastFrame = False
overshootCount = 0

# --- NEW: accumulate raw deltas per frame ---
frame_dx = 0
frame_dy = 0
frame_buttons = 0

# Logging
logData = (
    "trialNumber,time(ms),mouseX,mouseY,targetX,targetY,targetSize,"
    "formerTargetX,formerTargetY,formerTargetSize,distanceCenter,distanceEdge,"
    "timeSinceTarget,timeSinceEdge,clicked,hit,overshootCount,raw_dx,raw_dy,raw_buttons\n"
)
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
    global frame_dx, frame_dy, frame_buttons
    pointer.update(dx, dy)
    frame_dx += dx
    frame_dy += dy
    frame_buttons = buttons  # store latest button state

# ==========================
# Target logic
# ==========================
def pickNewTarget():
    global targetX, targetY, targetSize, targetOnLeft
    global formerTargetX, formerTargetY, formerTargetSize
    global targetShownTime, enteredEdgeTime, hasEnteredEdge, insideEdgeLastFrame, overshootCount
    global state, currentTrialSequence, currentTrialIndex

    if state == TRIAL:
        if not currentTrialSequence:
            currentTrialSequence = random.sample(conditions, totalTrialTargets)
            currentTrialIndex = 0
        A, W = currentTrialSequence[currentTrialIndex]
        currentTrialIndex += 1
    else:  # EXPERIMENT
        if not currentTrialSequence:
            currentTrialSequence = trial_sequence.copy()
        A, W = currentTrialSequence.pop(0)

    targetSize = W
    formerTargetX, formerTargetY, formerTargetSize = targetX, targetY, targetSize
    targetY = HEIGHT // 2

    # Alternate side placement
    if targetOnLeft:
        targetX = WIDTH // 2 - A // 2
    else:
        targetX = WIDTH // 2 + A // 2
    targetOnLeft = not targetOnLeft

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
    global frame_dx, frame_dy, frame_buttons

    x, y = pointer.get_pos()
    distanceCenter = ((x - targetX) ** 2 + (y - targetY) ** 2) ** 0.5
    distanceEdge = max(0, distanceCenter - targetSize / 2)

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

    # Log the summed dx/dy for this frame
    logData += (
        f"{currentTrialNumber},{pygame.time.get_ticks()},{x},{y},{targetX},{targetY},{targetSize},"
        f"{formerTargetX},{formerTargetY},{formerTargetSize},{distanceCenter},{distanceEdge},"
        f"{timeSinceTarget},{timeSinceEdge},{int(clicked)},{int(hit)},{overshootCount},"
        f"{frame_dx},{frame_dy},{frame_buttons}\n"
    )

    # Reset accumulated deltas after logging
    frame_dx = 0
    frame_dy = 0
    clicked = False
    hit = False

# --- Pointer drawing ---
def drawPointer(surface):
    x, y = pointer.get_pos()
    pointer_size = 10
    color = (0, 100, 255)
    pygame.draw.line(surface, color, (x - pointer_size, y), (x + pointer_size, y), 2)
    pygame.draw.line(surface, color, (x, y - pointer_size), (x, y + pointer_size), 2)
    pygame.draw.circle(surface, color, (x, y), 3)

def saveLog():
    global logSaved
    Path("./tests").mkdir(parents=True, exist_ok=True)
    with open("./tests/" + logFileName, "w") as f:
        f.write(logData)
    print(f"Log saved to: {logFileName}")
    logSaved = True

# ==========================
# Pygame Initialization
# ==========================
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("1D Fitts' Law Experiment")
font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()

# Initialize libpointing
device_uri = b"any:?debugLevel=2"
pointing_device = PointingDevice(device_uri)
pointing_device.setCallback(pointing_callback)
pygame.mouse.set_visible(False)

pickNewTarget()

# ==========================
# Main Loop
# ==========================
running = True
while running:
    screen.fill((240, 240, 240))
    pygame.draw.line(screen, (180, 180, 180), (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)
    x, y = pointer.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
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
                    state = COUNTDOWN
                    countdownStartTime = time.time()
            elif state == BREAK_SCREEN and event.key == pygame.K_c:
                state = COUNTDOWN
                countdownStartTime = time.time()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            distance = ((x - targetX) ** 2 + (y - targetY) ** 2) ** 0.5
            if state == START_SCREEN:
                state = TRIAL
                trialCount = 0
                pickNewTarget()
            elif state == TRIAL:
                if distance <= targetSize / 2:
                    hit = True
                    trialCount += 1
                    if trialCount >= totalTrialTargets:
                        state = TRANSITION
                    else:
                        pickNewTarget()
                else:
                    hit = False
            elif state == EXPERIMENT:
                if distance <= targetSize / 2:
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

    # Draw current state text
    def drawText(text, y, size=24):
        t = pygame.font.Font(None, size).render(text, True, (0, 0, 0))
        rect = t.get_rect(center=(WIDTH // 2, y))
        screen.blit(t, rect)

    if state == START_SCREEN:
        drawText("Fitts' Law Experiment", HEIGHT // 2 - 40)
        drawText("Click to begin a short trial session.", HEIGHT // 2 + 10, 18)
        drawText("Try clicking the targets as fast and accurately as you can.", HEIGHT // 2 + 40, 18)
    elif state == TRIAL:
        drawText("Trial Session", 40)
        drawText(f"Trial {trialCount + 1} of {totalTrialTargets}", HEIGHT - 30, 20)
    elif state == TRANSITION:
        drawText("Trial Session Complete!", HEIGHT // 2 - 60)
        drawText("Press 'C' to continue or 'R' to repeat the trial.", HEIGHT // 2 - 20, 18)
    elif state == EXPERIMENT:
        drawText("Main Experiment", 40)
        drawText(f"Trial {experimentCount + 1} of {totalExperimentTargets}", HEIGHT - 30, 20)
    elif state == BREAK_SCREEN:
        drawText("Take a short break!", HEIGHT // 2 - 30)
        drawText(f"You've completed {experimentCount} of {totalExperimentTargets} trials.", HEIGHT // 2, 18)
        drawText("Press 'C' to continue when ready.", HEIGHT // 2 + 40, 18)
    elif state == COUNTDOWN:
        elapsed = time.time() - countdownStartTime
        remaining = countdownDuration - int(elapsed)
        if remaining > 0:
            drawText("Get ready...", HEIGHT // 2 - 60)
            drawText(str(remaining), HEIGHT // 2, 64)
        else:
            state = EXPERIMENT
            pickNewTarget()
    elif state == END:
        drawText("Experiment Complete!", HEIGHT // 2 - 40)
        avgTime = sum(reactionTimes) / len(reactionTimes) if reactionTimes else 0
        drawText(f"Average Reaction Time: {avgTime:.2f} ms", HEIGHT // 2)
        if not logSaved:
            saveLog()

    if state in (TRIAL, EXPERIMENT):
        pygame.draw.circle(screen, (200, 0, 0), (int(targetX), int(targetY)), targetSize // 2)
        logMouseData()

    drawPointer(screen)
    pygame.display.flip()
    clock.tick(60)
    PointingDevice.idle(1)

saveLog()
del pointing_device
pygame.quit()
