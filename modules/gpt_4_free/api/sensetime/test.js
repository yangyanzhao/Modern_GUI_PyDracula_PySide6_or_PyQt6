function t(e) {
    var t = (e = btoa(encodeURIComponent(e).replace(/%([0-9A-F]{2})/g, (function (e, t) {
            return String.fromCharCode(parseInt("0x" + t))
        }
    )))).length / 2;
    e.length % 2 !== 0 && (t = e.length / 2 + 1);
    for (var n = "", r = 0; r < t; r++)
        n += e[r] + e[t + r];
    return n
}

function get__data__(message) {
    const e = {
        "action": "next",
        "session_id": "",
        "send_msg": [{"msg_type": "user_query", "user_query": message}],
        "channel": "chat-web",
        "client_chan": "chatOnCom",
        "parent_id": "0",
        "file_ids": []
    }
    return t(JSON.stringify(e))
}

a = t("/api/richmodal/v1.0.2/session/5b4b6acd-1185-481f-9884-2545e051e589");
console.log(a)