import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


# Model: Управление логикой таймера
class TimerModel:
    def __init__(self):
        self.work_time = 25 * 60  # 25 минут
        self.break_time = 5 * 60  # 5 минут
        self.current_time = self.work_time
        self.mode = "work"  # Текущий режим ("work" или "break")
        self.is_running = False
        self.restart_delay = 10  # Время ожидания перед автоматическим перезапуском (в секундах)

    def start_timer(self):
        self.is_running = True

    def pause_timer(self):
        self.is_running = False

    def reset_timer(self):
        self.is_running = False
        self.current_time = self.work_time if self.mode == "work" else self.break_time

    def switch_mode(self):
        self.mode = "break" if self.mode == "work" else "work"
        self.reset_timer()

    def decrement_time(self):
        if self.is_running and self.current_time > 0:
            self.current_time -= 1
        elif self.is_running and self.current_time == 0:
            self.is_running = False
            return True  # Таймер завершён
        return False

    def set_custom_times(self, work_minutes, break_minutes, restart_delay):
        """Установить пользовательские времена для работы, отдыха и ожидания."""
        self.work_time = work_minutes * 60
        self.break_time = break_minutes * 60
        self.restart_delay = restart_delay
        self.reset_timer()


# View: Интерфейс для пользователя
class TimerView:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Стилизация
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 14))
        self.root.configure(bg="#f5f5f5")

        # Заголовок
        self.title_label = tk.Label(
            root, text="Pomodoro Timer", font=("Helvetica", 18, "bold"), bg="#f5f5f5", fg="#333"
        )
        self.title_label.pack(pady=10)

        # Таймер
        self.label = tk.Label(root, text="25:00", font=("Helvetica", 48), bg="#f5f5f5", fg="#333")
        self.label.pack(pady=20)

        # Кнопки управления
        self.button_frame = tk.Frame(root, bg="#f5f5f5")
        self.button_frame.pack(pady=10)

        self.start_button = ttk.Button(self.button_frame, text="Start", width=10, command=None)
        self.start_button.grid(row=0, column=0, padx=10)

        self.pause_button = ttk.Button(self.button_frame, text="Pause", width=10, command=None)
        self.pause_button.grid(row=0, column=1, padx=10)

        self.reset_button = ttk.Button(self.button_frame, text="Reset", width=10, command=None)
        self.reset_button.grid(row=0, column=2, padx=10)

        # Кнопка "Настройки"
        self.settings_button = ttk.Button(root, text="Settings", width=10, command=None)
        self.settings_button.pack(pady=10)

    def update_time(self, time_left):
        minutes = time_left // 60
        seconds = time_left % 60
        self.label.config(text=f"{minutes:02}:{seconds:02}")

    def notify_user(self, message):
        messagebox.showinfo("Notification", message)


# Controller: Соединяет логику и интерфейс
class TimerController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Привязка кнопок
        self.view.start_button.config(command=self.start_timer)
        self.view.pause_button.config(command=self.pause_timer)
        self.view.reset_button.config(command=self.reset_timer)
        self.view.settings_button.config(command=self.open_settings)

        # Запуск цикла обновления интерфейса
        self.update_view()

    def start_timer(self):
        self.model.start_timer()

    def pause_timer(self):
        self.model.pause_timer()

    def reset_timer(self):
        self.model.reset_timer()
        self.view.update_time(self.model.current_time)

    def update_view(self):
        if self.model.decrement_time():
            self.view.notify_user(
                "Time to take a break!" if self.model.mode == "break" else "Back to work!"
            )
            self.start_restart_delay()
        else:
            self.view.update_time(self.model.current_time)
            self.view.root.after(1000, self.update_view)

    def start_restart_delay(self):
        """Запустить обратный отсчет перед перезапуском таймера."""
        delay = self.model.restart_delay

        def countdown():
            nonlocal delay
            if delay > 0:
                self.view.update_time(delay)
                delay -= 1
                self.view.root.after(1000, countdown)
            else:
                self.model.switch_mode()
                self.model.start_timer()
                self.update_view()

        countdown()

    def open_settings(self):
        """Открыть окно настроек для ввода пользовательских времен."""
        settings_window = tk.Toplevel(self.view.root)
        settings_window.title("Settings")
        settings_window.geometry("300x250")
        settings_window.resizable(False, False)
        settings_window.configure(bg="#f5f5f5")

        tk.Label(
            settings_window, text="Work Time (min):", font=("Helvetica", 12), bg="#f5f5f5", fg="#333"
        ).pack(pady=5)
        work_time_entry = ttk.Entry(settings_window, width=10)
        work_time_entry.pack(pady=5)

        tk.Label(
            settings_window, text="Break Time (min):", font=("Helvetica", 12), bg="#f5f5f5", fg="#333"
        ).pack(pady=5)
        break_time_entry = ttk.Entry(settings_window, width=10)
        break_time_entry.pack(pady=5)

        tk.Label(
            settings_window,
            text="Restart Delay (sec):",
            font=("Helvetica", 12),
            bg="#f5f5f5",
            fg="#333",
        ).pack(pady=5)
        restart_delay_entry = ttk.Entry(settings_window, width=10)
        restart_delay_entry.pack(pady=5)

        def save_settings():
            try:
                work_time = int(work_time_entry.get())
                break_time = int(break_time_entry.get())
                restart_delay = int(restart_delay_entry.get())
                self.model.set_custom_times(work_time, break_time, restart_delay)
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integers for times.")

        save_button = ttk.Button(settings_window, text="Save", command=save_settings)
        save_button.pack(pady=10)


# Инициализация приложения
if __name__ == "__main__":
    root = tk.Tk()
    model = TimerModel()
    view = TimerView(root)
    controller = TimerController(model, view)
    root.mainloop()
