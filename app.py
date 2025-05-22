import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DeepSeek import sendMessage

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("دردشة LLM - DeepSeek")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f5f7fa")

        # عنوان أنيق أعلى الدردشة
        self.title_label = tk.Label(root, text="💬 دردشة الذكاء الاصطناعي", font=("Cairo", 26, "bold"), bg="#f5f7fa", fg="#2d2d2d", pady=18)
        self.title_label.pack(side=tk.TOP, fill=tk.X)

        # إطار منطقة الدردشة مع تظليل
        self.chat_frame = tk.Frame(root, bg="#e3eaf2", bd=2, relief=tk.GROOVE)
        self.chat_frame.pack(padx=30, pady=(0, 20), fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, font=("Tahoma", 16), undo=True, bg="#fafdff", bd=0, highlightthickness=0)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.tag_configure('right', justify='right')
        self.chat_display.tag_configure('blue', foreground='#1e88e5', justify='right', font=("Cairo", 15, "bold"))
        self.chat_display.tag_configure('green', foreground='#43a047', justify='right', font=("Cairo", 15, "bold"))
        self.chat_display.tag_configure('black', foreground='#222', justify='right', font=("Cairo", 15))
        self.chat_display.tag_configure('red', foreground='#e53935', justify='right', font=("Cairo", 15, "bold"))
        self.chat_display.tag_configure('code', background='#f4f4f4', foreground='#2d2d2d', font=("Consolas", 14), lmargin1=20, lmargin2=20, justify='right', borderwidth=2, relief=tk.SOLID)

        self.chat_display.bind('<Double-Button-1>', self.copy_code_on_double_click)

        # إطار الإدخال والأزرار
        self.entry_frame = tk.Frame(root, bg="#f5f7fa")
        self.entry_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        self.user_input = tk.Entry(self.entry_frame, font=("Tahoma", 16), justify='right', bd=0, bg="#fafdff", highlightthickness=2, highlightbackground="#b0bec5", highlightcolor="#64b5f6")
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16), ipady=10)
        self.user_input.bind('<Return>', self.send_message)

        self.send_button = tk.Button(self.entry_frame, text="إرسال", font=("Cairo", 16, "bold"), command=self.send_message,
                                     bg="#64b5f6", fg="white", activebackground="#1976d2", activeforeground="white",
                                     bd=0, padx=24, pady=8, cursor="hand2")
        self.send_button.pack(side=tk.RIGHT)
        self.send_button.configure(relief=tk.FLAT)
        self.send_button.bind("<Enter>", lambda e: self.send_button.config(bg="#1976d2"))
        self.send_button.bind("<Leave>", lambda e: self.send_button.config(bg="#64b5f6"))

        self.message_id = None
        self.code_ranges = []  # قائمة لحفظ مواقع الكود البرمجي

    def send_message(self, event=None):
        prompt = self.user_input.get().strip()
        if not prompt:
            return
        self.append_message(f"أنت: {prompt}\n", "blue")
        self.user_input.delete(0, tk.END)
        threading.Thread(target=self.get_llm_response, args=(prompt,)).start()

    def get_llm_response(self, prompt):
        
        try:
            buffer = ""
            in_code = False
            skip_lang = False
            for message in sendMessage(prompt, self.message_id):
                self.message_id = message['id']
                text = message['message']
                parts = re.split(r"(```|''')", text)
                for part in parts:
                    if part in ("'''", "```"):
                        in_code = not in_code
                        skip_lang = in_code
                        if not in_code and buffer:
                            self.append_message(buffer, 'code', end="", track_code=True)
                            buffer = ""
                        continue
                    if in_code:
                        if skip_lang:
                            part = part.lstrip()
                            first_newline = part.find('\n')
                            if first_newline != -1:
                                lang_and_rest = part[:first_newline].split(None, 1)
                                if len(lang_and_rest) == 2:
                                    buffer += lang_and_rest[1] + part[first_newline:]
                                else:
                                    buffer += part[first_newline+1:]
                            else:
                                lang_and_rest = part.split(None, 1)
                                if len(lang_and_rest) == 2:
                                    buffer += lang_and_rest[1]
                            skip_lang = False
                        else:
                            buffer += part
                    else:
                        if buffer:
                            self.append_message(buffer, 'code', end="", track_code=True)
                            buffer = ""
                        self.append_message(part, "black", end="")
            if buffer:
                self.append_message(buffer, 'code', end="", track_code=True)
            self.append_message("\n", "black", end="")
        except Exception as e:
            self.append_message(f"\n[خطأ: {e}]\n", "red")

    def append_message(self, msg, color, end="\n", track_code=False):
        self.chat_display.config(state=tk.NORMAL)
        start_idx = self.chat_display.index(tk.END)
        self.chat_display.insert(tk.END, msg + end, (color, 'right'))
        end_idx = self.chat_display.index(tk.END)
        if track_code and msg.strip():
            self.code_ranges.append((start_idx, end_idx))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def copy_code_on_double_click(self, event):
        idx = self.chat_display.index(f"@{event.x},{event.y}")
        for start, end in self.code_ranges:
            if self.chat_display.compare(idx, ">=", start) and self.chat_display.compare(idx, "<", end):
                code_text = self.chat_display.get(start, end).rstrip()
                self.root.clipboard_clear()
                self.root.clipboard_append(code_text)
                self.show_temp_message("تم نسخ الكود!", duration=1200)
                break

    def show_temp_message(self, msg, duration=1200):
        temp = tk.Label(self.root, text=msg, bg="#dff0d8", fg="#3c763d", font=("Cairo", 14))
        temp.place(relx=0.5, rely=0.02, anchor="n")
        self.root.after(duration, temp.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
