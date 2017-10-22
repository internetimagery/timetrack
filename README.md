# Time tracking in Maya

Track time spent in Maya.

In UserSetup.py:

    import timetrack
    timetrack.ctrl.Monitor().start()

In a shelf icon.

    import timetrack
    timetrack.main()

Tracks time spent using Maya. Notes can be created and logged against the time via GUI or:

    timetrack.ctrl.Monitor().set_note("Note")
