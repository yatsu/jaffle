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

app "tornado_app" {
  options {
    args = ["--ip=${exec('hostname') | trim}", "--port=9999"]
  }
}

logger {
  replace_regex = [
    {
      from = "^  clear: (.*)"
      to   = "  clear: ${fg('blue')}\\1${reset()}"
    },
    {
      from = "^APIExampleHandler.get: (.*)"
      to   = "example: ${fg('yellow')}${jqf('.Host', '\\1')}${reset()}"
    },
  ]
}
