$(function() {
  console.log('hello world :o');


  $('form').submit(function(event) {
    event.preventDefault();
    var license = $('input').val();
    $.post('/lookup?' + $.param({'license': license}), function(data) {
      console.log('Data: ' + data);
      $('#license').html(data);
      $('input').val('');
      $('input').focus();
    });
  });

});
