// function preview(element) {
//     let file = element.files[0];
//     let reader = new FileReader();
//     reader.readAsDataURL(file);
//
//     reader.onload = function () {
//         let image = new Image();
//
//         image.src = reader.result;
//
//         image.onload = function() {
//             let w = this.width;
//             let h = this.height;
//             let ratio =  w / h;
//
//             let img = element.nextElementSibling.children[0];
//
//             if (w <= h) {
//                 img.width = 350 * ratio;
//                 img.height = 350;
//             } else {
//                 img.width = 350;
//                 img.height = 350 / ratio;
//             }
//             img.src = reader.result;
//         }
//     }
// }

function download(url) {
    let thumbnailElements = document.body.querySelectorAll(".drop-zone__thumb")
    let contentFilename = thumbnailElements[0].dataset.label

    let link = document.createElement('a');
    link.href = url;
    link.download = contentFilename.split('.')[0] + '_stylized.jpg'
    document.body.appendChild(link);
    link.click();
    console.log('CLICK')
    link.remove()
}

async function sendRequest() {
    const content = document.getElementById('content').files[0];
    const style = document.getElementById('style').files[0];

    if (typeof content == "undefined" || typeof style == "undefined") return;

    let stylized = document.getElementById('stylized');
    let thumb = stylized.querySelector('.drop-zone__thumb')

    if (stylized.querySelector(".drop-zone__prompt")) {
        stylized.querySelector(".drop-zone__prompt").remove();
    }

    if (!thumb) {
        thumb = document.createElement("div")
        thumb.classList.add('drop-zone__thumb')
        stylized.appendChild(thumb)
    }

    thumb.style.backgroundImage = "url('images/loader.gif')"

    let data = new FormData();
    data.append("content", content);
    data.append("style", style);

    return await fetch('/', {
        method: 'POST',
        body: data
    }).then(response => {
        response.arrayBuffer().then(obj => {

            let arrayBufferView = new Uint8Array(obj);
            let blob = new Blob([arrayBufferView], {type: 'image/jpeg'});
            let urlCreator = window.URL || window.webkitURL;
            let imageUrl = urlCreator.createObjectURL(blob);

            thumb.style.backgroundImage = `url('${ imageUrl }')`;
            thumb.dataset.label = 'CLICK TO DOWNLOAD';


            thumb.addEventListener('click', e => {
                download(imageUrl);
            })
        })
    })
}

// function showImages() {
//     let td = document.getElementById('style_td');
//
//     console.log(td)
//
//     for (let i = 1; i <= 20; i++) {
//         let img = document.createElement('img')
//         img.style.width = '50px';
//         img.style.height = '50px';
//         img.src = `images/default_style/default_style_${i}.jpg`
//         td.appendChild(img)
//
//     }
//
// }


document.querySelectorAll(".drop-zone__input").forEach(inputElement => {
    const dropZoneElement = inputElement.closest(".drop-zone");

    dropZoneElement.addEventListener("click", e => {
        inputElement.click()
    })

    inputElement.addEventListener("change", e => {
        if (inputElement.files.length) {
            updateThumbnail(dropZoneElement, inputElement.files[0]);
        }
    })

    dropZoneElement.addEventListener("dragover", e => {
        e.preventDefault()
        dropZoneElement.classList.add("drop-zone--over");
    });

    ["dragleave", "dragend"].forEach(type => {
        dropZoneElement.addEventListener(type, e => {
            dropZoneElement.classList.remove("drop-zone--over");
        })
    })

    dropZoneElement.addEventListener("drop", e => {
        e.preventDefault();

        if (e.dataTransfer.files.length) {
            inputElement.files = e.dataTransfer.files;
            updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
        }

        dropZoneElement.classList.remove("drop-zone--over");
    });
});

function updateThumbnail(dropZoneElement, file) {
    let thumbnailElement = dropZoneElement.querySelector(".drop-zone__thumb");

    // First time - remove the prompt
    if (dropZoneElement.querySelector(".drop-zone__prompt")) {
        dropZoneElement.querySelector(".drop-zone__prompt").remove();
    }

    // First time - there is no thumbnail element, so let's create it
    if (!thumbnailElement) {
        thumbnailElement = document.createElement("div");
        thumbnailElement.classList.add("drop-zone__thumb");
        dropZoneElement.appendChild(thumbnailElement);
    }

    thumbnailElement.dataset.label = file.name;

    // Show thumbnail for image files
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();

        reader.readAsDataURL(file);

        reader.onload = () => {
            let image = new Image();

            image.src = reader.result;

            // image.onload = () => {
            //     console.log(image.width)
            // }
            thumbnailElement.style.backgroundImage = `url('${ reader.result }')`;
        };
    } else {
        thumbnailElement.style.backgroundImage = null;
    }
}

