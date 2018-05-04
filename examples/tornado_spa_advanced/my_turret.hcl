variable "tornado_log_level" {
  default = "debug"
}

variable "tornado_threaded" {
  default = true
}

variable "disable_jest" {
  default = true
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
      from = "(invalidate|invalidating)"
      to   = "\033[31m\\1\033[0m"
    },
  ]
}
