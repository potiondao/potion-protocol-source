# potion-dapp

Application scaffolded with vue-cli. Important dependencies are:
- Vue2
- Tailwindcss
- ESLint
- Prettier

The application run the linter on pre-commit, be sure to check for errors before committing (⌐■_■)

## VSCode setup
Enable/Install:
- ESLint;
- Prettier;
- Headwind;

Headwind "is needed" to reorder Tailwind classes without doing it manually. If you don't use it it's not a problem, I'll run it time by time.

Add a workspace config to setup the format on save to work with eslint:
```json
// .vscode/settings.json
{
  "vetur.validation.template": false,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```


## Project setup
```
yarn install
yarn prepare:env
```

## Compiles and hot-reloads for development
```
yarn run serve
```

If you want to visualize Tailwindcss defaults, you can run
```
yarn run tailwind-config-viewer
```

## Compiles and minifies for production
```
yarn run build
```

## Lints and fixes files
```
yarn run lint
```
## Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
