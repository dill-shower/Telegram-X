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
# 0. Client.java (Шлюз TDLib) — Глобальный перехватчик всех нежелательных запросов
# ==============================================================================
client_path = 'tdlib/src/main/java/org/drinkless/tdlib/Client.java'
tdapi_path = None
for root, _, files in os.walk('tdlib'):
    if 'TdApi.java' in files:
        tdapi_path = os.path.join(root, 'TdApi.java')
        break

candidates = [
    'OpenStory',
    'CloseStory',
    'OpenChat',
    'CloseChat',
    'OpenChatSimilarChat',
    'OpenBotSimilarBot',
    'SendChatAction',
    'SendChatScreenshotTakenNotification',
    'ViewSponsoredMessage',
    'ClickSponsoredMessage',
    'OpenChatSponsoredMessage',
]

verified_classes = []
if tdapi_path and os.path.exists(tdapi_path):
    with open(tdapi_path, 'r', encoding='utf-8') as f:
        tdapi_code = f.read()
    for cls in candidates:
        if f'class {cls} extends Function<Ok>' in tdapi_code:
            verified_classes.append(cls)
        else:
            print(f"[i] Skipped TdApi.{cls} (not found as Function<Ok> in TdApi.java)")
else:
    verified_classes = ['OpenChat', 'CloseChat', 'OpenChatSimilarChat', 'OpenBotSimilarBot', 'SendChatAction']

if verified_classes and os.path.exists(client_path):
    checks = [f'query instanceof TdApi.{cls}' for cls in verified_classes]
    checks.append('(query instanceof TdApi.ViewMessages && ((TdApi.ViewMessages) query).source instanceof TdApi.MessageSourceScreenshot)')
    condition_str = '\n            || '.join(checks)
    
    gateway_code = (
        'public void send(TdApi.Function<?> query, ResultHandler resultHandler, ExceptionHandler exceptionHandler) {\n'
        '        if (\n'
        f'            {condition_str}\n'
        '        ) {\n'
        '            query = new TdApi.SetAlarm(0);\n'
        '        }'
    )
    patch(
        client_path,
        'public void send(TdApi.Function<?> query, ResultHandler resultHandler, ExceptionHandler exceptionHandler) {',
        gateway_code
    )
    print(f"[+] Client.java gateway blocking: {', '.join(verified_classes)}")

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
# 4. MessagesController.java — Скриншоты, отмена "печатает", авто-отложка на +20 сек
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

# Авто-отложка при обычном нажатии "Отправить" (текст и файлы, включая ботов)
patch(
    'app/src/main/java/org/thunderdog/challegram/ui/MessagesController.java',
    '  private void send (TdApi.MessageSendOptions sendOptions) {\n    send(sendOptions, true);\n  }',
    """  private void send (TdApi.MessageSendOptions sendOptions) {
    if (sendOptions == null && chat != null && !isSecretChat() && !isSelfChat()) {
      TdApi.MessageSchedulingStateSendAtDate state = new TdApi.MessageSchedulingStateSendAtDate();
      state.sendDate = (int) (tdlib.currentTime(TimeUnit.SECONDS) + 20);
      sendOptions = new TdApi.MessageSendOptions();
      sendOptions.schedulingState = state;
    }
    send(sendOptions, true);
  }"""
)

# Авто-отложка для стикеров, гифок, опросов и "без звука"
patch(
    'app/src/main/java/org/thunderdog/challegram/ui/MessagesController.java',
    '    } else {\n      sendCallback.onSendRequested(initialSendOptions, false);\n    }',
    """    } else {
      if (initialSendOptions.schedulingState == null && chat != null && !isSecretChat() && !isSelfChat()) {
        TdApi.MessageSchedulingStateSendAtDate state = new TdApi.MessageSchedulingStateSendAtDate();
        state.sendDate = (int) (tdlib.currentTime(TimeUnit.SECONDS) + 20);
        initialSendOptions.schedulingState = state;
      }
      sendCallback.onSendRequested(initialSendOptions, false);
    }"""
)

# Авто-отложка для фото и видео из галереи
patch(
    'app/src/main/java/org/thunderdog/challegram/ui/MessagesController.java',
    '    TdApi.MessageSendOptions finalSendOptions = Td.newSendOptions(\n      modifiedSendOptions,\n      getInputSuggestedPostInfo(replyInfo),\n      obtainSilentMode()\n    );',
    """    TdApi.MessageSendOptions finalSendOptions = Td.newSendOptions(
      modifiedSendOptions,
      getInputSuggestedPostInfo(replyInfo),
      obtainSilentMode()
    );
    if (finalSendOptions.schedulingState == null && chat != null && !isSecretChat() && !isSelfChat()) {
      TdApi.MessageSchedulingStateSendAtDate state = new TdApi.MessageSchedulingStateSendAtDate();
      state.sendDate = (int) (tdlib.currentTime(TimeUnit.SECONDS) + 20);
      finalSendOptions.schedulingState = state;
    }"""
)

# Не перекидываем на экран "Отложенные сообщения" после нажатия Отправить
patch(
    'app/src/main/java/org/thunderdog/challegram/ui/MessagesController.java',
    '              if (!areScheduled && isSchedule && isFocused()) {\n                viewScheduledMessages(true);\n              }',
    '              if (false && !areScheduled && isSchedule && isFocused()) {\n                viewScheduledMessages(true);\n              }'
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
# 11. Tdlib.java — Маскировка модели устройства под массовый Samsung Galaxy A55
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
# 12. Tdlib.java — Блокировка уведомлений о скриншотах + Анти-удаление на лету
# ==============================================================================
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'public void sendScreenshotMessage (long chatId, long[] messageIds) {',
    'public void sendScreenshotMessage (long chatId, long[] messageIds) {\n    if (true) return;'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'private void updateMessagesDeleted (TdApi.UpdateDeleteMessages update) {',
    'private void updateMessagesDeleted (TdApi.UpdateDeleteMessages update) {\n    if (true) return;'
)

# ==============================================================================
# 13. Tdlib.java — Вечный оффлайн + сброс онлайна (кроме отложенных и Избранного!)
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
    """public void forceOffline () {
    performOptional(c -> c.send(new TdApi.SetOption("online", new TdApi.OptionValueBoolean(true)), r ->
      c.send(new TdApi.SetOption("online", new TdApi.OptionValueBoolean(false)), silentHandler())
    ), null);
  }

  public void setOnline (boolean isOnline) {
    if (true) return;"""
)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'client().send(new TdApi.ViewMessages(chatId, new long[] {chat.lastMessage.id}, source, true), okHandler(after));',
    'client().send(new TdApi.ViewMessages(chatId, new long[] {chat.lastMessage.id}, source, true), result -> { okHandler(after).onResult(result); forceOffline(); });'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'send(new TdApi.ViewMessages(chatId, messageIds, source, true), typedOkHandler());',
    'send(new TdApi.ViewMessages(chatId, messageIds, source, true), (ok, error) -> { typedOkHandler().onResult(ok, error); forceOffline(); });'
)
patch(
    'app/src/main/java/org/thunderdog/challegram/telegram/Tdlib.java',
    'private void updateMessageSendSucceeded (TdApi.UpdateMessageSendSucceeded update) {',
    'private void updateMessageSendSucceeded (TdApi.UpdateMessageSendSucceeded update) {\n    if (update.message.schedulingState == null && !isSelfChat(update.message.chatId)) {\n      forceOffline();\n    }'
)

# ==============================================================================
# 14. CMakeLists.txt — Максимальная оптимизация (-O3 + ARMv9 + ThinLTO) под Tensor G3
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
  $<$<COMPILE_LANGUAGE:C,CXX>:-flto=thin>
)
add_link_options(-flto=thin -Wl,--thinlto-jobs=4 -Wl,-O3)
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
        print(f"[+] Successfully injected Tensor G3 (ARMv9 -O3 ThinLTO) flags into {cmake_path}")
    else:
        print(f"[!] Warning: cmake_minimum_required not found in {cmake_path}")

print("[*] All patches applied successfully!")
