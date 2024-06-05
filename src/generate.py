#!/usr/bin/env python3
import os
import sys

from helper.renderer_markdown import RendererMarkdown
from helper.cli_bitcoin import CliBitcoin
from helper.cli_controller import CliController


def main():
    output_dir = os.getcwd()
    controller = CliController()

    renderer = RendererMarkdown(output_dir)
    controller.generate(CliBitcoin("bitcoin-cli -signet"), renderer, None)
   

if __name__ == '__main__':
    main()
