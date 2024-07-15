# REF https://github.com/neknaj/jsonviewer
def json_viewer(data: str):
    return """
<html>
    <head>
        <meta charset="UTF-8">
        <script>
        window.data = {};
        function showJSON(obj,elm,defaultopen=false,hidekey=[]) {
            elm.classList.add("jsonviewer");
            elm.innerHTML = "";
            elm.appendChild(json_child(obj,defaultopen,hidekey));
        }
        function json_child(obj,defaultopen=false,hidekey=[]) {
            if (obj instanceof Array) {
                let details = document.createElement("details");
                details.classList.add("array");
                details.open = defaultopen;
                let summary = document.createElement("summary");
                {
                    let type = document.createElement("span");
                    let length = document.createElement("span");
                    let content = document.createElement("span");
                    type.innerText = "Array";
                    length.innerHTML = `(${obj.length})`;
                    content.innerText = JSON.stringify(obj);
                    content.classList.add("summary_content")
                    summary.appendChild(type);
                    summary.appendChild(length);
                    summary.appendChild(content);
                }
                details.appendChild(summary);
                for (let i in obj) {
                    let elm = obj[i];
                    let index = document.createElement("span");
                    let colon = document.createElement("span");
                    let comma = document.createElement("span");
                    let br = document.createElement("br");
                    comma.classList.add("comma");
                    index.classList.add("array_index");
                    index.innerText = i;
                    colon.innerText = ":";
                    comma.innerText = ",";
                    details.appendChild(index);
                    details.appendChild(colon);
                    details.appendChild(json_child(elm,defaultopen,hidekey));
                    details.appendChild(comma);
                    details.appendChild(br);
                }
                return details;
            }
            else if (obj instanceof Object) {
                let details = document.createElement("details");
                let summary = document.createElement("summary");
                {
                    let type = document.createElement("span");
                    type.innerText = "Object";
                    let content = document.createElement("span");
                    content.classList.add("summary_content")
                    content.innerText = JSON.stringify(obj);
                    summary.appendChild(type);
                    summary.appendChild(content);
                }
                details.open = defaultopen;
                details.classList.add("object");
                details.appendChild(summary);
                for (let elm in obj) {
                    if (hidekey.includes(elm)) {continue}
                    let p = document.createElement("p");
                    let addelm = json_child(elm,defaultopen,hidekey);
                    let colon = document.createElement("span");
                    let comma = document.createElement("span");
                    addelm.classList.add("object_key");
                    comma.classList.add("comma");
                    colon.innerText = ":";
                    comma.innerText = ",";
                    p.appendChild(addelm);
                    p.appendChild(colon);
                    p.appendChild(json_child(obj[elm],defaultopen,hidekey));
                    p.appendChild(comma);
                    details.appendChild(p);
                }
                return details;
            }
            else {
                if (typeof obj === "string") {
                    let span = document.createElement("span");
                    let span1 = document.createElement("span");
                    let span2 = document.createElement("span");
                    let span3 = document.createElement("span");
                    span.classList.add("string");
                    span1.innerText = "\\"";
                    span3.innerText = "\\"";
                    span2.innerText = obj.toString();
                    span.appendChild(span1);
                    span.appendChild(span2);
                    span.appendChild(span3);
                    return span;
                }
                else if (typeof obj === "number") {
                    let span = document.createElement("span");
                    span.classList.add("number");
                    span.innerText = obj.toString();
                    return span;
                }
                else if (typeof obj === "boolean") {
                    let span = document.createElement("span");
                    span.classList.add("boolean");
                    span.innerText = obj.toString();
                    return span;
                }
                else {
                    let span = document.createElement("span");
                    if (obj!=null) {
                        span.innerText = obj.toString();
                    }
                    return span;
                }
            }
        }
        </script>
        <style>
        .jsonviewer {
            padding: 10px;
            font-size: 80%;
            overflow: scroll;
            display: inline;
            position: relative;
            width: 100%;
        }
        .jsonviewer summary {
            color: rgb(139, 174, 255);
            width: fit-content;
        }
        .jsonviewer details {
            border: 1px solid rgba(255, 255, 255, 0);
            padding: 2px;
            padding-left: 10px;
            display: inline-block;
            position: relative;
        }
        .jsonviewer details[open] {
            box-shadow: inset 1px 0px 0px 0px rgba(255, 255, 255, 0.511);
        }
        .jsonviewer details:hover {
            border: 1px solid rgba(255, 255, 255, 0.308);
            background-color: rgba(48, 171, 212, 0.08);
        }
        .jsonviewer>details:hover {
            border: 1px solid rgba(255, 255, 255, 0);
        }
        .jsonviewer details>summary {
            font-size: 90%;
        }
        .jsonviewer details[open]>summary {
            color: rgb(85, 97, 123);
            font-size: 80%;
        }
        .jsonviewer details span {
            vertical-align: top;
            padding-left: 0.05em;
            padding-right: 0.05em;
            display: inline-block;
        }
        .jsonviewer details>p>span:nth-child(1) {
            min-width: 3em;
        }
        .jsonviewer details.object>summary>span:nth-child(2) {
            font-size: 70%;
        }
        .jsonviewer details.array>summary>span:nth-child(3) {
            font-size: 70%;
            vertical-align: bottom;
        }
        .jsonviewer details.object>summary>.summary_content,
        .jsonviewer details.array>summary>.summary_content {
            max-width: 200px;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
            vertical-align: bottom;
        }
        .jsonviewer span.string span {
            color: rgb(221, 136, 0);
            display: none;
        }
        .jsonviewer span.string:hover span {
            display: inherit;
        }
        .jsonviewer span.string span:nth-child(2) {
            color: rgb(255, 200, 0);
            display: inherit;
        }
        .jsonviewer span.number {
            color: rgb(183, 255, 0);
        }
        .jsonviewer span.boolean {
            color: rgb(255, 87, 230);
        }
        .jsonviewer details span.array_index {
            color: rgb(100, 234, 255);
        }
        .jsonviewer details span.string.object_key span {
            color: rgb(0, 144, 221);
        }
        .jsonviewer details span.string.object_key span:nth-child(2) {
            color: rgb(100, 255, 237);
        }
        .jsonviewer details>p>span:nth-child(2) {
            padding-right: 10px;
        }
        .jsonviewer p {
            margin: 1px;
            width: fit-content;
        }
        .jsonviewer details span.comma {
            vertical-align: bottom;
        }
        </style>
        <meta property="og:title" content="JSON Viewer">
        <meta property="og:description" content="JSON Viewer">
        <meta property="description" content="JSON Viewer">
    </head>
    <body>
        <div id="output"></div>
    </body>
    <script>
    function update() {
        showJSON(window.data,document.getElementById("output"), false);
    }
    window.onload = update;
    </script>
    <style>
        body {
            background-color: black;
            color: white;
            height: 100dvh;
            width: 100dvw;
            padding: 0;
            margin: 0;
            font-size: 1.2rem;
            display: flex;
        }
        body>div {
            width: 100%;
            border: 1px solid gray;
        }
    </style>
</html>
""".replace("{}", data)