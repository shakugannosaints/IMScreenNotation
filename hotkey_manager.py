from pynput import keyboard
import threading
from PyQt5.QtCore import QTimer

class HotkeyManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.listener = None
        self.hotkeys = {}
        self.pressed_keys = set()
        self.current_combination = set()
        self.last_triggered_hotkey = None  # 防止重复触发
        self.modifier_keys = {
            keyboard.Key.ctrl_l: 'ctrl',
            keyboard.Key.ctrl_r: 'ctrl', 
            keyboard.Key.alt_l: 'alt',
            keyboard.Key.alt_r: 'alt',
            keyboard.Key.shift_l: 'shift',
            keyboard.Key.shift_r: 'shift'
        }

    def register_hotkey(self, hotkey_str, callback):
        """注册热键"""
        if hotkey_str and hotkey_str.strip():
            self.hotkeys[hotkey_str] = callback
            print(f"注册热键: {hotkey_str}")

    def parse_hotkey(self, hotkey_str):
        """解析热键字符串，返回需要的修饰键和主键"""
        try:
            parts = hotkey_str.lower().split('+')
            modifiers = set()
            main_key = None
            
            for part in parts:
                part = part.strip()
                # 移除尖括号
                if part.startswith('<') and part.endswith('>'):
                    part = part[1:-1]
                
                if part in ['ctrl']:
                    modifiers.add('ctrl')
                elif part in ['alt']:
                    modifiers.add('alt')
                elif part in ['shift']:
                    modifiers.add('shift')
                else:
                    # 这是主键
                    main_key = part
            
            # 特殊处理一些主键
            if main_key and main_key.startswith('f') and main_key[1:].isdigit():
                # 确保功能键格式统一为 "f1", "f2" 等
                main_key = main_key.lower()
            
            print(f"解析热键 '{hotkey_str}' -> 修饰键: {modifiers}, 主键: {main_key}")
            return modifiers, main_key
        except Exception as e:
            print(f"Error parsing hotkey '{hotkey_str}': {e}")
            return set(), None

    def key_to_string(self, key):
        """将按键转换为字符串"""
        try:
            # 处理修饰键
            if key in self.modifier_keys:
                return self.modifier_keys[key]

            # 处理功能键 (F1-F12)
            if hasattr(key, 'name') and key.name.lower().startswith('f') and key.name[1:].isdigit():
                return key.name.lower()  # 返回如 "f1", "f2" 等
                
            # 优先处理 KeyCode 类型（普通字符键）
            if isinstance(key, keyboard.KeyCode):
                if key.char and ord(key.char) >= 32:
                    return key.char.lower()
                # 如果是 KeyCode 但 char 不可用，尝试用 vk
                if hasattr(key, 'vk') and 32 <= key.vk <= 126:
                    return chr(key.vk).lower()
                # 兜底
                return str(key).lower()

            # 处理 Key 类型（功能键等）
            if hasattr(key, 'name'):
                key_name = key.name.lower()
                if key_name.startswith('num_'):
                    return key_name[4:]
                if key_name.startswith('_') and len(key_name) == 2:
                    return key_name[1]
                return key_name

            # 处理其他情况
            key_str = str(key).lower()
            if key_str.startswith('key.'):
                key_str = key_str[4:]
            if key_str.startswith("'") and key_str.endswith("'"):
                key_str = key_str[1:-1]
            if key_str.startswith('<') and key_str.endswith('>'):
                try:
                    ascii_code = int(key_str[1:-1])
                    if 32 <= ascii_code <= 126:
                        return chr(ascii_code).lower()
                    elif 65 <= ascii_code <= 90:
                        return chr(ascii_code).lower()
                    elif 97 <= ascii_code <= 122:
                        return chr(ascii_code)
                    elif 48 <= ascii_code <= 57:
                        return chr(ascii_code)
                    else:
                        return f"ascii_{ascii_code}"
                except ValueError:
                    pass
            return key_str

        except Exception as e:
            print(f"Error converting key to string: {e}")
            return str(key).lower()

    def check_hotkey_match(self, hotkey_str):
        """检查当前按下的键是否匹配热键"""
        required_modifiers, main_key = self.parse_hotkey(hotkey_str)
        if main_key is None:
            return False
        
        # 获取当前按下的修饰键
        current_modifiers = set()
        for key in self.pressed_keys:
            if key in self.modifier_keys:
                current_modifiers.add(self.modifier_keys[key])
        
        # 检查修饰键是否匹配（当前按下的修饰键必须包含所有需要的修饰键）
        modifiers_match = required_modifiers.issubset(current_modifiers)
        
        # 调试输出
        if current_modifiers or main_key:
            print(f"检查热键 '{hotkey_str}': 需要修饰键={required_modifiers}, 当前修饰键={current_modifiers}, 主键={main_key}, 修饰键匹配={modifiers_match}")
        
        return modifiers_match
    
    def check_main_key_match(self, hotkey_str, pressed_key):
        """检查按下的键是否是热键的主键"""
        required_modifiers, main_key = self.parse_hotkey(hotkey_str)
        if main_key is None:
            return False
        
        key_str = self.key_to_string(pressed_key)
        
        # 对于功能键，处理special case
        if main_key.startswith('f') and main_key[1:].isdigit():
            # 检查是否是功能键 (f1-f12)
            if key_str == main_key or key_str == f"key_{main_key}":
                match = True
            else:
                match = False
        else:
            # 普通键的比较
            match = key_str == main_key
        
        # 增加调试信息
        print(f"    主键匹配检查: 期望='{main_key}', 实际='{key_str}', 匹配={match}")
        
        return match

    def on_press(self, key):
        """按键按下事件"""
        self.pressed_keys.add(key)
        
        # 记录按键信息，方便调试
        key_str = self.key_to_string(key)
        pressed_str = [self.key_to_string(k) for k in self.pressed_keys]
        print(f"按键按下: {key_str} (原始key: {key}) -> 当前组合: {pressed_str}")
        
        # 如果按下的是修饰键，不需要立即检查热键
        if key in self.modifier_keys:
            return
        
        # 检查热键匹配 - 只在按下非修饰键时检查
        try:
            # 对每个已注册的热键进行检查
            for hotkey_str, callback in self.hotkeys.items():
                required_modifiers, main_key = self.parse_hotkey(hotkey_str)
                if main_key is None:
                    continue
                
                # 检查主键是否匹配
                key_matched = False
                pressed_key_str = self.key_to_string(key)
                
                # 数字键的特殊处理
                if main_key.isdigit() and pressed_key_str.isdigit():
                    key_matched = main_key == pressed_key_str
                # 功能键的特殊处理
                elif main_key.startswith('f') and main_key[1:].isdigit():
                    # 处理f1-f12
                    func_key_name = main_key.lower()
                    if hasattr(key, 'name') and key.name.lower() == func_key_name:
                        key_matched = True
                    elif pressed_key_str == func_key_name:
                        key_matched = True
                else:
                    # 其他普通按键
                    key_matched = main_key == pressed_key_str
                
                # 检查修饰键是否匹配
                current_modifiers = set()
                for mod_key in self.pressed_keys:
                    if mod_key in self.modifier_keys:
                        current_modifiers.add(self.modifier_keys[mod_key])
                
                modifiers_matched = required_modifiers.issubset(current_modifiers)
                
                # 打印详细匹配信息
                print(f"  检查热键 '{hotkey_str}': 修饰键匹配={modifiers_matched}, 主键匹配={key_matched}")
                print(f"    需要修饰键={required_modifiers}, 当前修饰键={current_modifiers}")
                print(f"    期望主键='{main_key}', 实际主键='{pressed_key_str}'")
                
                # 如果主键和修饰键都匹配，触发回调
                if key_matched and modifiers_matched:
                    # 防止重复触发同一个热键
                    current_combination = f"{hotkey_str}_{pressed_key_str}"
                    if self.last_triggered_hotkey != current_combination:
                        print(f"✓ 热键匹配成功: {hotkey_str}")
                        self.last_triggered_hotkey = current_combination
                        
                        # 在主线程中执行回调，并添加异常处理
                        try:
                            # 使用一个更明确的方式确保在主线程中执行回调
                            print(f"尝试执行热键回调: {hotkey_str}, 回调类型: {type(callback).__name__}")
                            
                            # 尝试直接执行回调，而不是使用QTimer
                            try:
                                print(f"直接执行回调: {hotkey_str}")
                                callback()
                                print(f"✓ 回调直接执行成功: {hotkey_str}")
                            except Exception as direct_e:
                                print(f"直接执行回调失败，尝试使用QTimer: {direct_e}")
                                # 如果直接执行失败，则使用QTimer尝试
                                QTimer.singleShot(0, callback)
                                print(f"✓ 热键回调已通过QTimer安排执行: {hotkey_str}")
                                
                        except Exception as e:
                            print(f"✗ 热键回调执行失败: {hotkey_str}, 错误: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"热键重复触发，忽略: {hotkey_str}")
        except Exception as e:
            print(f"Hotkey processing error: {e}")
            import traceback
            traceback.print_exc()

    def on_release(self, key):
        """按键释放事件"""
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
            key_str = self.key_to_string(key)
            print(f"按键释放: {key_str}")
            
            # 如果释放的是主键（非修饰键），重置最后触发的热键
            if key not in self.modifier_keys:
                self.last_triggered_hotkey = None
                print("主键释放，重置热键状态")
            
            # 如果所有键都释放了，也重置状态
            if not self.pressed_keys:
                self.last_triggered_hotkey = None
                print("所有按键已释放，重置热键状态")

    def start_listening(self):
        """开始监听热键"""
        if self.listener is None:
            try:
                self.listener = keyboard.Listener(
                    on_press=self.on_press, 
                    on_release=self.on_release,
                    suppress=False  # 不拦截按键，让其他应用也能接收
                )
                self.listener.start()
                print("热键监听已启动")
                return True
            except Exception as e:
                print(f"启动热键监听失败: {e}")
                return False
        return True

    def stop_listening(self):
        """停止监听热键"""
        if self.listener:
            try:
                self.listener.stop()
                self.listener = None
                self.pressed_keys.clear()
                print("热键监听已停止")
            except Exception as e:
                print(f"停止热键监听失败: {e}")


