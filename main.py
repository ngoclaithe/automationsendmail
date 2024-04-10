from smtp_build import send_email_diy
from smtp_attachment import send_email_diy
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, filedialog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import re
import os
import imaplib
import email
from email.header import decode_header
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import json

def load_config(filename='configemail.json'):
    try:
        with open(filename, 'r') as json_file:
            config_data = json.load(json_file)
            email_info = config_data.get('email', {})
            user_email = email_info.get('username', '')
            user_password = email_info.get('password', '')
            return user_email, user_password
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {filename}: {e}")
        return None, None


RECIPIENTS_FILE = "recent_recipients.txt"
def load_recent_recipients():
    try:
        with open(RECIPIENTS_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

def add_item(recipient):
    if recipient not in recent_recipients:
        recent_recipients.append(recipient)
        with open(RECIPIENTS_FILE, "w") as file:
            file.write("\n".join(recent_recipients))
        # entry_new_item.delete(0, tk.END)
        # update_listbox_height()

def clear_text_input():
    text_input.delete('1.0', tk.END)
    e1.delete(0, tk.END)
    subj.delete(0, tk.END)
    attachment_label.config(text="No file selected")
    file_combobox["values"] = []
    file_combobox.set("")

def is_file_size_valid(file_path, max_size_mb=3):
    file_size = os.path.getsize(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024  
    return file_size <= max_size_bytes

def browse_file():
    file_paths = filedialog.askopenfilenames(filetypes=[("All Files", "*.*")])
    
    if len(file_paths) == 0 and attachment_label["text"] == "No file selected":
        attachment_label.config(text="No file selected")
        file_combobox["values"] = []
    else:
        attachment_path = attachment_label["text"]
        invalid_files = []

        for file_path in file_paths:
            if not is_file_size_valid(file_path):
                invalid_files.append(file_path)

        if invalid_files:
            warning_message = f"The following files exceed 3MB and cannot be selected:\n{', '.join(invalid_files)}"
            messagebox.showwarning("File Size Exceeded", warning_message)
        else:
            if attachment_path != 'No file selected':
                file_paths = [file_path for file_path in file_paths if file_path not in attachment_path.split(", ")]
                file_paths = (attachment_path.split(", ")) + file_paths
            file_combobox["values"] = [file_name.split('/')[-1] for file_name in file_paths]
            attachment_label.config(text=", ".join(file_paths))
            file_combobox.current(len(file_paths)-1)

def remove_file():
    selected_item = file_combobox.get()
    if len(selected_item) != 0:
        attachment_path = attachment_label["text"]
        attachment_path = attachment_path.split(", ")
        attachment_path = [path for path in attachment_path if path.split('/')[-1] != selected_item]
        attachment_label.config(text=", ".join(attachment_path))
        file_combobox["values"] = [file_name.split('/')[-1] for file_name in attachment_path]
        if len(attachment_path) == 0:
            file_combobox.set("")
            attachment_label.config(text="No file selected")
        else:
            file_combobox.current(0)
    else:
        messagebox.showerror("Error", "No file selected")

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
#Load file config json và file save data txt
recent_recipients = load_recent_recipients()
user_email, user_password = load_config()
print(user_email)
print(user_password)
def send_email():
    recipient = e1.get()
    
    if not is_valid_email(recipient):
        print("Error: Please enter a valid email address!")
        return
    subject = subj.get()
    content = text_input.get("1.0", tk.END).strip()

    cc_recipients = cc_str.get().split(';') if cc_str.get() else []

    attachment_path = attachment_label.cget("text") 
    try:

        send_email_diy(user_email,user_password,recipient,content,subject,cc_recipients,None,attachment_path)

        print("Email sent successfully!")

        add_item(recipient)
        clear_text_input()

    except Exception as e:
        print(f"Error sending email: {str(e)}")


def on_frame_configure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))
trang_thai_email = {}
class EmailViewer:
    def __init__(self, master, email_data):
        self.master = master
        self.email_data = email_data

        self.frame = tk.Frame(self.master)
        self.frame.pack()

        self.label_tieu_de = tk.Label(self.frame, text="Tiêu đề: " + email_data['subject'])
        self.label_tieu_de.pack()

        self.label_tu = tk.Label(self.frame, text="Từ: " + email_data['from'])
        self.label_tu.pack()

        ngay_gui = email_data['date']
        ngay_dinh_dang = datetime(*ngay_gui[:6]).strftime("%H:%M %d %b, %Y")
        self.label_ngay = tk.Label(self.frame, text="Ngày: " + ngay_dinh_dang)
        self.label_ngay.pack()

        self.text_noi_dung = tk.Text(self.frame, wrap=tk.WORD, width=60, height=10)
        self.text_noi_dung.insert(tk.END, email_data['content'])
        self.text_noi_dung.pack()

        self.button_file = tk.Button(self.frame, text="Download File Đính Kèm", command=self.download_file_dinh_kem)
        self.button_file.pack()

    def download_file_dinh_kem(self):
        file_path = filedialog.asksaveasfilename(initialfile=self.email_data['file_name'], defaultextension=".txt")
        if file_path:
            download_file_dinh_kem(self.email_data['file_data'], file_path)

def tai_thu_dien_tu():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        mail.login(user_email, user_password)
        mail.select("inbox")
        trang_thai, tin_nhans = mail.search(None, "ALL")

        if trang_thai == "OK":
            root = tk.Tk()
            root.title("Danh Sách Email")
            root.geometry("800x600")
            root.protocol("WM_DELETE_WINDOW", lambda: luu_trang_thai_email(root))
            
            canvas = tk.Canvas(root)
            frame = tk.Frame(canvas)
            scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            canvas.create_window((0, 0), window=frame, anchor="nw", tags="frame")

            frame.bind("<Configure>", lambda event, canvas=canvas: on_frame_configure(canvas))
            

                       

            for num in tin_nhans[0].split():
                trang_thai, du_lieu_tin_nhan = mail.fetch(num, "(RFC822)")

                if trang_thai == "OK":
                    tin_nhan_email = email.message_from_bytes(du_lieu_tin_nhan[0][1])
                    chu_de, encoding = decode_header(tin_nhan_email["Subject"])[0]
                    if isinstance(chu_de, bytes):
                        chu_de = chu_de.decode(encoding or "utf-8")

                    ngay_gui = email.utils.parsedate(tin_nhan_email["Date"])
                    ngay_dinh_dang = datetime(*ngay_gui[:6]).strftime("%H:%M %d %b, %Y")

                    email_data = {
                        'subject': chu_de,
                        'from': tin_nhan_email["From"],
                        'date': ngay_gui,
                        'content': tin_nhan_email.get_payload(),
                        'file_data': None,
                        'file_name': None,
                        'da_doc': False 
                    }

                    if tin_nhan_email.is_multipart():
                        for part in tin_nhan_email.walk():
                            if part.get_content_type() == "text/plain":
                                noi_dung = part.get_payload(decode=True).decode("utf-8")
                                email_data['content'] = noi_dung
                            elif part.get_content_type().startswith("application"):
                                ten_file = part.get_filename()
                                if ten_file:
                                    label_file = tk.Label(frame, text="File đính kèm: " + ten_file)
                                    label_file.pack()
                                    file_data = part.get_payload(decode=True)
                                    email_data['file_data'] = file_data
                                    email_data['file_name'] = ten_file

                    email_frame = tk.Frame(frame, bd=2, relief="groove")
                    email_frame.pack(side="top", fill="x", padx=5, pady=5)

                    label_tieu_de = tk.Label(email_frame, text="Tiêu đề: " + chu_de)
                    label_tieu_de.pack()

                    label_tu = tk.Label(email_frame, text="Từ: " + tin_nhan_email["From"])
                    label_tu.pack()

                    label_ngay = tk.Label(email_frame, text="Ngày: " + ngay_dinh_dang)
                    label_ngay.pack()

                    label_trang_thai = tk.Label(email_frame, text="Trạng thái: Chưa đọc", fg="red")
                    label_trang_thai.pack()
                    button_xem_chi_tiet = tk.Button(email_frame, text="Xem Chi Tiết",
                                                    command=lambda email_data=email_data, label_trang_thai=label_trang_thai: xem_chi_tiet_email(email_data, label_trang_thai))
                    button_xem_chi_tiet.pack()
            filter_entry = tk.Entry(root)
            filter_entry.pack(side="top", pady=5)

            filter_button = tk.Button(root, text="Lọc", command=lambda: loc_email(mail, frame, filter_entry.get()))
            filter_button.pack(side="top", pady=5)

            root.mainloop()

        mail.logout()

    except Exception as e:
        print(f"Lỗi khi tải email: {str(e)}")
def loc_email(mail, frame, filter_text):
    try:
        trang_thai, tin_nhans = mail.search(None, "ALL")

        if trang_thai == "OK":
            filtered_emails = []
            for num in tin_nhans[0].split():
                trang_thai, du_lieu_tin_nhan = mail.fetch(num, "(RFC822)")

                if trang_thai == "OK":
                    tin_nhan_email = email.message_from_bytes(du_lieu_tin_nhan[0][1])
                    chu_de, encoding = decode_header(tin_nhan_email["Subject"])[0]
                    if isinstance(chu_de, bytes):
                        chu_de = chu_de.decode(encoding or "utf-8")

                    ngay_gui = email.utils.parsedate(tin_nhan_email["Date"])
                    ngay_dinh_dang = datetime(*ngay_gui[:6]).strftime("%H:%M %d %b, %Y")

                    email_data = {
                        'subject': chu_de,
                        'from': tin_nhan_email["From"],
                        'date': ngay_dinh_dang,
                        'content': tin_nhan_email.get_payload(),
                        'file_data': None,
                        'file_name': None,
                        'da_doc': False 
                    }

                    if tin_nhan_email.is_multipart():
                        for part in tin_nhan_email.walk():
                            if part.get_content_type() == "text/plain":
                                noi_dung = part.get_payload(decode=True).decode("utf-8")
                                email_data['content'] = noi_dung
                            elif part.get_content_type().startswith("application"):
                                ten_file = part.get_filename()
                                if ten_file:
                                    label_file = tk.Label(frame, text="File đính kèm: " + ten_file)
                                    label_file.pack()
                                    file_data = part.get_payload(decode=True)
                                    email_data['file_data'] = file_data
                                    email_data['file_name'] = ten_file

                    if isinstance(filter_text, str) and (
                        filter_text.lower() in email_data['subject'].lower() or
                        filter_text.lower() in email_data['from'].lower() or
                        filter_text.lower() in email_data['content'].lower()
                    ):
                        filtered_emails.append(email_data)

            hien_thi_ket_qua_loc(filtered_emails)

    except Exception as e:
        print(f"Lỗi khi tải email: {str(e)}")


def hien_thi_ket_qua_loc(filtered_emails):
    new_window = tk.Toplevel()
    new_window.title("Kết Quả Lọc")
    new_window.geometry("400x600")

    canvas = tk.Canvas(new_window)
    frame = tk.Frame(canvas)
    scrollbar = tk.Scrollbar(new_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw", tags="frame")

    frame.bind("<Configure>", lambda event, canvas=canvas: on_frame_configure(canvas))

    for email_data in filtered_emails:
        email_frame = tk.Frame(frame, bd=2, relief="groove")
        email_frame.pack(side="top", fill="x", padx=5, pady=5)

        label_tieu_de = tk.Label(email_frame, text="Tiêu đề: " + email_data['subject'])
        label_tieu_de.pack()

        label_tu = tk.Label(email_frame, text="Từ: " + email_data['from'])
        label_tu.pack()

        label_ngay = tk.Label(email_frame, text="Ngày: " + email_data['date'])
        label_ngay.pack()

        # label_trang_thai = tk.Label(email_frame, text="Trạng thái: Chưa đọc", fg="red")
        # label_trang_thai.pack()
        # button_xem_chi_tiet = tk.Button(email_frame, text="Xem Chi Tiết",
        #                                 command=lambda email_data=email_data, label_trang_thai=label_trang_thai: xem_chi_tiet_email(email_data, label_trang_thai))
        # button_xem_chi_tiet.pack()

def xem_chi_tiet_email(email_data, label_trang_thai):
    new_window = tk.Toplevel()
    email_viewer = EmailViewer(new_window, email_data)
    if not email_data['da_doc']:
        email_data['da_doc'] = True
        label_trang_thai.config(text="Trạng thái: Đã đọc", fg="green")
        trang_thai_email[email_data['subject']] = True

def luu_trang_thai_email(root):
    with open("trang_thai_email.txt", "w") as file:
        for subject, da_doc in trang_thai_email.items():
            file.write(f"{subject}:{da_doc}\n")
    
    root.destroy() 

def download_file_dinh_kem(file_data, file_path):
    try:
        with open(file_path, 'wb') as f:
            f.write(file_data)
        print(f"File {file_path} downloaded successfully!")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")

window = tk.Tk()
window.title("Email Client")

x_pos = 500
y_pos = 100
window.geometry(f"+{x_pos}+{y_pos}")
font1 = ("Times new roman", 12)
font2 = ("Times new roman", 12)

recipient_label = tk.Label(window, text="TO:")
recipient_label.grid(row=0, column=0, sticky='w', padx=(25, 0))
e1_str = tk.StringVar()
e1 = tk.Entry(window, textvariable=e1_str, font=font1)
e1.grid(row=0, column=1, sticky="nsew", padx=(0, 20))

def my_down(event):
    l1.focus()
    l1.selection_set(0)

def my_up(event):
    selected_indices = l1.curselection()
    if selected_indices:
        index = int(selected_indices[0])
        if index > 0:
            l1.selection_clear(0, tk.END)
            l1.selection_set(index - 1)
            l1.activate(index - 1)
            l1.see(index - 1)
        else:
            e1.focus()

def my_upd(event):
    if event.widget == l1:
        selected_indices = l1.curselection()
        # update_listbox_height()

        index = int(selected_indices[0])
        value = l1.get(index)
        e1_str.set(value)
        l1.config(height=0)
        l1.delete(0, tk.END)
        e1.focus()
        e1.icursor(tk.END)
    else:
        search_term = e1.get()
        l1.delete(0, tk.END)
        cnt = 0
        for item in recent_recipients:
            if re.match(search_term, item, re.IGNORECASE):
                l1.insert(tk.END, item)
                cnt += 1
        l1.config(height=min(4, cnt))
    hide_listbox()

def get_data(*args):
    search_term = e1.get()
    l1.delete(0, tk.END)
    hide_listbox()
    if(len(search_term) != 0):
        visible_listbox()
        cnt = 0
        for item in recent_recipients:
            if re.match(search_term, item, re.IGNORECASE):
                l1.insert(tk.END, item)
                cnt += 1
        if(cnt == 0):
            hide_listbox()
        else:
            l1.config(height=min(4, cnt))

def hide_listbox():
    scrollbar.grid_remove()
    l1.grid_remove()

def visible_listbox():
    l1.grid()
    scrollbar.grid()

def l1_binding():
    e1.focus()

l1_height = 0  
l1 = tk.Listbox(window, height=l1_height, font=font2, relief='groove', bg='SystemButtonFace', highlightcolor='SystemButtonFace')
l1.grid(row=2, column=1, sticky="nsew", padx=(0, 20))
scrollbar = tk.Scrollbar(window, command=l1.yview)
scrollbar.grid(row=2, column=2, sticky="ns")
l1.configure(yscrollcommand=scrollbar.set)

e1.bind('<Down>', my_down)
l1.bind('<Return>', my_upd)
l1.bind('<Up>', my_up)
l1.bind('<ButtonRelease-1>', my_upd)
e1_str.trace('w', get_data)

cc_label = tk.Label(window, text="CC (separated by ;):", anchor='w')
cc_label.grid(row=1, column=0, sticky='w', padx=(25, 0))
cc_str = tk.StringVar()
cc_entry = tk.Entry(window, textvariable=cc_str, font=font1)
cc_entry.grid(row=1, column=1, sticky="nsew", padx=(0, 20))
subject = tk.Label(window, text="Subject:", anchor='w')
subject.grid(row=3, column=0, sticky='w', padx=(25, 0))
subj_str = tk.StringVar()
subj = tk.Entry(window, textvariable=subj_str, font=font1)
subj.grid(row=3, column=1, sticky="nsew", padx=(0, 20), pady=(10, 0))

text_label = tk.Label(window, text="Email Content:")
text_label.grid(row=4, column=0, pady=(10, 0), sticky='w', padx=(25, 0))
text_input = tk.Text(window, height=20)
text_input.grid(row=5, column=0, columnspan=2)

nut_tai_thu = tk.Button(window, text="Receiver Email", command=tai_thu_dien_tu, bd='5', anchor='e')
nut_tai_thu.grid(row=7, column=1, pady=(10, 0), columnspan=2, sticky='e', padx=10)


attachment_label = tk.Label(window, text="No file selected", anchor="w")

style = ttk.Style()
style.configure("Custom.TButton", padding=(0, 0, 0, 0), font=('Times new roman', 14), anchor='center')
style.map("Custom.TButton",
          foreground=[('pressed', 'black'), ('active', 'black'), ('!disabled', 'black')],
          background=[('pressed', '!disabled', 'white'), ('active', 'white')])

file_combobox = ttk.Combobox(window, state="readonly", font=font2, width=20)
file_combobox.grid(row=6, column=0, sticky='w', padx=(25, 0), pady=(10, 0))
browse_button = ttk.Button(window, text="📎", command=browse_file, style='Custom.TButton', width=3)
browse_button.grid(row=6, column=1, pady=(10, 0), sticky='w', padx=(0, 0))
browse_button.configure(compound='center')
dlt_button = ttk.Button(window, text="❌", command=remove_file, style='Custom.TButton', width=3)
dlt_button.grid(row=6, column=1, pady=(10, 0), sticky='w', padx=(50, 0))
dlt_button.configure(compound='center')

send_button = tk.Button(window, text="Send Email", command=send_email, bd='5', anchor='e')
send_button.grid(row=6, column=1, pady=(10, 0), columnspan=2, sticky='e', padx=10)

hide_listbox()

window.mainloop()
