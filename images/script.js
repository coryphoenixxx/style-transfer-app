function preview(element) {
    let file = element.files[0];
    let reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = function () {
        let image = new Image();

        image.src = reader.result;

        image.onload = function() {
            let w = this.width;
            let h = this.height;
            let ratio =  w / h;

            let img = element.nextElementSibling.children[0];

            if (w <= h) {
                img.width = 400 * ratio;
                img.height = 400;
            } else {
                img.width = 400;
                img.height = 400 / ratio;
            }
            img.src = reader.result;
        }

    }
}

async function sendRequest() {

    const content = document.getElementById('content').files[0]
    const style = document.getElementById('style').files[0]


    let sel_content = document.getElementById('sel_content')
    let sel_style = document.getElementById('sel_style')

    if (typeof content == "undefined") {

        sel_content.style.color = 'red'
    } else {
        sel_content.style.color = 'black'
    }

    if (typeof style == "undefined") {

        sel_style.style.color = 'red'
    } else {
        sel_style.style.color = 'black'
    }

    if (typeof content == "undefined" || typeof style == "undefined") return;

    let stylized = document.getElementById('stylized')
    stylized.src = 'images/loader.gif'


    let data = new FormData()
    data.append("content", content)
    data.append("style", style)

    return await fetch('/', {
        method: 'POST',
        body: data
    }).then(response => {
        response.json().then(obj => {
            stylized.src = obj.stylized_url
        })
    })
}

function showImages() {
    let td = document.getElementById('style_td');

    console.log(td)

    for (let i = 1; i <= 20; i++) {
        let img = document.createElement('img')
        img.style.width = '50px';
        img.style.height = '50px';
        img.src = `images/default_style/default_style_${i}.jpg`
        td.appendChild(img)

    }

}

