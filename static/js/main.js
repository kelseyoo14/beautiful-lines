
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

// ***************************************************************************

// Start and run study session

// in a loop
// go through list of shuffled images and add <img src> tag to html page in a modal
// then with timeout switch images after specified seconds

function startStudy(evt) {
    evt.preventDefault();
    console.log('Start');

    var time_intervals = $('#time-intervals').val();
    var num_of_images = $('#num-of-images').val();
    var formInputs = {
        'board_id': $('#board_id').val()
    };

    function shuffle_images(images) {
        console.log('shuffled_images');
        var i = 0;
        var j = 0;
        var temp = null;

        for (i = images.length - 1; i > 0; i -= 1) {
            j = Math.floor(Math.random() * (i + 1));
            temp = images[i];
            images[i] = images[j];
            images[j] = temp;
        }
        
        return images;
    }

    // function closeModal() {
    //     $('#study-modal').modal('hide');
    // }

    // function display_image(images, index) {
    //     console.log("display_image");
    //     $('#study-modal').modal('hide');

    //     $('#study-modal-image').attr('src', images[index]);
    //     $('#study-modal').modal('show');
    //     index++;

    //     console.log(index);
    //     // if (index > num_of_images) {
    //     //     cleartInterval(displayTimer);
    //     // }
    // }

    function get_images() {
        console.log('get_images');
        $.post('/study_images',
            formInputs,
            parse_results);

        function parse_results(result) {
            console.log('parse_results');
            images = JSON.parse(result);

            shuffled_images = shuffle_images(images);
            console.log('images have been shuffled');

            // index = 1;

            // var displayTimer = setInterval(
            //     function() {
            //         display_image(shuffled_images, index);
            //         }, 3000);


            var image_index = 0;
            function displayImages(images, image_index) {
                $('#study-modal-image').attr('src', images[image_index]);
                $('#study-modal').modal('show');
                // image_index++;
                if (image_index < num_of_images) {
                    setTimeout(function() {
                        console.log(image_index);
                        displayImages(images, image_index + 1);
                    }, 3000);
                }
                else{
                    $('#study-modal').modal('hide');
                }
            }


            displayImages(shuffled_images, image_index);
        }
    }
    get_images();
}

var index=1;

$('#study-form').on('submit', startStudy);










