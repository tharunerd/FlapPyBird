# Import asyncio for asynchronous programming
import asyncio

# Import sys to allow exiting the program
import sys

# Import pygame for game development
import pygame

# Import specific constants from pygame.locals for handling keyboard and quit events
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

# Import game entities from the local 'entities' module
from .entities import (
    Background,      # Handles background rendering
    Floor,           # Handles floor rendering and movement
    GameOver,        # Displays the game over screen
    Pipes,           # Manages pipe obstacles
    Player,          # Controls the bird/player
    PlayerMode,      # Enum for player states (e.g., SHM, NORMAL, CRASH)
    Score,           # Tracks and displays score
    WelcomeMessage,  # Displays welcome splash screen
)

# Import utility classes from the local 'utils' module
from .utils import GameConfig, Images, Sounds, Window


# Define the main Flappy Bird game class
class Flappy:
    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Set the window title
        pygame.display.set_caption("Flappy Bird")

        # Create a window object with width and height
        window = Window(288, 512)

        # Create the game screen with the window dimensions
        screen = pygame.display.set_mode((window.width, window.height))

        # Load all game images
        images = Images()

        # Set up the game configuration with screen, clock, FPS, window, images, and sounds
        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
        )

    # Main game loop that runs forever
    async def start(self):
        while True:
            # Initialize all game components
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.player = Player(self.config)
            self.welcome_message = WelcomeMessage(self.config)
            self.game_over_message = GameOver(self.config)
            self.pipes = Pipes(self.config)
            self.score = Score(self.config)

            # Show splash screen, play game, then show game over screen
            await self.splash()
            await self.play()
            await self.game_over()

    # Splash screen before the game starts
    async def splash(self):
        """Shows welcome splash screen animation of flappy bird"""

        # Set player mode to SHM (simple harmonic motion)
        self.player.set_mode(PlayerMode.SHM)

        # Loop until user taps to start the game
        while True:
            for event in pygame.event.get():
                # Check for quit event
                self.check_quit_event(event)

                # Check if user tapped to start
                if self.is_tap_event(event):
                    return

            # Update background, floor, player animation, and welcome message
            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.welcome_message.tick()

            # Refresh the screen
            pygame.display.update()

            # Yield control to event loop
            await asyncio.sleep(0)

            # Tick the game clock
            self.config.tick()

    # Handle quit events like pressing ESC or closing the window
    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    # Check if the user tapped the screen or pressed space/up arrow
    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()  # Check mouse left click
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN  # Check touchscreen tap
        return m_left or space_or_up or screen_tap

    # Main gameplay loop
    async def play(self):
        # Reset score and set player mode to NORMAL
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL)

        # Loop until player collides
        while True:
            # Check for collision with pipes or floor
            if self.player.collided(self.pipes, self.floor):
                return

            # Check if player crossed a pipe to increase score
            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            # Handle user input
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    self.player.flap()  # Make the player flap (jump)

            # Update all game components
            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()

            # Refresh the screen
            pygame.display.update()

            # Yield control to event loop
            await asyncio.sleep(0)

            # Tick the game clock
            self.config.tick()

    # Game over screen logic
    async def game_over(self):
        """crashes the player down and shows gameover image"""

        # Set player mode to CRASH
        self.player.set_mode(PlayerMode.CRASH)

        # Stop pipe and floor movement
        self.pipes.stop()
        self.floor.stop()

        # Loop until user taps to restart
        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)

                # If user taps and player has hit the ground, restart
                if self.is_tap_event(event):
                    if self.player.y + self.player.h >= self.floor.y - 1:
                        return

            # Update all components including game over message
            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.game_over_message.tick()

            # Tick the game clock and refresh screen
            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)