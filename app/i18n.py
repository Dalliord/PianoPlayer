"""UI translations. Language names remain native in every locale."""
LANGUAGES = (
    ("ru", "Русский", "ru"), ("en", "English", "us"),
    ("es", "Español", "es"), ("pt", "Português", "pt"),
    ("ja", "日本語", "jp"), ("ko", "한국어", "kr"),
    ("zh", "中文", "cn"), ("fr", "Français", "fr"), ("de", "Deutsch", "de"),
)

# Columns follow LANGUAGES. A single source table keeps coverage verifiable.
_ROWS = {
    "subtitle": "Фортепианные партитуры | Piano sheets | Partituras de piano | Partituras de piano | ピアノ楽譜 | 피아노 악보 | 钢琴乐谱 | Partitions de piano | Klaviernoten",
    "library": "БИБЛИОТЕКА | LIBRARY | BIBLIOTECA | BIBLIOTECA | ライブラリ | 라이브러리 | 曲库 | BIBLIOTHÈQUE | BIBLIOTHEK",
    "count": "Песен: {count} | Songs: {count} | Canciones: {count} | Músicas: {count} | 曲数：{count} | 곡 수: {count} | 歌曲：{count} | Morceaux : {count} | Stücke: {count}",
    "language": "Язык | Language | Idioma | Idioma | 言語 | 언어 | 语言 | Langue | Sprache",
    "new_song": "Добавить песню | Add song | Añadir canción | Adicionar música | 曲を追加 | 곡 추가 | 添加歌曲 | Ajouter un morceau | Stück hinzufügen",
    "delete_song": "Удалить песню | Delete song | Eliminar canción | Excluir música | 曲を削除 | 곡 삭제 | 删除歌曲 | Supprimer le morceau | Stück löschen",
    "undo_delete": "Отменить удаление | Undo deletion | Deshacer eliminación | Desfazer exclusão | 削除を取り消す | 삭제 취소 | 撤销删除 | Annuler la suppression | Löschen rückgängig machen",
    "song_deleted": "Песня удалена из библиотеки | Song deleted from the library | Canción eliminada de la biblioteca | Música excluída da biblioteca | ライブラリから曲を削除しました | 라이브러리에서 곡을 삭제했습니다 | 歌曲已从曲库删除 | Morceau supprimé de la bibliothèque | Stück aus der Bibliothek gelöscht",
    "song_restored": "Песня восстановлена | Song restored | Canción restaurada | Música restaurada | 曲を復元しました | 곡을 복원했습니다 | 歌曲已恢复 | Morceau restauré | Stück wiederhergestellt",
    "library_empty": "Библиотека пуста | Library is empty | La biblioteca está vacía | A biblioteca está vazia | ライブラリは空です | 라이브러리가 비어 있습니다 | 曲库为空 | La bibliothèque est vide | Die Bibliothek ist leer",
    "import_midi": "Импорт MIDI | Import MIDI | Importar MIDI | Importar MIDI | MIDIをインポート | MIDI 가져오기 | 导入 MIDI | Importer un MIDI | MIDI importieren",
    "advanced": "Настройки | Settings | Ajustes | Configurações | 設定 | 설정 | 设置 | Paramètres | Einstellungen",
    "advanced_tip": "Клавиатура и горячие клавиши | Keyboard and shortcuts | Teclado y atajos | Teclado e atalhos | キーボードとショートカット | 키보드 및 단축키 | 键盘和快捷键 | Clavier et raccourcis | Tastatur und Tastenkürzel",
    "song": "Песня | Song | Canción | Música | 曲 | 곡 | 歌曲 | Morceau | Stück",
    "sheet": "Партитура | Sheet | Partitura | Partitura | 楽譜 | 악보 | 乐谱 | Partition | Noten",
    "open": "Открыть… | Open… | Abrir… | Abrir… | 開く… | 열기… | 打开… | Ouvrir… | Öffnen…",
    "save": "Сохранить… | Save… | Guardar… | Salvar… | 保存… | 저장… | 保存… | Enregistrer… | Speichern…",
    "original": "Оригинал | Original | Original | Original | 元に戻す | 원본 | 原始版本 | Original | Original",
    "placeholder": "Выбери песню или вставь свою партитуру… | Choose a song or paste your sheet… | Elige una canción o pega tu partitura… | Escolha uma música ou cole sua partitura… | 曲を選択するか、楽譜を貼り付けてください… | 곡을 선택하거나 악보를 붙여넣으세요… | 选择歌曲或粘贴乐谱… | Choisissez un morceau ou collez votre partition… | Stück auswählen oder eigene Noten einfügen…",
    "notation": "Обозначения и темп | Notation and tempo | Notación y tempo | Notação e andamento | 記譜とテンポ | 표기법과 템포 | 记谱和速度 | Notation et tempo | Notation und Tempo",
    "timing": "ТАЙМИНГ | TIMING | TIEMPOS | TEMPORIZAÇÃO | タイミング | 타이밍 | 时间设置 | TEMPORISATION | ZEITSTEUERUNG",
    "note_delay": "Интервал нот | Note Delay | Intervalo entre notas | Intervalo entre notas | ノート間隔 | 음표 간격 | 音符间隔 | Intervalle des notes | Notenabstand",
    "key_hold": "Удержание клавиш | Key Hold Time | Duración de pulsación | Tempo de pressão | キーの保持時間 | 키 누름 시간 | 按键保持时间 | Durée de maintien | Haltedauer",
    "start_delay": "Задержка старта | Start Delay | Retraso de inicio | Atraso inicial | 開始までの時間 | 시작 지연 | 开始延迟 | Délai de départ | Startverzögerung",
    "humanize": "Очеловечивание | Humanize | Humanizar | Humanizar | 自然な演奏 | 자연스러운 연주 | 人性化演奏 | Humaniser | Menschliches Spiel",
    "humanize_tip": "Слегка варьировать нажатия, удержания и аккорды, сохраняя общий темп. | Slightly vary note timing, holds and chords while keeping the overall tempo. | Variar ligeramente las pulsaciones, duraciones y acordes conservando el tempo general. | Variar levemente os ataques, durações e acordes mantendo o andamento geral. | 全体のテンポを保ちつつ、発音や保持時間、和音にわずかな揺らぎを加えます。 | 전체 템포를 유지하면서 타이밍, 누름 시간, 화음을 조금씩 변화시킵니다. | 保持整体速度，轻微变化按键时机、时长及和弦。 | Varier légèrement les attaques, les durées et les accords en conservant le tempo global. | Anschläge, Haltedauern und Akkorde leicht variieren und das Gesamttempo beibehalten.",
    "reset_timing": "Пресет песни | Song preset | Ajustes de la canción | Predefinição da música | 曲の初期設定 | 곡 기본 설정 | 歌曲预设 | Réglage du morceau | Stückvorgabe",
    "reset_tip": "Вернуть исходные настройки этой песни. | Restore this song’s original timing. | Restaurar los tiempos originales de esta canción. | Restaurar os tempos originais desta música. | この曲のタイミングを初期設定に戻します。 | 이 곡의 기본 타이밍을 복원합니다. | 恢复这首歌的初始时间设置。 | Rétablir les temps d’origine de ce morceau. | Ursprüngliche Zeitwerte dieses Stücks wiederherstellen.",
    "ready": "Готово | Ready | Listo | Pronto | 準備完了 | 준비됨 | 就绪 | Prêt | Bereit",
    "play": "Играть | Play | Reproducir | Reproduzir | 再生 | 재생 | 播放 | Jouer | Abspielen",
    "pause": "Пауза | Pause | Pausa | Pausar | 一時停止 | 일시 정지 | 暂停 | Pause | Pause",
    "resume": "Продолжить | Resume | Continuar | Continuar | 再開 | 계속 | 继续 | Reprendre | Fortsetzen",
    "stop": "Стоп | Stop | Detener | Parar | 停止 | 정지 | 停止 | Arrêter | Stopp",
    "playing": "Воспроизведение | Playing | Reproduciendo | Reproduzindo | 再生中 | 재생 중 | 正在播放 | Lecture en cours | Wiedergabe läuft",
    "paused": "На паузе | Paused | En pausa | Em pausa | 一時停止中 | 일시 정지됨 | 已暂停 | En pause | Pausiert",
    "stopped": "Остановлено | Stopped | Detenido | Parado | 停止しました | 정지됨 | 已停止 | Arrêté | Gestoppt",
    "finished": "Завершено | Finished | Finalizado | Concluído | 完了 | 완료 | 已完成 | Terminé | Beendet",
    "emergency": "Аварийная остановка | Emergency stop | Parada de emergencia | Parada de emergência | 緊急停止 | 긴급 정지 | 紧急停止 | Arrêt d’urgence | Notstopp",
    "countdown": "Начало через {count}… | Starting in {count}… | Comienza en {count}… | Começando em {count}… | 開始まで {count}… | {count}초 후 시작… | {count} 秒后开始… | Départ dans {count}… | Start in {count}…",
    "toggle": "Играть / Пауза / Продолжить | Play / Pause / Resume | Reproducir / Pausa / Continuar | Reproduzir / Pausar / Continuar | 再生 / 一時停止 / 再開 | 재생 / 일시 정지 / 계속 | 播放 / 暂停 / 继续 | Jouer / Pause / Reprendre | Abspielen / Pause / Fortsetzen",
    "checking": "Проверка партитуры… | Checking sheet… | Comprobando partitura… | Verificando partitura… | 楽譜を確認中… | 악보 확인 중… | 正在检查乐谱… | Vérification de la partition… | Noten werden geprüft…",
    "valid": "Партитура готова · {count} событий | Sheet ready · {count} events | Partitura lista · {count} eventos | Partitura pronta · {count} eventos | 楽譜の準備完了 · {count} イベント | 악보 준비 완료 · 이벤트 {count}개 | 乐谱就绪 · {count} 个事件 | Partition prête · {count} événements | Noten bereit · {count} Ereignisse",
    "empty": "В партитуре нет нот. | The sheet has no notes. | La partitura no tiene notas. | A partitura não tem notas. | 楽譜に音符がありません。 | 악보에 음표가 없습니다. | 乐谱中没有音符。 | La partition ne contient aucune note. | Die Noten enthalten keine Töne.",
    "error": "Ошибка: {error} | Error: {error} | Error: {error} | Erro: {error} | エラー：{error} | 오류: {error} | 错误：{error} | Erreur : {error} | Fehler: {error}",
    "syntax_error": "Ошибка в позиции {position}: {error} | Error at position {position}: {error} | Error en la posición {position}: {error} | Erro na posição {position}: {error} | 位置 {position} のエラー：{error} | {position}번째 위치 오류: {error} | 第 {position} 个字符处出错：{error} | Erreur à la position {position} : {error} | Fehler an Position {position}: {error}",
    "title": "Название песни | Song title | Título de la canción | Título da música | 曲名 | 곡 제목 | 歌曲名称 | Titre du morceau | Titel des Stücks",
    "title_hint": "Введи название… | Enter a title… | Escribe un título… | Digite um título… | 曲名を入力… | 제목 입력… | 输入名称… | Saisissez un titre… | Titel eingeben…",
    "add": "Добавить | Add | Añadir | Adicionar | 追加 | 추가 | 添加 | Ajouter | Hinzufügen",
    "cancel": "Отмена | Cancel | Cancelar | Cancelar | キャンセル | 취소 | 取消 | Annuler | Abbrechen",
    "close": "Закрыть | Close | Cerrar | Fechar | 閉じる | 닫기 | 关闭 | Fermer | Schließen",
    "ok": "ОК | OK | Aceptar | OK | OK | 확인 | 确定 | OK | OK",
    "song_added": "Песня добавлена в библиотеку | Song added to the library | Canción añadida a la biblioteca | Música adicionada à biblioteca | ライブラリに曲を追加しました | 라이브러리에 곡을 추가했습니다 | 歌曲已添加到曲库 | Morceau ajouté à la bibliothèque | Stück zur Bibliothek hinzugefügt",
    "name_required": "Введи название песни. | Enter a song title. | Escribe un título para la canción. | Digite um título para a música. | 曲名を入力してください。 | 곡 제목을 입력하세요. | 请输入歌曲名称。 | Saisissez un titre pour le morceau. | Gib einen Titel für das Stück ein.",
    "save_error": "Не удалось сохранить настройки: {error} | Could not save settings: {error} | No se pudieron guardar los ajustes: {error} | Não foi possível salvar as configurações: {error} | 設定を保存できません：{error} | 설정을 저장하지 못했습니다: {error} | 无法保存设置：{error} | Impossible d’enregistrer les paramètres : {error} | Einstellungen konnten nicht gespeichert werden: {error}",
    "plan_error": "Не удалось создать план воспроизведения: {error} | Could not create playback plan: {error} | No se pudo crear el plan de reproducción: {error} | Não foi possível criar o plano de reprodução: {error} | 再生プランを作成できません：{error} | 재생 계획을 만들지 못했습니다: {error} | 无法创建播放计划：{error} | Impossible de créer le plan de lecture : {error} | Wiedergabeplan konnte nicht erstellt werden: {error}",
    "open_sheet": "Открыть партитуру | Open sheet | Abrir partitura | Abrir partitura | 楽譜を開く | 악보 열기 | 打开乐谱 | Ouvrir une partition | Noten öffnen",
    "save_sheet": "Сохранить партитуру | Save sheet | Guardar partitura | Salvar partitura | 楽譜を保存 | 악보 저장 | 保存乐谱 | Enregistrer la partition | Noten speichern",
    "text_files": "Текстовые файлы (*.txt) | Text files (*.txt) | Archivos de texto (*.txt) | Arquivos de texto (*.txt) | テキストファイル (*.txt) | 텍스트 파일 (*.txt) | 文本文件 (*.txt) | Fichiers texte (*.txt) | Textdateien (*.txt)",
    "all_files": "Все файлы (*) | All files (*) | Todos los archivos (*) | Todos os arquivos (*) | すべてのファイル (*) | 모든 파일 (*) | 所有文件 (*) | Tous les fichiers (*) | Alle Dateien (*)",
    "auto_ahk": "Автоматически найти AutoHotkey v2 | Auto-detect AutoHotkey v2 | Detectar AutoHotkey v2 automáticamente | Detectar AutoHotkey v2 automaticamente | AutoHotkey v2を自動検出 | AutoHotkey v2 자동 감지 | 自动检测 AutoHotkey v2 | Détecter AutoHotkey v2 automatiquement | AutoHotkey v2 automatisch erkennen",
    "browse": "Обзор… | Browse… | Examinar… | Procurar… | 参照… | 찾아보기… | 浏览… | Parcourir… | Durchsuchen…",
    "send_mode": "Режим отправки | Send mode | Modo de envío | Modo de envio | 送信モード | 입력 전송 방식 | 发送模式 | Mode d’envoi | Sendemodus",
    "hotkeys": "Горячие клавиши | Shortcuts | Atajos | Atalhos | ショートカット | 단축키 | 快捷键 | Raccourcis | Tastenkürzel",
    "hotkey_error": "Выберите три разные клавиши F1–F24. | Choose three different keys from F1–F24. | Elige tres teclas distintas entre F1 y F24. | Escolha três teclas diferentes de F1 a F24. | F1～F24から異なる3つのキーを選んでください。 | F1–F24 중 서로 다른 세 키를 선택하세요. | 请选择三个不同的 F1–F24 按键。 | Choisissez trois touches différentes de F1 à F24. | Wähle drei unterschiedliche Tasten von F1 bis F24.",
    "tracks": "Дорожки для фортепиано | Piano tracks | Pistas de piano | Faixas de piano | ピアノのトラック | 피아노 트랙 | 钢琴音轨 | Pistes de piano | Klavierspuren",
    "sustain": "Учитывать педаль sustain из MIDI | Use MIDI sustain pedal | Usar pedal de sustain del MIDI | Usar pedal de sustain do MIDI | MIDIのサステインペダルを反映 | MIDI 서스테인 페달 반영 | 使用 MIDI 延音踏板 | Utiliser la pédale de sustain MIDI | MIDI-Haltepedal berücksichtigen",
    "adapt": "Адаптировать диапазон и конфликты клавиш по октавам | Adapt range and key conflicts by octaves | Adaptar el rango y los conflictos por octavas | Adaptar a extensão e os conflitos por oitavas | 音域とキーの競合をオクターブ単位で調整 | 옥타브 이동으로 음역 및 키 충돌 조정 | 通过八度移调适配音域及按键冲突 | Adapter la tessiture et les conflits par octaves | Tonumfang und Tastenkonflikte durch Oktavierung anpassen",
    "reading_midi": "Чтение MIDI… | Reading MIDI… | Leyendo MIDI… | Lendo MIDI… | MIDIを読み込み中… | MIDI 읽는 중… | 正在读取 MIDI… | Lecture du MIDI… | MIDI wird gelesen…",
    "preparing": "Подготовка партитуры… | Preparing sheet… | Preparando partitura… | Preparando partitura… | 楽譜を準備中… | 악보 준비 중… | 正在准备乐谱… | Préparation de la partition… | Noten werden vorbereitet…",
    "track_notes": "{name} · {count} нот | {name} · {count} notes | {name} · {count} notas | {name} · {count} notas | {name} · {count} 音 | {name} · 음표 {count}개 | {name} · {count} 个音符 | {name} · {count} notes | {name} · {count} Noten",
    "drums": " · {count} ударных | · {count} drums | · {count} percusiones | · {count} percussões | · 打楽器 {count} 音 | · 타악기 {count}개 | · {count} 个打击乐音符 | · {count} percussions | · {count} Schlagzeugnoten",
    "midi_detail": "Темп и длительности берутся из файла. Ударные канала 10 исключаются. Клавиатура не передаёт громкость нот и тембры. | Tempo and durations come from the file. Channel 10 drums are excluded. A keyboard cannot convey note velocity or instrument timbres. | Se conservan el tempo y las duraciones del archivo. Se excluye la percusión del canal 10. El teclado no transmite intensidad ni timbres. | O andamento e as durações vêm do arquivo. A percussão do canal 10 é excluída. O teclado não transmite intensidade nem timbres. | ファイルのテンポと音価を使用します。チャンネル10の打楽器は除外されます。キー入力では強弱や音色を再現できません。 | 파일의 템포와 음 길이를 사용합니다. 채널 10의 타악기는 제외됩니다. 키보드로는 음의 세기나 악기 음색을 전달할 수 없습니다. | 保留文件中的速度和时长，排除第 10 通道打击乐。键盘无法传递力度和乐器音色。 | Le tempo et les durées proviennent du fichier. Les percussions du canal 10 sont exclues. Le clavier ne transmet ni vélocité ni timbre. | Tempo und Dauern stammen aus der Datei. Schlagzeug auf Kanal 10 wird ausgeschlossen. Die Tastatur überträgt weder Anschlagstärke noch Klangfarben.",
    "midi_stats": "{played} из {source} нот · {seconds:.2f} s · смен темпа: {tempo}\nПереносов по октавам: {octaves} · объединено: {merged} · пропущено: {omitted}\nПовторных нажатий: {retriggered} · ограничений удержания: {holds} · незакрытых нот: {repairs} | {played} of {source} notes · {seconds:.2f} s · tempo changes: {tempo}\nOctave shifts: {octaves} · merged: {merged} · omitted: {omitted}\nRetriggers: {retriggered} · bounded holds: {holds} · unclosed notes: {repairs} | {played} de {source} notas · {seconds:.2f} s · cambios de tempo: {tempo}\nCambios de octava: {octaves} · unidas: {merged} · omitidas: {omitted}\nRepeticiones: {retriggered} · duraciones limitadas: {holds} · notas sin cierre: {repairs} | {played} de {source} notas · {seconds:.2f} s · mudanças de andamento: {tempo}\nMudanças de oitava: {octaves} · unidas: {merged} · omitidas: {omitted}\nRepetições: {retriggered} · durações limitadas: {holds} · notas sem fim: {repairs} | {source} 音中 {played} 音 · {seconds:.2f} 秒 · テンポ変更：{tempo}\nオクターブ調整：{octaves} · 統合：{merged} · 省略：{omitted}\n再打鍵：{retriggered} · 保持時間制限：{holds} · 終了のない音：{repairs} | {source}개 중 {played}개 음표 · {seconds:.2f}초 · 템포 변경: {tempo}\n옥타브 이동: {octaves} · 병합: {merged} · 생략: {omitted}\n재타건: {retriggered} · 누름 시간 제한: {holds} · 끝이 없는 음표: {repairs} | {source} 个音符中保留 {played} 个 · {seconds:.2f} 秒 · 速度变化：{tempo}\n八度调整：{octaves} · 合并：{merged} · 省略：{omitted}\n重新触发：{retriggered} · 时长限制：{holds} · 未结束音符：{repairs} | {played} notes sur {source} · {seconds:.2f} s · changements de tempo : {tempo}\nOctaves déplacées : {octaves} · fusionnées : {merged} · omises : {omitted}\nRépétitions : {retriggered} · durées limitées : {holds} · notes sans fin : {repairs} | {played} von {source} Noten · {seconds:.2f} s · Tempowechsel: {tempo}\nOktavverschiebungen: {octaves} · zusammengeführt: {merged} · ausgelassen: {omitted}\nNeuanschläge: {retriggered} · begrenzte Haltedauern: {holds} · offene Noten: {repairs}",
}

_ROWS.update({
    "track_name": "Дорожка {number} | Track {number} | Pista {number} | Faixa {number} | トラック {number} | 트랙 {number} | 音轨 {number} | Piste {number} | Spur {number}",
    "midi_dependency": "Для импорта MIDI установи зависимости: pip install -r requirements.txt | To import MIDI, install dependencies: pip install -r requirements.txt | Para importar MIDI, instala las dependencias: pip install -r requirements.txt | Para importar MIDI, instale as dependências: pip install -r requirements.txt | MIDIのインポートには依存関係をインストール：pip install -r requirements.txt | MIDI를 가져오려면 의존성을 설치하세요: pip install -r requirements.txt | 导入 MIDI 前请安装依赖：pip install -r requirements.txt | Pour importer un MIDI, installez les dépendances : pip install -r requirements.txt | Für den MIDI-Import Abhängigkeiten installieren: pip install -r requirements.txt",
    "midi_zero_tempo": "В MIDI указан нулевой темп. | The MIDI contains a zero tempo. | El MIDI contiene un tempo de cero. | O MIDI contém um andamento zero. | MIDIのテンポが0です。 | MIDI에 템포 0이 있습니다. | MIDI 中存在零速度。 | Le MIDI contient un tempo nul. | Das MIDI enthält ein Tempo von null.",
    "midi_timing_error": "Не удалось сохранить тайминг MIDI. | Could not preserve MIDI timing. | No se pudieron conservar los tiempos MIDI. | Não foi possível preservar os tempos MIDI. | MIDIのタイミングを維持できません。 | MIDI 타이밍을 유지하지 못했습니다. | 无法保留 MIDI 时间。 | Impossible de conserver les temps MIDI. | MIDI-Timing konnte nicht erhalten werden.",
    "midi_read_error": "Не удалось прочитать MIDI: {error} | Could not read MIDI: {error} | No se pudo leer el MIDI: {error} | Não foi possível ler o MIDI: {error} | MIDIを読み込めません：{error} | MIDI를 읽지 못했습니다: {error} | 无法读取 MIDI：{error} | Impossible de lire le MIDI : {error} | MIDI konnte nicht gelesen werden: {error}",
    "ahk_start_error": "Ошибка запуска AHK: {error} | AHK could not start: {error} | No se pudo iniciar AHK: {error} | Não foi possível iniciar o AHK: {error} | AHKを起動できません：{error} | AHK를 시작하지 못했습니다: {error} | 无法启动 AHK：{error} | Impossible de démarrer AHK : {error} | AHK konnte nicht gestartet werden: {error}",
    "ahk_exit": "AHK завершился (код {code}). | AHK exited (code {code}). | AHK terminó (código {code}). | O AHK encerrou (código {code}). | AHKが終了しました（コード {code}）。 | AHK가 종료되었습니다(코드 {code}). | AHK 已退出（代码 {code}）。 | AHK s’est arrêté (code {code}). | AHK wurde beendet (Code {code}).",
    "h_notes": "отдельные ноты | single notes | notas individuales | notas individuais | 単音 | 단음 | 单音 | notes seules | einzelne Noten",
    "h_chord": "аккорд | chord | acorde | acorde | 和音 | 화음 | 和弦 | accord | Akkord",
    "h_fast": "быстрая последовательность | fast sequence | secuencia rápida | sequência rápida | 速い連続音 | 빠른 연속음 | 快速音列 | séquence rapide | schnelle Tonfolge",
    "h_rest": "пауза на один шаг | one-step rest | silencio de un paso | pausa de um passo | 1ステップの休符 | 한 스텝 쉼 | 休止一步 | silence d’un pas | Pause von einem Schritt",
    "h_hold": "удерживать аккорд 1000 ms | hold chord for 1000 ms | mantener el acorde 1000 ms | segurar o acorde por 1000 ms | 和音を1000 ms保持 | 화음을 1000 ms 동안 유지 | 和弦保持 1000 ms | maintenir l’accord 1000 ms | Akkord 1000 ms halten",
    "h_perkey": "разные удержания одновременно | independent simultaneous holds | duraciones simultáneas independientes | durações simultâneas independentes | 各音を個別の長さで保持 | 동시에 각 음을 다른 길이로 유지 | 同时按下，分别保持 | maintiens simultanés indépendants | gleichzeitige, unabhängige Haltedauern",
    "h_fraction": "дробная длительность в ms | fractional duration in ms | duración fraccionaria en ms | duração fracionária em ms | 小数の保持時間（ms） | 소수 단위 길이(ms) | 小数时长（ms） | durée fractionnaire en ms | gebrochene Dauer in ms",
    "h_bpm": "120 четвертей в минуту | 120 quarter notes per minute | 120 negras por minuto | 120 semínimas por minuto | 1分間に四分音符120拍 | 분당 4분음표 120개 | 每分钟 120 个四分音符 | 120 noires par minute | 120 Viertelnoten pro Minute",
    "h_step": "четверть доли (шестнадцатая) | quarter of a beat (sixteenth note) | cuarto de pulso (semicorchea) | quarto de um tempo (semicolcheia) | 1拍の4分の1（十六分音符） | 한 박의 1/4(16분음표) | 四分之一拍（十六分音符） | quart de temps (double croche) | Viertelschlag (Sechzehntelnote)",
    "h_triplet": "треть доли (триоль) | third of a beat (triplet) | tercio de pulso (tresillo) | terço de um tempo (tercina) | 1拍の3分の1（3連符） | 한 박의 1/3(셋잇단음표) | 三分之一拍（三连音） | tiers de temps (triolet) | Drittelschlag (Triole)",
    "h_ramp": "плавно к 180 BPM за 8 долей | gradually reach 180 BPM over 8 beats | llegar gradualmente a 180 BPM en 8 pulsos | chegar gradualmente a 180 BPM em 8 tempos | 8拍かけて180 BPMへ変化 | 8박 동안 180 BPM으로 서서히 변화 | 在 8 拍内渐变至 180 BPM | atteindre 180 BPM en 8 temps | über 8 Schläge allmählich auf 180 BPM",
    "h_delay": "точный шаг в миллисекундах | exact step in milliseconds | paso exacto en milisegundos | passo exato em milissegundos | 正確なステップ間隔（ms） | 정확한 스텝 간격(ms) | 精确步长（毫秒） | pas exact en millisecondes | exakter Schritt in Millisekunden",
    "h_zero": "не двигать время после ноты | no time advance after a note | no avanzar el tiempo tras la nota | não avançar o tempo após a nota | 音の後に時間を進めない | 음표 뒤에 시간을 진행하지 않음 | 音符后不推进时间 | ne pas avancer après la note | nach der Note keine Zeit vorrücken",
    "h_wait": "добавить паузу ровно 250.5 ms | add exactly 250.5 ms of silence | añadir exactamente 250.5 ms de silencio | adicionar exatamente 250.5 ms de pausa | 正確に250.5 msの休止を追加 | 정확히 250.5 ms의 쉼 추가 | 添加恰好 250.5 ms 的停顿 | ajouter exactement 250.5 ms de silence | genau 250.5 ms Pause hinzufügen",
    "h_reset": "вернуть базовый интервал нот | restore base Note Delay | restaurar el intervalo base | restaurar o intervalo base | 基本ノート間隔に戻す | 기본 음표 간격 복원 | 恢复基本音符间隔 | rétablir l’intervalle de base | grundlegenden Notenabstand wiederherstellen",
    "h_summary": "Команды действуют на следующие ноты. Удержания не блокируют игру. BPM и step имеют приоритет перед интервалом нот. Wait добавляет абсолютную паузу без продвижения долей. Для точного тайминга MIDI выключи очеловечивание. | Commands apply to following notes. Holds do not block playback. BPM and step override Note Delay. Wait adds absolute silence without advancing musical beats. Turn humanization off for exact MIDI timing. | Los comandos se aplican a las notas siguientes. Las duraciones no bloquean la reproducción. BPM y step tienen prioridad sobre el intervalo base. Wait añade silencio absoluto sin avanzar los pulsos. Desactiva Humanizar para un MIDI exacto. | Os comandos se aplicam às notas seguintes. As notas sustentadas não bloqueiam a reprodução. BPM e step têm prioridade sobre o intervalo base. Wait adiciona uma pausa absoluta sem avançar os tempos. Desative Humanizar para tempos MIDI exatos. | コマンドは後続の音に適用されます。保持中も演奏は進みます。BPMとstepは基本間隔より優先されます。Waitは拍を進めずに休止を追加します。MIDIを正確に再現するには自然な演奏をオフにしてください。 | 명령은 이후 음표에 적용됩니다. 음을 누른 채로 연주를 계속할 수 있습니다. BPM과 step은 기본 간격보다 우선합니다. Wait는 박을 진행하지 않고 쉼을 추가합니다. 정확한 MIDI 타이밍을 원하면 자연스러운 연주를 끄세요. | 命令作用于后续音符，保持按键不妨碍继续演奏。BPM 和 step 优先于基本间隔。Wait 添加绝对停顿而不推进拍数。要使用精确 MIDI 时间，请关闭人性化演奏。 | Les commandes s’appliquent aux notes suivantes. Les maintiens ne bloquent pas la lecture. BPM et step remplacent l’intervalle de base. Wait ajoute un silence absolu sans avancer les temps. Désactivez Humaniser pour un MIDI exact. | Befehle gelten für folgende Noten. Gehaltene Tasten blockieren die Wiedergabe nicht. BPM und step haben Vorrang vor dem Notenabstand. Wait fügt eine absolute Pause ohne Schlagfortschritt ein. Für exaktes MIDI-Timing menschliches Spiel ausschalten.",
    "err_brackets": "Вложенные, несовпадающие или незакрытые скобки. | Nested, mismatched or unclosed brackets. | Corchetes anidados, incompatibles o sin cerrar. | Colchetes aninhados, incompatíveis ou não fechados. | 括弧が入れ子、不一致、または閉じていません。 | 괄호가 중첩되었거나 맞지 않거나 닫히지 않았습니다. | 括号嵌套、不匹配或未闭合。 | Parenthèses imbriquées, incompatibles ou non fermées. | Verschachtelte, unpassende oder offene Klammern.",
    "err_empty_group": "Пустая группа. | Empty group. | Grupo vacío. | Grupo vazio. | グループが空です。 | 빈 그룹입니다. | 分组为空。 | Groupe vide. | Leere Gruppe.",
    "err_hold": "Удержание ставится сразу после ноты или группы: a<1000>. Диапазон: 5–60000 ms. | Place a hold directly after a note or group: a<1000>. Range: 5–60000 ms. | La duración va justo después de una nota o grupo: a<1000>. Rango: 5–60000 ms. | A duração vai logo após uma nota ou grupo: a<1000>. Limite: 5–60000 ms. | 音またはグループの直後に保持時間を指定：a<1000>。範囲：5～60000 ms。 | 음표나 그룹 바로 뒤에 누름 시간을 지정하세요: a<1000>. 범위: 5–60000 ms. | 在音符或分组后紧接保持时间：a<1000>。范围：5–60000 ms。 | Indiquez la durée juste après une note ou un groupe : a<1000>. Plage : 5–60000 ms. | Haltedauer direkt nach einer Note oder Gruppe angeben: a<1000>. Bereich: 5–60000 ms.",
    "err_command": "Проверь команду тайминга и закрывающие |. Команды указываются вне нотных групп. | Check the timing command and closing |. Commands belong outside note groups. | Revisa el comando y el cierre |. Los comandos van fuera de los grupos. | Verifique o comando e o fechamento |. Os comandos ficam fora dos grupos. | タイミングコマンドと末尾の「|」を確認してください。コマンドはグループ外に置きます。 | 타이밍 명령과 닫는 「|」를 확인하세요. 명령은 음표 그룹 밖에 입력하세요. | 检查时间命令及闭合的 |。命令应放在音符分组外。 | Vérifiez la commande et le «|» final. Placez les commandes hors des groupes. | Zeitbefehl und abschließendes „|“ prüfen. Befehle stehen außerhalb von Notengruppen.",
    "err_key": "Неподдерживаемая клавиша. Используй клавиши английской раскладки. | Unsupported key. Use English keyboard characters. | Tecla no compatible. Usa caracteres del teclado inglés. | Tecla não suportada. Use caracteres do teclado inglês. | 未対応のキーです。英語キーボードの文字を使用してください。 | 지원하지 않는 키입니다. 영문 키보드 문자를 사용하세요. | 不支持此按键。请使用英文键盘字符。 | Touche non prise en charge. Utilisez les caractères du clavier anglais. | Nicht unterstützte Taste. Zeichen der englischen Tastatur verwenden.",
    "err_hour": "Максимальная длительность — 1 час. | Maximum duration is one hour. | La duración máxima es una hora. | A duração máxima é uma hora. | 最大時間は1時間です。 | 최대 길이는 1시간입니다. | 最长时长为一小时。 | La durée maximale est d’une heure. | Die Höchstdauer beträgt eine Stunde.",
    "err_tracks": "Выбери хотя бы одну дорожку с нотами. | Select at least one track with notes. | Elige al menos una pista con notas. | Selecione pelo menos uma faixa com notas. | 音符のあるトラックを1つ以上選択してください。 | 음표가 있는 트랙을 하나 이상 선택하세요. | 请至少选择一个有音符的音轨。 | Sélectionnez au moins une piste avec des notes. | Mindestens eine Spur mit Noten auswählen.",
    "err_adapt": "Включи адаптацию по октавам для нот вне C2–C7 и конфликтов Shift. | Enable octave adaptation for notes outside C2–C7 and Shift conflicts. | Activa la adaptación por octavas para notas fuera de C2–C7 y conflictos con Shift. | Ative a adaptação por oitavas para notas fora de C2–C7 e conflitos com Shift. | C2～C7外の音やShiftの競合にはオクターブ調整を有効にしてください。 | C2–C7 밖의 음이나 Shift 충돌을 해결하려면 옥타브 조정을 켜세요. | 请开启八度适配以处理 C2–C7 外的音符和 Shift 冲突。 | Activez l’adaptation par octaves pour les notes hors C2–C7 et les conflits Shift. | Oktavanpassung für Noten außerhalb C2–C7 und Shift-Konflikte aktivieren.",
    "err_midi_format": "Поддерживаются MIDI 0/1 с PPQN. Форматы 2 и SMPTE не поддерживаются. | MIDI 0/1 with PPQN is supported. Type 2 and SMPTE are unsupported. | Se admite MIDI 0/1 con PPQN. No se admiten tipo 2 ni SMPTE. | MIDI 0/1 com PPQN é suportado. Tipo 2 e SMPTE não são suportados. | PPQN形式のMIDI 0/1に対応しています。形式2とSMPTEは未対応です。 | PPQN 방식의 MIDI 0/1을 지원합니다. 형식 2와 SMPTE는 지원하지 않습니다. | 支持 PPQN 格式的 MIDI 0/1，不支持类型 2 和 SMPTE。 | MIDI 0/1 avec PPQN est pris en charge. Type 2 et SMPTE ne le sont pas. | MIDI 0/1 mit PPQN wird unterstützt. Typ 2 und SMPTE werden nicht unterstützt.",
    "err_midi_size": "Слишком большой MIDI: максимум 16 MB, 200 000 нот, 500 000 событий. | MIDI limit: 16 MB, 200,000 notes, 500,000 events. | Límite MIDI: 16 MB, 200 000 notas, 500 000 eventos. | Limite MIDI: 16 MB, 200 000 notas, 500 000 eventos. | MIDIの上限：16 MB、20万音、50万イベント。 | MIDI 제한: 16 MB, 음표 200,000개, 이벤트 500,000개. | MIDI 上限：16 MB、200,000 个音符、500,000 个事件。 | Limite MIDI : 16 MB, 200 000 notes, 500 000 événements. | MIDI-Grenze: 16 MB, 200.000 Noten, 500.000 Ereignisse.",
    "err_ahk": "AutoHotkey v2 не найден. Установи его или укажи путь в настройках. | AutoHotkey v2 was not found. Install it or set its path in Settings. | No se encontró AutoHotkey v2. Instálalo o indica su ruta en Ajustes. | AutoHotkey v2 não encontrado. Instale-o ou defina o caminho nas Configurações. | AutoHotkey v2が見つかりません。インストールするか、設定でパスを指定してください。 | AutoHotkey v2를 찾을 수 없습니다. 설치하거나 설정에서 경로를 지정하세요. | 未找到 AutoHotkey v2。请安装或在设置中指定路径。 | AutoHotkey v2 est introuvable. Installez-le ou indiquez son chemin dans les paramètres. | AutoHotkey v2 wurde nicht gefunden. Installieren oder den Pfad in den Einstellungen angeben.",
})

TRANSLATIONS = {code: {} for code, _, _ in LANGUAGES}
for _key, _row in _ROWS.items():
    _values = _row.split(" | ")
    if len(_values) != len(LANGUAGES):
        raise ValueError(f"Incomplete translation: {_key}")
    for (_code, _, _), _value in zip(LANGUAGES, _values):
        TRANSLATIONS[_code][_key] = _value


def tr(language: str, key: str, **values) -> str:
    return TRANSLATIONS.get(language, TRANSLATIONS["ru"])[key].format(**values)


def install_qt_translator(language: str) -> None:
    """Translate Qt's file pickers, context menus and standard buttons too."""
    from PySide6.QtCore import QLibraryInfo, QTranslator
    from PySide6.QtWidgets import QApplication
    application = QApplication.instance()
    previous = getattr(application, "_piano_translator", None)
    if previous:
        application.removeTranslator(previous)
        previous.deleteLater()
    translator = QTranslator(application)
    locale = {"pt": "pt_BR", "zh": "zh_CN"}.get(language, language)
    translator.load("qtbase_" + locale, QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
    application.installTranslator(translator)
    application._piano_translator = translator


def status_text(language: str, text: str) -> str:
    import re
    keys = {"Ready": "ready", "Playing": "playing", "Paused": "paused", "Stopped": "stopped",
            "Finished": "finished", "Emergency stopped": "emergency", "ERROR": "error",
            "Song added to the library": "song_added", "Song deleted from the library": "song_deleted",
            "Song restored": "song_restored"}
    if text in keys:
        return tr(language, keys[text], error="").rstrip(":： ")
    match = re.fullmatch(r"Starting in (\d+)\.\.\.", text)
    if match:
        return tr(language, "countdown", count=match[1])
    return error_text(language, text)


def error_text(language: str, message: str) -> str:
    import re
    if message.startswith("AutoHotkey v2 не найден"):
        return tr(language, "err_ahk")
    for prefix, key in [("Не удалось прочитать MIDI: ", "midi_read_error"), ("Ошибка запуска AHK: ", "ahk_start_error")]:
        if message.startswith(prefix):
            return tr(language, key, error=message[len(prefix):])
    match = re.fullmatch(r"AHK завершился \(код (-?\d+)\)\.", message)
    if match:
        return tr(language, "ahk_exit", code=match[1])
    if language == "ru":
        return {"The sheet has no notes.": tr(language, "empty"),
                "Enter a song title.": tr(language, "name_required")}.get(message, message)
    if "скобк" in message:
        key = "err_brackets"
    elif "Пустая группа" in message:
        key = "err_empty_group"
    elif "Удержание" in message or "удержания <" in message:
        key = "err_hold"
    elif message.startswith(("Команды", "Не закрыта команда")):
        key = "err_command"
    elif message.startswith("Неподдерживаемая клавиша"):
        key = "err_key"
    elif "1 час" in message or "одного часа" in message:
        key = "err_hour"
    elif "AutoHotkey v2 не найден" in message:
        key = "err_ahk"
    elif "адаптацию по октавам" in message:
        key = "err_adapt"
    elif "хотя бы одну дорожку" in message:
        key = "err_tracks"
    elif "PPQN" in message:
        key = "err_midi_format"
    elif "16 MB" in message or "200 000 нот" in message:
        key = "err_midi_size"
    elif "нет мелодических нот" in message or message == "The sheet has no notes.":
        key = "empty"
    elif "pip install" in message:
        key = "midi_dependency"
    elif "нулевой темп" in message:
        key = "midi_zero_tempo"
    elif message == "Не удалось сохранить тайминг MIDI.":
        key = "midi_timing_error"
    elif message == "Enter a song title.":
        key = "name_required"
    else:
        return message
    return tr(language, key)


def notation_text(language: str) -> str:
    examples = [("a b c", "notes"), ("[asd]", "chord"), ("{asdf}", "fast"), ("-", "rest"),
                ("[asd]<1000>", "hold"), ("[a<1000>s<200>]", "perkey"), ("a<125.5>", "fraction"),
                ("|bpm=120|", "bpm"), ("|step=1/4|", "step"), ("|step=1/3|", "triplet"),
                ("|ramp=180,8|", "ramp"), ("|delay=75.5|", "delay"), ("|delay=0|", "zero"),
                ("|wait=250.5|", "wait"), ("|reset|", "reset")]
    return "\n".join(f'{code:<18} {tr(language, "h_" + key)}' for code, key in examples) + "\n\n" + tr(language, "h_summary")
