import multiprocessing
import time
import os
from tkinter import filedialog as fd

import customtkinter as ctk

import constants as c
from helpers import sequence_sorter, sequence_collector
from frame_inspector import detect_edges

class App(ctk.CTk):
    """Defines Frame Inspector GUI"""
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        # ctk.set_default_color_theme("light-blue")

        self.title("DK Frame Inspector")
        self.geometry(f"{str(c.WINSIZE[0])}x{str(c.WINSIZE[1])}")
        self.maxsize(c.WINSIZE[0], c.WINSIZE[0])
        self.minsize(c.WINSIZE[0], c.WINSIZE[1])

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.font = ctk.CTkFont('Inter', 12, "bold")

        self.files = []
        self.sequence = []
        self.selected_sequence = ""
        self.seq_sframes = []
        self.seq_eframes = []
        self.suspects = []

        self.top_frame = ctk.CTkFrame(master=self)
        self.top_frame.grid(row=0, column=0, padx=10, pady=5)
        self.folder_entry = ctk.CTkEntry(master=self.top_frame, placeholder_text='Render directory:', font=self.font, width=c.FOLDER_ENTRY_WIDTH)
        self.folder_entry.grid(row=0, column=0, padx=10, pady=5)
        self.folder_entry.configure(state='readonly')
        self.folder_btn = ctk.CTkButton(master=self.top_frame, text='Browse', font=self.font, command=self.folder_btn_callback)
        self.folder_btn.grid(row=0, column=1, padx=10, pady=5)

        self.options_frame = ctk.CTkFrame(master=self, fg_color='transparent', bg_color='transparent')
        self.options_frame.grid(row=1, column=0, padx=0, pady=0)

        self.range_frame = ctk.CTkFrame(master=self.options_frame)
        self.range_frame.grid(row=0, column=0, padx=5, pady=5)
        self.range_check = ctk.CTkCheckBox(master=self.range_frame, text='Limit Range', onvalue=True, offvalue=False, font=self.font)
        self.range_check.grid(row=0, column=0, padx=10, pady=5)
        self.range_sframe = ctk.CTkEntry(master=self.range_frame, placeholder_text='First Frame', font=self.font, width=c.RANGE_ENTRY_WIDTH)
        self.range_sframe.grid(row=0, column=1, padx=10, pady=5)
        self.range_eframe = ctk.CTkEntry(master=self.range_frame, placeholder_text='Last Frame', font=self.font, width=c.RANGE_ENTRY_WIDTH)
        self.range_eframe.grid(row=0, column=2, padx=10, pady=5)

        self.method_frame = ctk.CTkFrame(master=self.options_frame)
        self.method_frame.grid(row=0, column=1, padx=5, pady=5)
        self.method_opt = ctk.CTkOptionMenu(master=self.method_frame, values=c.METHOD_OPTIONS, font=self.font, width=90)
        self.method_opt.grid(row=0, column=3, padx=10, pady=5)
        self.method_label = ctk.CTkLabel(master=self.method_frame, text='Method', font=self.font)
        self.method_label.grid(row=0, column=4, padx=10, pady=5)

        self.chan_frame = ctk.CTkFrame(master=self.options_frame)
        self.chan_frame.grid(row=0, column=2, padx=5, pady=5)
        self.chan_val = ctk.StringVar(value='A')
        self.chan_opt = ctk.CTkOptionMenu(master=self.chan_frame, values=c.CHAN_OPTIONS, font=self.font, width=60)
        self.chan_opt.grid(row=0, column=5, padx=10, pady=5)
        self.chan_label = ctk.CTkLabel(master=self.chan_frame, text='Channel', font=self.font)
        self.chan_label.grid(row=0, column=6, padx=10, pady=5)

        self.btn_frame = ctk.CTkFrame(master=self)
        self.btn_frame.grid(row=2, column=0, padx=10, pady=5)

        self.show_btn = ctk.CTkButton(master=self.btn_frame, text="Show Selection", font=self.font, command=self.log_frames)
        self.show_btn.grid(row=0, column=0, padx=10, pady=5)

        self.inspect_btn = ctk.CTkButton(master=self.btn_frame, text='Inspect', font=self.font, command=self.inspect_btn_callback)
        self.inspect_btn.grid(row=0, column=1, padx=10, pady=5)

        self.copy_missing_btn = ctk.CTkButton(master=self.btn_frame, text='To Clipboard', font=self.font)
        self.copy_missing_btn.grid(row=0, column=2, padx=10, pady=5)

        self.seq_frame = ctk.CTkFrame(master=self)
        self.seq_frame.grid(row=3, column=0, padx=5, pady=5)
        self.sequence_textbox = ctk.CTkTextbox(master=self.seq_frame, font=self.font, wrap='none', height = c.SEQ_HEIGHT, width=c.SEQ_WIDTH, fg_color="#BDC3C7")
        self.sequence_textbox.grid(row=0, column=0)
        self.sequence_textbox.bind("<Button-1>", self.on_click)
        self.sequence_textbox.configure(state='disabled')

        self.bottom_frame = ctk.CTkFrame(master=self)
        self.bottom_frame.grid(row=4, column=0, padx=5, pady=0)
        self.log_label = ctk.CTkLabel(master=self.bottom_frame, text='Log: ', font=self.font)
        self.log_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.log = ctk.CTkTextbox(master=self.bottom_frame, font=self.font, wrap="none",  height=c.LOG_HEIGHT, width=c.LOG_WIDTH, fg_color="#E0E0E0")
        self.log.grid(row=1, column=0, sticky='nsew')
        self.log.configure(state='disabled')

    def folder_btn_callback(self):
        """Browse render output folder to"""
        directory = fd.askdirectory()
        if directory != "":
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert("end", directory)
            self.folder_entry.configure(state="readonly")
            self.sequence, self.seq_sframes, self.seq_eframes, viz = sequence_sorter(
                directory)
            self.sequence_textbox.configure(state='normal')
            self.sequence_textbox.delete("0.0", "end")
            for i in range(len(self.sequence)):
                self.sequence_textbox.insert("end", f"{viz[i]}\n")
            self.sequence_textbox.configure(state='disabled')

    def log_frames(self):
        """Outputs all found frames in the log"""
        range_min, range_max = self.preflight_check()
        self.files = sequence_collector(self.folder_entry.get(), self.selected_sequence, self.range_check.get(), range_min, range_max)     
        self.log.configure(state='normal')
        self.log.delete("0.0", "end")
        if self.files == "":
            self.log.insert("end", "Please set a valid frame range.")
            self.log.configure(state='disabled')
            return
        for file in self.files:
            self.log.insert("end", f"{file}\n")
        self.log.configure(state='disabled')

    def inspect_btn_callback(self):
        """Let's a go."""
        range_min, range_max = self.preflight_check()
        self.files = sequence_collector(self.folder_entry.get(), self.selected_sequence, self.range_check.get(), range_min, range_max)
        self.log.configure(state='normal')
        self.log.delete("0.0", "end")
        t1 = time.time()

        file_chunks = [self.files[i:i+8] for i in range(0, len(self.files), 8)]

        for chunk in file_chunks:
            with multiprocessing.Pool(processes=8) as pool:
            
                temp = ((file, self.chan_val.get()) for file in chunk)
                # print(temp)
                result_chunk = pool.starmap(detect_edges, temp)
                self.suspects.extend(result_chunk)
                print(f'\nProcessed {len(chunk)} files.')

            self.log.delete("0.0", "end")                                        
            for s in self.suspects:
                print(f"{s} -> Suspected!")
                self.log.insert("end", f"{s} -> Suspected!\n")
                
        t2 = time.time()
        time_diff_min, time_diff_sec = divmod(t2-t1, 60)
        self.log.insert("0.0", f"Inspection completed in: {int(time_diff_min)} minutes and {int(time_diff_sec)} seconds.\nNumber of suspected files: {len(self.suspects)}.\n\n")
        self.log.configure(state='disabled')

    def on_click(self, event):
        """Defines sequence texbox behaviour for mouse selection"""
        index = self.sequence_textbox.index(f"@{event.x},{event.y}")
        line_start = self.sequence_textbox.index(f"{index} linestart")
        line_end = self.sequence_textbox.index(f"{index} lineend")
        self.sequence_textbox.tag_remove("highlight", "0.0", "end")
        self.sequence_textbox.tag_add("highlight", line_start, line_end)
        self.sequence_textbox.tag_config("highlight", background="#7b3b3b", foreground='white')

    def preflight_check(self):
        """Final check before inspecting"""
        self.log.configure(state='normal')
        selected_line = int(self.sequence_textbox.index('insert').split('.', maxsplit=1)[0])
        if selected_line+1 >= int(self.sequence_textbox.index("end").split('.', maxsplit=1)[0]):
            self.log.delete("0.0", "end")
            self.log.insert("end", "Please select a sequence")
            self.log.configure(state='disabled')
            return
        self.selected_sequence = self.sequence[selected_line-1]
        if self.range_check:
            if self.range_sframe.get() == "" or self.range_eframe.get() == "":
                self.range_sframe.insert(0, "0")
                self.range_eframe.insert(0, "0")
        range_min = int(self.range_sframe.get())
        range_max = int(self.range_eframe.get())
        self.log.configure(state='disabled')
        return range_min, range_max
