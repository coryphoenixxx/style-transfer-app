"use strict";

function urlToFile(url, filename){
        return (fetch(url)
            .then(function(res){return res.arrayBuffer();})
            .then(function(buf){
                return new File([buf], filename,{type: 'image/jpeg'});})
        );
    }

function download(url) {
    const thumbnailElements = document.body.querySelectorAll(".drop-zone__thumb")
    const contentFilename = thumbnailElements[0].dataset.label
    const link = document.createElement('a');
    link.href = url;
    link.download = contentFilename.split('.')[0] + '_stylized.jpg'
    document.body.appendChild(link);
    link.click();
    link.remove()
}

function getBackgroundImageUrl(element) {
    const backgroundImage = element.style.backgroundImage;
    return backgroundImage.slice(4, -1).replace(/"/g, "");
}

function calcSize(w, h) {

}

// Create selection style images box
// const styles_box = document.body.querySelector("#styles-box")
// for (let i=1; i<=20; i++) {
//     const styleElem = document.createElement('div');
//     const styleImgUrl = `images/default_style/default_style_${i}.jpg`;
//     styleElem.classList.add('style-elem');
//     styleElem.style.backgroundImage = `url(${ styleImgUrl })`;
//
//     styleElem.addEventListener("click", e => {
//         const styleZone = document.getElementById('style-drop-zone');
//         const filename = `default_style_${i}.jpg`
//         urlToFile(styleImgUrl, filename)
//             .then(function(file) {updateThumbnail(styleZone, file)})
//     })
//     styles_box.appendChild(styleElem)
// }
//
// styles_box.addEventListener("wheel", e => {
//          e.preventDefault();
//          styles_box.scrollLeft += e.deltaY;
//     })


function convertPXToVW(px) {
	return px * (100 / document.documentElement.clientWidth);
}


const styles_box = document.body.querySelector("#style-drop-zone")
for (let i=1; i<=20; i++) {
    const styleElem = document.createElement('div');
    styleElem.classList.add('style-elem');

    const styleImgUrl = `images/default_style/default_style_${i}.jpg`;
    styleElem.style.backgroundImage = `url(${ styleImgUrl })`;



    styleElem.addEventListener("mouseover", e => {
        let previewElem = document.createElement("div")
        previewElem.style.backgroundImage = `url(${ styleImgUrl })`;
        previewElem.classList.add("preview")
        let offsets = styleElem.getBoundingClientRect()

        let image = new Image();
        image.src = styleImgUrl;

        let w, h;

        image.onload = function() {
            w = image.width
            h = image.height
        }







        previewElem.style.left = convertPXToVW(offsets.left) + 10 + 'vw'
        previewElem.style.top = convertPXToVW(offsets.top) + -2 + 'vw'
        previewElem.dataset.label = styleImgUrl;
        document.body.appendChild(previewElem)

        setTimeout(function () {
            previewElem.style.visibility = 'visible'
        }, 500)
    })

    styleElem.addEventListener("mouseout", e => {
        let previewElem = document.querySelector(".preview")
        document.body.removeChild(previewElem)
    })

    // styleElem.addEventListener("click", e => {
    //     const styleZone = document.getElementById('style-drop-zone');
    //     const filename = `default_style_${i}.jpg`
    //     urlToFile(styleImgUrl, filename)
    //         .then(function(file) {updateThumbnail(styleZone, file)})
    // })
    styles_box.appendChild(styleElem)
}

// styles_box.addEventListener("wheel", e => {
//          e.preventDefault();
//          styles_box.scrollLeft += e.deltaY;
//     })




document.querySelectorAll(".drop-zone__input").forEach(inputElement => {
    const dropZoneElement = inputElement.closest(".drop-zone");
    const promptElement = dropZoneElement.querySelector(".drop-zone__prompt");

    dropZoneElement.addEventListener("click", e => {
        inputElement.click()
    })

    inputElement.addEventListener("change", e => {
        if (inputElement.files.length) {
            updateThumbnail(dropZoneElement, inputElement.files[0]);
        }
        inputElement.value = ''
    })

    dropZoneElement.addEventListener("dragover", e => {
        e.preventDefault()
        promptElement.classList.add("drop-zone__prompt--over");
        // dropZoneElement.classList.add("drop-zone--over");
    });

    ["dragleave", "dragend"].forEach(type => {
        dropZoneElement.addEventListener(type, e => {
            promptElement.classList.remove("drop-zone__prompt--over");
            // dropZoneElement.classList.remove("drop-zone--over");
        })
    })

    dropZoneElement.addEventListener("drop", e => {
        e.preventDefault();

        if (e.dataTransfer.files.length) {
            inputElement.files = e.dataTransfer.files;
            updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
        }

        promptElement.classList.remove("drop-zone__prompt--over");
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
            thumbnailElement.style.backgroundImage = `url('${reader.result}')`;
        };
    } else {
        thumbnailElement.style.backgroundImage = null;
    }
}

async function sendRequest() {
    let Thumbs = document.body.querySelectorAll('.drop-zone__thumb')
    let contentImageUrl = getBackgroundImageUrl(Thumbs[0])
    let styleImageUrl = getBackgroundImageUrl(Thumbs[1])


    let contentFile = await urlToFile(contentImageUrl, 'content.jpg')
    let styleFile = await urlToFile(styleImageUrl, 'style.jpg')


    // if (typeof content == "undefined" || typeof style == "undefined") return;

    let stylized = document.getElementById('stylized-output-zone');
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
    data.append("content", contentFile);
    data.append("style", styleFile);

    return await fetch('/', {
        method: 'POST',
        body: data
    }).then(response => {
        response.arrayBuffer().then(stylized_image => {

            let arrayBufferView = new Uint8Array(stylized_image);
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

