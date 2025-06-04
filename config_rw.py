import configparser

class ConfigReadWriter:
    config = configparser.ConfigParser()
    def __init__(self) -> None:
        self.file_path = 'C:\\Users\\ThinkPad\\2ndCourse_config.ini'
        self.config.read(self.file_path)

    def read_campus_restriction(self) -> dict:
        return {"jiuli": self.config.get('campus-restriction', 'jiuli')}
    
    def write_campus_restriction(self, campus:str, checked:str):
        self.config['campus-restriction'][campus] = str(checked)
    
    def read_department_restriction(self) -> dict:
        return {"jingguan": self.config.get('department-restriction', 'jingguan')}
    
    def write_department_restriction(self, department:str, checked:str):
        self.config['department-restriction'][department] = str(checked)
    
    def read_search_count(self) -> str:
        return self.config.get("search-count", "value")
    
    def write_search_count(self, count:int):
        self.config['search-count']['value'] = str(count)

    def read_number_of_participants_is_full(self) -> bool:
        return self.config.get('number-of-participants-is-full', 'isfull') == "True"
    
    def write_number_of_participants_is_full(self, isfull:bool):
        self.config['number-of-participants-is-full']["isfull"] = str(isfull)

    def read_times_up(self) -> bool:
        return self.config.get('time-restriction', "timesup") == "True"
    
    def write_times_up(self, timesup:bool):
        self.config['time-restriction']['timesup'] = str(timesup)
    
    def read_is_early(self) -> bool:
        return self.config.get('time-restriction', "isearly") == "True"
    
    def write_is_early(self, isearly:bool):
        self.config['time-restriction']['isearly'] = str(isearly)

    def write_to_file(self):
        with open(self.file_path, 'w') as configfile:
            self.config.write(configfile)

if __name__ == "__main__":
    pass
