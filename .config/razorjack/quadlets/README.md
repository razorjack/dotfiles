# Dev service quadlets (opt-in containers)

`setup_linux` installs Postgres / Valkey / Memcached / LavinMQ **natively** via
dnf, and MongoDB best-effort via the RHEL9 repo. These Quadlet files are an
alternative: rootless podman containers you can switch to per-service, whenever
you want. They live here as a **staging area** - systemd does not read this
directory, so nothing here runs until you activate it.

Why you might switch:

- **MongoDB** has no official Fedora package; a container is the clean path.
- You want to pin an exact version (like mise pins Ruby/Node) instead of
  following whatever Fedora ships.
- On Linux, podman runs on the bare kernel (no VM), so it's fast - unlike
  Docker-on-Mac.

## Switching

`dbswitch` (in this directory; on PATH once the repo's `.local/bin` is set up,
or run it directly) stops the native service and starts the container, or vice
versa:

```sh
dbswitch mongodb container   # native off (if any) -> rootless container on
dbswitch postgres container
dbswitch postgres native     # container off -> native back on
dbswitch status              # what's running in which mode
```

It copies the chosen `*.container` into `~/.config/containers/systemd/` (the
path Quadlet actually reads), runs `systemctl --user daemon-reload`, and starts
the generated `*.service`. It also enables lingering so containers start at
boot without a login.

## Everyday use

```sh
systemctl --user status postgres      # health / logs pointer
journalctl --user -u postgres -f      # follow logs
systemctl --user restart postgres     # restart
podman ps                             # running containers
```

## Upgrading

Edit the `Image=` tag in the `*.container` file, then:

```sh
dbswitch postgres container   # re-copies the file, or:
systemctl --user daemon-reload && systemctl --user restart postgres
```

The container is disposable; your data is in the named volume, so it survives
the image bump. A **major** Postgres jump still needs `pg_upgrade` or
dump/restore because the on-disk format changes - same as native.

## Data & persistence

Each service uses a podman **named volume** (`pgdata`, `valkeydata`,
`mongodata`, `lavinmqdata`) under `~/.local/share/containers/storage/volumes/`.
The volume outlives the container.

```sh
podman volume ls
podman volume inspect pgdata
# backup a volume:
podman volume export pgdata --output pgdata.tar
```

**Native and container modes do not share data.** Switching starts from an
empty datastore for that mode unless you dump from one and restore into the
other.

## Removing

```sh
dbswitch mongodb native            # or just stop it
rm ~/.config/containers/systemd/mongodb.container
systemctl --user daemon-reload
podman volume rm mongodata         # deletes the data - be sure
```

Ports (all bound to 127.0.0.1): Postgres 5432, Valkey 6379, Memcached 11211,
LavinMQ 5672 + 15672 (management UI), MongoDB 27017.
