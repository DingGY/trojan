import tempfile
import threading
import win32file
import win32con
import os
dirs_to_monitor = ["C:\\WINDOWS\\Temp",tempfile.gettempdir()]
# file modification constants
FILE_CREATED = 1
FILE_DELETED = 2
FILE_MODIFIED = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO = 5

def start_monitor(path_to_watch):
    FILE_LIST_DIRECTORY = 0x0001
    h_directory = win32file.CreateFile(\
        path_to_watch,\
        FILE_LIST_DIRECTORY,\
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,\
        None,\
        win32con.OPEN_EXISTING,\
        win32con.FILE_FLAG_BACKUP_SEMANTICS,\
        None)
    while True:
        try:
            results = win32file.ReadDirectoryChangesW(\
                h_directory,\
                1024,\
                True,\
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |\
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |\
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |\
                win32con.FILE_NOTIFY_CHANGE_SIZE |\
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |\
                win32con.FILE_NOTIFY_CHANGE_SECURITY,\
                None,\
                None)
            #print results
            for action,file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)
                if action == FILE_CREATED:
                    print "[ + ] Created %s" % full_filename
                elif action == FILE_DELETED:
                    print "[ - ] Deleted %s" % full_filename
                elif action == FILE_MODIFIED:
                    print "[ * ] Modified %s" % full_filename
                    # dump out the file contents
                    print "[vvv] Dumping contents..."
                    try:
                        fd = open(full_filename,"rb")
                        contents = fd.read()
                        fd.close()
                        print contents
                        print "[^^^] Dump complete."
                    except:
                        print "[!!!] Failed"

                elif action == FILE_RENAMED_FROM:
                    print "[ > ] Renamed from: %s" % full_filename
                elif action == FILE_RENAMED_TO:
                    print "[ < ] Renamed to: %s" % full_filename
                else:
                    print "[???] Unknown: %s" % full_filename
        except Exception as e:
            print e
            pass
def main():
    monitor_thread_list = []
    for path in dirs_to_monitor:
        monitor_thread = threading.Thread(target=start_monitor,args=(path,))
        print "[ * ] Spawning monitoring thread for path: %s" % path
        monitor_thread.start()
        monitor_thread_list.append(monitor_thread)
    for t in monitor_thread_list:
        t.join()
__name__ = "__main__"
if __name__ == "__main__":
    main()