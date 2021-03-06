import threading
import abc

# This is the base class for all processes we need performed in
# a thread separate from the UI thread.  Work-intensive operations
# should be done in a separate thread, so that the UI thread doesn't
# become "unresponsive"

class WorkThread():

    # This method needs to be overridden .. it defines the custom work to be done by
    # the work thread.
    @abc.abstractmethod
    def codeToRunInThread(self):
        pass

    def __init__(self, solver, puzzleBoard):
        # The solver object to be used by the work thread
        self.solver = solver

        # The puzzle board object to be worked on by the worker thread
        self.pb = puzzleBoard

        self.__threadHandle = threading.Thread(target=self.codeToRunInThread, args=(), daemon=True)

        # We use a collection of thread events to provide communications and
        # synchronization between the work thread and the main UI thread.

        # This event allows the work thread (which can't show any UI), to request that the
        # UI thread show the current results of the work being done by the work thread; usuall,
        # the work thread will pause what it is doing, until the UI thread signals that it should
        # resume working.
        self.showResultsEvent = threading.Event()
        self.showResultsEvent.clear()

        # Event used by the UI thread to signal that it is done displaying the current results
        # generated by the work thread, so the work thread should resume doing what it was doing.
        self.resumeEvent = threading.Event()
        self.resumeEvent.clear()

        # This event allows the UI to tell the work thread that the user has cancelled the current
        # work request, so the work thread should clean up and exit.
        self.cancelEvent = threading.Event()
        self.cancelEvent.clear()

    # This method signals to the work thread that it should stop what it was doing and exit
    def cancelWorkThread(self):
        self.cancelEvent.set()

    # Spawns the work thread
    def start(self):
        self.__threadHandle.start()

    # Returns a boolean, indicating whether the associated work thread is still alive
    def isAlive(self):
        return((self.__threadHandle.is_alive()))

    # Some work threads support the ability for the user to cancel them, while others
    # may not .. this method indicates whether the work thread supports this feature
    # or not.  The default is "no" .. so this method must be overridden, if the work
    # thread supports cancellation.
    def supportsCancelRequest(self):
        return(False)

    # In order for the UI thread to communicate with (and monitor) the work thread,
    # it uses a timer to periodically wake up and check the status of the thread.
    # It will also give the work thread object the opportunity to see if there
    # are any special UI requests which have been requested by the work thread.
    # This method should be overridden, if the work thread has any custom communications
    # it needs to monitor, or UI it wants displayed.
    #
    # The return value is a boolean, where 'True' indicates that some modal UI had
    # been displayed (and is now gone), so the UI thread needs to "lift" the main
    # UI windows (since .. for some reason .. after removing the modal UI, the
    # application windows seem to jump to the back of the window stacking order!).
    def timerHandler(self, parentWindow):
        return(False)
