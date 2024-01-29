import pygame


class Input:
    def __init__(self):
        self.keyboard = {}
        self.controller = {}

    def load_controls(self, dictionary):
        ...