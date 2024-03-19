### IMPORTS ###
import pygame as pg

from gui.panel import Panel
from gui.panel.level import LevelPanel
from gui.panel.log import LogPanel
from gui.panel.info import InfoPanel
from gui.panel.menu import MenuPanel
from gui.popout import Popout
from gui.button import Button

from util.tuples import *


### CONSTANTS ###
# values represent percentages,
# to be compared to screen size
LEVEL_COORD = (0, 0)
LEVEL_DIMEN = (0.75, 0.75)

LOG_COORD = (0, 0.75)
LOG_DIMEN = (0.75, 0.25)

INFO_COORD = (0.75, 0)
INFO_DIMEN = (0.25, 0.75)

MENU_COORD = (0.75, 0.75)
MENU_DIMEN = (0.25, 0.25)

# path to game over art
game_over_art = pg.image.load("data/bones.png")


class GUI():
    """ user interface object which handles all the graphical stuff """

    def __init__(self, screen_size, fonts, level):
        self.screen_size = screen_size
        self.li = fonts['li']
        self.h1 = fonts['h1']

        self.game_over = False
        self.exit_button = None

        self.panels = []

        popout_size = (screen_size[0] - 60, screen_size[1] - 60)
        sample_popout = Popout((30, 30), popout_size)
        self.popout = None


        # level panel
        level_coord = multiply_tuples(LEVEL_COORD, screen_size)
        level_dimen = multiply_tuples(LEVEL_DIMEN, screen_size)
        self.level = LevelPanel(level_coord, level_dimen, level)
        self.panels.append(self.level)

        # log panel
        log_coord = multiply_tuples(LOG_COORD, screen_size)
        log_dimen = multiply_tuples(LOG_DIMEN, screen_size)
        self.log = LogPanel(log_coord, log_dimen, fonts)
        self.panels.append(self.log)

        # info panel
        info_coord = multiply_tuples(INFO_COORD, screen_size)
        info_dimen = multiply_tuples(INFO_DIMEN, screen_size)
        self.info = InfoPanel(info_coord, info_dimen)
        self.panels.append(self.info)

        # menu panel
        menu_coord = multiply_tuples(MENU_COORD, screen_size)
        menu_dimen = multiply_tuples(MENU_DIMEN, screen_size)
        self.menu = MenuPanel(menu_coord, menu_dimen, level, self)
        self.panels.append(self.menu)

        # set borders where needed
        self.log.set_border(mid_color = (10, 50, 0))
        self.info.set_border(mid_color = (0, 80, 20))

    def draw(self, surface):
        """ general drawer for all GUI elements """

        # draw game-over menu if needed
        if self.game_over:
            surface.fill("#dddcc9")
            screenx, screeny = self.screen_size[0], self.screen_size[1]
            surface.blit(game_over_art, (0, self.screen_size[1] - 240))

            render = self.h1.render("You died!", None, (0, 0, 0))
            surface.blit(render, (screenx * 3/5, screeny * 1/7))

            """
            stats to print:
            level
            player level
            most coolest posession
            """
            
            render = self.li.render("Exit", None, (0, 0, 0))
            self.exit_button = Button(
                (300, 200),
                (100, 50),
                (255, 255, 255),
                exit,
                text= render
            )
            self.exit_button.draw(surface)

            return


        # draw panels
        self.level.draw(surface)
        self.log.draw(surface)
        self.info.draw(surface, self.li, self.h1)
        self.menu.draw(surface)
        if self.popout is not None:
            self.popout.draw(surface)


    def change_level(self, new_level):
        """ adjust the gui to reflect the current level """
        level_coord = multiply_tuples(LEVEL_COORD, self.screen_size)
        level_dimen = multiply_tuples(LEVEL_DIMEN, self.screen_size)
        self.level = LevelPanel(level_coord, level_dimen, new_level)


    def add_messages(self, messages):
        """ automatic and easy message logger """
        self.log.add_messages(self.li, messages)


    def update(self):
        """ general update method to keep panels up to date """
        for panel in self.panels:
            panel.update()

    def scroll(self, direction):
        """ register mouse scrolling """
        mouse_pos = pg.mouse.get_pos()
        log_xrange = range(
            self.log.rect.left,
            self.log.rect.left + self.log.rect.width
        )
        log_yrange = range(
            self.log.rect.top,
            self.log.rect.top + self.log.rect.height
        )
        if mouse_pos[0] in log_xrange and mouse_pos[1] in log_yrange:
            match direction:
                case 'up': self.log.scroll_up()
                case 'down': self.log.scroll_down()


    def click_move(self):
        """ register mouse clicking """
        mouse_pos = pg.mouse.get_pos()

        # see if clicking in board
        if self.level.rect.collidepoint(mouse_pos):
            loc_x = mouse_pos[0] - self.level.rect.left
            loc_y = mouse_pos[1] - self.level.rect.top
            clicked_tile = self.level.rect.get_pixel(loc_x, loc_y)
            if clicked_tile is None:
                return None
            if clicked_tile.visible or clicked_tile in self.level.rect.shadows:
                return (clicked_tile.tile_x, clicked_tile.tile_y)
        return None


    def click_button(self):
        """ register mouse clicking """
        mouse_pos = pg.mouse.get_pos()

        # buttons should only be located in the menu panel or in a popout
        for button in self.menu.buttons:
            if button.rect.collidepoint(mouse_pos):
                button.click()
        if self.exit_button is not None and self.exit_button.rect.collidepoint(mouse_pos):
            self.exit_button.click()