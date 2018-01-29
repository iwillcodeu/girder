#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright 2013 Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import cherrypy  # pragma: no cover
import click
import os  # pragma: no cover

try:  # pragma: no cover
    from girder.utility import server
except ImportError:
    # Update python path to ensure server respawning works. See #732
    source_root_dir = os.path.dirname(os.path.dirname(__file__))
    import sys
    cherrypy.engine.log("[Girder] Appending source root dir to 'sys.path': %s"
                        % source_root_dir)
    sys.path.append(source_root_dir)
    from girder.utility import server


@click.command(name='serve', short_help='Run the Girder server.')
@click.option('-t', '--testing', is_flag=True, help='run in testing mode')
@click.option('-d', '--database', help='to what database url should Girder connect')
@click.option('-H', '--host', help='on what host should Girder serve')
@click.option('-p', '--port', type=int, help='on what port should Girder serve')
def main(testing, database, host, port):
    if database:
        cherrypy.config['database']['uri'] = database
    if host:
        cherrypy.config['server.socket_host'] = host
    if port:
        cherrypy.config['server.socket_port'] = port
    server.setup(testing)

    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':  # pragma: no cover
    main()
