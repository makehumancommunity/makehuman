Structural Organization of MakeHuman
*************************************

MakeHuman is organized hierarchically.  
There is a root application (type :class:`gui3d.Application` ) that handles rendering of objects (:class:`guicommon.Object`). These objects can be added/removed to/from the root application.  
Objects added to root application are always visible in the canvas [#]_. Every added object has an openGL counterpart.

mhmain.MHApplication inherits from root application to construct main application. A view is a visual context. A tab is a view, for example, the main application is a view [#]_. 

The Root application [#]_ contains Categories. A Category (:class:`gui3d.Category`) is a specialised view object which contains multple taskiew objects (:class:`gui3d.TaskView`).   Taskview objects are specialised view objects with a panes and tab.  In context of MakeHuman interface, Category objects constitute the  upper row of tabs while taskview objects constitute the lower row of tabs. 

Objects (:class:`guicommon.Object`) can be added/removed to/from a taskview.  Objects added to a taskview are only visible if the taskview is visible.  For example, a skeleton added to the skeleton chooser is only visible  when the skeleton chooser taskview is visible.  Objects added to root application [#]_ are always visible.  Thus objects like human and all proxies such as clothes are added to the application, because they should always be visible. Visiblilty can be disabled by setting the visibility flag on objects but an object that is not added to a currently visible taskview, or the application, is not visible, even if its visibility flag is set positive. [#]_ 

An object can only be added to one context. So an object is either added to one taskview, or the application, not two different taskviews.

Apart from root application, there is another application (type qtui.Application) which implements MH gui structures using Qtlibraries. mhmain.MHApplication inherits from this application too for handling of gui content.e 

General structure in MH can be represented as:

.. figure::  _static/mh-inheritance.png
   :align:   center

   MakeHuman general structure
   
.. [#] I'm wondering if this is really true? - There are object on hidden tabs and the skeleton or mesh can be visible or not.  Am I confusing the distinction between 'canvass' and 'view'? - RWB
.. [#] The main application IS a view or the main application HAS a view? "the "main application frame/window is a view?"- RWB
.. [#] You do mean root and not main? - RWB
.. [#] root not main? - RWB
.. [#] [Wording needs improving -- 'should always be visible' and a 'visibility flag' are mixed message - RWB

  

