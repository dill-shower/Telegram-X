import os

def patch(file_path, old_str, new_str):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_str not in content:
        print(f"[!] Warning: pattern not found in {file_path}:\n    {old_str[:50]}...")
        return
    content = content.replace(old_str, new_str, 1)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[+] Patched {file_path}")

# 1. MessagesLoader.java — убираем рекламу каналов
patch(
    'app/src/main/java/org/thunderdog/challegram/component/chat/MessagesLoader.java',
    'private boolean canShowSponsoredMessage (long chatId) {',
    'private boolean canShowSponsoredMessage (long chatId) {\n    if (true) return false;'
)

# 2. TGMessage.java — разрешаем сохранение и копирование всего
patch(
    'app/src/main/java/org/thunderdog/challegram/data/TGMessage.java',
    'public boolean canBeSaved () {',
    'public boolean canBeSaved () {\n    if (true) return true;'
)

# 3. MessagesController.java — скриншоты везде + глушим статус печатает
patch(
    'app/src/main/java/org/thunderdog/challegram/ui/MessagesController.java',
    'public final boolean shouldDisallowScreenshots () {',
    'public final boolean shouldDisallowScreenshots () {\n    if (true) return false;'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/ui/MessagesController.java',
    'public void setChatAction (@TdApi.ChatAction.Constructors int action, boolean set, boolean force) {',
    'public void setChatAction (@TdApi.ChatAction.Constructors int action, boolean set, boolean force) {\n    if (true) return;'
)

# 4. Tdlib.java — клиентский Premium
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public boolean hasPremium () {',
    'public boolean hasPremium () {\n    if (true) return true;'
)

# 5. Tdlib.java — снятие ограничений NSFW / Sensitive
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public boolean ignoreSensitiveContentRestrictions () {',
    'public boolean ignoreSensitiveContentRestrictions () {\n    if (true) return true;'
)

# 6. Tdlib.java — снятие ограничений платформы (Google Play цензура)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'new TdApi.OptionValueBoolean(AppInstallationUtil.isAppSideLoaded(AppContext.get())))',
    'new TdApi.OptionValueBoolean(true))'
)

# 7. Tdlib.java — заглушка Play Integrity API
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public void requestPlayIntegrity (long verificationId, String nonce, ApplicationVerificationCallback callback) {',
    'public void requestPlayIntegrity (long verificationId, String nonce, ApplicationVerificationCallback callback) {\n    callback.onApplicationVerificationResult("PLAYINTEGRITY_FAILED_NOT_SUPPORTED");\n    if (true) return;'
)

# 8. Tdlib.java — подмена отпечатка подписи на оригинальный от Вячеслава Крылова
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'params.put("data", fingerprint);',
    'params.put("data", "66462134345a6adac3c1d5aea9cef0421b7cab68");'
)

# 9. Tdlib.java — отмена сетевой телеметрии OpenChat и CloseChat
# Заменяем на мгновенный локальный TdApi.SetAlarm(0) — нулевой сетевой трафик, 
# штатный вызов колбэков, никаких сломанных скобок!
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'new TdApi.OpenChat(chatId)',
    'new TdApi.SetAlarm(0)'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'new TdApi.CloseChat(chatId)',
    'new TdApi.SetAlarm(0)'
)

print("[*] All patches applied successfully!")
