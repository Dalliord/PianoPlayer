; Physical US-layout keys, independent of the active Windows text input language.
; Held keys have independent release deadlines, so long holds don't slow onsets.
global HeldKeys := Map()
global HeldModifiers := Map()
global USLayout := DllCall("LoadKeyboardLayoutW", "Str", "00000409", "UInt", 0, "Ptr")
global SendMethod := "Event"
global KeyEmitter := SendKeys

MapCodePoint(code) {
    global USLayout
    result := DllCall("VkKeyScanExW", "UShort", code, "Ptr", USLayout, "Short")
    if result = -1
        throw Error("Unsupported keyboard character: " code)
    return {vk: result & 255, modifiers: (result >> 8) & 7}
}

SendKeys(sequence) {
    global SendMethod
    if sequence = ""
        return
    if SendMethod = "Input"
        SendInput("{Blind}" sequence)
    else
        SendEvent("{Blind}" sequence)
}

KeyToken(vk, direction) {
    return "{vk" Format("{:02X}", vk) " " direction "}"
}

PressGroup(codes, deadline) {
    global HeldKeys, HeldModifiers, KeyEmitter
    keys := Map()
    for code in codes {
        mapped := MapCodePoint(code)
        mapped.code := code
        keys[mapped.vk] := mapped
    }
    sequence := ""
    released := Map()
    ; Retriggering the same physical key requires releasing its previous press.
    for vk, mapped in keys {
        if HeldKeys.Has(vk) {
            held := HeldKeys[vk]
            AddToGroup(released, held.modifiers, vk)
            HeldKeys.Delete(vk)
        }
    }
    AppendGroups(released, "up", deadline, &sequence)
    groups := Map()
    for vk, mapped in keys {
        AddToGroup(groups, mapped.modifiers, vk)
        HeldKeys[vk] := {deadline: deadline, modifiers: mapped.modifiers, code: mapped.code}
    }
    ; All chord DOWN events are one packet, with no Sleep or note interval between them.
    ; Modifier transitions within the packet preserve mixed characters such as [ejTu].
    AppendGroups(groups, "down", deadline, &sequence)
    KeyEmitter(sequence)
}

ReleaseDue(now) {
    global HeldKeys, HeldModifiers, KeyEmitter
    due := []
    groups := Map()
    sequence := ""
    for vk, held in HeldKeys {
        if held.deadline <= now {
            AddToGroup(groups, held.modifiers, vk)
            due.Push(vk)
        }
    }
    for vk in due
        HeldKeys.Delete(vk)
    if groups.Count = 0
        return
    ; Browser key-up must have the same character as key-down, including Shift.
    AppendGroups(groups, "up", now, &sequence)
    RestoreHeldModifiers(&sequence)
    KeyEmitter(sequence)
}

SnapshotHeldKeys(now) {
    global HeldKeys
    groups := Map()
    for vk, held in HeldKeys {
        if held.deadline <= now
            continue
        remaining := held.deadline - now
        groupId := Format("{:.6f}", remaining)
        if !groups.Has(groupId)
            groups[groupId] := {keys: [], remaining: remaining}
        groups[groupId].keys.Push(held.code)
    }
    return groups
}

RestoreHeldKeys(groups, now) {
    for groupId, group in groups
        PressGroup(group.keys, now + group.remaining)
}

ReleaseAllKeys() {
    global HeldKeys, HeldModifiers, KeyEmitter
    sequence := ""
    groups := Map()
    for vk, held in HeldKeys
        AddToGroup(groups, held.modifiers, vk)
    AppendGroups(groups, "up", 0, &sequence)
    HeldKeys.Clear()
    AppendModifiers(0, 0, &sequence)
    sequence .= "{Shift up}{Ctrl up}{Alt up}{LWin up}{RWin up}"
    KeyEmitter(sequence)
}

AddToGroup(groups, modifiers, vk) {
    if !groups.Has(modifiers)
        groups[modifiers] := []
    groups[modifiers].Push(vk)
}

AppendGroups(groups, direction, deadline, &sequence) {
    for modifiers, keys in groups {
        AppendModifiers(modifiers, deadline, &sequence)
        for vk in keys
            sequence .= KeyToken(vk, direction)
    }
}

AppendModifiers(modifiers, deadline, &sequence) {
    global HeldModifiers
    ; Explicit modifier transitions for both DOWN and UP; no text or clipboard input.
    for bit, vk in Map(1, 0x10, 2, 0x11, 4, 0x12) {
        if !(modifiers & bit) && HeldModifiers.Has(vk) {
            sequence .= KeyToken(vk, "up")
            HeldModifiers.Delete(vk)
        }
    }
    for bit, vk in Map(1, 0x10, 2, 0x11, 4, 0x12) {
        if modifiers & bit {
            if !HeldModifiers.Has(vk)
                sequence .= KeyToken(vk, "down")
            HeldModifiers[vk] := deadline
        }
    }
}

RestoreHeldModifiers(&sequence) {
    global HeldKeys
    modifiers := 0
    deadline := 0
    for vk, held in HeldKeys {
        modifiers |= held.modifiers
        deadline := Max(deadline, held.deadline)
    }
    AppendModifiers(modifiers, deadline, &sequence)
}
