# cloudify-haproxy-blueprint
A Cloudify blueprint for HAProxy

There is a types file in types/haproxy.yaml that describes the haproxy types that you can instantiate in your blueprints.

There is a blueprint.yaml file that you may build your own blueprints off of, or ignore completely.

You need to include the types.yaml file in your blueprints imports either way.


There are install, configure, start, and stop scripts in the scripts folder.

Configure creates the configuration file in /etc/haproxy/haproxy.cfg based off the topology provided.


