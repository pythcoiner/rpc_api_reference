import os
import shutil
from pathlib import Path

from .help_data import display_name, capitalize, uncapitalize


class Page:
    def __init__(self):
        self.out = ""

    def tag(self, name, arg=None):
        if arg:
            self.out += arg + " "

        return Tag(self, name)

    def text(self, text):
        self.out += text + "\n"

    def nl(self):
        self.text("")


class RendererMarkdown:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

    def add_see_also_command(self, page, command):
        pass

    def add_see_also_glossary(self, page, text, link):
        pass

    def add_see_also_message(self, page, message, text):
        pass

    def add_see_also(self, page):
        pass

    def arg_summary(self, arg):
        return arg["name"]

    def arg_n(self, arg):
        return arg["name"]

    def arg_t(self, arg):
        t = arg["type"].split(", ")[0]
        if t == "numeric":
            t = "number (int)"
        return t

    def arg_p(self, arg):
        arg_line = arg["type"].split(", ")
        if len(arg_line) == 1:
            return "Required"
        else:
            p = arg_line[1]
            if p == "required":
                return "Required"
            elif p == "optional":
                if len(arg_line) == 3:
                    return "Optional<br>" + capitalize(arg_line[2])
                else:
                    return "Optional"
            else:
                return p

    def arg_d(self, arg):
        d = arg["description"]
        return d

    def result_t(self, result):
        t = result["type"]
        if t == "numeric":
            t = "number (int)"
        elif t == "string":
            t += " (hex)"
        return t

    def result_null(self):
        pass

    def yaml_escape(self, text):
        return text.replace('"', '\\"')

    def guarded_code_block(self, block):
        return f"\n```\n{block}\n```\n"
        # return self.code_block(block)

    def code_block(self, block):
        min_indentation = 999
        split_block = block.splitlines()
        for line in split_block:
            indentation = len(line) - len(line.lstrip(" "))
            if indentation < min_indentation:
                min_indentation = indentation

        indented_block = ""
        for line in split_block:
            if min_indentation <= 4:
                indented_block += " " * (4 - min_indentation) + line
            else:
                indented_block += line[min_indentation - 4:]
            indented_block += "\n"
        if not indented_block.endswith("\n"):
            indented_block += "\n"
        return indented_block

    def add_license_header(self, page):
        with page.tag("comment"):
            page.text("This file is licensed under the MIT License (MIT) available on\n"
                      "http://opensource.org/licenses/MIT.")

    def split_description(self, full_description):
        if full_description:
            if "." in full_description:
                summary = uncapitalize(full_description.partition(".")[0]) + "."
                description = full_description[len(summary) + 1:].lstrip()
            else:
                summary = uncapitalize(full_description.rstrip()) + "."
                description = ""
            summary = " ".join(summary.splitlines())
        else:
            summary = "%s" % display_name(self.command)
            description = None
        return summary, description

    def process_command_help(self, help_data):
        self.help_data = help_data
        self.command = help_data["command"].split(" ")[0]

        page = Page()

        lower_name = self.command

        title = f'# {lower_name}'
        if self.command == "ping":
            title += " {#ping-rpc}"
        page.text(title)
        page.nl()
        summary, description = self.split_description(help_data["description"])

        if description:
            for line in description.splitlines():
                page.text(line)
            page.nl()

        if "arguments" in help_data:
            if not help_data["arguments"]:
                page.text("*Argument: none*\n")
            else:
                count = 1
                for arg in help_data["arguments"]:
                    page.text(f"## Argument #{count}-{self.arg_summary(arg)}\n")
                    
                    page.nl()
                    page.text(f'Type: {self.arg_t(arg)}, {self.arg_p(arg)}')
                    
                    page.nl()
                    page.text(f'Description: {self.arg_d(arg)}')
                    
                    page.nl()
                    
                    if "literal_description" in arg:
                        page.text(self.guarded_code_block(
                            arg["literal_description"]))
                        page.nl()
                    count += 1

        if help_data["results"] == [{'title_extension': ''}] or help_data["results"] == []:
            pass
        else:
            for result in help_data["results"]:
                result_header = "## Result"
                if "title_extension" in result and result["title_extension"]:
                    result_header += "---" + \
                        result["title_extension"].lstrip()
                result_header += "\n"
                page.text(result_header)
                if result["format"] == "literal":
                    page.text(self.guarded_code_block(result["text"]))
                else:
                    page.text(f'Type: {self.result_t(result)}')
                    page.nl()
                    page.text(f'Description: {result["description"]}')
                    page.nl()

        return page.out

    def render_cmd_page(self, command, help_data):
        command_file = command + ".md"
        if not os.path.exists(self.output_dir / "rpcs"):
            os.mkdir(self.output_dir / "rpcs")
        with open(self.output_dir / "rpcs" / command_file, "w") as file:
            file.write(self.process_command_help(help_data))

    def render_overview_page(self, all_commands, render_version_info=True):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        summary = f'{self.output_dir}/SUMMARY.md'
        index = f'{self.output_dir}/index.md'
        
        with open(summary, "w") as file:
            page = Page()

            page.nl()
            page.nl()
            
            page.text("- [Summary](SUMMARY.md)")

            for category in all_commands:
                page.text(f'- [{category}]()')

                page.nl()
              
                for command in all_commands[category]:
                    cmd = command.split(" ")[0]

                    page.text(f'    - [{cmd}](rpcs/{cmd}.md)')
                page.nl()

            file.write(page.out)
        shutil.copyfile(summary, index)
