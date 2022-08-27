SUCCESS = "<a:success:833138608532750357>"
LOADING = "<a:loading:833127464636907551>"
FAILURE = "<a:failure:1009516770161336372>"


def success_url(size: int = 24) -> str:
    return f"https://cdn.discordapp.com/emojis/833138608532750357.gif?size={size}&quality=lossless"


def loading_url(size: int = 24) -> str:
    return f"https://cdn.discordapp.com/emojis/833127464636907551.gif?size={size}&quality=lossless"


def failed_url(size: int = 24) -> str:
    return f"https://cdn.discordapp.com/emojis/1009516770161336372.gif?size={size}&quality=lossless"
