

$(".save-button").click(function() {
    var pinid = $(this).data('pinid');
    $("#save-image-hidden-input").val(pinid);
});

function showSaveResults(result) {
    $("#saveImageModal").modal("hide");
}

function saveToBoard(evt) {
    evt.preventDefault();

    var formInputs = {
        "board": $('input[name="board-to-save-image"]:checked').val(),
        'pin_id': $("#save-image-hidden-input").val()
    };

    console.log(formInputs);

    $.post("/save_image",
            formInputs,
            showSaveResults
            );
}

$("#save-image-to-board").on('submit', saveToBoard);
