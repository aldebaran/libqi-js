#!/usr/bin/python2

import tornado
import tornadio2
import qi
import sys
import simplejson as json
import base64

URL = None
sid = 1

def is_member_of(o, mtype, name):
    members = o.metaObject()[mtype]
    for i in members:
        if members[i]["name"] == name:
            return True
    return False

class QiMessagingHandler2(tornadio2.conn.SocketConnection):

    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, bytearray):
                return list(obj)
            return json.JSONEncoder.default(self, obj)

    def on_open(self, info):
        global sid
        self.objs = dict()
        self.sid = sid
        self.subs = dict()
        sid = sid + 1
        self.qim = qi.Session()
        self.qim.connect(URL)
        print("[%d] New connection from %s" % (self.sid, info.ip))
        self.qim.disconnected.connect(lambda x: self.close())

    def reply(self, idm, mtype, data):
        try:
            if qi.isinstance(data, qi.Object):
                o = len(self.objs)
                self.objs[o] = data
                data = { "pyobject": o, "metaobject": data.metaObject() }
            evt = dict(name = mtype, args = {})
            if data is not None:
                evt["args"]["result"] = data
            if mtype != "signal":
                evt["args"]["idm"] = idm
            message = u'5:::%s' % (json.dumps(evt, cls=self.SetEncoder, allow_nan=False))
            tornado.ioloop.IOLoop.instance().add_callback(self.session.send_message, message)
        except (AttributeError, ValueError) as exc:
            self.reply(idm, "error", str(exc))

    def do_callback(self, service, signal, idm):
        def cbk(*args):
            self.reply(None, "signal",
                       { "obj": service, "signal": signal, "data": args, "link": self.subs[idm] })
        return cbk

    def do_reply(self, idm, keepLink):
        def rep(fut):
            if fut.hasError():
                self.reply(idm, "error", fut.error())
            else:
                if keepLink:
                    self.subs[idm] = fut.value()
                self.reply(idm, "reply", fut.value())
        return rep

    @tornadio2.event
    def call(self, idm, params):
        try:
            service = params["obj"]
            member = params["member"]
            args = params["args"]
            if service == "ServiceDirectory" and member == "service":
                fut = self.qim.service(str(*args), _async = True)
            else:
                obj = self.objs[service]
                attr = getattr(obj, member)
                if args != [] and args[0] == "connect" and is_member_of(obj, "signals", member):
                    self.subs[idm] = -1
                    fut = attr.connect(self.do_callback(service, member, idm), _async = True)
                elif args != [] and args[0] == "disconnect" and is_member_of(obj, "signals", member):
                    fut = attr.disconnect(args[1], _async = True)
                elif args != [] and args[0] == "value" and is_member_of(obj, "properties", member):
                    fut = attr.value(_async = True)
                elif args != [] and args[0] == "setValue" and is_member_of(obj, "properties",  member):
                    fut = attr.setValue(args[1], _async = True)
                else:
                    fut = attr(*args, _async = True)
            fut.addCallback(self.do_reply(idm, args != [] and args[0] == "connect"))
        except (AttributeError, RuntimeError, Exception) as exc:
            self.reply(idm, 'error', str(exc))

    def on_close(self):
        self.objs = dict()
        self.subs = dict()
        self.qim = None
        print("[%d] Disconnected" % (self.sid))


class QiMessagingHandler1_0(QiMessagingHandler2):

    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, bytearray):
                return base64.b64encode(obj)
            return json.JSONEncoder.default(self, obj)

    @tornadio2.event
    def call(self, idm, params):
        try:
            service = params["obj"]
            method = params["method"]
            args = params["args"]
            if service == "ServiceDirectory" and method == "service":
                fut = self.qim.service(str(args[0]), _async = True)
            elif method == "registerEvent":
                obj = self.objs[service]
                self.subs[idm] = -1
                evt = getattr(obj, args[0])
                fut = evt.connect(self.do_callback(service, args[0], idm), _async = True)
            elif method == "unregisterEvent":
                obj = self.objs[service]
                evt = getattr(obj, args[0])
                fut = evt.disconnect(args[1], _async = True)
            else:
                obj = self.objs[service]
                met = getattr(obj, method)
                fut = met(*args, _async = True)
            fut.addCallback(self.do_reply(idm, method == "registerEvent"))
        except (AttributeError, RuntimeError) as exc:
            self.reply(idm, 'error', str(exc))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        URL = "tcp://127.0.0.1:9559"
    else:
        URL = sys.argv[1]

    print("Will connect to " + URL)

    QI_APP = qi.Application()

    SOCK_APP = tornado.web.Application(
      tornadio2.TornadioRouter(QiMessagingHandler1_0, namespace='1.0').urls +
      tornadio2.TornadioRouter(QiMessagingHandler2, namespace='2').urls,
      socket_io_port = 8002
    )

    tornadio2.server.SocketServer(SOCK_APP)
