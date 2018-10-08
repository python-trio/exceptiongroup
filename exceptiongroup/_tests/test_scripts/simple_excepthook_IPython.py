import _common

# To tickle the "is IPython loaded?" logic, make sure that our package
# tolerates IPython loaded but not actually in use
import IPython

import simple_excepthook
