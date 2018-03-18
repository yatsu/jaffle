define(['base/js/namespace', 'jquery'], function init(IPython, $) {
  'use strict';

  function load_ipython_extension() {
    $(IPython.toolbar.add_buttons_group([{
      label: 'My Extension', help: 'My Extension', icon: 'fa-heart',
      callback: function() { alert('My Extension'); }
    }])).find('.btn').attr('id', 'myext-btn');
  }

  return {
    load_ipython_extension: load_ipython_extension
  };
});
