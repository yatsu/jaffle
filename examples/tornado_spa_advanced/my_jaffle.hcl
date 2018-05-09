variable "watchdog_log_level" {
  default = "debug"
}

variable "tornado_log_level" {
  default = "debug"
}

variable "tornado_threaded" {
  default = true
}

variable "disable_jest" {
  default = true
}

logger {
  replace_regex = [
    {
      from = "^  clear: (.*)"
      to   = "  clear: ${fg('blue')}\\1${reset()}"
    },
  ]
}
