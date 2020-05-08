 #!/bin/bash
set -e

# Duplicating the function from https://github.com/elastic/elasticsearch/blob/7.6/distribution/docker/src/docker/bin/docker-entrypoint.sh

run_as_other_user_if_needed() {
  if [[ "$(id -u)" == "0" ]]; then
    # If running as root, drop to specified UID and run command
    exec chroot --userspec=1000 / "${@}"
  else
    # Either we are running in Openshift with random uid and are a member of the root group
    # or with a custom --user
    exec "${@}"
  fi
}

# Run elastic search 
run_as_other_user_if_needed /usr/share/elasticsearch/bin/elasticsearch &

# Run the Proxy and reporting
cd /opt && python3 /opt/prox.py