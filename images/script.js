function preview(element) {
    let file = element.files[0];
    let reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = function () {
        let img = element.nextElementSibling.children[0];
        img.src = reader.result;
    }
}

async function sendRequest() {

    const content = document.getElementById('content').files[0]
    const style = document.getElementById('style').files[0]

    let data = new FormData()
    data.append("content", content)
    data.append("style", style)


    return await fetch('/', {
        method: 'POST',
        body: data
    }).then(response => {
        response.json().then(obj => {
            let stylized = document.getElementById('stylized')
            stylized.src = obj.stylized_url
        })
    })
}

