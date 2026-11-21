package policy
import rego.v1

# Install on the external broker BEFORE provisioning any resources. Replace only
# with an explicitly reviewed, job-scoped policy plus real reference measurements.
default allow = false
