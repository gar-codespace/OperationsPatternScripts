
import apps

class openSystemConsole(jmri.jmrit.automat.AbstractAutomaton) :
  def init(self):

    console = apps.SystemConsole.getConsole()
    console.setVisible(True)
    return

  def handle(self):
    return False

openSystemConsole().start()
