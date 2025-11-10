# GenX CLI

This is the command-line interface for the GenX Trading Platform.

## Usage

To see a list of available commands, run:

```bash
npx genx-cli --help
```

## Plugins

The GenX CLI is a plugin-based system. The following plugins are available:

- **jules_plugin**: A plugin for Jules to perform core development tasks.
- **codacy_plugin**: A plugin to integrate with Codacy for code quality scanning.
- **license_checker**: A Python-based license checker plugin.
- **amp_adapter**: An adapter for the AMP AI Coder.

### Running a Plugin

To run a specific plugin, use the `--run-plugin` flag:

```bash
npx genx-cli --run-plugin <plugin-name>
```

For example, to run the license checker, you would use the following command:

```bash
npx genx-cli --run-plugin license_checker
```

## Configuration

The CLI can be configured via the `config.json` file. This file contains a list of the plugins that are available to the CLI.
