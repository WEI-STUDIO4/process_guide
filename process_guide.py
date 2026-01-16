import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import json
import os
import threading
import time
from datetime import datetime
import queue

# 全局模块可用性检查
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("注意: keyboard模块未安装，按键录制功能不可用")
    print("请运行: pip install keyboard")

try:
    import mouse
    MOUSE_AVAILABLE = True
except ImportError:
    MOUSE_AVAILABLE = False
    print("注意: mouse模块未安装，鼠标录制功能不可用")
    print("请运行: pip install mouse")

class SAAPFileManager:
    """SAAP文件管理器"""
    
    @staticmethod
    def save_data(filepath, processes, settings):
        """保存数据到SAAP文件"""
        try:
            data = {
                'metadata': {
                    'format': 'SAAP',
                    'version': '1.0',
                    'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'process_count': len(processes)
                },
                'settings': settings,
                'processes': []
            }
            
            for process in processes:
                data['processes'].append({
                    'display_name': process['display_name'],
                    'key': process['key']
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            raise Exception(f"保存失败: {str(e)}")
    
    @staticmethod
    def load_data(filepath):
        """从SAAP文件加载数据"""
        try:
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证文件格式
            if not isinstance(data, dict) or 'processes' not in data:
                raise ValueError("无效的SAAP文件格式")
            
            return data
        except Exception as e:
            raise Exception(f"加载失败: {str(e)}")
    
    @staticmethod
    def get_default_filename():
        """获取默认文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"process_guide_{timestamp}.saap"
    
    @staticmethod
    def is_saap_file(filepath):
        """检查是否为SAAP文件"""
        return filepath.lower().endswith('.saap')


class GuideWindow:
    """独立的引导提示窗口"""
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("按键提示")
        self.window.attributes('-topmost', True)  # 始终置顶
        self.window.overrideredirect(True)  # 无边框
        self.window.configure(bg='yellow')
        
        # 设置窗口位置（屏幕右上角）
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"400x100+{screen_width-420}+20")
        
        # 创建标签
        self.label = tk.Label(self.window, text="", font=('Arial', 20, 'bold'), 
                             fg='red', bg='yellow', wraplength=380)
        self.label.pack(expand=True, fill='both', padx=10, pady=10)
        
        # 初始隐藏
        self.window.withdraw()
    
    def show(self, text):
        """显示提示"""
        self.label.config(text=text)
        self.window.deiconify()
    
    def hide(self):
        """隐藏提示"""
        self.window.withdraw()
    
    def update_text(self, text):
        """更新提示文本"""
        self.label.config(text=text)
    
    def set_colors(self, fg_color, bg_color, transparent=False):
        """设置文字颜色和背景颜色"""
        self.label.config(fg=fg_color)
        if not transparent:
            self.label.config(bg=bg_color)
            self.window.config(bg=bg_color)
        else:
            # 设置透明背景
            self.label.config(bg=bg_color)
            self.window.config(bg=bg_color)
            self.window.attributes('-alpha', 0.8)  # 设置透明度


class KeyEventRecorder:
    """按键事件录制器（支持键盘和鼠标）"""
    
    def __init__(self):
        self.is_recording = False
        self.recorded_keys = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.max_events = 50
        
        # 存储当前按下的修饰键
        self.current_modifiers = {
            'ctrl': False,
            'shift': False,
            'alt': False
        }
        
    def start_recording(self):
        """开始录制"""
        with self.lock:
            if self.is_recording:
                return False
            
            self.is_recording = True
            self.recorded_keys = []
            self.current_modifiers = {'ctrl': False, 'shift': False, 'alt': False}
            self.stop_event.clear()
            
            # 启动录制线程
            self.recording_thread = threading.Thread(target=self._recording_thread, daemon=True)
            self.recording_thread.start()
            
            return True
    
    def stop_recording(self):
        """停止录制"""
        with self.lock:
            if not self.is_recording:
                return
            
            self.is_recording = False
            self.stop_event.set()
            
            # 清理钩子
            if KEYBOARD_AVAILABLE:
                try:
                    keyboard.unhook_all()
                except:
                    pass
            if MOUSE_AVAILABLE:
                try:
                    mouse.unhook_all()
                except:
                    pass
    
    def get_recorded_keys(self):
        """获取录制的按键"""
        with self.lock:
            return self.recorded_keys.copy()
    
    def _recording_thread(self):
        """录制线程"""
        try:
            # 设置键盘钩子
            if KEYBOARD_AVAILABLE:
                keyboard.hook(self._on_keyboard_event)
            
            # 设置鼠标钩子
            if MOUSE_AVAILABLE:
                mouse.hook(self._on_mouse_event)
            
            # 等待停止信号
            while not self.stop_event.is_set() and len(self.recorded_keys) < self.max_events:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"录制线程异常: {e}")
        finally:
            # 确保清理钩子
            if KEYBOARD_AVAILABLE:
                try:
                    keyboard.unhook_all()
                except:
                    pass
            if MOUSE_AVAILABLE:
                try:
                    mouse.unhook_all()
                except:
                    pass
    
    def _on_keyboard_event(self, event):
        """键盘事件处理"""
        if not self.is_recording:
            return
        
        key_name = event.name.upper()
        
        # 更新修饰键状态
        if key_name in ['CTRL', 'CONTROL', 'LEFT CTRL', 'RIGHT CTRL']:
            self.current_modifiers['ctrl'] = (event.event_type == keyboard.KEY_DOWN)
        elif key_name in ['SHIFT', 'LEFT SHIFT', 'RIGHT SHIFT']:
            self.current_modifiers['shift'] = (event.event_type == keyboard.KEY_DOWN)
        elif key_name in ['ALT', 'LEFT ALT', 'RIGHT ALT', 'ALT GR']:
            self.current_modifiers['alt'] = (event.event_type == keyboard.KEY_DOWN)
        
        # 只处理按键按下事件
        if event.event_type != keyboard.KEY_DOWN:
            return
        
        # 检查当前按下的修饰键
        modifiers = []
        if self.current_modifiers['ctrl']:
            modifiers.append('CTRL')
        if self.current_modifiers['shift']:
            modifiers.append('SHIFT')
        if self.current_modifiers['alt']:
            modifiers.append('ALT')
        
        # 跳过单独的修饰键按下事件
        if key_name in ['CTRL', 'CONTROL', 'LEFT CTRL', 'RIGHT CTRL', 
                       'SHIFT', 'LEFT SHIFT', 'RIGHT SHIFT',
                       'ALT', 'LEFT ALT', 'RIGHT ALT', 'ALT GR',
                       'WINDOWS', 'WIN', 'LEFT WINDOWS', 'RIGHT WINDOWS']:
            return
        
        # 构建按键字符串
        if modifiers:
            key_str = '+'.join(modifiers + [key_name])
        else:
            key_str = key_name
        
        # 特殊处理空格键
        if key_name == 'SPACE':
            key_str = 'SPACE'
        
        # 添加到录制列表
        with self.lock:
            if len(self.recorded_keys) < self.max_events:
                self.recorded_keys.append(key_str)
    
    def _on_mouse_event(self, event):
        """鼠标事件处理"""
        if not self.is_recording:
            return
        
        key_str = None
        
        if isinstance(event, mouse.ButtonEvent):
            if event.event_type == mouse.DOWN:
                button_names = {
                    mouse.LEFT: "鼠标左键",
                    mouse.RIGHT: "鼠标右键",
                    mouse.MIDDLE: "鼠标中键",
                    mouse.X: "鼠标侧键",
                    mouse.X2: "鼠标侧键2"
                }
                button_name = button_names.get(event.button, f"鼠标按钮{event.button}")
                
                # 使用当前修饰键状态
                modifiers = []
                if self.current_modifiers['ctrl']:
                    modifiers.append('CTRL')
                if self.current_modifiers['shift']:
                    modifiers.append('SHIFT')
                if self.current_modifiers['alt']:
                    modifiers.append('ALT')
                
                if modifiers:
                    key_str = '+'.join(modifiers + [button_name])
                else:
                    key_str = button_name
                    
        elif isinstance(event, mouse.WheelEvent):
            direction = "滚轮向上" if event.delta > 0 else "滚轮向下"
            
            # 使用当前修饰键状态
            modifiers = []
            if self.current_modifiers['ctrl']:
                modifiers.append('CTRL')
            if self.current_modifiers['shift']:
                modifiers.append('SHIFT')
            if self.current_modifiers['alt']:
                modifiers.append('ALT')
            
            if modifiers:
                key_str = '+'.join(modifiers + [direction])
            else:
                key_str = direction
        
        if key_str:
            with self.lock:
                if len(self.recorded_keys) < self.max_events:
                    self.recorded_keys.append(key_str)


class ProcessGuideApp:
    def __init__(self, root):
        self.root = root
        self.root.title("工序按键引导程序 - SAAP格式")
        self.root.geometry("900x700")
        
        # 存储工序的列表
        self.processes = []
        self.current_process_index = -1
        self.is_guiding = False
        self.loop_guide = False
        
        # 颜色设置
        self.text_color = 'red'
        self.bg_color = 'yellow'
        self.transparent = False
        
        # 创建独立的引导窗口
        self.guide_window = GuideWindow()
        
        # 创建事件录制器
        self.recorder = KeyEventRecorder()
        
        # 创建GUI组件
        self.create_widgets()
        
        # 加载最近的文件
        self.current_file = None
        self.load_recent_file()
        
        # 绑定全局按键事件
        self.root.bind('<Key>', self.handle_key_press)
        
    def create_widgets(self):
        # 顶部控制区域
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 文件操作按钮
        self.new_button = ttk.Button(control_frame, text="新建", command=self.new_file)
        self.new_button.grid(row=0, column=0, padx=5)
        
        self.load_button = ttk.Button(control_frame, text="加载", command=self.load_file)
        self.load_button.grid(row=0, column=1, padx=5)
        
        self.save_button = ttk.Button(control_frame, text="保存", command=self.save_file)
        self.save_button.grid(row=0, column=2, padx=5)
        
        self.save_as_button = ttk.Button(control_frame, text="另存为", command=self.save_as_file)
        self.save_as_button.grid(row=0, column=3, padx=5)
        
        # 添加工序按钮
        self.add_button = ttk.Button(control_frame, text="添加工序", command=self.add_process)
        self.add_button.grid(row=0, column=4, padx=5)
        
        # 录制工序按钮
        self.record_button = ttk.Button(control_frame, text="录制工序", command=self.record_processes)
        self.record_button.grid(row=0, column=5, padx=5)
        
        # 开始引导按钮
        self.start_button = ttk.Button(control_frame, text="开始引导", command=self.start_guide)
        self.start_button.grid(row=0, column=6, padx=5)
        
        # 停止引导按钮
        self.stop_button = ttk.Button(control_frame, text="停止引导", command=self.stop_guide, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=7, padx=5)
        
        # 循环模式复选框
        self.loop_var = tk.BooleanVar(value=False)
        self.loop_check = ttk.Checkbutton(control_frame, text="循环模式", 
                                         variable=self.loop_var,
                                         command=self.on_loop_change)
        self.loop_check.grid(row=0, column=8, padx=5)
        
        # 颜色设置区域
        color_frame = ttk.LabelFrame(self.root, text="提示窗口颜色设置", padding="10")
        color_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # 文字颜色选择
        ttk.Label(color_frame, text="文字颜色:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.text_color_btn = ttk.Button(color_frame, text="选择", command=self.choose_text_color)
        self.text_color_btn.grid(row=0, column=1, padx=5, pady=5)
        self.text_color_label = tk.Label(color_frame, text="红色", bg='red', width=10)
        self.text_color_label.grid(row=0, column=2, padx=5, pady=5)
        
        # 背景颜色选择
        ttk.Label(color_frame, text="背景颜色:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.bg_color_btn = ttk.Button(color_frame, text="选择", command=self.choose_bg_color)
        self.bg_color_btn.grid(row=1, column=1, padx=5, pady=5)
        self.bg_color_label = tk.Label(color_frame, text="黄色", bg='yellow', width=10)
        self.bg_color_label.grid(row=1, column=2, padx=5, pady=5)
        
        # 透明背景复选框
        self.transparent_var = tk.BooleanVar(value=False)
        self.transparent_check = ttk.Checkbutton(color_frame, text="透明背景", 
                                               variable=self.transparent_var,
                                               command=self.on_transparent_change)
        self.transparent_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # 应用颜色按钮
        self.apply_color_btn = ttk.Button(color_frame, text="应用颜色", command=self.apply_colors)
        self.apply_color_btn.grid(row=2, column=2, padx=5, pady=5)
        
        # 工序列表区域
        list_frame = ttk.LabelFrame(self.root, text="工序列表", padding="10")
        list_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # 创建Treeview显示工序
        columns = ('序号', '显示名称', '按键', '操作')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # 操作按钮区域
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, pady=10)
        
        self.edit_button = ttk.Button(button_frame, text="修改选中", command=self.edit_selected, state=tk.DISABLED)
        self.edit_button.grid(row=0, column=0, padx=5)
        
        self.delete_button = ttk.Button(button_frame, text="删除选中", command=self.delete_selected, state=tk.DISABLED)
        self.delete_button.grid(row=0, column=1, padx=5)
        
        self.move_up_button = ttk.Button(button_frame, text="上移", command=self.move_up, state=tk.DISABLED)
        self.move_up_button.grid(row=0, column=2, padx=5)
        
        self.move_down_button = ttk.Button(button_frame, text="下移", command=self.move_down, state=tk.DISABLED)
        self.move_down_button.grid(row=0, column=3, padx=5)
        
        # 绑定Treeview选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # 文件信息显示
        self.file_info_var = tk.StringVar()
        self.file_info_var.set("未加载文件")
        file_info_label = ttk.Label(self.root, textvariable=self.file_info_var)
        file_info_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 - 共 0 个工序")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 配置主窗口网格权重
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        
    def new_file(self):
        """新建文件"""
        if self.processes and not messagebox.askyesno("确认", "当前数据未保存，确定要新建吗？"):
            return
        
        self.processes = []
        self.current_file = None
        self.update_treeview()
        self.update_status()
        self.file_info_var.set("新建文件")
        self.root.title("工序按键引导程序 - SAAP格式 [新建]")
    
    def load_file(self):
        """加载SAAP文件"""
        from tkinter import filedialog
        
        filepath = filedialog.askopenfilename(
            title="选择SAAP文件",
            filetypes=[
                ("SAAP文件", "*.saap"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if not filepath:
            return
        
        try:
            data = SAAPFileManager.load_data(filepath)
            if not data:
                messagebox.showerror("错误", "无法加载文件")
                return
            
            # 清空现有数据
            self.processes = []
            
            # 加载工序
            for i, item in enumerate(data.get('processes', [])):
                self.processes.append({
                    'display_name': item['display_name'],
                    'key': item['key'],
                    'index': i
                })
            
            # 加载设置
            settings = data.get('settings', {})
            self.loop_guide = settings.get('loop_guide', False)
            self.loop_var.set(self.loop_guide)
            
            self.text_color = settings.get('text_color', 'red')
            self.text_color_label.config(text=self.text_color, bg=self.text_color)
            
            self.bg_color = settings.get('bg_color', 'yellow')
            self.bg_color_label.config(text=self.bg_color, bg=self.bg_color)
            
            self.transparent = settings.get('transparent', False)
            self.transparent_var.set(self.transparent)
            
            # 应用颜色设置
            self.guide_window.set_colors(self.text_color, self.bg_color, self.transparent)
            
            # 更新UI
            self.current_file = filepath
            self.update_treeview()
            self.update_status()
            
            # 显示文件信息
            filename = os.path.basename(filepath)
            process_count = len(self.processes)
            self.file_info_var.set(f"已加载: {filename} ({process_count}个工序)")
            self.root.title(f"工序按键引导程序 - SAAP格式 [{filename}]")
            
            messagebox.showinfo("成功", f"已加载 {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载失败: {str(e)}")
    
    def save_file(self):
        """保存文件"""
        if not self.current_file:
            return self.save_as_file()
        
        try:
            settings = {
                'loop_guide': self.loop_guide,
                'text_color': self.text_color,
                'bg_color': self.bg_color,
                'transparent': self.transparent
            }
            
            SAAPFileManager.save_data(self.current_file, self.processes, settings)
            
            filename = os.path.basename(self.current_file)
            self.file_info_var.set(f"已保存: {filename}")
            messagebox.showinfo("成功", f"已保存到 {filename}")
            
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            return False
    
    def save_as_file(self):
        """另存为SAAP文件"""
        from tkinter import filedialog
        
        default_filename = SAAPFileManager.get_default_filename()
        filepath = filedialog.asksaveasfilename(
            title="保存为SAAP文件",
            defaultextension=".saap",
            filetypes=[
                ("SAAP文件", "*.saap"),
                ("所有文件", "*.*")
            ],
            initialfile=default_filename
        )
        
        if not filepath:
            return False
        
        # 确保扩展名正确
        if not SAAPFileManager.is_saap_file(filepath):
            filepath += '.saap'
        
        try:
            settings = {
                'loop_guide': self.loop_guide,
                'text_color': self.text_color,
                'bg_color': self.bg_color,
                'transparent': self.transparent
            }
            
            SAAPFileManager.save_data(filepath, self.processes, settings)
            
            self.current_file = filepath
            filename = os.path.basename(filepath)
            self.file_info_var.set(f"已保存: {filename}")
            self.root.title(f"工序按键引导程序 - SAAP格式 [{filename}]")
            
            messagebox.showinfo("成功", f"已保存到 {filename}")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            return False
    
    def load_recent_file(self):
        """加载最近的文件"""
        # 检查是否有默认的SAAP文件
        default_files = ['default.saap', 'process_guide.saap']
        for filename in default_files:
            if os.path.exists(filename):
                try:
                    data = SAAPFileManager.load_data(filename)
                    if data:
                        self.load_from_data(data, filename)
                        return
                except:
                    pass
    
    def load_from_data(self, data, filepath):
        """从数据加载"""
        self.processes = []
        
        for i, item in enumerate(data.get('processes', [])):
            self.processes.append({
                'display_name': item['display_name'],
                'key': item['key'],
                'index': i
            })
        
        settings = data.get('settings', {})
        self.loop_guide = settings.get('loop_guide', False)
        self.loop_var.set(self.loop_guide)
        
        self.text_color = settings.get('text_color', 'red')
        self.text_color_label.config(text=self.text_color, bg=self.text_color)
        
        self.bg_color = settings.get('bg_color', 'yellow')
        self.bg_color_label.config(text=self.bg_color, bg=self.bg_color)
        
        self.transparent = settings.get('transparent', False)
        self.transparent_var.set(self.transparent)
        
        self.guide_window.set_colors(self.text_color, self.bg_color, self.transparent)
        
        self.current_file = filepath
        self.update_treeview()
        self.update_status()
        
        filename = os.path.basename(filepath)
        self.file_info_var.set(f"已加载: {filename}")
        self.root.title(f"工序按键引导程序 - SAAP格式 [{filename}]")
    
    def add_process(self):
        """添加新工序"""
        dialog = ProcessDialog(self.root, "添加工序")
        if dialog.result:
            display_name, key = dialog.result
            process = {
                'display_name': display_name,
                'key': key,
                'index': len(self.processes)
            }
            self.processes.append(process)
            self.update_treeview()
            self.update_status()
    
    def record_processes(self):
        """录制多个工序按键"""
        if not KEYBOARD_AVAILABLE and not MOUSE_AVAILABLE:
            messagebox.showwarning("警告", "keyboard和mouse模块均未安装，无法录制")
            print("请运行: pip install keyboard mouse")
            return
        
        dialog = RecordProcessesDialog(self.root, "录制工序", self.recorder)
        if dialog.result:
            # 清空现有工序
            self.processes = []
            
            # 添加录制的工序
            for i, key in enumerate(dialog.result):
                process = {
                    'display_name': f"步骤{i+1}",
                    'key': key,
                    'index': i
                }
                self.processes.append(process)
            
            self.update_treeview()
            self.update_status()
            messagebox.showinfo("成功", f"已录制 {len(dialog.result)} 个工序")
    
    def edit_selected(self):
        """修改选中的工序"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = int(self.tree.item(item, 'values')[0]) - 1
        
        if 0 <= index < len(self.processes):
            process = self.processes[index]
            dialog = ProcessDialog(self.root, "修改工序", 
                                 initial_name=process['display_name'],
                                 initial_key=process['key'])
            if dialog.result:
                display_name, key = dialog.result
                self.processes[index]['display_name'] = display_name
                self.processes[index]['key'] = key
                self.update_treeview()
    
    def delete_selected(self):
        """删除选中的工序"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = int(self.tree.item(item, 'values')[0]) - 1
        
        if 0 <= index < len(self.processes):
            del self.processes[index]
            # 更新剩余工序的索引
            for i in range(len(self.processes)):
                self.processes[i]['index'] = i
            self.update_treeview()
            self.update_status()
    
    def move_up(self):
        """上移选中的工序"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = int(self.tree.item(item, 'values')[0]) - 1
        
        if index > 0:
            # 交换位置
            self.processes[index], self.processes[index-1] = self.processes[index-1], self.processes[index]
            # 更新索引
            for i in range(len(self.processes)):
                self.processes[i]['index'] = i
            self.update_treeview()
            self.tree.selection_set(self.tree.get_children()[index-1])
    
    def move_down(self):
        """下移选中的工序"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = int(self.tree.item(item, 'values')[0]) - 1
        
        if index < len(self.processes) - 1:
            # 交换位置
            self.processes[index], self.processes[index+1] = self.processes[index+1], self.processes[index]
            # 更新索引
            for i in range(len(self.processes)):
                self.processes[i]['index'] = i
            self.update_treeview()
            self.tree.selection_set(self.tree.get_children()[index+1])
    
    def start_guide(self):
        """开始引导流程"""
        if not self.processes:
            messagebox.showwarning("警告", "请先添加工序！")
            return
        
        self.is_guiding = True
        self.current_process_index = 0
        self.update_guide_display()
        
        # 更新按钮状态
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.add_button.config(state=tk.DISABLED)
        self.record_button.config(state=tk.DISABLED)
        
        # 显示引导窗口
        self.guide_window.window.deiconify()
    
    def stop_guide(self):
        """停止引导流程"""
        self.is_guiding = False
        self.current_process_index = -1
        self.guide_window.hide()
        
        # 更新按钮状态
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)
        self.record_button.config(state=tk.NORMAL)
    
    def update_guide_display(self):
        """更新引导显示"""
        if self.is_guiding and 0 <= self.current_process_index < len(self.processes):
            process = self.processes[self.current_process_index]
            text = f"接下来该按下: {process['display_name']} ({process['key']})"
            self.guide_window.update_text(text)
        else:
            self.guide_window.hide()
    
    def handle_key_press(self, event):
        """处理按键事件"""
        if not self.is_guiding:
            return
        
        # 获取按下的键
        modifiers = []
        if event.state & 0x4:  # Ctrl键
            modifiers.append('CTRL')
        if event.state & 0x1:  # Shift键
            modifiers.append('SHIFT')
        if event.state & 0x8:  # Alt键
            modifiers.append('ALT')
        
        key_name = event.keysym.upper()
        
        # 构建按键字符串
        if modifiers:
            pressed_key = '+'.join(modifiers + [key_name])
        else:
            pressed_key = key_name
        
        # 特殊处理空格键
        if key_name == 'SPACE':
            pressed_key = 'SPACE'
        
        # ESC键退出引导
        if pressed_key == 'ESCAPE' or (modifiers and key_name == 'ESCAPE'):
            self.stop_guide()
            return
        
        if self.current_process_index < len(self.processes):
            expected_key = self.processes[self.current_process_index]['key'].upper()
            
            # 简化匹配逻辑，忽略大小写
            if pressed_key.upper() == expected_key.upper():
                # 按键正确，进入下一个工序
                self.current_process_index += 1
                
                if self.current_process_index >= len(self.processes):
                    # 所有工序完成
                    if self.loop_guide:
                        # 循环模式：返回第一项继续指导
                        self.current_process_index = 0
                        self.update_guide_display()
                    else:
                        # 单次指导：显示完成消息
                        self.guide_window.update_text("所有工序已完成！")
                        # 2秒后自动隐藏
                        self.root.after(2000, self.stop_guide)
                else:
                    # 显示下一个工序
                    self.update_guide_display()
            # 注意：不再显示错误提示，只是忽略错误的按键
    
    def update_treeview(self):
        """更新Treeview显示"""
        # 清空现有项
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加新项
        for i, process in enumerate(self.processes):
            self.tree.insert('', 'end', values=(
                i + 1,
                process['display_name'],
                process['key'],
                "点击右侧按钮操作"
            ))
    
    def on_tree_select(self, event):
        """处理Treeview选择事件"""
        selection = self.tree.selection()
        if selection:
            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.move_up_button.config(state=tk.NORMAL)
            self.move_down_button.config(state=tk.DISABLED)
        else:
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            self.move_up_button.config(state=tk.DISABLED)
            self.move_down_button.config(state=tk.DISABLED)
    
    def update_status(self):
        """更新状态栏"""
        self.status_var.set(f"就绪 - 共 {len(self.processes)} 个工序")
    
    def update_file_info(self):
        """更新文件信息"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.file_info_var.set(f"当前文件: {filename}")
        else:
            self.file_info_var.set("未加载文件")
    
    def on_loop_change(self):
        """循环指导复选框变化"""
        self.loop_guide = self.loop_var.get()
    
    def on_transparent_change(self):
        """透明背景复选框变化"""
        self.transparent = self.transparent_var.get()
    
    def choose_text_color(self):
        """选择文字颜色"""
        color = colorchooser.askcolor(title="选择文字颜色", initialcolor=self.text_color)
        if color[1]:
            self.text_color = color[1]
            self.text_color_label.config(text=color[1], bg=color[1])
    
    def choose_bg_color(self):
        """选择背景颜色"""
        color = colorchooser.askcolor(title="选择背景颜色", initialcolor=self.bg_color)
        if color[1]:
            self.bg_color = color[1]
            self.bg_color_label.config(text=color[1], bg=color[1])
    
    def apply_colors(self):
        """应用颜色设置到引导窗口"""
        self.guide_window.set_colors(self.text_color, self.bg_color, self.transparent)
        messagebox.showinfo("成功", "颜色设置已应用到引导窗口")


class RecordProcessesDialog:
    """录制多个工序对话框"""
    
    def __init__(self, parent, title, recorder):
        self.parent = parent
        self.recorder = recorder
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry(f"+{parent.winfo_rootx()+100}+{parent.winfo_rooty()+100}")
        
        # 说明标签
        ttk.Label(self.dialog, text="录制多个工序事件（键盘+鼠标）", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)
        
        ttk.Label(self.dialog, text="支持: 单个按键、组合键(如Ctrl+C)、鼠标点击、滚轮", 
                 wraplength=450).grid(row=1, column=0, columnspan=3, pady=5)
        ttk.Label(self.dialog, text="按ESC键结束录制", foreground="red").grid(
            row=2, column=0, columnspan=3, pady=5)
        
        # 录制状态显示
        self.status_var = tk.StringVar(value="准备录制")
        self.status_label = ttk.Label(self.dialog, textvariable=self.status_var, 
                                     font=('Arial', 10, 'bold'))
        self.status_label.grid(row=3, column=0, columnspan=3, pady=10)
        
        # 已录制事件显示
        ttk.Label(self.dialog, text="已录制的事件:").grid(
            row=4, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        self.events_text = tk.Text(self.dialog, height=10, width=50)
        self.events_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)
        self.events_text.config(state=tk.DISABLED)
        
        # 按钮区域
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="开始录制", command=self.start_recording)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = ttk.Button(button_frame, text="停止录制", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        
        # 绑定ESC键
        self.dialog.bind('<Escape>', lambda e: self.stop_recording())
        
        # 定期更新显示
        self.update_display()
        
        self.dialog.wait_window()
    
    def start_recording(self):
        """开始录制"""
        if self.recorder.start_recording():
            self.status_var.set("正在录制...按ESC键结束")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
    
    def stop_recording(self):
        """停止录制"""
        self.recorder.stop_recording()
        recorded_keys = self.recorder.get_recorded_keys()
        self.status_var.set(f"录制完成，共 {len(recorded_keys)} 个事件")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        recorded_keys = self.recorder.get_recorded_keys()
        
        self.events_text.config(state=tk.NORMAL)
        self.events_text.delete(1.0, tk.END)
        
        for i, key in enumerate(recorded_keys):
            self.events_text.insert(tk.END, f"{i+1}. {key}\n")
        
        self.events_text.config(state=tk.DISABLED)
        
        # 定期更新
        if hasattr(self, 'dialog') and self.dialog.winfo_exists():
            self.dialog.after(500, self.update_display)
    
    def on_ok(self):
        """确定按钮处理"""
        recorded_keys = self.recorder.get_recorded_keys()
        
        if not recorded_keys:
            messagebox.showwarning("警告", "请先录制至少一个事件！")
            return
        
        self.result = recorded_keys
        self.recorder.stop_recording()
        self.dialog.destroy()
    
    def on_cancel(self):
        """取消按钮处理"""
        self.recorder.stop_recording()
        self.dialog.destroy()


class ProcessDialog:
    """添加工序对话框"""
    
    def __init__(self, parent, title, initial_name="", initial_key=""):
        self.result = None
        self.recorder = KeyEventRecorder()
        self.is_recording = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry(f"+{parent.winfo_rootx()+150}+{parent.winfo_rooty()+150}")
        
        # 显示名称
        ttk.Label(self.dialog, text="显示名称:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.name_var = tk.StringVar(value=initial_name)
        self.name_entry = ttk.Entry(self.dialog, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10)
        
        # 按键输入区域
        ttk.Label(self.dialog, text="按键:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.key_var = tk.StringVar(value=initial_key)
        self.key_entry = ttk.Entry(self.dialog, textvariable=self.key_var, width=30)
        self.key_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # 录制按钮
        self.record_button = ttk.Button(self.dialog, text="录制按键", command=self.toggle_recording)
        self.record_button.grid(row=1, column=2, padx=5, pady=10)
        
        # 录制状态显示
        self.recording_var = tk.StringVar(value="")
        self.recording_label = ttk.Label(self.dialog, textvariable=self.recording_var, 
                                        foreground="red")
        self.recording_label.grid(row=2, column=0, columnspan=3, pady=5)
        
        # 支持的按键说明
        help_text = """支持的按键格式:
• 单个键: A, 1, F1, ESC, SPACE, ENTER
• 组合键: CTRL+C, SHIFT+A, CTRL+SHIFT+S
• 鼠标: 鼠标左键, 鼠标右键, 滚轮向上, 滚轮向下
• 组合鼠标: CTRL+鼠标左键, SHIFT+滚轮向上"""
        
        help_label = tk.Label(self.dialog, text=help_text, justify=tk.LEFT, 
                             wraplength=350)
        help_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        
        # 按钮区域
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.on_ok())
        self.dialog.bind('<Escape>', lambda e: self.on_cancel())
        
        # 初始焦点
        if initial_name:
            self.key_entry.focus_set()
        else:
            self.name_entry.focus_set()
        
        # 定期更新显示
        self.update_display()
        
        self.dialog.wait_window()
    
    def toggle_recording(self):
        """切换录制状态"""
        if not KEYBOARD_AVAILABLE and not MOUSE_AVAILABLE:
            messagebox.showwarning("警告", "keyboard和mouse模块均未安装，无法录制")
            return
        
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """开始录制"""
        if self.recorder.start_recording():
            self.is_recording = True
            self.recording_var.set("正在录制...按任意键或点击鼠标")
            self.record_button.config(text="停止录制")
    
    def stop_recording(self):
        """停止录制"""
        self.recorder.stop_recording()
        self.is_recording = False
        self.recording_var.set("")
        self.record_button.config(text="录制按键")
        
        # 获取录制的最后一个键
        recorded_keys = self.recorder.get_recorded_keys()
        if recorded_keys:
            self.key_var.set(recorded_keys[-1])
    
    def update_display(self):
        """更新显示"""
        if self.is_recording:
            recorded_keys = self.recorder.get_recorded_keys()
            if recorded_keys:
                self.recording_var.set(f"已录制: {recorded_keys[-1]}")
        
        # 定期更新
        if hasattr(self, 'dialog') and self.dialog.winfo_exists():
            self.dialog.after(500, self.update_display)
    
    def on_ok(self):
        """确定按钮处理"""
        name = self.name_var.get().strip()
        key = self.key_var.get().strip()
        
        if not name:
            messagebox.showwarning("警告", "请输入显示名称！")
            return
        
        if not key:
            messagebox.showwarning("警告", "请输入或录制按键！")
            return
        
        # 停止录制
        if self.is_recording:
            self.stop_recording()
        
        # 验证按键（允许各种格式）
        if key:
            self.result = (name, key)
            self.dialog.destroy()
        else:
            messagebox.showwarning("警告", "请输入有效的按键！")
    
    def on_cancel(self):
        """取消按钮处理"""
        # 停止录制
        if self.is_recording:
            self.stop_recording()
        
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = ProcessGuideApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()