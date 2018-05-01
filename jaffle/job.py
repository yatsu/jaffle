# -*- coding: utf-8 -*-


class Job(object):
    """
    Job is an one-shot command execution.
    """

    def __init__(self, log, name, command):
        """
        Initializes Job.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        name : str
            Job name.
        command : str
            Job command and arguments separated by whichspaces.
        """
        self.log = log
        self.name = name
        self.command = command

    def __repr__(self):
        """
        Returns string representation of Job.

        Returns
        -------
        repr : str
            String representation of Job.
        """
        return '<%s {name: %s command: %s}>' % (
            self.__class__.__name__, self.name, self.command
        )
