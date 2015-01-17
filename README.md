# cloudify-haproxy-blueprint
A Cloudify blueprint for HAProxy

There is a types file in types/haproxy.yaml that describes the haproxy types that you can instantiate in your blueprints.

There is an example blueprint file that installs the nodecellar example application on openstack: openstack-nodecellar-example-blueprint.yaml. There is an example inputs.json in the inputs folder.

There are install, configure, start, and stop scripts in the scripts folder. It also includes the nodecellar example's scripts.

Finally, there is a haproxy configuration template. This uses the Jinja2 templating markup. The script in scripts/haproxy/configure.py builds a config file off of this template. So you should make sure that any edits you make to the template will work with that script.
