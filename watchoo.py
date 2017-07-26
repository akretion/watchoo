#!/usr/bin/python

import pyinotify
import erppeek
import yaml
import base64

config = yaml.safe_load(open('watchoo.yml').read())

odoo = erppeek.Client(
    config['odoo']['url'],
    config['odoo']['db'],
    config['odoo']['user'],
    config['odoo']['password'])

def generate_report(ev):
    for report, params in config['reports'].items():
        view_id = params['watch'].get(ev.name)
        if view_id:
            print 'try to push data'
            try:
                odoo.model('ir.ui.view').write([view_id], {
                    u'arch': open(ev.name).read()})
            except Exception, e:
                print 'fail to push'
                return
            try:
                print 'render report'
                result = odoo.render_report(
                    params['generate']['report_name'],
                    [params['generate']['object_id']])
                out_name = u'%s.%s' % (report, result['format'])
                out = open(out_name, 'w')
                out.write(base64.b64decode(result['result']))
                out.close()
            except Exception, e:
                print 'fail to render', e

wm = pyinotify.WatchManager()
wm.add_watch('.', pyinotify.IN_MODIFY, generate_report)
notifier = pyinotify.Notifier(wm)
notifier.loop()
