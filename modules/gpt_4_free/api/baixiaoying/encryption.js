//引入本地加密库
function i() {
    return exports
}
function o(t, e) {
    let r = i().enc.Utf8.parse("0000000000000000");
    return i().AES.encrypt(t, i().enc.Utf8.parse(e), {
        iv: r,
        mode: i().mode.CBC,
        padding: i().pad.Pkcs7
    }).toString()
}

function runs_sign() {
    //构建入参
    const n = Date.now()
    const r = undefined
    const a = `${n.toString()}retry=3&thread_info=[object Object]`
    // const a = `${n.toString()}id=6042075`

    // 执行关键o函数
    let s = o(a, r ? r.substring(0, 16) : "uwlACMuXQApWgO0Q");
    // 截取逻辑
    return s.length > 64 && (s = s.substring(0, 64)),
        {
            "x-bc-sig": s,
            "x-bc-ts": n.toString()
        }
}

function delete_sign(id) {
    //构建入参
    const n = Date.now()
    const r = undefined
    const a = `${n.toString()}id=${id}`

    // 执行关键o函数
    let s = o(a, r ? r.substring(0, 16) : "uwlACMuXQApWgO0Q");
    // 截取逻辑
    return s.length > 64 && (s = s.substring(0, 64)),
        {
            "x-bc-sig": s,
            "x-bc-ts": n.toString()
        }
}
