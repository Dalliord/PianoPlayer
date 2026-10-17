#Requires AutoHotkey v2.0
#NoTrayIcon
#SingleInstance Off
#Include %A_ScriptDir%\..\ahk\input_utils.ahk
#Include %A_ScriptDir%\..\ahk\plan_reader.ahk

; This replacement is installed before any playback call. No physical input,
; hotkeys, timers or Sleep are used: all times below are absolute simulated ms.
global KeyEmitter := Capture
global CharacterEvents := []
global CaptureModifiers := 0
global CaptureHeld := Map()
global CapturePackets := 0
global Characters := Map()
global ExpectedMapping := Map()
global ExpectedHeld := Map()
global Context := "initialization"
global Output := FileOpen("*", "w", "UTF-8-RAW")

try {
    ; Independently specified US layout: do not derive expectations from the
    ; production MapCodePoint/VkKeyScanExW, which is what this test validates.
    plain := [96,49,50,51,52,53,54,55,56,57,48,45,61,91,93,92,59,39,44,46,47]
    shifted := [126,33,64,35,36,37,94,38,42,40,41,95,43,123,125,124,58,34,60,62,63]
    vks := [0xC0,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x30,0xBD,0xBB,0xDB,0xDD,0xDC,0xBA,0xDE,0xBC,0xBE,0xBF]
    for index, code in plain
        RegisterASCII(code, shifted[index], vks[index])
    loop 26
        RegisterASCII(A_Index + 96, A_Index + 64, A_Index + 64)

    Check(A_Args.Length = 1, "expected numeric-plan manifest path")
    manifest := FileOpen(A_Args[1], "r", "UTF-8")
    count := 0
    while !manifest.AtEOF {
        line := Trim(manifest.ReadLine(), "`r`n")
        if line = ""
            continue
        fields := StrSplit(line, "`t")
        Check(fields.Length = 2, "invalid manifest row")
        ReplayPlan(fields[1], fields[2])
        count += 1
    }
    manifest.Close()
    Output.Write("OK`tcatalog keyboard contract`t" count " plans`n")
    Output.Read(0)
    ExitApp(0)
} catch as err {
    Output.Write("ERROR`t" Context ": " err.Message "`n")
    Output.Read(0)
    ExitApp(1)
}

RegisterASCII(plain, shifted, vk) {
    global Characters, ExpectedMapping
    Characters["0:" vk] := Chr(plain)
    Characters["1:" vk] := Chr(shifted)
    ExpectedMapping[plain] := {vk: vk, modifiers: 0}
    ExpectedMapping[shifted] := {vk: vk, modifiers: 1}
}

ReplayPlan(songId, path) {
    global Context, CharacterEvents, CaptureModifiers, CaptureHeld, ExpectedHeld, HeldKeys, HeldModifiers
    Context := songId
    Check(ExpectedHeld.Count = 0 && HeldKeys.Count = 0 && HeldModifiers.Count = 0,
          "previous plan left held keys")
    Check(CaptureModifiers = 0, "previous plan left a captured modifier")
    Check(CaptureHeld.Count = 0, "previous plan left a captured physical key")
    plan := ReadPlaybackPlan(path)
    duration := plan.duration
    index := 0
    for event in plan.events {
        index += 1
        offset := event.offset
        Context := songId " event " index " source " event.sourceStart ":" event.sourceEnd " at " offset " ms"
        ReleaseUntil(offset)
        CharacterEvents := []
        ReleaseDue(offset)
        CheckCapture([])
        CheckHeld()
        if event.kind = "PAUSE"
            continue
        ExpectPress(event.keys, offset + event.hold)
    }
    Context := songId " final release"
    ReleaseUntil(duration)
    Check(ExpectedHeld.Count = 0 && HeldKeys.Count = 0, "plan duration leaves held notes")
    Check(HeldModifiers.Count = 0 && CaptureModifiers = 0, "plan duration leaves a modifier")
    CharacterEvents := []
    ReleaseAllKeys()
    CheckCapture([])
    CheckHeld()
}

ExpectPress(codes, deadline) {
    global ExpectedMapping, ExpectedHeld, CharacterEvents, CapturePackets
    unique := Map()
    for code in codes {
        Check(ExpectedMapping.Has(code), "unsupported expected ASCII " code)
        vk := ExpectedMapping[code].vk
        if unique.Has(vk) && unique[vk] != code
            throw Error("different characters '" Chr(unique[vk]) "' and '" Chr(code) "' share physical key vk" Format("{:02X}", vk))
        unique[vk] := code ; [aa] is one physical key, not two notes.
    }
    expected := []
    for vk, code in unique {
        if ExpectedHeld.Has(vk)
            expected.Push({direction: "up", code: ExpectedHeld[vk].code})
        expected.Push({direction: "down", code: code})
        ExpectedHeld[vk] := {code: code, deadline: deadline}
    }
    CharacterEvents := []
    beforePackets := CapturePackets
    PressGroup(codes, deadline)
    Check(CapturePackets = beforePackets + 1, "chord/retrigger must be one emitter packet")
    CheckCapture(expected)
    CheckHeld()
}

ReleaseUntil(timestamp) {
    global ExpectedHeld, CharacterEvents
    loop {
        nextDeadline := timestamp + 1
        for vk, held in ExpectedHeld
            nextDeadline := Min(nextDeadline, held.deadline)
        if nextDeadline > timestamp
            break

        ; Check each release boundary independently from the production state.
        CharacterEvents := []
        ReleaseDue(nextDeadline - 0.001)
        CheckCapture([])
        CheckHeld()
        expected := []
        due := []
        for vk, held in ExpectedHeld {
            if held.deadline <= nextDeadline {
                expected.Push({direction: "up", code: held.code})
                due.Push(vk)
            }
        }
        for vk in due
            ExpectedHeld.Delete(vk)
        CharacterEvents := []
        ReleaseDue(nextDeadline)
        CheckCapture(expected)
        CheckHeld()
    }
}

Capture(sequence) {
    global CharacterEvents, CaptureModifiers, CaptureHeld, CapturePackets, Characters
    CapturePackets += 1
    position := 1
    while found := RegExMatch(sequence, "\{vk([0-9A-F]{2}) (down|up)\}", &token, position) {
        vk := Integer("0x" token[1])
        direction := token[2]
        bit := vk = 0x10 ? 1 : vk = 0x11 ? 2 : vk = 0x12 ? 4 : 0
        if bit {
            if direction = "down"
                CaptureModifiers |= bit
            else
                CaptureModifiers &= ~bit
        } else {
            lookup := CaptureModifiers ":" vk
            Check(Characters.Has(lookup), "unknown emitted US key/modifier " lookup)
            code := Ord(Characters[lookup])
            if direction = "down" {
                Check(!CaptureHeld.Has(vk), "repeated physical key pressed before release")
                CaptureHeld[vk] := code
            } else {
                Check(CaptureHeld.Has(vk), "physical key released without a previous press")
                Check(CaptureHeld[vk] = code, "key-up character does not match key-down")
                CaptureHeld.Delete(vk)
            }
            CharacterEvents.Push({direction: direction, code: code})
        }
        position := found + StrLen(token[0])
    }
}

CheckCapture(expected) {
    global CharacterEvents
    counts := Map()
    for event in expected {
        key := event.direction ":" event.code
        counts[key] := counts.Get(key, 0) + 1
    }
    for event in CharacterEvents {
        key := event.direction ":" event.code
        Check(counts.Get(key, 0) > 0, "unexpected " event.direction " character '" Chr(event.code) "'")
        counts[key] -= 1
    }
    for key, remaining in counts
        Check(remaining = 0, "missing character event " key)
    Check(CharacterEvents.Length = expected.Length, "wrong character event count")
}

CheckHeld() {
    global ExpectedHeld, ExpectedMapping, HeldKeys, CaptureHeld
    Check(HeldKeys.Count = ExpectedHeld.Count, "wrong held-key count")
    Check(CaptureHeld.Count = ExpectedHeld.Count, "wrong captured physical-key count")
    for vk, held in ExpectedHeld {
        Check(HeldKeys.Has(vk), "missing held physical key " vk)
        Check(CaptureHeld.Has(vk) && CaptureHeld[vk] = held.code, "wrong captured held-key character")
        actual := HeldKeys[vk]
        Check(Abs(actual.deadline - held.deadline) < 0.0001, "wrong release deadline")
        Check(actual.modifiers = ExpectedMapping[held.code].modifiers, "wrong held-key modifier")
    }
}

Check(condition, label) {
    if !condition
        throw Error(label)
}
