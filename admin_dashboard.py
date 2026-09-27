import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font
import json
import subprocess
import requests
import threading
from chat import load_model  # Import the load_model function
from PIL import Image, ImageTk, ImageSequence  # For adding the university logo
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId

class AdminDashboard:
    """
    Admin Dashboard for managing chatbot intents and unanswered questions.
    """
    LOGO_PATH = "static/images/admin_dashboard UEP LOGO.png"
    LOADING_ICON_PATH = "static/images/XOsx.gif"
    WINDOW_TITLE = "Admin Dashboard"
    BACKGROUND_COLOR = "#0000A0"
    BUTTON_COLOR = "#FFA500"
    BUTTON_ACTIVE_COLOR = "#FFD700"
    FONT_FAMILY = "Segoe UI"

    def __init__(self, root):
        """
        Initialize the Admin Dashboard.
        """
        self.root = root
        self.root.title(self.WINDOW_TITLE)
        self.root.configure(bg=self.BACKGROUND_COLOR)

        self.unanswered = []

        self.title_font = Font(family=self.FONT_FAMILY, size=26, weight="bold")
        self.label_font = Font(family=self.FONT_FAMILY, size=16)
        self.button_font = Font(family=self.FONT_FAMILY, size=16, weight="bold")
        self.entry_font = Font(family=self.FONT_FAMILY, size=14)

        # MongoDB connection
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['chatbot']
        self.intents_collection = self.db['intents']
        self.unanswered_collection = self.db['unanswered_questions']

        # Start the change stream listener in a separate thread
        listener_thread = threading.Thread(target=self.listen_to_changes)
        listener_thread.start()

        self.add_logo()
        self.add_title()
        self.create_widgets()
        self.add_footer()
        self.load_unanswered_questions()

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def add_logo(self):
        """
        Add the university logo to the dashboard.
        """
        try:
            logo_image = Image.open(self.LOGO_PATH)
            logo_image = logo_image.resize((120, 120), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(self.root, image=self.logo_photo, bg=self.BACKGROUND_COLOR)
            logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load logo image: {e}")

    def add_title(self):
        """
        Add the title to the dashboard.
        """
        title_label = tk.Label(
            self.root, text="ADMIN DASHBOARD", font=self.title_font, fg="white", bg=self.BACKGROUND_COLOR
        )
        title_label.place(relx=0.5, rely=0, anchor="n")

    def create_widgets(self):
        """
        Create the widgets for the dashboard.
        """
        self.create_unanswered_frame()
        self.create_entry_frame()
        self.create_delete_button()  # Add delete button
        self.create_reload_unanswered_button()
        self.create_loading_icon()

    def create_unanswered_frame(self):
        """
        Create the frame for displaying unanswered questions.
        """
        unanswered_frame = tk.LabelFrame(
            self.root,
            text="UNANSWERED QUESTIONS",
            font=self.label_font,
            fg="white",
            bg=self.BACKGROUND_COLOR,
            bd=2,
            relief="ridge",
        )
        unanswered_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.unanswered_listbox = tk.Listbox(
            unanswered_frame,
            font=self.entry_font,
            highlightthickness=1,
            selectbackground=self.BUTTON_ACTIVE_COLOR,
            selectforeground="black",
        )
        self.unanswered_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.unanswered_listbox.bind('<MouseWheel>', self.on_mouse_wheel)
        self.unanswered_listbox.bind('<<ListboxSelect>>', self.on_question_select)

    def create_entry_frame(self):
        """
        Create the frame for adding new intents.
        """
        entry_frame = tk.LabelFrame(
            self.root,
            text="ADD NEW INTENT",
            font=self.label_font,
            fg="white",
            bg=self.BACKGROUND_COLOR,
            bd=2,
            relief="ridge",
        )
        entry_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.create_label_and_text(entry_frame, "QUESTION:", 0)
        self.create_label_and_text(entry_frame, "RESPONSE:", 1)
        self.create_label_and_entry(entry_frame, "TAG:", 2)
        self.create_add_button(entry_frame)  # Move Add Intent button here

    def create_label_and_text(self, frame, text, row):
        """
        Create a label and text widget.
        """
        label = tk.Label(frame, text=text, font=self.label_font, fg="white", bg=self.BACKGROUND_COLOR)
        label.grid(row=row, column=0, padx=10, pady=10, sticky="nw")
        text_widget = tk.Text(frame, width=50, height=5, font=self.entry_font, bd=2, relief="solid", wrap="word")
        text_widget.grid(row=row, column=1, padx=10, pady=10, sticky="w")

        text_widget.bind('<MouseWheel>', self.on_mouse_wheel)

        if text == "QUESTION:":
            self.question_text = text_widget
        elif text == "RESPONSE:":
            self.response_text = text_widget

    def create_label_and_entry(self, frame, text, row):
        """
        Create a label and entry widget.
        """
        label = tk.Label(frame, text=text, font=self.label_font, fg="white", bg=self.BACKGROUND_COLOR)
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        entry = tk.Entry(frame, width=50, font=self.entry_font, bd=2, relief="solid")
        entry.grid(row=row, column=1, padx=10, pady=10, sticky="w")
        if text == "TAG:":
            self.tag_entry = entry

    def create_add_button(self, frame=None):
        """
        Create the button for adding a new intent.
        """
        self.add_button = tk.Button(
            frame if frame else self.root,
            text="Add Intent",
            font=self.button_font,
            bg=self.BUTTON_COLOR,
            fg="black",
            activebackground=self.BUTTON_ACTIVE_COLOR,
            command=self.add_intent,
            relief="flat",
            bd=0,
        )
        self.add_button.grid(row=3, column=1, pady=20, sticky="n")
        self.add_button.bind("<Enter>", self.on_enter)
        self.add_button.bind("<Leave>", self.on_leave)

    def create_reload_unanswered_button(self):
        """
        Create the button for reloading unanswered questions.
        """
        self.reload_unanswered_button = tk.Button(
            self.root,
            text="Reload",
            font=self.button_font,
            bg=self.BUTTON_COLOR,
            fg="black",
            activebackground=self.BUTTON_ACTIVE_COLOR,
            command=self.load_unanswered_questions,
            relief="flat",
            bd=0,
        )
        self.reload_unanswered_button.grid(row=0, column=2, padx=10, pady=10, sticky="ne")
        self.reload_unanswered_button.bind("<Enter>", self.on_enter_reload_unanswered)
        self.reload_unanswered_button.bind("<Leave>", self.on_leave_reload_unanswered)

    def create_delete_button(self):
        """
        Create the button for deleting a selected unanswered question.
        """
        self.delete_button = tk.Button(
            self.root,
            text="Delete Question",
            font=self.button_font,
            bg=self.BUTTON_COLOR,
            fg="black",
            activebackground=self.BUTTON_ACTIVE_COLOR,
            command=self.delete_unanswered_question,
            relief="flat",
            bd=0,
        )
        self.delete_button.grid(row=2, column=0, pady=20, sticky="n")
        self.delete_button.bind("<Enter>", self.on_enter_delete)
        self.delete_button.bind("<Leave>", self.on_leave_delete)

    def on_enter_delete(self, e):
        """
        Change delete button background color on hover.
        """
        self.delete_button['background'] = self.BUTTON_ACTIVE_COLOR

    def on_leave_delete(self, e):
        """
        Revert delete button background color on leave.
        """
        self.delete_button['background'] = self.BUTTON_COLOR

    def create_loading_icon(self):
        """
        Create the loading icon.
        """
        try:
            self.loading_icon_image = Image.open(self.LOADING_ICON_PATH)
            self.loading_icon_frames = [ImageTk.PhotoImage(frame.convert("RGBA").resize((75, 75))) for frame in ImageSequence.Iterator(self.loading_icon_image)]
            self.loading_icon = tk.Label(self.root, bg=self.BACKGROUND_COLOR)
            self.loading_icon.grid(row=3, column=0, columnspan=3, pady=10, sticky="n")
            self.loading_icon.grid_remove()  # Hide the loading icon initially
        except FileNotFoundError:
            self.loading_icon = None
            messagebox.showerror("Error", f"Loading icon file not found: {self.LOADING_ICON_PATH}")

    def animate_loading_icon(self, frame_index=0):
        """
        Animate the loading icon.
        """
        if self.loading_icon and self.loading_icon_frames:
            frame = self.loading_icon_frames[frame_index]
            self.loading_icon.config(image=frame)
            self.root.after(100, self.animate_loading_icon, (frame_index + 1) % len(self.loading_icon_frames))

    def show_loading_icon(self):
        """
        Show the loading icon.
        """
        if self.loading_icon:
            self.loading_icon.grid()
            self.animate_loading_icon()
            self.root.update_idletasks()  # Ensure the GUI updates

    def hide_loading_icon(self):
        """
        Hide the loading icon.
        """
        if self.loading_icon:
            self.loading_icon.grid_remove()

    def on_enter(self, e):
        """
        Change button background color on hover.
        """
        self.add_button['background'] = self.BUTTON_ACTIVE_COLOR

    def on_leave(self, e):
        """
        Revert button background color on leave.
        """
        self.add_button['background'] = self.BUTTON_COLOR

    def on_enter_reload_unanswered(self, e):
        """
        Change reload button background color on hover.
        """
        self.reload_unanswered_button['background'] = self.BUTTON_ACTIVE_COLOR

    def on_leave_reload_unanswered(self, e):
        """
        Revert reload button background color on leave.
        """
        self.reload_unanswered_button['background'] = self.BUTTON_COLOR

    def add_footer(self):
        """
        Add the footer to the dashboard.
        """
        footer_label = tk.Label(
            self.root,
            text="University of Eastern Philippines © 2025",
            font=(self.FONT_FAMILY, 12),
            fg="white",
            bg=self.BACKGROUND_COLOR,
        )
        footer_label.grid(row=4, column=0, columnspan=3, pady=10, sticky="s")

    def load_unanswered_questions(self):
        """
        Load unanswered questions from the database and clear the input fields.
        """
        try:
            self.unanswered = list(self.unanswered_collection.find({}, {"_id": 0, "question": 1}))
            self.unanswered_listbox.delete(0, tk.END)
            for question in self.unanswered:
                self.unanswered_listbox.insert(tk.END, question['question'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load unanswered questions: {e}")

        self.load_intents()  # Reload intents

        # Clear the input fields
        self.question_text.delete("1.0", tk.END)
        self.response_text.delete("1.0", tk.END)
        self.tag_entry.delete(0, tk.END)

    def load_intents(self):
        """
        Load intents from the database.
        """
        try:
            self.intents = {'intents': list(self.intents_collection.find({}, {"_id": 0}))}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load intents: {e}")

    def add_intent(self):
        """
        Add a new question and answer to the corresponding tag in the MongoDB document.
        If the tag does not exist, create a new intent.
        Automatically delete the selected unanswered question after adding it.
        """
        question = self.question_text.get("1.0", tk.END).strip()
        response = self.response_text.get("1.0", tk.END).strip()
        tag = self.tag_entry.get().strip()

        if not question or not response or not tag:
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return

        try:
            # Check if the tag already exists in the document
            existing_intent = self.intents_collection.find_one(
                {"_id": ObjectId("67a5ae062a9acecea0842f1d"), "intents.tag": tag},
                {"intents.$": 1}
            )

            if existing_intent:
                # If the tag exists, add the new question and response to the existing intent
                self.intents_collection.update_one(
                    {"_id": ObjectId("67a5ae062a9acecea0842f1d"), "intents.tag": tag},
                    {
                        "$push": {
                            "intents.$.patterns": question,
                            "intents.$.responses": response
                        }
                    }
                )
                messagebox.showinfo("Success", f"Question and response added to existing tag: {tag}")
            else:
                # If the tag does not exist, create a new intent
                new_intent = {
                    "tag": tag,
                    "patterns": [question],
                    "responses": [response]
                }
                self.intents_collection.update_one(
                    {"_id": ObjectId("67a5ae062a9acecea0842f1d")},
                    {"$push": {"intents": new_intent}},
                    upsert=True
                )
                messagebox.showinfo("Success", "New intent created successfully.")

            # Automatically delete the unanswered question from the list
            self.delete_unanswered_question()

            # Reload the model after adding the intent
            self.reload_model()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add intent: {e}")

    def delete_unanswered_question(self):
        """
        Delete the selected unanswered question from the database and update the UI.
        """
        try:
            selected_index = self.unanswered_listbox.curselection()[0]
            selected_question = self.unanswered[selected_index]['question']
            self.unanswered_collection.delete_one({"question": selected_question})
            self.load_unanswered_questions()
            messagebox.showinfo("Success", "Unanswered question deleted successfully.")
        except IndexError:
            messagebox.showwarning("Warning", "Please select a question to delete.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete unanswered question: {e}")

    def on_question_select(self, event):
        """
        Handle the selection of an unanswered question.
        """
        try:
            selected_index = self.unanswered_listbox.curselection()[0]
            selected_question = self.unanswered[selected_index]['question']
            self.question_text.delete("1.0", tk.END)
            self.question_text.insert(tk.END, selected_question)
        except IndexError:
            pass

    def on_mouse_wheel(self, event):
        """
        Handle mouse wheel scrolling.
        """
        self.unanswered_listbox.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def reload_model(self):
        """
        Reload the chatbot model.
        """
        self.show_loading_icon()
        threading.Thread(target=self._reload_model_thread).start()

    def _reload_model_thread(self):
        """
        Thread to reload the chatbot model.
        """
        try:
            response = requests.post('http://127.0.0.1:5000/reload_model')
            if response.status_code == 200:
                messagebox.showinfo("Success", "Model reloaded successfully.")
            else:
                messagebox.showerror("Error", f"Failed to reload model: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload model: {e}")
        finally:
            self.hide_loading_icon()

    def train_model(self):
        """
        Train the chatbot model.
        """
        try:
            result = subprocess.run(['python', 'train.py'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(result.stderr)
            print("Model trained successfully.")
        except Exception as e:
            print(f"Error training model: {e}")

    def listen_to_changes(self):
        """
        Listen to changes in the intents collection and train the model.
        """
        try:
            with self.intents_collection.watch() as stream:
                for change in stream:
                    print("Change detected:", change)
                    self.train_model()
                    self.reload_model()  # Reload the model after training
        except PyMongoError as e:
            print(f"Error listening to changes: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()