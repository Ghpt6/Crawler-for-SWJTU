
class Wprinter:
    signal = None
    def __init__(self) -> None:
        pass
    def print(self, text:str):
        print(text)
        if not self.signal:
            raise Exception("signal is None.")
        
        self.signal.emit(text)

wp = Wprinter()