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

app "watchdog" {
  logger {
    level = "${var.watchdog_log_level}"
  }
}

app "tornado_app" {
  logger {
    level = "${var.tornado_log_level}"
  }

  options {
    threaded = "${var.tornado_threaded}"
  }
}

process "jest" {
  disabled = "${var.disable_jest}"
}

logger {
  replace_regex = [
    {
      from = "^  clear: (.*)"
      to   = "  clear: ${fg('blue')}\\1${reset()}"
    },
  ]
}
