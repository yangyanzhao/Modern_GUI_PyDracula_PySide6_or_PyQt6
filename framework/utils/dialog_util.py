from framework.widgets.cocos_widgets import CConfirmDialog


# 执行方法之前出确定弹框
async def are_you_sure_dialog(parent, function, keyword="执行"):
    confirm = CConfirmDialog(title="执行",
                             content="您确定要执行吗？",
                             parent=parent)
    exec_ = confirm.exec_()
    if exec_ == 1:
        await function()
    else:
        return
