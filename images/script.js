"use strict";

function urlToFile(url, filename){
        return (fetch(url)
            .then(function(res){return res.arrayBuffer();})
            .then(function(buf){
                return new File([buf], filename, { type: 'image/jpeg'}); })
        );
    }


function PXToVW(px) {
	return px * (100 / document.documentElement.clientWidth);
}


function getBackgroundImageUrl(element) {
    const backgroundImage = element.style.backgroundImage;
    return backgroundImage.slice(4, -1).replace(/"/g, "");
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


function setBackgroundImageByFile(element, file) {
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.readAsDataURL(file);

        let image = new Image();

        reader.onload = () => {
            image.src = reader.result;
            element.style.backgroundImage = `url('${reader.result}')`;
        };
    }
}


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

    setBackgroundImageByFile(thumbnailElement, file)
}


function createContentImgElement(file) {
    const contentElem = document.createElement('div');
    contentElem.classList.add('image-element', 'content-img-elem');
    setBackgroundImageByFile(contentElem, file)

    contentElem.addEventListener("click", e => {
        const contentZone = document.getElementById('content-drop-zone');
        updateThumbnail(contentZone, file)
    })

    return contentElem;
}


function getNewSizes(width, height) {
    const defaultSize = 30;
    const ratio =  width / height;
    let new_width, new_height;

    if (width < height) {
        new_width = defaultSize * ratio;
        new_height = defaultSize;
    } else {
        new_width = defaultSize;
        new_height = defaultSize / ratio;
    }

    return [new_width, new_height]
}


function displayPreview(styleElem, file) {
    let previewElem = document.createElement("div")
    previewElem.classList.add("preview")

    let offsets = styleElem.getBoundingClientRect()

    const reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = () => {
        let image = new Image();
        let new_width, new_height;
        image.src = reader.result;

        [new_width, new_height] = getNewSizes(image.width, image.height)

        previewElem.style.width = new_width + 'vw'
        previewElem.style.height = new_height + 'vw'

        previewElem.style.left = PXToVW(offsets.left) + 10 + 'vw'

        if (offsets.top < window.innerHeight / 2) {
            previewElem.style.top = PXToVW(offsets.top) - 8 + 'vw'
        } else {
            previewElem.style.top = PXToVW(offsets.top) - 16 + 'vw'
        }

        previewElem.style.backgroundImage = `url('${reader.result}')`;

        previewElem.dataset.label = file.name;
    }

    setTimeout(function () {
        previewElem.style.visibility = 'visible'
    }, 750)

    document.body.appendChild(previewElem)
}


const contentsBox = document.body.querySelector("#contents-box")
for (let i=1; i<=6; i++) {
    const contentImgUrl = `images/default_content/default_content_${i}.jpg`;
    const filename = `default_content_${i}.jpg`

    urlToFile(contentImgUrl, filename)
            .then(function(file) {
                const contentElem = createContentImgElement(file)
                contentsBox.appendChild(contentElem)
    })
}
contentsBox.addEventListener("wheel", e => {
         e.preventDefault();
         contentsBox.scrollLeft += e.deltaY;
    })



function createStyleImgElement(file) {
    const styleElem = document.createElement('div');
    styleElem.classList.add('image-element', 'style-img-elem');
    setBackgroundImageByFile(styleElem, file)

    styleElem.addEventListener("mouseover", e => {
        displayPreview(styleElem, file)
    })

    styleElem.addEventListener("mouseout", e => {
        let previewElem = document.querySelector(".preview")
        document.body.removeChild(previewElem)
    })

    styleElem.addEventListener('click', e => {
        if (styleElem.classList.contains("style-img-elem-onclick")) {
            styleElem.classList.remove("style-img-elem-onclick")
            return;
        }
        styleElem.classList.add("style-img-elem-onclick")

    })

    return styleElem;
}


const stylesBox = document.body.querySelector("#style-select-box")
for (let i=1; i<=20; i++) {
    const styleImgUrl = `images/default_style/default_style_${i}.jpg`;
    const filename = `default_style_${i}.jpg`

    urlToFile(styleImgUrl, filename)
            .then(function (file) {
                const styleElem = createStyleImgElement(file)
                stylesBox.appendChild(styleElem)
            })
}

function insertUploadImages(smallDropZoneElement, files) {
    const imageBox = smallDropZoneElement.parentElement;
    for (let file of files) {
        if (file.type.startsWith('image/')) {
            if (imageBox.id === "contents-box") {
                let newImgElement = createContentImgElement(file)
                imageBox.insertBefore(newImgElement, imageBox.childNodes[2])
            } else {
                let newImgElement = createStyleImgElement(file)
                imageBox.insertBefore(newImgElement, imageBox.childNodes[2])
            }
        }
    }
}

document.querySelectorAll(".drop-zone").forEach(dropZoneElement => {
    const inputElement = dropZoneElement.querySelector('.drop-zone__input')
    const promptElement = dropZoneElement.querySelector(".drop-zone__prompt");

    dropZoneElement.addEventListener('click', e => {
        inputElement.click();
    })

    inputElement.addEventListener('change', e => {
        if (inputElement.files.length) {
            if (dropZoneElement.id === 'content-drop-zone') {
                updateThumbnail(dropZoneElement, inputElement.files[0]);
            } else {
                insertUploadImages(dropZoneElement, inputElement.files);
            }
        }
    })

    dropZoneElement.addEventListener("dragover", e => {
        e.preventDefault()
        promptElement.classList.add("drop-zone__prompt--over")
    })

    dropZoneElement.addEventListener("dragleave", e => {
        promptElement.classList.remove("drop-zone__prompt--over");
    })

    dropZoneElement.addEventListener("dragend", e => {
        promptElement.classList.remove("drop-zone__prompt--over");
    })


    dropZoneElement.addEventListener("drop", e => {
        e.preventDefault();
        if (e.dataTransfer.files.length) {
            if (dropZoneElement.id === 'content-drop-zone') {
                updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
            } else {
                insertUploadImages(dropZoneElement, e.dataTransfer.files);
            }
        }

        promptElement.classList.remove("drop-zone__prompt--over");
    });

})


function createResultElement() {
    let thumb = document.createElement("div")
    thumb.style.backgroundImage = "url('images/loader.gif')"
    thumb.classList.add('result_thumb');
    return thumb;
}

function getImageSize(url) {
    return new Promise((resolve, reject) => {
        let img = new Image();
        img.onload = () => resolve([img.width, img.height]);
        img.onerror = () => reject();
        img.src = url;
    });
}


async function sendRequest() {
    let contentImageThumb = document.body.querySelectorAll('.drop-zone__thumb')[0]
    let contentImageUrl = getBackgroundImageUrl(contentImageThumb)

    let w, h;
    [w, h] = await getImageSize(contentImageUrl);

    let [new_w, new_h] = getNewSizes(w, h)


    let contentFile = await urlToFile(contentImageUrl, 'content.jpg')

    let selectedStyleElems = document.querySelectorAll('.style-img-elem-onclick')

    let resultsBox = document.getElementById('results-box')

    resultsBox.addEventListener("wheel", e => {
         e.preventDefault();
         resultsBox.scrollLeft += e.deltaY;
    })

    for (let i=0; i<selectedStyleElems.length; i++) {

        let styleImageUrl = getBackgroundImageUrl(selectedStyleElems[i])


        let styleFile = await urlToFile(styleImageUrl, 'style.jpg')


        // if (typeof content == "undefined" || typeof style == "undefined") return;

        let thumb = createResultElement()
        thumb.style.minWidth = new_w + 'vw'
        thumb.style.height = new_h + 'vw'

        resultsBox.appendChild(thumb)


        const data = new FormData();
        data.append("content", contentFile);
        data.append("style", styleFile);

        await fetch('/', {
            method: 'POST',
            body: data
        }).then(response => {response.arrayBuffer()
            .then(stylizedImage => {
                const arrayBufferView = new Uint8Array(stylizedImage);
                const blob = new Blob([arrayBufferView], {type: 'image/jpeg'});
                const urlCreator = window.URL || window.webkitURL;
                const imageUrl = urlCreator.createObjectURL(blob);

                thumb.style.backgroundImage = `url('${imageUrl}')`;
                thumb.dataset.label = 'CLICK TO DOWNLOAD';

                thumb.addEventListener('click', e => {
                    download(imageUrl);
                })


            })
        })
    }
}

