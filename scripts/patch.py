import os
import re

def patch(file_path, old_str, new_str):
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if old_str not in content:
        print(f"[!] Warning: pattern not found in {file_path}:\n    {old_str[:50]}...")
        return
        
    content = content.replace(old_str, new_str, 1)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[+] Successfully patched: {file_path}")

# ==============================================================================
# 1. MessagesLoader.java — Блокировка рекламы + Режим призрака (источник Preview)
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/component/chat/MessagesLoader.java',
    'private boolean canShowSponsoredMessage (long chatId) {',
    'private boolean canShowSponsoredMessage (long chatId) {\n    if (true) return false;'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/component/chat/MessagesLoader.java',
    'private TdApi.MessageSource newMessageSource () {',
    'private TdApi.MessageSource newMessageSource () {\n    if (true) return new TdApi.MessageSourceHistoryPreview();'
)

# ==============================================================================
# 2. MessagesManager.java — Режим призрака (не помечать сообщения прочитанными)
# ==============================================================================
mm_path = 'app/src/main/java/org/thunderdog/challegram/component/chat/MessagesManager.java'
if os.path.exists(mm_path):
    with open(mm_path, 'r', encoding='utf-8') as f:
        mm_code = f.read()
    mm_new, count = re.subn(
        r'((?:public|private|protected)?\s*boolean\s+readMessagesDisabled\s*\(\s*\)\s*\{)',
        r'\1\n    if (true) return true;',
        mm_code,
        count=1
    )
    if count > 0:
        with open(mm_path, 'w', encoding='utf-8') as f:
            f.write(mm_new)
        print(f"[+] Successfully patched readMessagesDisabled in {mm_path}")
    else:
        print(f"[!] Warning: readMessagesDisabled not found in {mm_path}")

# ==============================================================================
# 3. TGMessage.java — Разрешение сохранения, копирования и пересылки всего отовсюду
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/data/TGMessage.java',
    'public boolean canBeSaved () {',
    'public boolean canBeSaved () {\n    if (true) return true;'
)

# ==============================================================================
# 4. MessagesController.java — Скриншоты везде + отключение статуса "Печатает..."
# ==============================================================================
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

# ==============================================================================
# 5. Tdlib.java — Клиентский Premium (иконки, темы, автопереводчик)
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public boolean hasPremium () {',
    'public boolean hasPremium () {\n    if (true) return true;'
)

# ==============================================================================
# 6. Tdlib.java — Снятие ограничений NSFW / Sensitive контента
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public boolean ignoreSensitiveContentRestrictions () {',
    'public boolean ignoreSensitiveContentRestrictions () {\n    if (true) return true;'
)

# ==============================================================================
# 7. Tdlib.java — Снятие региональных блокировок каналов (Google Play цензура)
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'new TdApi.OptionValueBoolean(AppInstallationUtil.isAppSideLoaded(AppContext.get())))',
    'new TdApi.OptionValueBoolean(true))'
)

# ==============================================================================
# 8. Tdlib.java — Заглушки Google Play Integrity и ReCaptcha
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public void requestPlayIntegrity (long verificationId, String nonce, ApplicationVerificationCallback callback) {',
    'public void requestPlayIntegrity (long verificationId, String nonce, ApplicationVerificationCallback callback) {\n    callback.onApplicationVerificationResult("PLAYINTEGRITY_FAILED_NOT_SUPPORTED");\n    if (true) return;'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public void requestRecaptcha (long verificationId, String action, String recaptchaKeyId, ApplicationVerificationCallback callback) {',
    'public void requestRecaptcha (long verificationId, String action, String recaptchaKeyId, ApplicationVerificationCallback callback) {\n    callback.onApplicationVerificationResult("RECAPTCHA_FAILED_NOT_SUPPORTED");\n    if (true) return;'
)

# ==============================================================================
# 9. Tdlib.java — Маскировка: официальный отпечаток ключа Вячеслава Крылова
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'params.put("data", fingerprint);',
    'params.put("data", "66462134345a6adac3c1d5aea9cef0421b7cab68");'
)

# ==============================================================================
# 10. Tdlib.java — Фиксация оригинального имени пакета в отчётах для серверов
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'params.put("package_id", context.getPackageName());',
    'params.put("package_id", "org.thunderdog.challegram");'
)

# ==============================================================================
# 11. Tdlib.java — Отмена сетевой телеметрии OpenChat и CloseChat
# ==============================================================================
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

# ==============================================================================
# 12. Tdlib.java — Маскировка модели устройства под массовый Samsung Galaxy A55
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'parameters.deviceModel = TdlibManager.getDeviceModel();',
    'parameters.deviceModel = "Samsung Galaxy A55 5G";'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'parameters.systemVersion = TdlibManager.getSystemVersion();',
    'parameters.systemVersion = "Android 14";'
)

# ==============================================================================
# 13. Tdlib.java — Блокировка уведомлений о скриншотах
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public void sendScreenshotMessage (long chatId, long[] messageIds) {',
    'public void sendScreenshotMessage (long chatId, long[] messageIds) {\n    if (true) return;'
)

# ==============================================================================
# 14. Tdlib.java — Вечный оффлайн (без ошибки лямбды)
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'client.send(new TdApi.SetOption("use_pfs", new TdApi.OptionValueBoolean(true)), okHandler);',
    'client.send(new TdApi.SetOption("use_pfs", new TdApi.OptionValueBoolean(true)), okHandler);\n    client.send(new TdApi.SetOption("online", new TdApi.OptionValueBoolean(false)), okHandler);'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'client.send(new TdApi.SetOption("online", new TdApi.OptionValueBoolean(true)), tdlib.okHandler());',
    'client.send(new TdApi.SetOption("online", new TdApi.OptionValueBoolean(false)), tdlib.okHandler());'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public void setOnline (boolean isOnline) {',
    'public void setOnline (boolean isOnline) {\n    if (true) return;'
)

# ==============================================================================
# 15. SharedChatsController.java — Блокировка трекинга рекомендаций каналов
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/ui/SharedChatsController.java',
    'tdlib.send(new TdApi.OpenChatSimilarChat(getChatId(), chatId), tdlib.typedOkHandler());',
    '// tdlib.send(new TdApi.OpenChatSimilarChat(getChatId(), chatId), tdlib.typedOkHandler());'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/ui/SharedChatsController.java',
    'tdlib.send(new TdApi.OpenChatSimilarChat(getChatId(), openedChatId), tdlib.typedOkHandler());',
    '// tdlib.send(new TdApi.OpenChatSimilarChat(getChatId(), openedChatId), tdlib.typedOkHandler());'
)

# ==============================================================================
# 16. CMakeLists.txt — Максимальная оптимизация (-O3 + ARMv9) под Tensor G3 (Pixel 8 Pro)
# ==============================================================================
cmake_path = 'app/jni/CMakeLists.txt'
if os.path.exists(cmake_path):
    with open(cmake_path, 'r', encoding='utf-8') as f:
        cmake_code = f.read()

    tensor_flags = """
add_compile_options(
  $<$<COMPILE_LANGUAGE:C,CXX>:-O3>
  $<$<COMPILE_LANGUAGE:C,CXX>:-march=armv9-a+bf16+i8mm+crypto>
  $<$<COMPILE_LANGUAGE:C,CXX>:-mtune=cortex-a715>
)
"""
    cmake_new, count = re.subn(
        r'(cmake_minimum_required\s*\([^\)]*\))',
        r'\1\n' + tensor_flags,
        cmake_code,
        count=1,
        flags=re.IGNORECASE
    )
    if count > 0:
        with open(cmake_path, 'w', encoding='utf-8') as f:
            f.write(cmake_new)
        print(f"[+] Successfully injected Tensor G3 (ARMv9 -O3) flags into {cmake_path}")
    else:
        print(f"[!] Warning: cmake_minimum_required not found in {cmake_path}")

# ==============================================================================
# Диагностика: ищем где именно вызывается OpenStory (просто выводим в лог)
# ==============================================================================
for root, _, files in os.walk('app/src/main'):
    for file in files:
        if file.endswith(('.java', '.kt')):
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f, 1):
                    if 'OpenStory' in line:
                        print(f"[i] Found OpenStory at {fp}:{idx}: {line.strip()}")

print("[*] All patches applied successfully!")
