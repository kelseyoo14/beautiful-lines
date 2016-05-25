
// Save image to db ------------------------------------------------------------

// Pass pinid and imageid to #saveImageModal form hidden inputs,
// to pass to '/save_image' route when form is submitted
$(".save-button").click(function() {
    var pinid = $(this).data('pinid');
    var imageid = $(this).data('imageid');

    $("#hidden-pinid").val(pinid);
    $("#hidden-imageid").val(imageid);
});

function closeModal(result) {
    $("#saveImageModal").modal("hide");
}

function saveToBoard(evt) {
    evt.preventDefault();

    var formInputs = {
        "board": $('input[name="board-to-save-image"]:checked').val(),
        'pin_id': $('#hidden-pinid').val(),
        'image_id': $('#hidden-imageid').val()
    };

    console.log(formInputs);

    $.post('/save_image',
            formInputs,
            closeModal
            );
}

$("#save-image-to-board").on('submit', saveToBoard);


// Delete image from db ------------------------------------------------------------

function reloadPage(result) {
    location.reload(true);
}


function deleteFromBoard(evt) {
    evt.preventDefault();

    var formInputs = {
        'board_id': $(this).find('.board_id').val(),
        'image_id': $(this).find('.image_id').val()
    };

    console.log(formInputs);
    console.log("TEST");

    $.post('/delete_image',
            formInputs,
            reloadPage
            );
}

$(".delete-image-from-board").on('submit', deleteFromBoard);


// Start and run study session ------------------------------------------------------

function startStudy(evt) {
    evt.preventDefault();

    var time_intervals = $('#time-intervals').val();
    var num_of_images = $('#num-of-images').val();
    var formInputs = {
        'board_id': $('#board_id').val()
    };

    // shuffle list of image urls
    function shuffle_images(images) {
        // var i = 0;
        var j = 0;
        var temp;

        for (var i = images.length - 1; i > 0; i--) {
            j = Math.floor(Math.random() * (i + 1));
            temp = images[i];
            images[i] = images[j];
            images[j] = temp;
        }
        
        return images;
    }

    // get images from database through /study_images route
    function get_images() {
        $.post('/study_images',
            formInputs,
            parse_results);

        function parse_results(result) {
            var original_images = JSON.parse(result);
            var images = original_images.slice();

            shuffled_images = shuffle_images(images);

            // if user wants to study more images than exist in board, 
            // reshuffle images and add to shuffled_images list
            while (num_of_images > shuffled_images.length) {
                var more_shuffled_images = shuffle_images(original_images);
                shuffled_images.push.apply(shuffled_images, more_shuffled_images);
            }

            $('.stop-study').on('click', function() {
                clearTimeout(study_timeout);
                $('#study-modal').modal('hide');
            });

            var count_images = 0;
            var study_timeout;
            $('#study-modal').modal('show');
            function displayImages(shuffled_images, count_images) {
                $('#study-modal-image').attr('src', shuffled_images[count_images]);

                if (count_images < num_of_images) {
                    study_timeout = setTimeout(function() {
                        // recursively call displayImages to loop through images in shuffled list
                        displayImages(images, count_images+1);
                    }, 2000);
                } else {
                    $('#study-modal').modal('hide');
                }
            }
            // Start displaying images
            displayImages(shuffled_images, count_images);
        }
    }
    get_images();
}

// When user clicks on 'Start Drawing' button, start displaying 'studying' (displaying images)
$('#study-form').on('submit', startStudy);

$('#study-modal .modal-body').height($('#study-modal-image').height());

// Start Zoom Image and Image Canvas ------------------------------------------------------

$('body').on('click', 'img', function() {
    var pinsrc = $(this).attr('src');
    $('#zoomed-image').attr('src', pinsrc);
    $('#zoom-modal').modal('show');
});

$('#zoom-modal .modal-body').height($('#zoomed-image').height());


