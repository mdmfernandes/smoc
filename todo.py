def send_skill(self, expr):
    """Sends expr to virtuoso for evaluation.

    Parameters
    ----------
    expr : string
        the skill expression.
    """
    self.virt_in.write(expr)
    self.virt_in.flush()

def recv_skill(self):
    """Receive response from virtuoso"""
    num_bytes = int(self.virt_out.readline())
    msg = self.virt_out.read(num_bytes)
    if msg[-1] == '\n':
        msg = msg[:-1]
    return msg

def close(self):
    """Close this server."""
    self.handler.close()