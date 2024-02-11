Rubrical uses a YAML/JSON/TOml file is used to configure checks for your application.  By default, it will use the `rubrical.yaml` in your local directory.  You can specify your own file with the `--config` flag.

```yaml
version: 1
package_managers:
  - name: jsonnet
    packages:
      - name: "xunleii/vector_jsonnet" # Name of the dependency
        block: v0.1.0  # If dependency is less than this, error.
        warn: v0.1.2  # If dependency is less than this, warn.
  - name: python
    packages:
      - name: Mopidy-Dirble
        block: v1.2.1
        warn: v1.2.2
  - name: go
    packages:
      - name: github.com/adrg/xdg
        block: v0.5.0
        warn: v0.6.0
  - name: nodejs
    packages:
      - name: react
        block: v17.0.3
        warn: v17.0.4
```
