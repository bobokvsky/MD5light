import uuid
import threading
import time
import queue
import requests
import hashlib
import os
from email.message import EmailMessage

NUM_OF_DOWNLOAD_WORKERS = 5  # for downloading the files
CHUNK_SIZE = 1024  # for response.iter_content()

class TaskDao:
    """DataBase of tasks"""

    def __init__(self):
        self.tasks = dict()
        self.lock = threading.Lock()

    def __getitem__(self, key):
        self.lock.acquire()
        res = self.tasks[key]
        self.lock.release()
        return res
    
    def __setitem__(self, key, value):
        self.lock.acquire()
        self.tasks[key] = value
        self.lock.release()

    def keys(self):
        self.lock.acquire()
        res = self.tasks.keys()
        self.lock.release()
        return res


class SolverTasks:
    """Class used to solve tasks"""

    def __init__(self):
        self.tasks = TaskDao()
        self.queue = queue.Queue()

        self.SMTP = None
        self.sender = None
        self.lock = threading.Lock()

    def set_SMTP_and_sender(self, SMTP, sender):
        self.lock.acquire()
        self.SMTP = SMTP
        self.sender = sender
        self.lock.release()

    def get_SMTP_and_sender(self):
        self.lock.acquire()
        res = (self.SMTP, self.sender)
        self.lock.release()
        return res

    def add_task(self, url, email) -> str:
        task = dict()

        task["url"] = url
        task["md5"] = None
        task["status"] = "running"

        task_id = str(uuid.uuid4())
        self.tasks[task_id] = task
        
        self.queue.put(task_id)
        if threading.activeCount() < NUM_OF_DOWNLOAD_WORKERS:
            worker = threading.Thread(target=self.get_md5, args=(task_id, url, email, ))
            worker.start()
        
        return "{'id': '" + task_id + "'}"

    def get_task(self, task_id) -> str:
        if task_id in self.tasks.keys():
            return str(self.tasks[task_id])
        else:
            return "This task not exists."

    def get_all_ids(self) -> str:
        return str([*self.tasks.keys()])

    def get_md5(self, task_id, url, email):
        while not self.queue.empty():
            task_id = self.queue.get()
            
            is_success = False
            is_responsed = False
            
            md5 = hashlib.md5()
            try:
                response = requests.get(url, stream=True)
                is_responsed = True
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            md5.update(chunk)
                    is_success = True
            except:
                pass

            if is_success:
                self.tasks[task_id]["status_code"] = response.status_code
                self.tasks[task_id]["status"] = "done"
                self.tasks[task_id]["md5"] = md5.hexdigest()
            else:
                self.tasks[task_id]["status"] = "failed"
                if is_responsed:
                    self.tasks[task_id]["status_code"] = response.status_code
                else:
                    self.tasks[task_id]["status_code"] = "invalid url"
            
            SMTP, sender = self.get_SMTP_and_sender()
            if SMTP != None and sender != None:
                msg = EmailMessage()
                msg['Subject'] = "Result of task {'%s'}" % task_id
                msg['From'] = sender
                msg['To'] = email
                msg.set_content(str(self.tasks[task_id]))
                
                self.lock.acquire()
                SMTP.send_message(msg)
                self.lock.release()

            self.queue.task_done()