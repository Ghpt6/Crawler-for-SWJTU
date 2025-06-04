import configparser
from typing import Any
# import traceback

class ConfigManager:

    _CONFIG_SPEC = {
        'campus_jiuli': ('campus-restriction', 'jiuli', bool, False),
        'department_jingguan': ('department-restriction', 'jingguan', bool, False),
        'search_count': ('search-count', 'value', int, 0),
        'participants_full': ('number-of-participants-is-full', 'isfull', bool, False),
        'times_up': ('time-restriction', 'timesup', bool, False),
        'is_early': ('time-restriction', 'isearly', bool, False),
        'venue': ('teaching-venue', 'venue', str, 'jiuli'),
    }

    def __init__(self):
        self.file_path = "C:\\Users\\ThinkPad\\2ndCourse_config.ini"
        self.config = configparser.ConfigParser()
        self._load_or_init_config()

    def _load_or_init_config(self):
        """加载配置文件，不存在则初始化默认配置"""
        self.config.read(self.file_path)
        
        # 确保所有配置项存在
        save_flag = False
        for key, (section, option, _, default) in self._CONFIG_SPEC.items():
            if not self.config.has_section(section):
                save_flag = True
                self.config.add_section(section)
            if not self.config.has_option(section, option):
                save_flag = True
                self.set(key, default, save=False)
        if save_flag:
            self._save()

    def get(self, item: str) -> Any:
        """获取配置值"""
        section, option, type_cast, default = self._CONFIG_SPEC[item]
        value = self.config.get(section, option)

        if type_cast == bool:
            value = value.lower() == "true"
        else:
            value = type_cast(value)
        return value

    def set(self, item: str, value: Any, save: bool = True):
        """设置配置值并默认保存"""
        section, option, type_cast, _ = self._CONFIG_SPEC[item]
        str_value = str(value).lower()
        
        self.config.set(section, option, str_value)
        
        if save:
            self._save()

    def _save(self):
        """保存配置到文件"""
        with open(self.file_path, 'w') as f:
            self.config.write(f)


if __name__ == "__main__":
    cm = ConfigManager()
    f = lambda: cm.get("is_early") == True
    print(f())