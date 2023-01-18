const maxWords = 10
const className = '.article'
function hide(el) {
    el = el.closest(className)
    contents = $(el).contents()
    let words = contents[0].textContent.trim().split(' ')
    let head = words.slice(0, maxWords)
    let tail = words.slice(maxWords)

    if (tail.length) {
        let headstr = head.join(' ')
        let tailstr = tail.join(' ')
        $(el).html(headstr + '<a href="javascript: void 0" onclick="show(this)">&nbsp;Показать детали&nbsp;</a><span style="display:none">' + tailstr + '</span>')
    }
};

function show(el) {
    let art = $(el).closest(className)
    let contents = art.contents()
    let head = contents[0].textContent
    let tail = contents[2].textContent
    let data = head + ' ' + tail + '<a href="javascript: void 0" onclick="hide(this)">&nbsp;Скрыть&nbsp;</a>'
    $(art).html(data)
};