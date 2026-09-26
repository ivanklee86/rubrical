{
  name: "rubrical",
  postCreateCommand+: {
    "rubrical-post-install": "bash ./.devcontainer/post_install.sh",
  },
}
