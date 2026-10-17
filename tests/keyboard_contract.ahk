#Requires AutoHotkey v2.0
#NoTrayIcon
#Include %A_ScriptDir%\..\ahk\input_utils.ahk

; Replace the emitter with a recorder: no physical input is generated in this test.
global Captured := []
global CharacterEvents := []
global CaptureModifiers := 0
global Characters := Map()
loop 94 {
    code := A_Index + 32
    mapped := MapCodePoint(code)
    Characters[mapped.modifiers ":" mapped.vk] := Chr(code)
}
global KeyEmitter := Capture
global Output := FileOpen("*", "w", "UTF-8-RAW")
try {
    mapped := MapCodePoint(65)
    Check(mapped.vk = 0x41 && mapped.modifiers = 1, "uppercase mapping")
    mapped := MapCodePoint(33)
    Check(mapped.vk = 0x31 && mapped.modifiers = 1, "shift symbol mapping")

    PressGroup([97, 115, 100], 35)
    Check(HeldKeys.Count = 3, "chord presses together")
    batch := Captured[Captured.Length]
    Check(InStr(batch, "{vk41 down}") && InStr(batch, "{vk53 down}") && InStr(batch, "{vk44 down}"), "chord down batch")
    ReleaseDue(34)
    Check(HeldKeys.Count = 3, "hold not shortened")
    ReleaseDue(35)
    Check(HeldKeys.Count = 0, "chord releases together")
    batch := Captured[Captured.Length]
    Check(InStr(batch, "{vk41 up}") && InStr(batch, "{vk53 up}") && InStr(batch, "{vk44 up}"), "chord up batch")

    PressGroup([65], 100)
    PressGroup([98], 135)
    Check(HeldKeys.Count = 2, "independent overlapping holds")
    Check(HeldModifiers.Count = 0, "lowercase onset clears previous Shift")
    ReleaseDue(100)
    Check(!HeldKeys.Has(0x41) && HeldKeys.Has(0x42), "independent release deadlines")
    PressGroup([98], 150)
    Check(HeldKeys[0x42].deadline = 150, "repeated key retriggers")
    ReleaseDue(135)
    Check(HeldKeys.Has(0x42), "old repeated release cannot cancel new press")
    ReleaseAllKeys()
    Check(HeldKeys.Count = 0 && HeldModifiers.Count = 0, "stop clears all held keys")

    CharacterEvents := []
    packetStart := Captured.Length
    PressGroup([101, 106, 84, 117], 200) ; [ejTu] from the reported failing position.
    Check(Captured.Length = packetStart + 1, "mixed chord is one packet")
    CheckCharacters("down", ["e", "j", "T", "u"])
    ReleaseDue(199)
    Check(HeldKeys.Count = 4, "200 ms chord hold respected")
    ReleaseDue(200)
    CheckCharacters("up", ["e", "j", "T", "u"])
    Check(HeldKeys.Count = 0 && HeldModifiers.Count = 0, "mixed chord fully released")

    CharacterEvents := []
    PressGroup([100, 69, 117, 119], 400) ; [dEuw] after the failing chord.
    ReleaseAllKeys()
    CheckCharacters("down", ["d", "E", "u", "w"])
    CheckCharacters("up", ["d", "E", "u", "w"])

    CharacterEvents := []
    PressGroup([83], 500)
    PressGroup([97], 550)
    ReleaseDue(500)
    ReleaseDue(550)
    CheckCharacters("down", ["S", "a"])
    CheckCharacters("up", ["S", "a"])

    ; Simulate a paused long chord under a short melody note. The recorder
    ; verifies releases and resumed deadlines; no real key is pressed.
    PressGroup([97, 83, 100], 5000)
    PressGroup([102], 1200)
    paused := SnapshotHeldKeys(1000)
    ReleaseAllKeys()
    Check(HeldKeys.Count = 0 && HeldModifiers.Count = 0, "pause releases long holds")
    CharacterEvents := []
    RestoreHeldKeys(paused, 10000)
    CheckCharacters("down", ["a", "S", "d", "f"])
    Check(HeldKeys[0x41].deadline = 14000 && HeldKeys[0x53].deadline = 14000,
          "resume restores remaining chord duration")
    Check(HeldKeys[0x46].deadline = 10200, "resume preserves independent melody deadline")
    ReleaseDue(10200)
    Check(HeldKeys.Count = 3, "melody release keeps long chord down")
    ReleaseDue(13999)
    Check(HeldKeys.Count = 3, "long chord is not released early after resume")
    ReleaseDue(14000)
    Check(HeldKeys.Count = 0 && HeldModifiers.Count = 0, "resumed chord fully releases")

    PressGroup([97, 115, 100], 60000)
    ReleaseAllKeys()
    Check(HeldKeys.Count = 0 && HeldModifiers.Count = 0, "stop cancels maximum sustain immediately")
    Check(SnapshotHeldKeys(0).Count = 0, "stopped keys cannot be restored by resume")

    Output.Write("OK`tkeyboard contract`n")
    Output.Read(0)
    ExitApp(0)
} catch as err {
    Output.Write("ERROR`t" err.Message "`n")
    Output.Read(0)
    ExitApp(1)
}

Capture(sequence) {
    global Captured, CharacterEvents, CaptureModifiers, Characters
    if sequence != ""
        Captured.Push(sequence)
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
            character := Characters.Get(CaptureModifiers ":" vk, "?")
            CharacterEvents.Push({direction: direction, character: character})
        }
        position := found + StrLen(token[0])
    }
}

CheckCharacters(direction, expected) {
    global CharacterEvents
    found := Map()
    count := 0
    for event in CharacterEvents {
        if event.direction = direction {
            found[event.character] := true
            count += 1
        }
    }
    Check(count = expected.Length, "character count for " direction)
    for character in expected
        Check(found.Has(character), "missing " direction " character: " character)
}

Check(condition, label) {
    if !condition
        throw Error(label)
}
