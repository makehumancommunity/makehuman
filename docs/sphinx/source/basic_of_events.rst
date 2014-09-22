Basics of event handling in Makehuman
*************************************

Makehuman is a GUI based, interactive, Qt application in which objects interact by sending messages to each other. The Qt class QEvent encapsulates notion of low level events like mouse events, key press events, action events, etc. A Qt application is event loop-based, which is basically a program structure which allows events to be prioritized, queued and dispatched to application objects.   

In a Qt based application, there are different sources of events. Some events like key events and mouse events come from window system, while some others originate from within application. When an event occurs, Qt creates an event object to represent it by constructing an instance of the appropriate QEvent subclass, and delivers it to a particular instance of QObject (or one of its subclasses) by calling its event() function. This function does not handle the event itself, but rather, it calls an event handler based on the type of event delivered, and sends an acknowlegement based on whether the event was accepted or ignored.

QCoreApplication::exec() method enters the main event loop and waits until exit() is called. It is necessary to call this function to start event handling. In MH, it is done in lib.qtui.Application which inherits from QApplication which in turn inherits from QCoreApplication::

    def start(self):
            self.OnInit()
            self.callAsync(self.started)
            self.messages.start()
            self.exec_()

In MH, event handling falls in two broad categories.

- Event handling for containers (application, categories, taskviews)
- Event handling for widgets (contained in containers)

Event handling for containers
===============================

MH is organized hierarchically in the context of containers.  At top is the main application (:class:`core.mhmain.MHMainApplication`).  It contains categories (core.gui.Category), which in turn contains taskviews (core.gui.TaskView).

In a Qt-based application, there are five different ways of events processing, as listed below:

1. Reimplementing an event handler function like paintEvent(), mousePressEvent() and so on. This is the most common, easiest, but least powerful approach.
2. Reimplementing QCoreApplication::notify ( QObject * receiver, QEvent * event ).  This is very powerful, providing complete control; but only one subclass can be active at a time.  
   Qt's event loop and sendEvent() calls use this approach to dispatch events.
3.  Installing an event filter on QCoreApplication::instance().  Such an event filter is able to process all events for all widgets.  It's just as powerful as reimplementing notify();
   furthermore, it's possible to have more than one application-global event filter. Global event filters even see mouse events for disabled widgets. 
   Note that application event filters are only called for objects that live in the main thread. [I believe that MH is single threaded - implications?  RWB]
4. Reimplementing QObject::event() (as QWidget does). 
   If you do this you get Tab key presses [<--Explain what is special about TAB and shift-TAB presses ?- RWB], and you get to see the events before any widget-specific event filters.
5. Installing an event filter on the object itself.  Such an event filter gets all the events, including Tab and Shift+Tab key press events [<--Explain what is special about TAB and shift-TAB presses ?- RWB], as long as they do not change the focus widget.

In MakeHuman, approaches 2 and 4  are used for extensively for event handling.  As part of strategy 2,in lib.qtui.Application (which extends QApplication), notify has been reimplemented: [I don''t understand the implication of this? Expond? -RWB]::

    def notify(self, object, event):
            self.logger_event.debug('notify(%s, %s(%s))', object, event, event.type())
            return super(Application, self).notify(object, event)
        
object is the receiver object. Class implementing notify has to be singleton.  [Clarify? - RWB]

In MakeHuman, MHApplication subclasses lib.qtui.Application.MHApplication object is the main application object. It's notify function receives notification from the event loop in the underlying Qt layer about each [container only or widgets too?] event, which is then relayed to receiver object's event method. The receiver object's event method is either inherited from QObject or reimplemented. The Receiver object then either sends TRUE or FALSE, as the case may be, to [WHERE??] - RWB

lib.qtui.Application also implements an event function, which is called if the receiver object is MHApplication object itself.  Then, lib.qtui.Application.event() checks if its a user-defined event or not,and it is so true is returned, else we call super class's event().   In case of true being returned,Qt dispatches event to receiver object's callEvent function which determines which function to be called on object to handle the event. Called function then handles the event or propagate it to its parent(or to current task if its application object), as may seem fit.

Event handling for widgets
=============================

Most of MH widgets are wrappers around Qt widgets. These widgets (defined in module lib.qtgui) inherit from the respective Qt widgets and the Widget class (lib.qtgui.Widget).  MH makes use of signal and slot mechanism by making the connection between the signal originating from the Qt layer and the corresponding handler function. For example, class TabBase connects the signal 'currentChanged' to its function 'tabChanged' as follows::

    class TabsBase(Widget):
        def __init__(self):
            super(TabsBase, self).__init__()
            self.tabBar().setExpanding(False)
            self.connect(self, QtCore.SIGNAL('currentChanged(int)'), self.tabChanged)

        
Any class inheriting from TabsBase(e.g., lib.qtgui.Tabs or lib.qtgui.TabBar) also gets this facility.  So now whenever signal 'currentChanged' is emitted from Qt layer function 'tabChanged' is called. The result is that when a user clicks the mouse on a tab, the 'tabChanged' code  will be called,

Similarly, MH Slider widget connects various slider operations to its event handling functions as::

    self.connect(self.slider, QtCore.SIGNAL('sliderMoved(int)'), self._changing)
    self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), self._changed)
    self.connect(self.slider, QtCore.SIGNAL('sliderReleased()'), self._released)
    self.connect(self.slider, QtCore.SIGNAL('sliderPressed()'), self._pressed)


  

