class Writer:
    def __init__(self, filename: str, option: str, target):
        self.filename = filename
        self.option = option
        self.target = target

    def write_in_file(self):
        with open(self.filename, self.option) as file:
            file.writelines(self.target)
