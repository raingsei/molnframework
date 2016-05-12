from io import StringIO
from subprocess import Popen, PIPE

def _execute(command):
	process = Popen(command, stdout=PIPE,stderr=PIPE,shell=True)
	output, error = process.communicate()
	retcode = process.poll()

	return (retcode,output,error)

class CommandExecuteException(object):
    pass

class KubectlCommand(object):
    EXE_PATH = '/bin/kubectl'

    def execute(argument_str):
        retcode,output,error = _execute("%s %s" % (KubectlCommand.EXE_PATH,argument_str))

        if retcode !=0:
            raise CommandExecuteException(("Return code:%s, Output:%s, Error:%s" % retcode,output,error))
