from subprocess import check_output
import locale
import re
import sys

class GPUInfo(object):

    commands = {
        "odgc": ["aticonfig", "--adapter={0}", "--odgc"],
        "odgt": ["aticonfig", "--adapter={0}", "--odgt"],
        "fan":  ["aticonfig", "--pplib-cmd", "get fanspeed {0}"],
        "lsmod": ["lsmod"],
    }

    gpu_mem_posit = {
        "gpu": 1,
        "mem": 2,
    }

    def __init__(self):
        self.encoding = "utf-8"
        self.isCatalystLoaded()

    def isCatalystLoaded(self):
        info = self.getInformation("lsmod")
        if "fglrx" in info:
            return True
        print("The 'fglrx' module is not currently loaded, or the AMD Catalyst software is not properly installed.")
        sys.exit(1)

    def getInformation(self, source, adapter=0):
        command = [part.format(adapter) for part in self.commands[source]] 
        try:
            info = check_output(command)
        except OSError:
            print("The command '{0}' software cannot be found.".format(command[0]))
            sys.exit(1)
        return info.decode(self.encoding)

    def getLoad(self, adapter=0):
        info = self.getInformation("odgc", adapter).split("\n")
        for line in info:
            try:
                load_match = re.search(r"GPU load\D+(\d+)%", line)
                if load_match:
                    return load_match.group(1)
            except IndexError:
                print("Unable to parse output from the 'aticonfig' command.")
                sys.exit(1)

    def getFanspeed(self, adapter=0):
        info = self.getInformation("fan", adapter)
        try:
            fan_match = re.search("(\d{1,3})%", info)
            return fan_match.group(1)
        except IndexError:
            print("Unable to parse output from the 'aticonfig' command.")
            sys.exit(1)

    def getCurrentClock(self, gpu_or_mem, adapter=0):
        if gpu_or_mem not in self.gpu_mem_posit:
            print("getCurrentClock only supports options 'gpu' or 'mem'.")
            sys.exit(1)
        info = self.getInformation("odgc", adapter).split("\n")
        current_clock_regex = re.compile(r'Current Peak\D+(\d+)\s+(\d+)')
        for line in info:
            current_clock_match = current_clock_regex.search(line)
            if current_clock_match:
                return current_clock_match.group(self.gpu_mem_posit[gpu_or_mem])
        return None
    
    def getMaxClock(self, gpu_or_mem, adapter=0):
        if gpu_or_mem not in self.gpu_mem_posit:
            print("getMaxClock only supports options 'gpu' or 'mem'.")
            sys.exit(1)
        info = self.getInformation("odgc", adapter).split("\n")
        max_clock_regex = re.compile(r'Current Peak\D+(\d+)\s+(\d+)')
        for line in info:
            max_clock_match = max_clock_regex.search(line)
            if max_clock_match:
                return max_clock_match.group(self.gpu_mem_posit[gpu_or_mem])

    def getTemperature(self, adapter=0):
        info = self.getInformation("odgt", adapter)
        try:
            temp_match = re.search(r'(\d{2,3})\.\d{2} C', info)
            return temp_match.group(1)
        except IndexError:
            print("Could not parse temperature data.")
            sys.exit(1)

