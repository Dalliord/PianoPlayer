; Pure numeric-plan reader. Loading and validation never sends keyboard input.
ReadPlaybackPlan(path) {
    file := FileOpen(path, "r", "UTF-8")
    if !file
        throw Error("Cannot open playback plan")
    try {
        header := StrSplit(file.ReadLine(), "`t")
        if header.Length != 4 || header[1] != "ROBLOXSHEETS" || (header[2] != "1" && header[2] != "2" && header[2] != "3")
            throw Error("Invalid playback plan header")
        version := Integer(header[2])
        hold := ReadPlanNumber(header[3])
        duration := ReadPlanNumber(header[4])
        if hold < 5 || hold > 200
            throw Error("Invalid playback timing")
        loaded := []
        previous := -1.0
        while !file.AtEOF {
            line := file.ReadLine()
            if line = ""
                continue
            fields := StrSplit(line, "`t")
            if fields.Length != (version >= 2 ? 6 : 5)
                throw Error("Invalid playback plan row")
            offset := ReadPlanNumber(fields[1])
            if offset < previous || offset > duration
                throw Error("Invalid playback offset")
            previous := offset
            kind := fields[2]
            if kind != "NOTE" && kind != "CHORD" && kind != "PAUSE"
                throw Error("Invalid playback event")
            start := ReadPlanIndex(fields[4])
            end := ReadPlanIndex(fields[5])
            if end < start
                throw Error("Invalid playback source span")
            eventHold := version >= 2 ? ReadPlanNumber(fields[6]) : hold
            keys := []
            if kind = "PAUSE" {
                if fields[3] != "0" || (version >= 2 && eventHold != 0)
                    throw Error("Invalid playback pause")
                eventHold := 0
            } else {
                if eventHold < 5 || eventHold > (version = 3 ? 60000 : 200)
                    throw Error("Invalid playback hold")
                ; Independent three-decimal TSV rounding can differ by 0.001 ms.
                if version >= 2 && offset + eventHold > duration + 0.0011
                    throw Error("Playback hold exceeds duration")
                for text in StrSplit(fields[3], ",") {
                    code := ReadPlanIndex(text)
                    if code < 33 || code > 126
                        throw Error("Invalid key code")
                    MapCodePoint(code)
                    keys.Push(code)
                }
                if kind = "NOTE" && keys.Length != 1
                    throw Error("Invalid playback note")
            }
            loaded.Push({offset: offset, kind: kind, keys: keys, hold: eventHold,
                         sourceStart: start, sourceEnd: end})
        }
        return {events: loaded, hold: hold, duration: duration, version: version}
    } finally {
        file.Close()
    }
}

ReadPlanNumber(value) {
    ; Reject signs, exponent overflow and non-finite values before conversion.
    if !RegExMatch(value, "^\d+(?:\.\d+)?$") || StrLen(value) > 18
        throw Error("Invalid numeric playback value")
    return Float(value)
}

ReadPlanIndex(value) {
    if !RegExMatch(value, "^\d+$") || StrLen(value) > 12
        throw Error("Invalid playback integer")
    return Integer(value)
}
